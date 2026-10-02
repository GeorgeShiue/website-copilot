"""VLM 並行上限實驗（code cleanup plan C2「並行上限實驗」）。

以正式的 ImageSummarizer 呼叫路徑（修正後的 semaphore 控制並行數），
對同一張圖片送出 2N 個摘要請求，逐級提高 summary_max_workers=N，直到出現失敗或跑完所有級距。

- 關閉自動重試（litellm_kwargs max_retries=0），讓 429 直接以失敗呈現。
- 以包裝函式取代模組的 acompletion，記錄每個請求的時間、結果、例外與 x-ratelimit-* header。
- 輸出：raw.jsonl（每請求一行）、summary.jsonl（每級一行），皆為附加寫入。

用法（於專案根目錄）：
    uv run python docs/exp/memo/webpage_image_summarizer/vlm_concurrency/probe.py --dry-run --levels 20 30 --gap 1 --out <暫存資料夾>
    uv run python docs/exp/memo/webpage_image_summarizer/vlm_concurrency/probe.py --levels 20
    uv run python docs/exp/memo/webpage_image_summarizer/vlm_concurrency/probe.py --levels 30 40 50 60 70 80 90 100
"""

import argparse
import asyncio
import json
import os
import random
import statistics
import time
from datetime import datetime
from types import SimpleNamespace
from typing import Any

from website_copilot.config.image_summarizer_config import ImageSummarizerConfig
from website_copilot.ingestion.augmentation import image_summarizer as module
from website_copilot.ingestion.augmentation.image_summarizer import ImageSummarizer

IMAGE_URL = "https://www.csie.ncu.edu.tw/static/file/13/1013/img/NCU_WASN_Lab.png"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
REQUESTS_PER_WORKER = 2


class Recorder:
    """包裝 acompletion：記錄每個請求並統計同時進行中的最大數量。"""

    def __init__(self, acompletion: Any) -> None:
        self._acompletion = acompletion
        self.records: list[dict[str, Any]] = []
        self.in_flight = 0
        self.peak = 0

    async def __call__(self, **kwargs: Any) -> Any:
        self.in_flight += 1
        self.peak = max(self.peak, self.in_flight)
        record: dict[str, Any] = {"start": time.monotonic()}
        try:
            response = await self._acompletion(**kwargs)
        except Exception as e:
            record.update(
                ok=False,
                error=type(e).__name__,
                status_code=getattr(e, "status_code", None),
                message=str(e)[:300],
            )
            raise
        else:
            hidden = getattr(response, "_hidden_params", None) or {}
            headers = hidden.get("additional_headers") or {}
            usage = getattr(response, "usage", None)
            record.update(
                ok=True,
                cost_usd=_cost(response),
                prompt_tokens=getattr(usage, "prompt_tokens", None),
                completion_tokens=getattr(usage, "completion_tokens", None),
                ratelimit={k: v for k, v in headers.items() if "ratelimit" in k},
            )
            return response
        finally:
            self.in_flight -= 1
            record["end"] = time.monotonic()
            record["latency"] = record["end"] - record["start"]
            self.records.append(record)


def _cost(response: Any) -> float:
    try:
        return float(module.completion_cost(completion_response=response))
    except Exception:
        return 0.0


async def _fake_acompletion(**_kwargs: Any) -> Any:
    """--dry-run 用：不呼叫 API，模擬 0.2～0.5 秒延遲。"""
    await asyncio.sleep(random.uniform(0.2, 0.5))
    message = SimpleNamespace(content="caption")
    return SimpleNamespace(
        choices=[SimpleNamespace(message=message)],
        usage=SimpleNamespace(prompt_tokens=0, completion_tokens=0, total_tokens=0),
        _hidden_params={"additional_headers": {}},
    )


def _percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(round(q * (len(ordered) - 1))))]


def run_level(
    summarizer: ImageSummarizer,
    image_base64_url: str,
    workers: int,
    dry_run: bool,
    out_dir: str,
) -> dict[str, Any]:
    recorder = Recorder(_fake_acompletion if dry_run else module.acompletion)
    original = module.acompletion
    module.acompletion = recorder
    if dry_run:
        original_cost = module.completion_cost
        module.completion_cost = lambda **_: 0.0
    try:
        summarizer.summary_max_workers = workers
        images = {
            f"{IMAGE_URL}#{i}": image_base64_url
            for i in range(workers * REQUESTS_PER_WORKER)
        }
        started = time.monotonic()
        asyncio.run(summarizer._agenerate_image_captions(images))
        wall = time.monotonic() - started
    finally:
        module.acompletion = original
        if dry_run:
            module.completion_cost = original_cost

    records = recorder.records
    ok = [r for r in records if r["ok"]]
    failed = [r for r in records if not r["ok"]]
    latencies = [r["latency"] for r in ok] or [0.0]
    last_ratelimit = max(ok, key=lambda r: r["end"])["ratelimit"] if ok else {}
    min_remaining = {
        key: min(
            (int(r["ratelimit"][key]) for r in ok if key in r["ratelimit"]),
            default=None,
        )
        for key in last_ratelimit
        if "remaining" in key
    }
    summary = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "dry_run": dry_run,
        "workers": workers,
        "requests": len(records),
        "success": len(ok),
        "failure": len(failed),
        "errors": sorted({f"{r['error']}({r['status_code']})" for r in failed}),
        "peak_concurrency": recorder.peak,
        "latency_p50": round(statistics.median(latencies), 2),
        "latency_p95": round(_percentile(latencies, 0.95), 2),
        "latency_max": round(max(latencies), 2),
        "wall_seconds": round(wall, 2),
        "cost_usd": round(sum(r.get("cost_usd", 0.0) for r in ok), 6),
        "avg_prompt_tokens": _mean(ok, "prompt_tokens"),
        "avg_completion_tokens": _mean(ok, "completion_tokens"),
        "ratelimit_last": last_ratelimit,
        "ratelimit_min_remaining": min_remaining,
    }

    with open(os.path.join(out_dir, "raw.jsonl"), "a", encoding="utf-8") as f:
        for r in records:
            row = {k: v for k, v in r.items() if k not in ("start", "end")}
            row.update(workers=workers, dry_run=dry_run, start=r["start"] - started)
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    with open(os.path.join(out_dir, "summary.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(summary, ensure_ascii=False) + "\n")
    return summary


def _mean(records: list[dict[str, Any]], key: str) -> float | None:
    values = [r[key] for r in records if r.get(key) is not None]
    return round(statistics.mean(values), 1) if values else None


def main() -> None:
    parser = argparse.ArgumentParser(description="VLM 並行上限實驗")
    parser.add_argument("--levels", type=int, nargs="+", required=True)
    parser.add_argument("--gap", type=float, default=60.0, help="兩級之間等待秒數")
    parser.add_argument("--dry-run", action="store_true", help="以 fake VLM 執行")
    parser.add_argument("--out", default=OUT_DIR, help="raw／summary 輸出資料夾")
    args = parser.parse_args()

    config = ImageSummarizerConfig.from_yaml("default")
    summarizer = ImageSummarizer(
        download_timeout=config.init.download_timeout,
        download_max_workers=config.init.download_max_workers,
        success_threshold=config.init.success_threshold,
        max_retries=0,
    )
    # 以空爬取結果走一次公開流程：完成 model／API key 解析並設定 prompt 與 litellm 參數
    summarizer.summarize_crawl_results_images(
        {},
        model=config.summarize.model,
        prompt=config.summarize.prompt,
        summary_max_workers=args.levels[0],
        image_source=config.summarize.image_source,
        **{**config.litellm_kwargs, "max_retries": 0},
    )
    image_base64_url = summarizer._download_image(IMAGE_URL)
    if image_base64_url is None:
        raise SystemExit(f"圖片下載失敗：{IMAGE_URL}")

    print(f"model={config.summarize.model} image={IMAGE_URL} dry_run={args.dry_run}")
    for index, workers in enumerate(args.levels):
        if index > 0:
            print(f"等待 {args.gap:.0f} 秒讓每分鐘額度重置…")
            time.sleep(args.gap)
        summary = run_level(
            summarizer, image_base64_url, workers, args.dry_run, args.out
        )
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        if summary["failure"]:
            print(f"N={workers} 出現失敗，停止。")
            break


if __name__ == "__main__":
    main()
