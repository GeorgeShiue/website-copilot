"""Prepare 階段 workflow：網站爬蟲 → 圖片摘要 → RAG 建置，結果 publish 到 data/。

只依賴爬蟲／VLM／RAG 建置相關模組，不 import agent 與 server。
"""

import os
import shutil
import tempfile

from website_copilot.config.image_summarizer_config import ImageSummarizerConfig
from website_copilot.config.pipeline_config import (
    ImageSummarizerRunConfig,
    RAGBuildRunConfig,
    WebsiteCrawlerRunConfig,
)
from website_copilot.config.rag_config import RAGConfig
from website_copilot.config.website_crawler_config import WebsiteCrawlerConfig
from website_copilot.ingestion.augmentation.image_summarizer import (
    ImageSummarizer,
)
from website_copilot.ingestion.crawling.markdown_cleaner import WebpageMarkdownCleaner
from website_copilot.ingestion.crawling.website_crawler import WebsiteCrawler
from website_copilot.retrieval.factory import build_rag
from website_copilot.storage.data_manager import DataManager
from website_copilot.storage.run_context import (
    create_run_context,
    run_workflow_context,
)
from website_copilot.storage.run_persistence import (
    load_latest_results,
    save_generated_exclude_words,
    save_results_as_md,
)
from website_copilot.utils.config_helper import (
    log_config,
    save_module_config_as_toml,
    save_run_config_as_toml,
)
from website_copilot.utils.log_helper import (
    log_run_summary,
    log_run_time,
    log_session,
    reset_run_summary,
)


def run_website_crawler(
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    save: bool = True,
    publish: bool = False,
    run_config: WebsiteCrawlerRunConfig | None = None,
    **config_overrides,
) -> dict[str, dict] | None:
    """執行網站爬蟲工作流程。

    Args:
        config_name: WebsiteCrawlerConfig 名稱（對應 configs/website_crawler/{name}.toml）。
        run_name_use_config_name: 是否使用 config_name 作為 run_name。
        save: 是否將本次執行結果落盤到 runs/（預設 True）。
        publish: 是否將本次執行結果 publish 到 data/（預設 False）。
        run_config: RunConfig 實例（可選，用於落盤 run config toml）。
        **config_overrides: WebsiteCrawlerConfig 覆寫值（含 site_id）。

    Returns:
        爬取結果 dict | None。
    """
    # ----- 初始化設定和路徑 -----
    config = WebsiteCrawlerConfig.from_toml(config_name, **config_overrides)
    run_manager, run_title = create_run_context(
        module="website_crawler",
        config_name=config_name,
        config=config,
        run_name_use_config_name=run_name_use_config_name,
        save=save,
    )
    data_manager = DataManager()

    crawl_results = None
    with run_workflow_context(run_title, run_manager=run_manager):
        # ----- 初始化物件 -----
        log_config(f"{config.__class__.__name__} Loaded from toml", config)
        website_crawler = WebsiteCrawler(
            max_depth=config.max_depth,
            max_pages=config.max_pages,
            content_threshold=config.content_threshold,
            light_mode=config.light_mode,
            wait_for_images=config.wait_for_images,
            cleaner=WebpageMarkdownCleaner(
                model=config.llm_model,
                sample_ratio=config.sample_ratio,
                repeat=config.repeat,
                max_prompt_tokens=config.max_prompt_tokens,
                seed=config.seed,
            ),
        )

        # ---- 執行網站爬蟲 -----
        log_session("Website Crawling", style="cyan")
        crawl_results = website_crawler.crawl_website(
            url=config.url,
            url_patterns=config.url_patterns,
            allowed_domains=config.allowed_domains,
            path_prefix=config.path_prefix,
        )

        # ----- 輸出完成訊息 -----
        if crawl_results is None:
            log_session("Website Crawling Failed", style="red")
            return None
        log_session("Website Crawling Completed", style="cyan")

        # ----- Save（存到 runs/） -----
        if save:
            assert run_manager is not None
            if website_crawler.generation_result is not None:
                save_generated_exclude_words(
                    website_crawler.generation_result,
                    website_crawler.raw_pages,
                    run_manager.run_path,
                )
            run_manager.save_results_as_json(crawl_results)
            save_results_as_md(
                crawl_results, run_manager.results_folder_path, "fit_markdown"
            )
            save_module_config_as_toml(config, run_manager.module_config_toml_path)
            if run_config is not None:
                save_run_config_as_toml(run_config, run_manager.run_config_toml_path)

        # ----- Publish（publish 到 data/） -----
        if publish:
            data_manager.publish_crawl_results(
                site_id=config.site_id,
                results=crawl_results,
            )
            if website_crawler.generation_result is not None:
                data_manager.publish_generated_exclude_words(
                    site_id=config.site_id,
                    generation_result=website_crawler.generation_result,
                    raw_pages=website_crawler.raw_pages,
                )
            data_manager.publish_run_metadata(
                site_id=config.site_id,
                category="raw_webpages",
                config=config,
                run_config=run_config,
                log_path=run_manager.log_path if run_manager is not None else None,
            )

    return crawl_results


def run_image_summarizer(
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    crawl_results: dict[str, dict] | None = None,
    save: bool = True,
    publish: bool = False,
    run_config: ImageSummarizerRunConfig | None = None,
    **config_overrides,
) -> dict[str, dict] | None:
    """執行網頁圖片摘要工作流程。

    Args:
        config_name: ImageSummarizerConfig 名稱（對應 configs/image_summarizer/{name}.toml）。
        run_name_use_config_name: 是否使用 config_name 作為 run_name。
        crawl_results: 爬取結果 dict（可選，None 時從最新結果載入）。
        save: 是否將本次執行結果落盤到 runs/（預設 True）。
        publish: 是否將本次執行結果 publish 到 data/（預設 False）。
        run_config: RunConfig 實例（可選，用於落盤 run config toml）。
        **config_overrides: ImageSummarizerConfig 覆寫值（含 site_id）。

    Returns:
        增強後的爬取結果 dict | None。
    """
    # ----- 初始化設定和路徑 -----
    config = ImageSummarizerConfig.from_toml(config_name, **config_overrides)
    run_manager, run_title = create_run_context(
        module="image_summarizer",
        config_name=config_name,
        config=config,
        run_name_use_config_name=run_name_use_config_name,
        save=save,
    )
    data_manager = DataManager()

    with run_workflow_context(run_title, run_manager=run_manager):
        # ----- 初始化物件 -----
        log_config(f"{config.__class__.__name__} Loaded from toml", config)
        image_summarizer = ImageSummarizer(
            download_timeout=config.download_timeout,
            success_threshold=config.success_threshold,
            max_retries=config.max_retries,
            cache_download_images=config.cache_download_images,
            cache_image_captions=config.cache_image_captions,
        )

        # ----- 獲取最近一次結果 -----
        if crawl_results is None:
            log_session("Loading Latest Results", style="cyan")
            crawl_results = load_latest_results(
                run_manager.base_folder if run_manager is not None else "runs",
                "website_crawler",
            )

        # ---- 執行圖片摘要 -----
        log_session("Image Summarization", style="cyan")
        enhanced_results = image_summarizer.summarize_crawl_results_images(
            crawl_results,
            model=config.model,
            prompt=config.prompt,
            vlm_max_workers=config.vlm_max_workers,
            image_source=config.image_source,
            **config.litellm_kwargs,
        )

        # ----- 輸出完成訊息 -----
        if enhanced_results is None:
            log_session("Image Summarization Failed", style="red")
            return None
        log_session("Image Summarization Completed", style="cyan")

        # ----- Save（存到 runs/） -----
        if save:
            assert run_manager is not None
            run_manager.save_results_as_json(enhanced_results)
            save_results_as_md(
                enhanced_results, run_manager.results_folder_path, "enhanced_markdown"
            )
            save_module_config_as_toml(config, run_manager.module_config_toml_path)
            if run_config is not None:
                save_run_config_as_toml(run_config, run_manager.run_config_toml_path)

        # ----- Publish（publish 到 data/） -----
        if publish:
            data_manager.publish_markdown(
                site_id=config.site_id,
                enhanced_results=enhanced_results,
            )
            data_manager.publish_run_metadata(
                site_id=config.site_id,
                category="webpages",
                config=config,
                run_config=run_config,
                log_path=run_manager.log_path if run_manager is not None else None,
            )

    return enhanced_results


def run_rag_build(
    config_name: str = "default",
    webpages_data_use_latest_results: bool = False,
    save: bool = True,
    publish: bool = False,
    run_name_use_config_name: bool = False,
    run_config: RAGBuildRunConfig | None = None,
    **config_overrides,
) -> None:
    """建構 RAG 並落盤結果。完整包含建立 rag 流程。

    一律重建向量庫，不受既有向量庫是否存在影響；建庫絕不直接寫入
    data/rag/{site_id}/milvus.db，只透過 publish 原子替換。建庫位置：

    - save=True：建在該次 run 的 results/（保留於 runs/）。
    - save=False, publish=True：建在 data/rag/{site_id}/.staging-*，publish 時
      以 rename 移入正式位置，staging 一律刪除。
    - save=False, publish=False：建在系統暫存資料夾，結束時刪除（不留任何檔案）。
    """
    config = RAGConfig.from_toml(config_name, **config_overrides)
    run_manager, run_title = create_run_context(
        module="rag_build",
        config_name=config_name,
        config=config,
        run_name_use_config_name=run_name_use_config_name,
        save=save,
    )
    data_manager = DataManager()

    # ----- 決定向量庫建置位置（save=True 時由 build_rag 依 run_manager 決定）-----
    staging_dir: str | None = None
    if run_manager is None:
        staging_dir = (
            data_manager.create_vector_store_staging(config.site_id)
            if publish
            else tempfile.mkdtemp(prefix="rag_build_")
        )
        config.milvus_uri = os.path.join(staging_dir, "milvus.db")

    try:
        with run_workflow_context(run_title, run_manager=run_manager):
            # ---- 建置 RAG -----
            log_config(f"{config.__class__.__name__} Loaded from toml", config)
            rag = build_rag(
                config=config,
                force_rebuild=True,
                webpages_data_use_latest_results=webpages_data_use_latest_results,
                run_manager=run_manager,
                build_query_engine=False,
            )
            rag.close()

            # ----- 輸出完成訊息 -----
            log_session("RAG Build Completed", style="cyan")

            # ----- Save（存到 runs/；向量庫已由上面 build_rag 決定位置） -----
            if save:
                assert run_manager is not None
                save_module_config_as_toml(config, run_manager.module_config_toml_path)
                if run_config is not None:
                    save_run_config_as_toml(
                        run_config, run_manager.run_config_toml_path
                    )

            # ----- Publish（原子替換到 data/） -----
            if publish:
                if rag.milvus_uri and os.path.exists(rag.milvus_uri):
                    rag_path = data_manager.publish_vector_store(
                        site_id=config.site_id,
                        source_path=rag.milvus_uri,
                        move=staging_dir is not None,
                    )
                    # 發布的 module_config 記錄正式路徑，而非 runs/ 或 staging
                    config.milvus_uri = os.path.join(rag_path, "milvus.db")
                data_manager.publish_run_metadata(
                    site_id=config.site_id,
                    category="rag",
                    config=config,
                    run_config=run_config,
                    log_path=run_manager.log_path if run_manager is not None else None,
                )
    finally:
        if staging_dir is not None:
            shutil.rmtree(staging_dir, ignore_errors=True)


def run_prepare(config_name: str = "default", publish: bool = True) -> None:
    """執行完整 prepare 階段：網站爬蟲 → 圖片摘要 → RAG 建置。

    與 serve 階段以 data/ 目錄為唯一介面：本階段負責寫入，serve 階段只讀取已 publish
    的向量庫。任一階段無產出時提前結束；結束時印出各階段耗時與花費摘要。

    Args:
        config_name: 各階段共用的 config 名稱（對應 configs/{module}/{name}.toml）。
        publish: True 時各階段結果 publish 到 data/（不存 runs/）；False 時只存到
            runs/，不寫入 data/，RAG 以 runs/ 中本次的圖片摘要結果建庫（供測試使用）。
    """
    reset_run_summary()
    save = not publish

    with log_run_time(f"Prepare Workflow ({config_name})"):
        log_session(f"Prepare Workflow ({config_name})", style="purple")

        try:
            # ----- Website Crawler -----
            crawl_results = run_website_crawler(
                config_name=config_name,
                save=save,
                publish=publish,
            )
            if crawl_results is None:
                return

            # ----- Image Summarizer -----
            enhanced_results = run_image_summarizer(
                config_name=config_name,
                crawl_results=crawl_results,
                save=save,
                publish=publish,
            )
            if enhanced_results is None:
                return

            # ----- RAG Build -----
            run_rag_build(
                config_name=config_name,
                webpages_data_use_latest_results=not publish,
                save=save,
                publish=publish,
            )

            # ----- 輸出完成訊息 -----
            log_session("Prepare Workflow Completed", style="cyan")
        finally:
            log_run_summary()
