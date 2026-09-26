"""Prepare 階段入口：網站爬蟲 → 圖片摘要 → RAG 建置，結果 publish 到 data/。

與 serve 階段（src/serve.py）以 data/ 目錄為唯一介面：本階段負責寫入，
serve 階段只讀取已 publish 的向量庫。
"""

from dataclasses import dataclass

from website_copilot.config.pipeline_config import PrepareRunConfig
from website_copilot.pipelines.prepare import (
    run_rag_build,
    run_webpage_image_summarizer,
    run_website_crawler,
)
from website_copilot.utils.log_helper import (
    log_run_summary,
    log_run_time,
    log_session,
    reset_run_summary,
    setup_logging,
)


@dataclass
class PrepareCLI:
    run: PrepareRunConfig


def main(config_name: str = "default") -> None:
    reset_run_summary()

    with log_run_time(f"Prepare Workflow ({config_name})"):
        # ----- 初始化 Prepare Workflow -----
        setup_logging("info")
        log_session(f"Prepare Workflow ({config_name})", style="purple")

        try:
            # ----- Website Crawler -----
            crawl_results = run_website_crawler(
                config_name=config_name,
                save=False,
                publish=True,
            )
            if crawl_results is None:
                return

            # ----- Webpage Image Summarizer -----
            enhanced_results = run_webpage_image_summarizer(
                config_name=config_name,
                crawl_results=crawl_results,
                save=False,
                publish=True,
            )
            if enhanced_results is None:
                return

            # ----- RAG Build -----
            run_rag_build(
                config_name=config_name,
                save=False,
                publish=True,
            )

            # ----- 輸出完成訊息 -----
            log_session("Prepare Workflow Completed", style="cyan")
        finally:
            log_run_summary()


if __name__ == "__main__":
    import tyro

    cli_arg = tyro.cli(PrepareCLI)
    main(config_name=cli_arg.run.config_name)
