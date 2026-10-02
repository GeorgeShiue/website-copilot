"""以 ncucsie 對圖片摘要做一次完整驗證（code cleanup plan「完整驗證」）。

runs/ 沒有 ncucsie 的爬蟲結果，`run image-summarizer ncucsie` 會找不到輸入；
改載入 data/aug_webpages/ncucsie/results.json（含 fit_markdown、images，結構同爬蟲結果）
當輸入，走正式的 run_image_summarizer（跨頁快取、單頁並行、統計表格）。
save=True、publish=False：只寫入 runs/，不覆寫 data/。會呼叫 VLM（約 $0.16）。

用法（於專案根目錄）：
    uv run python docs/exp/memo/webpage_image_summarizer/download_concurrency/validate.py 40
參數為 download_max_workers（summary_max_workers 使用預設值 50）。
"""

import json
import sys

from website_copilot.config.pipeline_config import ImageSummarizerRunConfig
from website_copilot.pipelines.prepare import run_image_summarizer
from website_copilot.utils.log_helper import setup_logging

SOURCE_RESULTS = "data/aug_webpages/ncucsie/results.json"


def main() -> None:
    download_max_workers = int(sys.argv[1])
    setup_logging("debug")
    with open(SOURCE_RESULTS, encoding="utf-8") as f:
        crawl_results = json.load(f)
    run_image_summarizer(
        ImageSummarizerRunConfig(
            site="ncucsie", config_name="default", save=True, publish=False
        ),
        overrides={"init": {"download_max_workers": download_max_workers}},
        crawl_results=crawl_results,
    )


if __name__ == "__main__":
    main()
