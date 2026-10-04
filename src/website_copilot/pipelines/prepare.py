"""Prepare 階段 workflow：網站爬蟲 → augmenter（圖片摘要、文件）→ RAG 建置，結果 publish 到 data/。

只依賴爬蟲／VLM／RAG 建置相關模組，不 import agent 與 server。
"""

import os
import shutil
import tempfile
from typing import Any

from website_copilot.config.augmenter_config import AugmenterConfig
from website_copilot.config.pipeline_config import (
    AugmenterRunConfig,
    PrepareRunConfig,
    RAGBuildRunConfig,
    WebsiteCrawlerRunConfig,
)
from website_copilot.config.rag_config import RAGConfig
from website_copilot.config.site_config import SiteConfig
from website_copilot.config.website_crawler_config import WebsiteCrawlerConfig
from website_copilot.ingestion.augmentation.augmenter import Augmenter
from website_copilot.ingestion.augmentation.documents import DocumentOptions
from website_copilot.ingestion.crawling.markdown_cleaner import WebpageMarkdownCleaner
from website_copilot.ingestion.crawling.website_crawler import WebsiteCrawler
from website_copilot.retrieval.factory import build_rag, build_target
from website_copilot.storage.data_manager import DataManager
from website_copilot.storage.data_paths import (
    AUG_WEBPAGES,
    FILES_FOLDER,
    RAW_WEBPAGES,
    vector_store_name,
)
from website_copilot.storage.run_context import (
    create_run_context,
    publish_log_file,
    run_workflow_context,
)
from website_copilot.storage.run_persistence import (
    load_latest_results,
    save_document_files,
    save_generated_exclude_words,
    save_results_as_md,
)
from website_copilot.utils.config_helper import log_config, save_run_configs
from website_copilot.utils.http_downloader import HttpDownloader
from website_copilot.utils.log_helper import (
    log_run_summary,
    log_run_time,
    log_session,
    print_log,
    reset_run_summary,
)


def run_website_crawler(
    run_config: WebsiteCrawlerRunConfig,
    overrides: dict[str, Any] | None = None,
) -> dict[str, dict] | None:
    """執行網站爬蟲工作流程。

    Args:
        run_config: 執行參數（site 對應 configs/sites/{site}.yml；config_name 對應
            configs/website_crawler/{name}.yml；save 落盤到 runs/、publish 發布到 data/）。
        overrides: WebsiteCrawlerConfig 的巢狀覆寫值。

    Returns:
        爬取結果 dict | None。
    """
    # ----- 初始化設定和路徑 -----
    save, publish = run_config.save, run_config.publish
    site = SiteConfig.from_yaml(run_config.site)
    config = WebsiteCrawlerConfig.from_yaml(run_config.config_name, overrides)
    run_manager, run_title = create_run_context(
        module="website_crawler",
        config_name=run_config.config_name,
        site_id=site.site_id,
        config=config,
        run_name_use_config_name=run_config.run_name_use_config_name,
        save=save,
    )
    data_manager = DataManager()

    crawl_results = None
    with publish_log_file(run_manager, publish) as log_path:
        with run_workflow_context(
            run_title, run_manager=run_manager, log_path=log_path
        ):
            # ----- 初始化物件 -----
            log_config("SiteConfig Loaded from yaml", site)
            log_config(f"{config.__class__.__name__} Loaded from yaml", config)
            website_crawler = WebsiteCrawler(
                max_depth=config.init.max_depth,
                max_pages=config.init.max_pages,
                content_threshold=config.init.content_threshold,
                light_mode=config.init.light_mode,
                wait_for_images=config.init.wait_for_images,
                cleaner=WebpageMarkdownCleaner(
                    model=config.clean.llm_model,
                    sample_ratio=config.clean.sample_ratio,
                    repeat=config.clean.repeat,
                    max_prompt_tokens=config.clean.max_prompt_tokens,
                    seed=config.clean.seed,
                ),
            )

            # ---- 執行網站爬蟲 -----
            log_session("Website Crawling", style="cyan")
            crawl_results = website_crawler.crawl_website(
                url=site.crawl.url,
                url_patterns=site.crawl.url_patterns,
                allowed_domains=site.crawl.allowed_domains,
                path_prefix=site.crawl.path_prefix,
                document_url_patterns=site.documents.url_patterns,
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
                save_run_configs(run_manager.run_path, config, site, run_config)

            # ----- Publish（publish 到 data/） -----
            if publish:
                data_manager.publish_crawl_results(
                    site_id=site.site_id,
                    results=crawl_results,
                )
                if website_crawler.generation_result is not None:
                    data_manager.publish_generated_exclude_words(
                        site_id=site.site_id,
                        generation_result=website_crawler.generation_result,
                        raw_pages=website_crawler.raw_pages,
                    )

        # ----- Publish run metadata：log 要在 workflow context 結束後才完整 -----
        if publish:
            data_manager.publish_run_metadata(
                site_id=site.site_id,
                category=RAW_WEBPAGES,
                config=config,
                site=site,
                run_config=run_config,
                log_path=log_path,
            )

    return crawl_results


def run_augmenter(
    run_config: AugmenterRunConfig,
    overrides: dict[str, Any] | None = None,
    crawl_results: dict[str, dict] | None = None,
) -> dict[str, dict] | None:
    """執行 augmenter 工作流程：頁面圖片摘要，以及網站連結的文件（轉 Markdown、含內嵌圖片摘要）。

    Args:
        run_config: 執行參數（site 對應 configs/sites/{site}.yml；config_name 對應
            configs/augmenter/{name}.yml；save 落盤到 runs/、publish 發布到 data/）。
        overrides: AugmenterConfig 的巢狀覆寫值。
        crawl_results: 爬取結果 dict（可選，None 時載入 runs/ 中同站點最新的爬蟲結果）。

    Returns:
        增強後的爬取結果 dict（含文件的獨立 entry）| None。
    """
    # ----- 初始化設定和路徑 -----
    save, publish = run_config.save, run_config.publish
    site = SiteConfig.from_yaml(run_config.site)
    config = AugmenterConfig.from_yaml(run_config.config_name, overrides)
    run_manager, run_title = create_run_context(
        module="augmenter",
        config_name=run_config.config_name,
        site_id=site.site_id,
        config=config,
        run_name_use_config_name=run_config.run_name_use_config_name,
        save=save,
    )
    data_manager = DataManager()

    with publish_log_file(run_manager, publish) as log_path:
        with run_workflow_context(
            run_title, run_manager=run_manager, log_path=log_path
        ):
            # ----- 初始化物件 -----
            log_config(f"{config.__class__.__name__} Loaded from yaml", config)
            augmenter = Augmenter(
                downloader=HttpDownloader(
                    max_concurrency=config.download.max_concurrency,
                    timeout=config.download.timeout,
                    max_retries=config.download.max_retries,
                    max_bytes=config.download.max_bytes,
                ),
                success_threshold=config.retry.success_threshold,
                max_retries=config.retry.max_retries,
            )

            # ----- 獲取最近一次結果 -----
            if crawl_results is None:
                log_session("Loading Latest Results", style="cyan")
                crawl_results = load_latest_results(
                    run_manager.base_folder if run_manager is not None else "runs",
                    "website_crawler",
                    site_id=site.site_id,
                )

            # ---- 執行擴充（圖片摘要、文件）-----
            documents = (
                DocumentOptions(
                    formats=tuple(config.documents.formats),
                    caption_images=config.documents.caption_images,
                    url_patterns=tuple(site.documents.url_patterns),
                    allowed_domains=(
                        None
                        if site.crawl.allowed_domains is None
                        else tuple(site.crawl.allowed_domains)
                    ),
                )
                if config.documents.enabled
                else None
            )
            log_session("Augmentation", style="cyan")
            enhanced_results = augmenter.augment(
                crawl_results,
                model=config.images.model,
                prompt=config.images.prompt,
                image_max_concurrency=config.images.max_concurrency,
                image_source=config.images.source,
                image_min_size=config.images.min_size,
                images_enabled=config.images.enabled,
                documents=documents,
                **config.litellm_kwargs,
            )

            # ----- 輸出完成訊息 -----
            if enhanced_results is None:
                log_session("Augmentation Failed", style="red")
                return None
            log_session("Augmentation Completed", style="cyan")

            # ----- Save（存到 runs/） -----
            if save:
                assert run_manager is not None
                run_manager.save_results_as_json(enhanced_results)
                save_results_as_md(
                    enhanced_results,
                    run_manager.results_folder_path,
                    "enhanced_markdown",
                )
                save_document_files(
                    augmenter.document_files,
                    os.path.join(run_manager.run_path, FILES_FOLDER),
                )
                save_run_configs(run_manager.run_path, config, site, run_config)

            # ----- Publish（publish 到 data/） -----
            if publish:
                data_manager.publish_markdown(
                    site_id=site.site_id,
                    enhanced_results=enhanced_results,
                    document_files=augmenter.document_files,
                )

        # ----- Publish run metadata：log 要在 workflow context 結束後才完整 -----
        if publish:
            data_manager.publish_run_metadata(
                site_id=site.site_id,
                category=AUG_WEBPAGES,
                config=config,
                site=site,
                run_config=run_config,
                log_path=log_path,
            )

    return enhanced_results


def run_rag_build(
    run_config: RAGBuildRunConfig,
    overrides: dict[str, Any] | None = None,
) -> None:
    """建構 RAG 並落盤結果。完整包含建立 rag 流程。

    run_config.site 對應 configs/sites/{site}.yml、config_name 對應 configs/rag/{name}.yml；
    overrides 為 RAGConfig 的巢狀覆寫值。建庫資料來源預設為 data/aug_webpages/{site_id}，
    run_config.use_latest_results 為 True 時改用 runs/ 中同站點最新的 augmenter 結果。

    一律重建向量庫，不受既有向量庫是否存在影響；建庫絕不直接寫入
    data/vector_db/{site_id}.db，只透過 publish 原子替換（設定紀錄放在其中的 meta/，一起替換）。
    建庫位置：

    - save=True：建在該次 run 的 results/milvus.db（保留於 runs/）。
    - save=False, publish=True：建在 data/vector_db/.staging-*/{site_id}.db，publish 時
      以 rename 移入正式位置，staging 一律刪除。
    - save=False, publish=False：建在系統暫存資料夾，結束時刪除（不留任何檔案）。
    """
    save, publish = run_config.save, run_config.publish
    site = SiteConfig.from_yaml(run_config.site)
    config = RAGConfig.from_yaml(run_config.config_name, overrides)
    run_manager, run_title = create_run_context(
        module="rag_build",
        config_name=run_config.config_name,
        site_id=site.site_id,
        config=config,
        run_name_use_config_name=run_config.run_name_use_config_name,
        save=save,
    )
    data_manager = DataManager()

    # ----- 決定向量庫建置位置：run 的 results/、data/ 的 staging 或系統暫存 -----
    staging_dir: str | None = None
    if run_manager is not None:
        milvus_uri = os.path.join(run_manager.results_folder_path, "milvus.db")
    else:
        staging_dir = (
            data_manager.create_vector_store_staging(site.site_id)
            if publish
            else tempfile.mkdtemp(prefix="rag_build_")
        )
        milvus_uri = os.path.join(staging_dir, vector_store_name(site.site_id))

    try:
        with publish_log_file(run_manager, publish) as log_path:
            with run_workflow_context(
                run_title, run_manager=run_manager, log_path=log_path
            ):
                # ---- 建置 RAG -----
                log_config("SiteConfig Loaded from yaml", site)
                log_config(f"{config.__class__.__name__} Loaded from yaml", config)
                target = build_target(
                    site.site_id,
                    milvus_uri,
                    use_latest_results=run_config.use_latest_results,
                    runs_folder=run_manager.base_folder
                    if run_manager is not None
                    else "runs",
                    data_folder=data_manager.base_folder,
                )
                rag = build_rag(config, target)
                rag.close()

                # ----- 輸出完成訊息 -----
                log_session("RAG Build Completed", style="cyan")

                # ----- Save（存到 runs/；向量庫已建在本次 run 的 results/） -----
                if save:
                    assert run_manager is not None
                    save_run_configs(run_manager.run_path, config, site, run_config)

            # ----- Publish（原子替換到 data/）：log 要在 workflow context 結束後才完整，
            # 並隨 meta/ 一起替換 -----
            if publish:
                if os.path.exists(target.milvus_uri):
                    data_manager.publish_vector_store(
                        site_id=site.site_id,
                        source_path=target.milvus_uri,
                        move=staging_dir is not None,
                        write_meta=lambda meta_dir: data_manager.write_run_metadata(
                            meta_dir, config, site, run_config, log_path
                        ),
                    )
                else:
                    print_log("建庫無產出，略過 publish（設定紀錄隨向量庫發布）")
    finally:
        if staging_dir is not None:
            shutil.rmtree(staging_dir, ignore_errors=True)


def run_prepare(run_config: PrepareRunConfig) -> None:
    """執行完整 prepare 階段：網站爬蟲 → augmenter（圖片摘要、文件）→ RAG 建置。

    與 serve 階段以 data/ 目錄為唯一介面：本階段負責寫入，serve 階段只讀取已 publish
    的向量庫。任一階段無產出時提前結束；結束時印出各階段耗時與花費摘要。

    Args:
        run_config: site 與 config_name 為各階段共用的站點與 config 名稱（對應
            configs/sites/{site}.yml 與 configs/{module}/{name}.yml）；
            publish=True 時各階段結果 publish 到 data/（不存 runs/）；False 時只存到
            runs/，不寫入 data/，RAG 以 runs/ 中本次的 augmenter 結果建庫（供測試使用）。
    """
    reset_run_summary()
    site = run_config.site
    config_name = run_config.config_name
    publish = run_config.publish
    save = not publish

    with log_run_time(f"Prepare Pipeline ({site}, {config_name})"):
        log_session(f"Prepare Pipeline ({site}, {config_name})", style="purple")

        try:
            # ----- Website Crawler -----
            crawl_results = run_website_crawler(
                WebsiteCrawlerRunConfig(
                    site=site, config_name=config_name, save=save, publish=publish
                )
            )
            if crawl_results is None:
                return

            # ----- Augmenter -----
            enhanced_results = run_augmenter(
                AugmenterRunConfig(
                    site=site, config_name=config_name, save=save, publish=publish
                ),
                crawl_results=crawl_results,
            )
            if enhanced_results is None:
                return

            # ----- RAG Build -----
            run_rag_build(
                RAGBuildRunConfig(
                    site=site,
                    config_name=config_name,
                    save=save,
                    publish=publish,
                    use_latest_results=not publish,
                )
            )

            # ----- 輸出完成訊息 -----
            log_session("Prepare Pipeline Completed", style="cyan")
        finally:
            log_run_summary()
