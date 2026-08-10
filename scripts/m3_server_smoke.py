"""M3 聊天伺服器端到端 smoke 驗證腳本。

確認 server 的 SSE 串流問答端到端正常：
- 單輪：逐 token 串流 + done 事件（response / sources / thread_id）
- 多輪：同 thread_id 續問記得上下文
- 落盤：chats/<ts>/agent/<config>/results.json 每輪更新

執行方式：
- 已啟動 server（如 `uv run python src/cli.py server-cli`）：
    uv run python scripts/m3_server_smoke.py
- 一鍵：自動啟動 server → 驗證 → 關閉（含建庫等待，約 40 秒）：
    uv run python scripts/m3_server_smoke.py --start-server
- 自訂參數：
    uv run python scripts/m3_server_smoke.py --base-url http://127.0.0.1:8018 --query "問題"

只使用標準庫（urllib / json / subprocess），與 m0_rag_smoke.py 同屬 scripts/ 慣例。
"""

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_QUERY = "實驗室的成員有哪些人？"
DEFAULT_FOLLOW_UP = "這些人中，有誰是研究生？"
HEALTH_TIMEOUT_SEC = 300  # 建庫約 30 秒 + embedding，留足餘裕
HEALTH_INTERVAL_SEC = 5


def _parse_events(body: str) -> list[dict]:
    """解析 SSE body（data: JSON 行，空行分隔）為事件 dict 列表。"""
    events: list[dict] = []
    for block in body.split("\n\n"):
        data_lines = [
            line[6:] for line in block.split("\n") if line.startswith("data:")
        ]
        if data_lines:
            events.append(json.loads("".join(data_lines)))
    return events


def wait_ready(base_url: str, timeout: int = HEALTH_TIMEOUT_SEC) -> float:
    """輪詢 /api/health 直到 server 就緒，回傳等待秒數。"""
    url = f"{base_url}/api/health"
    deadline = time.monotonic() + timeout
    start = time.monotonic()
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=3) as resp:
                if resp.status == 200 and json.loads(resp.read())["status"] == "ok":
                    return time.monotonic() - start
        except (urllib.error.URLError, OSError, json.JSONDecodeError):
            pass
        time.sleep(HEALTH_INTERVAL_SEC)
    raise TimeoutError(f"server 未就緒（{timeout}s 內 /api/health 未回應）")


def stream_chat(
    base_url: str,
    query: str,
    thread_id: str | None = None,
) -> list[dict]:
    """POST /api/chat 並回傳解析後的 SSE 事件列表。"""
    payload = json.dumps({"query": query, "thread_id": thread_id}).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return _parse_events(resp.read().decode("utf-8"))


def check_single_turn(events: list[dict]) -> dict:
    """驗證單輪 SSE：token 事件 + done 事件（response 含引用 URL / thread_id）。"""
    types = [event["type"] for event in events]
    if "token" not in types:
        raise AssertionError(f"缺少 token 事件（實際事件: {types}）")
    if types[-1] != "done":
        raise AssertionError(f"最後事件應為 done（實際: {types[-1]}）")

    done = events[-1]
    if not done["response"].strip():
        raise AssertionError("done 事件的 response 為空")
    if "sites.google.com" not in done["response"]:
        raise AssertionError(
            "done 事件的 response 未含引用來源 URL（agent 應將引用寫入回覆）"
        )
    if not done["thread_id"]:
        raise AssertionError("done 事件缺少 thread_id")
    # 引用已由 agent 寫入 response；done 事件不再回傳 sources
    if "sources" in done:
        raise AssertionError("done 事件不應包含 sources（已由 response 內引用取代）")

    return {
        "token_count": types.count("token"),
        "response_chars": len(done["response"]),
        "thread_id": done["thread_id"],
    }


def latest_results_json() -> Path | None:
    """回傳最新的 chats/*/agent/*/results.json（依 mtime）。"""
    files = sorted(
        PROJECT_ROOT.glob("chats/*/agent/*/results.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[0] if files else None


def check_persistence(before: Path | None) -> Path:
    """驗證落盤：驗證後最新 results.json 比驗證前新，results 非空且含 sources。"""
    after = latest_results_json()
    if after is None:
        raise AssertionError("找不到 chats/*/agent/*/results.json")
    if before is not None and after.stat().st_mtime <= before.stat().st_mtime:
        raise AssertionError(f"results.json 未更新（{after} mtime 未前進）")
    with after.open(encoding="utf-8") as f:
        data = json.load(f)
    if not data.get("results"):
        raise AssertionError(f"results.json 的 results 為空（{after}）")
    # sources 不回傳前端，但落盤 result 仍須保留
    if not data["results"][0].get("sources"):
        raise AssertionError(f"results.json 的 result 缺少 sources（{after}）")
    return after


def run_server(args: argparse.Namespace) -> subprocess.Popen:
    """spawn `uv run python src/cli.py server-cli` 子程序（cwd=專案根）。"""
    log_handle = None
    if args.server_log:
        log_handle = open(args.server_log, "w", encoding="utf-8")
    cmd = [
        sys.executable,
        "src/cli.py",
        "server-cli",
        "--run.port",
        str(args.port),
    ]
    return subprocess.Popen(
        cmd,
        cwd=PROJECT_ROOT,
        stdout=log_handle or subprocess.DEVNULL,
        stderr=log_handle or subprocess.DEVNULL,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="M3 聊天伺服器端到端 smoke 驗證")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--query", default=DEFAULT_QUERY)
    parser.add_argument("--follow-up", default=DEFAULT_FOLLOW_UP)
    parser.add_argument(
        "--start-server",
        action="store_true",
        help="自動啟動 server（子程序）並於驗證後關閉",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument(
        "--server-log",
        default=None,
        help="--start-server 時將 server log 寫入此檔案（預設丟棄）",
    )
    args = parser.parse_args()

    base_url = args.base_url
    proc: subprocess.Popen | None = None
    try:
        if args.start_server:
            base_url = f"http://{args.host}:{args.port}"
            print(f"[M3 SERVER SMOKE] 啟動 server（port={args.port}）...")
            proc = run_server(args)
        else:
            print(f"[M3 SERVER SMOKE] 使用既有 server（{base_url}）")

        elapsed = wait_ready(base_url)
        print(f"  ✓ server 就緒（/api/health，{elapsed:.1f}s）")

        # 落盤 baseline：驗證前最新 results.json
        before = latest_results_json()

        # 單輪驗證
        events = stream_chat(base_url, args.query)
        single = check_single_turn(events)
        print(
            f"  ✓ 單輪 SSE：token x{single['token_count']} + done，"
            f"response {single['response_chars']} 字元（含引用 URL）、"
            f"thread_id={single['thread_id']}"
        )

        # 多輪驗證：以 done 回傳的 thread_id 續問
        follow_up_events = stream_chat(base_url, args.follow_up, single["thread_id"])
        follow_up = check_single_turn(follow_up_events)
        print(
            f"  ✓ 多輪記憶：同 thread 續問「{args.follow_up}」"
            f"（response {follow_up['response_chars']} 字元，含引用 URL）"
        )

        # 落盤驗證
        after = check_persistence(before)
        print(f"  ✓ 落盤：{after.relative_to(PROJECT_ROOT)} 已更新（results 非空）")

        print("SMOKE OK: M3 server 端到端驗證通過")
        return 0
    except (
        TimeoutError,
        AssertionError,
        urllib.error.URLError,
        json.JSONDecodeError,
    ) as exc:
        print(f"SMOKE FAIL: {exc}", file=sys.stderr)
        if args.server_log:
            print(
                f"server log 已寫入 {args.server_log}（可查看建庫/錯誤細節）",
                file=sys.stderr,
            )
        return 1
    finally:
        if proc is not None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    sys.exit(main())
