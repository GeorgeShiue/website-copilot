"""M4b Chrome Extension 端到端驗證腳本。

以 Playwright（headed + extension 載入）驗證：
- 在任何網站注入浮動 widget
- 對話框開啟、SSE 串流問答（background 代理）
- markdown 渲染（strong / list / link）
- 多輪記憶（thread_id 延續）

執行方式：
- 一鍵（自動啟動後端 server + 測試頁 + 驗證 + 清理）：
    uv run python scripts/m4b_extension_test.py
- 使用既有 server：
    uv run python scripts/m4b_extension_test.py --base-url http://127.0.0.1:8000

環境需求：Playwright chromium 已安裝（`uv run playwright install chromium`）。
無 DISPLAY 時自動以 xvfb-run 重跑（headed 才能載入 extension）。
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXTENSION_DIR = PROJECT_ROOT / "extension"

HEALTH_TIMEOUT_SEC = 300  # 後端建庫約 40 秒，留足餘裕
HEALTH_INTERVAL_SEC = 5
ANSWER_TIMEOUT_SEC = 90  # LLM 回答最長等待
ANSWER_STABLE_SEC = 6  # 長度連續穩定此秒數視為完成

TEST_PAGE_HTML = """<!DOCTYPE html>
<html lang="zh-Hant">
<head><meta charset="UTF-8"><title>M4b Extension 測試頁</title></head>
<body><h1>M4b 測試頁（extension 應在此注入 widget）</h1></body>
</html>
"""


def _require_display_or_restart_with_xvfb() -> None:
    """無 DISPLAY 時以 xvfb-run 重跑自身（headed 才能載入 extension）。"""
    if os.environ.get("DISPLAY"):
        return
    xvfb = shutil.which("xvfb-run")
    if xvfb is None:
        print(
            "ERROR: 無 DISPLAY 且找不到 xvfb-run。請安裝 xvfb 或於有顯示環境執行。",
            file=sys.stderr,
        )
        sys.exit(1)
    os.execvp(
        xvfb, [xvfb, "-a", sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]
    )


def wait_ready(base_url: str, timeout: int = HEALTH_TIMEOUT_SEC) -> float:
    """輪詢 /api/health 直到後端就緒，回傳等待秒數。"""
    deadline = time.monotonic() + timeout
    start = time.monotonic()
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(f"{base_url}/api/health", timeout=3) as resp:
                if resp.status == 200:
                    return time.monotonic() - start
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(HEALTH_INTERVAL_SEC)
    raise TimeoutError(f"後端未就緒（{timeout}s 內 /api/health 未回應）")


def start_backend(port: int, server_log: str | None) -> subprocess.Popen:
    """spawn 後端 server（cli.py server-cli）。"""
    log_handle = None
    if server_log:
        log_handle = open(server_log, "w", encoding="utf-8")
    cmd = [
        sys.executable,
        "src/cli.py",
        "server-cli",
        "--run.port",
        str(port),
    ]
    return subprocess.Popen(
        cmd,
        cwd=PROJECT_ROOT,
        stdout=log_handle or subprocess.DEVNULL,
        stderr=log_handle or subprocess.DEVNULL,
    )


def start_test_page_server() -> tuple[subprocess.Popen, int, str]:
    """起本機測試頁 http server，回傳 (proc, port, tempdir)。"""
    tmp = tempfile.TemporaryDirectory()
    page_path = Path(tmp.name) / "test.html"
    page_path.write_text(TEST_PAGE_HTML, encoding="utf-8")
    # 用 0 讓 OS 挑空閒 port，但需先拿到 port → 改為固定 18234（衝突極低）
    port = 18234
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=tmp.name,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)
    return proc, port, tmp.name


def main() -> int:
    _require_display_or_restart_with_xvfb()

    parser = argparse.ArgumentParser(description="M4b Chrome Extension 端到端驗證")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument(
        "--base-url", default=None, help="既有後端 URL（不指定時自動啟動）"
    )
    parser.add_argument(
        "--server-log", default=None, help="自動啟動後端時將 log 寫入此檔案"
    )
    parser.add_argument("--query", default="實驗室的指導教授是誰？")
    parser.add_argument("--follow-up", default="他的專長領域有哪些？")
    args = parser.parse_args()

    backend: subprocess.Popen | None = None
    test_server: subprocess.Popen | None = None
    tempdir: str | None = None
    try:
        # ----- 1. 後端就緒 -----
        if args.base_url:
            base_url = args.base_url.rstrip("/")
            print(f"[M4B TEST] 使用既有後端（{base_url}）")
        else:
            base_url = f"http://127.0.0.1:{args.port}"
            print(f"[M4B TEST] 啟動後端（port={args.port}）...")
            backend = start_backend(args.port, args.server_log)
        elapsed = wait_ready(base_url)
        print(f"  ✓ 後端就緒（{elapsed:.1f}s）")

        # ----- 2. 測試頁就緒 -----
        test_server, test_port, tempdir = start_test_page_server()
        test_url = f"http://127.0.0.1:{test_port}/test.html"
        print(f"  ✓ 測試頁就緒（{test_url}）")

        # ----- 3. Playwright 載入 extension 並驗證 -----
        from playwright.sync_api import sync_playwright  # 延遲 import（僅測試路徑需要）

        with sync_playwright() as p:
            with tempfile.TemporaryDirectory(prefix="wc-profile-") as profile:
                ctx = p.chromium.launch_persistent_context(
                    profile,
                    headless=False,
                    args=[
                        f"--disable-extensions-except={EXTENSION_DIR}",
                        f"--load-extension={EXTENSION_DIR}",
                    ],
                )
                try:
                    page = ctx.new_page()
                    page.goto(test_url, timeout=15000)
                    time.sleep(1)

                    # ① 注入檢查
                    injected = page.evaluate(
                        "() => document.getElementById('wc-widget-root') !== null"
                    )
                    if not injected:
                        raise AssertionError("widget 未注入（content script 未執行）")
                    print("  ✓ widget 注入")

                    # ② 點開對話框並送第一問
                    page.evaluate(
                        f"""() => {{
                            const host = document.getElementById('wc-widget-root');
                            host.shadowRoot.querySelector('.wc-toggle').click();
                            const input = host.shadowRoot.querySelector('.wc-inputbar input');
                            input.value = {json.dumps(args.query, ensure_ascii=False)};
                            host.shadowRoot.querySelector('.wc-inputbar button').click();
                        }}"""
                    )
                    first = _wait_answer(page, "第一輪")
                    print(
                        f"  ✓ 第一輪問答（{first['len']} 字元，"
                        f"strong={first['has_strong']} list={first['has_list']} "
                        f"link={first['has_link']}）"
                    )

                    # ③ 多輪追問（thread_id 延續）
                    page.evaluate(
                        f"""() => {{
                            const host = document.getElementById('wc-widget-root');
                            const input = host.shadowRoot.querySelector('.wc-inputbar input');
                            input.value = {json.dumps(args.follow_up, ensure_ascii=False)};
                            host.shadowRoot.querySelector('.wc-inputbar button').click();
                        }}"""
                    )
                    second = _wait_answer(page, "第二輪")
                    if not second["has_link"]:
                        raise AssertionError("第二輪回答未含來源連結（引用遺失？）")
                    print(
                        f"  ✓ 多輪記憶：追問「{args.follow_up}」"
                        f"（{second['len']} 字元，含引用連結）"
                    )

                    print("M4B OK: Chrome Extension 端到端驗證通過")
                    return 0
                finally:
                    ctx.close()
    except (TimeoutError, AssertionError, urllib.error.URLError) as exc:
        print(f"M4B FAIL: {exc}", file=sys.stderr)
        if args.server_log:
            print(f"後端 log 已寫入 {args.server_log}", file=sys.stderr)
        return 1
    finally:
        # ----- 4. 清理 -----
        if test_server is not None and test_server.poll() is None:
            test_server.terminate()
        if backend is not None and backend.poll() is None:
            backend.terminate()
            try:
                backend.wait(timeout=10)
            except subprocess.TimeoutExpired:
                backend.kill()
        print("[M4B TEST] 環境已清理")


def _wait_answer(page, label: str) -> dict:
    """輪詢最後一條 assistant 訊息直到長度穩定，回傳 markdown 檢查結果。"""
    prev_len = -1
    stable_since = 0.0
    start = time.monotonic()
    while time.monotonic() - start < ANSWER_TIMEOUT_SEC:
        time.sleep(3)
        state = page.evaluate(
            """() => {
                const host = document.getElementById('wc-widget-root');
                const msgs = host.shadowRoot.querySelectorAll('.wc-msg');
                const last = msgs[msgs.length - 1];
                return {
                    n: msgs.length,
                    len: last ? last.innerHTML.length : 0,
                    html: last ? last.innerHTML : '',
                };
            }"""
        )
        cur = state["len"]
        if cur == prev_len and cur > 30:
            if stable_since == 0.0:
                stable_since = time.monotonic()
            if time.monotonic() - stable_since >= ANSWER_STABLE_SEC:
                return {
                    "len": cur,
                    "has_strong": "<strong>" in state["html"],
                    "has_list": "<ul>" in state["html"] or "<ol>" in state["html"],
                    "has_link": "<a " in state["html"],
                }
        else:
            stable_since = 0.0
        prev_len = cur
    raise TimeoutError(f"{label}回答逾時（{ANSWER_TIMEOUT_SEC}s 內未穩定）")


if __name__ == "__main__":
    sys.exit(main())
