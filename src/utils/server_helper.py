"""Shared server lifecycle and SSE validation utilities.

Extracted from scripts/server_up.py and scripts/m3_server_smoke.py
to eliminate duplication of health polling, SSE parsing, single-turn
validation, and persistence checks across test and convenience scripts.
"""

import json
import logging
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Literal, TextIO

from utils.log_helper import log_session, print_log

logger = logging.getLogger(__name__)

# src/utils/ → ../../ = project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

HEALTH_TIMEOUT_SEC = 600  # Build + embedding, generous for CI
HEALTH_INTERVAL_SEC = 5
DEFAULT_QUERY = "實驗室的成員有哪些人？"
DEFAULT_FOLLOW_UP = "這些人中，有誰是研究生？"


# ── Server lifecycle ────────────────────────────────────────


def spawn_server(
    host: str,
    port: int,
    config_name: str = "default",
    *,
    output: Literal["inherit", "devnull"] | Path = "devnull",
    cwd: Path = PROJECT_ROOT,
) -> subprocess.Popen:
    """Spawn ``app.run_server()`` as a child process.

    Parameters
    ----------
    host:
        Bind address (used only for logging; the server reads its own).
    port:
        Server port forwarded to ``app.run_server()``.
    config_name:
        Config name forwarded to ``app.run_server()``.
    output:
        Where stdout/stderr go.  ``"inherit"`` shares the parent's fds,
        ``"devnull"`` discards output (default), and a ``Path`` opens the
        file for writing.
    cwd:
        Working directory for the subprocess (defaults to project root).
    """
    assert config_name.isidentifier(), (
        f"config_name must be a valid Python identifier, got {config_name!r}"
    )
    cmd = [
        sys.executable,
        "-c",
        (
            f"from app.server.app import start_uvicorn; "
            f"start_uvicorn(host='{host}', port={port}, "
            f"config_name='{config_name}')"
        ),
    ]

    stdout_kw: int | TextIO | None
    stderr_kw: int | TextIO | None
    if output == "inherit":
        stdout_kw = None  # inherit parent
        stderr_kw = None
    elif output == "devnull":
        stdout_kw = subprocess.DEVNULL
        stderr_kw = subprocess.DEVNULL
    else:  # Path
        # Path → open file for writing; caller is responsible for
        # eventual shutdown via shutdown_server which terminates proc.
        fh = open(output, "w", encoding="utf-8")
        stdout_kw = fh
        stderr_kw = fh

    # Ensure the child process can import app.* even when launched via
    # ``python -c`` (which unlike ``python src/script.py`` does NOT put
    # src/ on sys.path automatically).
    import os

    src_dir = str(PROJECT_ROOT / "src")
    child_env = os.environ.copy()
    existing = child_env.get("PYTHONPATH")
    child_env["PYTHONPATH"] = (
        f"{src_dir}{os.pathsep}{existing}" if existing else src_dir
    )

    logger.info("Spawning server on %s:%d (config=%s)", host, port, config_name)
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=stdout_kw,
        stderr=stderr_kw,
        env=child_env,
    )
    # Attach file handle so shutdown_server can close it.
    if isinstance(output, Path):
        proc._output_fh = fh  # type: ignore[attr-defined]
    return proc


def wait_ready(
    base_url: str,
    timeout: int = HEALTH_TIMEOUT_SEC,
    interval: int = HEALTH_INTERVAL_SEC,
) -> None:
    """Poll ``GET {base_url}/api/health`` until the server is ready.

    Returns elapsed seconds.  Raises ``TimeoutError`` if the deadline
    is exceeded.
    """
    url = f"{base_url}/api/health"
    deadline = time.monotonic() + timeout
    start = time.monotonic()
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=3) as resp:
                if resp.status == 200 and json.loads(resp.read())["status"] == "ok":
                    wait_time = time.monotonic() - start
                    logger.info("Waited server ready for %.1f seconds", wait_time)
                    return
        except (urllib.error.URLError, OSError, json.JSONDecodeError):
            pass
        time.sleep(interval)
    raise TimeoutError(f"server 未就緒（{timeout}s 內 /api/health 未回應）")


def shutdown_server(
    proc: subprocess.Popen,
    sigterm_timeout: int = 10,
    kill_timeout: int = 5,
) -> None:
    """Gracefully terminate then kill *proc* if still alive.

    SIGTERM → wait *sigterm_timeout* → SIGKILL → wait *kill_timeout*.
    If the process already exited, this is a no-op.
    """
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=sigterm_timeout)
    except subprocess.TimeoutExpired:
        logger.warning("SIGTERM timed out, sending SIGKILL")
        proc.kill()
        try:
            proc.wait(timeout=kill_timeout)
        except subprocess.TimeoutExpired:
            logger.error("SIGKILL timed out — process %d may be a zombie", proc.pid)
    # Close parent-side file handle if attached by spawn_server.
    fh = getattr(proc, "_output_fh", None)
    if fh is not None and not fh.closed:
        fh.close()


# ── SSE parsing & validation ────────────────────────────────


def parse_sse_events(body: str) -> list[dict]:
    """Parse an SSE body (``data:`` JSON lines separated by blank lines).

    Returns a list of deserialised event dicts.
    """
    events: list[dict] = []
    for block in body.split("\n\n"):
        data_lines = [
            line[6:] for line in block.split("\n") if line.startswith("data:")
        ]
        if data_lines:
            events.append(json.loads("".join(data_lines)))
    return events


def stream_chat(
    base_url: str,
    query: str,
    thread_id: str | None = None,
    timeout: int = 120,
) -> list[dict]:
    """POST to ``/api/chat`` and return parsed SSE events."""
    payload = json.dumps({"query": query, "thread_id": thread_id}).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return parse_sse_events(resp.read().decode("utf-8"))


def check_single_turn(events: list[dict]) -> dict:
    """Validate single-turn SSE: token events + done as last event.

    The done event must contain a non-empty response with citation URLs,
    a thread_id, and must NOT include a "sources" key (citations are
    embedded in the response text instead).

    Returns ``{"token_count", "response_chars", "thread_id"}``.
    Raises ``AssertionError`` on any validation failure.
    """
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
    if "sources" in done:
        raise AssertionError("done 事件不應包含 sources（已由 response 內引用取代）")

    return {
        "token_count": types.count("token"),
        "response_chars": len(done["response"]),
        "thread_id": done["thread_id"],
    }


# ── Persistence checks ──────────────────────────────────────


def latest_results_json(project_root: Path) -> Path | None:
    """Return the most recent ``chats/*/agent/*/results.json`` by mtime."""
    files = sorted(
        project_root.glob("chats/*/agent/*/results.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[0] if files else None


def check_persistence(
    project_root: Path,
    before: Path | None,
) -> Path:
    """Validate that a new results.json was written after *before*.

    Checks that results are non-empty and contain sources.
    Raises ``AssertionError`` on any validation failure.
    Returns the path to the updated results file.
    """
    after = latest_results_json(project_root)
    if after is None:
        raise AssertionError("找不到 chats/*/agent/*/results.json")
    if before is not None and after.stat().st_mtime <= before.stat().st_mtime:
        raise AssertionError(f"results.json 未更新（{after} mtime 未前進）")
    with after.open(encoding="utf-8") as f:
        data = json.load(f)
    if not data.get("results"):
        raise AssertionError(f"results.json 的 results 為空（{after}）")
    if not data["results"][0].get("sources"):
        raise AssertionError(f"results.json 的 result 缺少 sources（{after}）")
    return after


# ── Server E2E validation ─────────────────────────────────────


def validate_server(
    base_url: str,
    query: str,
    follow_up: str,
) -> None:
    """SSE 單輪/多輪驗證 + 落盤檢查。"""
    project_root = Path(__file__).resolve().parent.parent.parent

    # 1. 落盤 baseline
    before = latest_results_json(project_root)

    # 2. 單輪 SSE
    log_session("Single-turn SSE", style="cyan")
    events = stream_chat(base_url, query)
    single = check_single_turn(events)
    print_log(
        f"token x{single['token_count']} + done, "
        f"{single['response_chars']} chars, "
        f"thread_id={single['thread_id']}"
    )

    # 3. 多輪記憶（同 thread_id 續問）
    log_session("Multi-turn Memory", style="cyan")
    follow_up_events = stream_chat(base_url, follow_up, single["thread_id"])
    follow_up_result = check_single_turn(follow_up_events)
    assert follow_up_result["thread_id"] == single["thread_id"]
    print_log(
        f"follow-up {follow_up_result['response_chars']} chars, thread_id preserved"
    )

    # 4. 落盤驗證
    log_session("Persistence Check", style="cyan")
    after = check_persistence(project_root, before)
    print_log(f"results.json updated: {after}")

    log_session("Server E2E Test Passed", style="green")
