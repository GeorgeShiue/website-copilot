"""聊天伺服器啟動腳本：一條指令完成「啟動 + 等待就緒 + 保持運行」。

執行：
    uv run python scripts/server_up.py [--port 8000] [--config-name test] [--server-log FILE]

行為：
1. 啟動 `uv run python src/cli.py server-cli`（背景子程序）
2. 輪詢 /api/health 直到就緒（最長 300 秒，建庫約 40 秒）
3. 列印 READY 後保持運行（供瀏覽器手動測試）
4. Ctrl+C 結束：自動 terminate 子程序並確認釋放（解決直接跑 cli.py 時 Ctrl+C 關不乾淨的問題）

只使用標準庫 + tyro / rich（專案既有依賴），與 scripts/ 慣例一致。
"""

import json
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import tyro

# scripts/ 慣例：讓 app.* / utils.* 可 import（與 m0_rag_smoke.py 一致）
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from utils.log_helper import log_run_time, log_session, print_log

PROJECT_ROOT = Path(__file__).resolve().parent.parent

HEALTH_TIMEOUT_SEC = 300  # 建庫約 30 秒 + embedding，留足餘裕
HEALTH_INTERVAL_SEC = 5


@dataclass
class ServerUpConfig:
    """聊天伺服器啟動參數。"""

    # ----- server config -----
    host: str = "127.0.0.1"
    port: int = 8000
    config_name: str = "default"  # AgentConfig 名稱（對應 configs/agent/{name}.toml）
    server_log: str | None = None  # 將 server log 寫入此檔案（預設繼承本終端機輸出）


def wait_ready(base_url: str, timeout: int = HEALTH_TIMEOUT_SEC) -> float:
    """輪詢 /api/health 直到 server 就緒，回傳等待秒數。"""
    deadline = time.monotonic() + timeout
    start = time.monotonic()
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(f"{base_url}/api/health", timeout=3) as resp:
                if resp.status == 200 and json.loads(resp.read())["status"] == "ok":
                    return time.monotonic() - start
        except (urllib.error.URLError, OSError, json.JSONDecodeError):
            pass
        time.sleep(HEALTH_INTERVAL_SEC)
    raise TimeoutError(f"server 未就緒（{timeout}s 內 /api/health 未回應）")


def _raise_interrupt(signum: int, frame: object) -> None:
    """SIGINT/SIGTERM handler：以 KeyboardInterrupt 觸發統一清理流程。"""
    raise KeyboardInterrupt


def main() -> int:
    args = tyro.cli(ServerUpConfig)

    base_url = f"http://{args.host}:{args.port}"
    cmd = [
        sys.executable,
        "src/cli.py",
        "server-cli",
        "--run.port",
        str(args.port),
        "--run.config-name",
        args.config_name,
    ]

    log_handle = None
    if args.server_log:
        log_handle = open(args.server_log, "w", encoding="utf-8")

    # stdout/stderr 傳 None 表示繼承父程序（能看到建庫進度）；指定 server-log 時寫檔
    proc = subprocess.Popen(
        cmd,
        cwd=PROJECT_ROOT,
        stdout=log_handle or None,
        stderr=log_handle or None,
    )
    try:
        with log_run_time("Server"):
            log_session("Starting Server", style="purple")
            print_log(f"[cyan]{base_url}[/cyan]")
            elapsed = wait_ready(base_url)
            log_session("Server Ready", style="green")
            print_log(
                f"[bold green]驗證通過[/bold green]，瀏覽器開啟 [cyan]{base_url}/[/cyan]（啟動花費 {elapsed:.1f}s，使用 Ctrl+C 關閉）"
            )
            proc.wait()  # 保持運行，直到 Ctrl+C
    except TimeoutError as exc:
        print_log(f"[bold red]FAIL: {exc}[/bold red]")
        return 1
    except KeyboardInterrupt:
        log_session("Sever Shutting Down", style="yellow")
        print_log("收到終止訊號，關閉 server...")
    finally:
        if log_handle:
            log_handle.close()
        if proc.poll() is None:
            # SIGTERM → uvicorn 優雅關閉（lifespan shutdown 會釋放 agent 資源）
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
        log_session("Server Stopped", style="red")
    return 0


if __name__ == "__main__":
    # 統一處理 SIGINT（Ctrl+C）與 SIGTERM（kill/關終端機），皆走 KeyboardInterrupt 清理
    signal.signal(signal.SIGINT, _raise_interrupt)
    signal.signal(signal.SIGTERM, _raise_interrupt)
    sys.exit(main())
