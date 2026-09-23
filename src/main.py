from dataclasses import dataclass

from app.configs.workflow_config import MainRunConfig
from app.workflow.workflow import (
    run_rag_build,
    run_webpage_image_summarizer,
    run_website_crawler,
)
from utils.log_helper import (
    log_main_workflow_run_summary,
    log_run_time,
    log_session,
    reset_run_summary,
    setup_logging,
)


@dataclass
class MainCLI:
    run: MainRunConfig


def main(config_name: str = "default") -> None:
    reset_run_summary()

    with log_run_time(f"Main Workflow ({config_name})"):
        # ----- 初始化 Main Workflow -----
        setup_logging("info")
        log_session(f"Main Workflow ({config_name})", style="purple")

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
                force_rebuild=True,
                save=False,
                publish=True,
            )

            # ----- 輸出完成訊息 -----
            log_session("Main Workflow Completed", style="cyan")
        finally:
            log_main_workflow_run_summary()

    # 暫時移除 Chat Server 的啟動，避免在測試時啟動 server
    # # ----- Chat Server -----
    # server, chat_app = run_app(config_name="default")  # server 不因網站變更 config

    # try:
    #     server.run()
    # except KeyboardInterrupt:
    #     pass
    # finally:
    #     chat_app.close()
    #     log_session("Server Stopped", style="cyan")


if __name__ == "__main__":
    import tyro

    cli_arg = tyro.cli(MainCLI)
    main(config_name=cli_arg.run.config_name)
