"""下載並行上限實驗（code cleanup plan C2「後續：下載並行上限實驗」）。

以正式的 ImageSummarizer._download_images 對 ncucsie 的圖片送出 2N 個下載請求
（一次傳入全部 URL，繞過正式流程「每頁各自一個執行緒池」的限制），
逐級提高 download_max_workers=N，直到某一級失敗率超過門檻或跑完所有級距。

- URL：取自 data/aug_webpages/ncucsie/results.json，排除固定失敗（404、不支援的格式）與第三方主機，
  僅留 www.csie.ncu.edu.tw 上確定可下載的圖片，失敗即代表限流或伺服器壓力。
- 量測：包裝 _download_image，記錄每個請求的時間、成功或失敗、失敗原因、位元組數。
- 停止條件：某一級失敗率 > --max-failure-rate（預設 0.2，對齊 success_threshold 0.8）。
- 輸出：raw.jsonl（每請求一行）、summary.jsonl（每級一行），皆為附加寫入。

用法（於專案根目錄）：
    # 乾跑（不連網；--fail-from 模擬從該級開始限流，用來驗證停止條件）
    uv run python docs/exp/memo/webpage_image_summarizer/download_concurrency/probe.py \\
        --dry-run --levels 20 30 40 50 --gap 1 --out <暫存資料夾> [--fail-from 40]
    # 正式
    uv run python docs/exp/memo/webpage_image_summarizer/download_concurrency/probe.py \\
        --levels 20 30 40 50
"""

import argparse
import json
import os
import random
import re
import statistics
import threading
import time
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

from website_copilot.config.image_summarizer_config import ImageSummarizerConfig
from website_copilot.ingestion.augmentation.image_summarizer import (
    UNSUPPORTED_IMAGE_SUFFIXES,
    ImageSummarizer,
    PageStats,
)
from website_copilot.utils.text_helper import MARKDOWN_IMAGE_PATTERN

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_RESULTS = "data/aug_webpages/ncucsie/results.json"
HOST = "www.csie.ncu.edu.tw"
# 上一次完整執行（data/aug_webpages/ncucsie/terminal.log「Failed Images」）的固定失敗圖片
KNOWN_BAD_SUBSTRINGS = (
    "pdf.gif%20",  # 404
    "doc.gif%20",  # 404
    "%E8%AB%8B%E6%9B%BF%E6%8F%9B",  # 「請替換」資料夾下 4 張地圖，404
)
REQUESTS_PER_WORKER = 2
# 限流或伺服器壓力造成的失敗（其餘歸為 other）
THROTTLE_PATTERN = re.compile(
    r"HTTP Error (429|403|503)|timed out|reset|refused|EOF|Remote end closed",
    re.IGNORECASE,
)


def usable_urls(path: str = SOURCE_RESULTS) -> list[str]:
    """ncucsie 上確定可下載的不重複圖片 URL（依首次出現順序）。"""
    with open(path, encoding="utf-8") as f:
        pages = json.load(f)
    urls: dict[str, None] = {}
    for page in pages.values():
        for url in MARKDOWN_IMAGE_PATTERN.findall(page.get("fit_markdown", "")):
            parsed = urlparse(url)
            if parsed.netloc != HOST:
                continue
            if parsed.path.lower().endswith(UNSUPPORTED_IMAGE_SUFFIXES):
                continue
            if any(bad in url for bad in KNOWN_BAD_SUBSTRINGS):
                continue
            urls[url] = None
    return list(urls)


class Recorder:
    """包裝 summarizer._download_image：記錄每個請求並統計同時進行中的最大數量。"""

    def __init__(self, summarizer: ImageSummarizer, fake: Any = None) -> None:
        self._summarizer = summarizer
        self._download = fake or summarizer._download_image
        self._lock = threading.Lock()
        self.records: list[dict[str, Any]] = []
        self.in_flight = 0
        self.peak = 0

    def __call__(self, url: str) -> str | None:
        with self._lock:
            self.in_flight += 1
            self.peak = max(self.peak, self.in_flight)
        start = time.monotonic()
        try:
            result = self._download(url)
        finally:
            end = time.monotonic()
            with self._lock:
                self.in_flight -= 1
        reason = None
        if result is None:
            reason = self._summarizer._download_failure_reasons.get(url, "unknown")
        with self._lock:
            self.records.append(
                {
                    "url": url,
                    "ok": result is not None,
                    "reason": reason,
                    "bytes": len(result) * 3 // 4 if result else 0,
                    "start": start,
                    "end": end,
                    "latency": end - start,
                }
            )
        return result


def _percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(round(q * (len(ordered) - 1))))]


def make_fake_download(
    summarizer: ImageSummarizer, workers: int, fail_from: int | None
) -> Any:
    """--dry-run 用：不連網，模擬 0.05～0.15 秒延遲；fail_from 以上的級距模擬 429。"""

    def fake(url: str) -> str | None:
        time.sleep(random.uniform(0.05, 0.15))
        if fail_from is not None and workers >= fail_from:
            summarizer._download_failure_reasons[url] = (
                "HTTP Error 429: Too Many Requests"
            )
            return None
        return "data:image/png;base64," + "A" * 400

    return fake


def run_level(
    summarizer: ImageSummarizer,
    all_urls: list[str],
    workers: int,
    seen: set[str],
    dry_run: bool,
    fail_from: int | None,
    out_dir: str,
) -> dict[str, Any]:
    urls = list(all_urls)
    random.Random(workers).shuffle(urls)
    urls = urls[: workers * REQUESTS_PER_WORKER]
    repeated = sum(1 for u in urls if u in seen)
    seen.update(urls)

    summarizer.download_max_workers = workers
    summarizer._image_cache = {}
    summarizer._failed_images = {}
    summarizer._download_failure_reasons = {}
    summarizer._page_stats = PageStats()
    summarizer._current_page = f"probe-N{workers}"

    fake = make_fake_download(summarizer, workers, fail_from) if dry_run else None
    recorder = Recorder(summarizer, fake)
    original = summarizer._download_image
    summarizer._download_image = recorder  # type: ignore[method-assign]
    try:
        started = time.monotonic()
        summarizer._download_images(urls)
        wall = time.monotonic() - started
    finally:
        summarizer._download_image = original  # type: ignore[method-assign]

    records = recorder.records
    ok = [r for r in records if r["ok"]]
    failed = [r for r in records if not r["ok"]]
    latencies = [r["latency"] for r in ok] or [0.0]
    total_bytes = sum(r["bytes"] for r in ok)
    reasons: dict[str, int] = {}
    for r in failed:
        reasons[r["reason"]] = reasons.get(r["reason"], 0) + 1
    throttle = sum(1 for r in failed if THROTTLE_PATTERN.search(r["reason"] or ""))
    summary = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "dry_run": dry_run,
        "workers": workers,
        "requests": len(records),
        "repeated_from_earlier_levels": repeated,
        "success": len(ok),
        "failure": len(failed),
        "failure_rate": round(len(failed) / max(1, len(records)), 4),
        "throttle_failures": throttle,
        "failure_reasons": reasons,
        "peak_concurrency": recorder.peak,
        "latency_p50": round(statistics.median(latencies), 2),
        "latency_p95": round(_percentile(latencies, 0.95), 2),
        "latency_max": round(max(latencies), 2),
        "wall_seconds": round(wall, 2),
        "images_per_second": round(len(ok) / wall, 2) if wall else None,
        "total_mb": round(total_bytes / 1e6, 2),
        "mb_per_second": round(total_bytes / 1e6 / wall, 2) if wall else None,
        "avg_kb": round(total_bytes / 1024 / max(1, len(ok)), 1),
    }

    with open(os.path.join(out_dir, "raw.jsonl"), "a", encoding="utf-8") as f:
        for r in records:
            row = {k: v for k, v in r.items() if k not in ("start", "end")}
            row.update(
                workers=workers,
                dry_run=dry_run,
                start=round(r["start"] - started, 3),
                end=round(r["end"] - started, 3),
            )
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    with open(os.path.join(out_dir, "summary.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(summary, ensure_ascii=False) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="下載並行上限實驗")
    parser.add_argument("--levels", type=int, nargs="+", required=True)
    parser.add_argument("--gap", type=float, default=60.0, help="兩級之間等待秒數")
    parser.add_argument(
        "--max-failure-rate", type=float, default=0.2, help="超過即停止（預設 0.2）"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="不連網，以 fake 下載執行"
    )
    parser.add_argument("--fail-from", type=int, help="dry-run：從此級距起模擬 429")
    parser.add_argument("--out", default=OUT_DIR, help="raw／summary 輸出資料夾")
    args = parser.parse_args()

    urls = usable_urls()
    needed = max(args.levels) * REQUESTS_PER_WORKER
    print(f"可用 URL {len(urls)} 個（{HOST}）；最大級距需要 {needed} 個請求")
    if len(urls) < needed:
        raise SystemExit("可用 URL 不足，無法在同一級內避免重複")

    config = ImageSummarizerConfig.from_yaml("default")
    summarizer = ImageSummarizer(
        download_timeout=config.init.download_timeout,
        download_max_workers=args.levels[0],
        success_threshold=config.init.success_threshold,
        max_retries=0,
    )
    print(
        f"download_timeout={config.init.download_timeout}s dry_run={args.dry_run} "
        f"stop_if_failure_rate>{args.max_failure_rate}"
    )

    seen: set[str] = set()
    for index, workers in enumerate(args.levels):
        if index > 0:
            print(f"等待 {args.gap:.0f} 秒讓限流視窗重置…")
            time.sleep(args.gap)
        summary = run_level(
            summarizer, urls, workers, seen, args.dry_run, args.fail_from, args.out
        )
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        if summary["failure_rate"] > args.max_failure_rate:
            print(
                f"N={workers} 失敗率 {summary['failure_rate']:.0%} "
                f"> {args.max_failure_rate:.0%}，停止。"
            )
            break
        if summary["failure"]:
            print(f"N={workers} 有 {summary['failure']} 個失敗（未超過門檻），繼續。")


if __name__ == "__main__":
    main()
