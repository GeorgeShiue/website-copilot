import os

from app.configs.rag_config import (
    RagConfig,
)
from app.configs.webpage_image_summarizer_config import WebpageImageSummarizerConfig
from app.configs.website_crawler_config import WebsiteCrawlerConfig
from app.modules.rag import Rag
from app.modules.rag_factory import RagBuilder
from app.modules.webpage_image_summarizer import WebpageImageSummarizer
from app.modules.website_crawler import WebsiteCrawler
from app.workflow.workflow_manager import RunManager
from utils.config_helper import log_config, save_module_config_as_toml
from utils.log_helper import (
    log_run_time,
    log_session,
    save_logging_file,
)


def run_website_crawler(
    run_manager: RunManager | None = None,
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    **config_overrides,
) -> dict[str, dict] | None:
    # ----- 初始化設定和路徑 -----
    website_crawler = WebsiteCrawler()
    config = WebsiteCrawlerConfig.from_toml(config_name, **config_overrides)
    if run_manager is None:
        run_manager = RunManager("website_crawler")
    if run_name_use_config_name:
        run_manager.set_run_path(config_name)
    else:
        run_manager.set_run_path(config.run_name)
    run_manager.init_module_run_paths()

    crawl_results = None
    with (
        save_logging_file(run_manager.log_path),
        log_run_time("Website Crawling"),
    ):
        # ----- 輸出開始訊息 -----
        log_session(f"Website Crawler ({config_name})", style="purple")
        log_config("WebsiteCrawler Config Loaded from toml", config)
        log_session("Run Paths", style="cyan")
        run_manager.log_run_paths("init")

        # ----- 初始化物件 -----
        website_crawler.override_init_config(
            max_depth=config.max_depth,
            max_pages=config.max_pages,
            content_threshold=config.content_threshold,
            light_mode=config.light_mode,
            wait_for_images=config.wait_for_images,
        )

        # ---- 執行網站爬蟲 -----
        log_session("Website Crawling", style="cyan")
        crawl_results = website_crawler.crawl_website(
            url=config.url,
            url_patterns=config.url_patterns,
            allowed_domains=config.allowed_domains,
            exclude_words=config.exclude_words,
        )

        if crawl_results is None:
            log_session("Website Crawling Failed", style="red")
            return None

        # ----- 儲存設定和結果 -----
        save_module_config_as_toml(config, run_manager.module_config_toml_path)
        run_manager.save_results_as_json(crawl_results)
        run_manager.save_results_as_md(crawl_results, "fit_markdown")

        # ----- 輸出完成訊息 -----
        log_session("Website Crawling Completed", style="cyan")

    return crawl_results


def run_webpage_image_summarizer(
    run_manager: RunManager | None = None,
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    crawl_results: dict[str, dict] | None = None,
    **config_overrides,
) -> dict[str, dict] | None:
    # ----- 初始化設定和路徑 -----
    webpage_image_summarizer = WebpageImageSummarizer()
    config = WebpageImageSummarizerConfig.from_toml(config_name, **config_overrides)
    if run_manager is None:
        run_manager = RunManager("webpage_image_summarizer")
    if run_name_use_config_name:
        run_manager.set_run_path(config_name)
    else:
        run_manager.set_run_path(config.run_name)
    run_manager.init_module_run_paths()

    with (
        save_logging_file(run_manager.log_path),
        log_run_time("Image Summarization"),
    ):
        # ----- 輸出開始訊息 -----
        log_session(f"Webpage Image Summarizer ({config_name})", style="purple")
        log_config("WebpageImageSummarizer Config Loaded from toml", config)
        log_session("Run Paths", style="cyan")
        run_manager.log_run_paths("init")

        # ----- 初始化物件 -----
        webpage_image_summarizer.override_init_config(
            download_timeout=config.download_timeout,
            success_threshold=config.success_threshold,
            max_retries=config.max_retries,
            cache_download_images=config.cache_download_images,
            cache_image_captions=config.cache_image_captions,
        )

        # ----- 獲取最近一次結果 -----
        if crawl_results is None:
            log_session("Loading Latest Results", style="cyan")
            crawl_results = run_manager.load_latest_results_from_json()

        # ---- 執行圖片摘要 -----
        log_session("Image Summarization", style="cyan")
        enhanced_results = webpage_image_summarizer.summarize_crawl_results_images(
            crawl_results,
            model=config.model,
            prompt=config.prompt,
            vlm_max_workers=config.vlm_max_workers,
            image_source=config.image_source,
            **config.litellm_kwargs,
        )

        if enhanced_results is None:
            log_session("Image Summarization Failed", style="red")
            return None

        # ----- 儲存設定和結果 -----
        save_module_config_as_toml(config, run_manager.module_config_toml_path)
        run_manager.save_results_as_json(enhanced_results)
        run_manager.save_results_as_md(enhanced_results, "enhanced_markdown")

        # ----- 輸出完成訊息 -----
        log_session("Image Summarization Completed", style="cyan")

    return enhanced_results


def run_rag_build(
    run_manager: RunManager | None = None,
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    webpages_data_use_latest_results: bool = False,
    **config_overrides,
) -> None:
    # ----- 初始化設定和路徑 -----
    config = RagConfig.from_toml(config_name, **config_overrides)
    if run_manager is None:
        run_manager = RunManager("rag_build")
    if run_name_use_config_name:
        run_manager.set_run_path(config_name)
    else:
        run_manager.set_run_path(config.run_name)
    run_manager.init_module_run_paths()
    run_title = f"RAG Build ({config_name})"

    # ----- 解決 webpages 資料路徑（如有需要可覆蓋 config 預設值）-----
    if webpages_data_use_latest_results:
        log_session("Finding Latest Webpages Data", style="cyan")
        webpages_data_folder_path = run_manager.load_latest_summarizer_run_path()
        config.webpages_data_folder_path = webpages_data_folder_path

    # ----- 使用 RagBuilder 一鍵建構 -----
    rag = RagBuilder(config).build()

    with (
        rag,
        save_logging_file(run_manager.log_path),
        log_run_time(run_title),
    ):
        # ----- 輸出開始訊息 -----
        log_session(run_title, style="purple")
        log_config("Rag Config Loaded from toml", config)

        # ----- Query & Response -----
        log_session("Query & Response", style="cyan")
        rag.query(config.query, log_sources=True)

        # ----- 儲存設定和結果 -----
        save_module_config_as_toml(config, run_manager.module_config_toml_path)


# TODO: 此function內支援多份query
def run_rag_query(
    run_manager: RunManager | None = None,
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    force_rebuild: bool = False,
    query_times: int = 1,
    **config_overrides,
) -> None:
    # ----- 初始化設定和路徑 -----
    config = RagConfig.from_toml(config_name, **config_overrides)
    if run_manager is None:
        run_manager = RunManager("rag_query")
    if run_name_use_config_name:
        run_manager.set_run_path(config_name)
    else:
        run_manager.set_run_path(config.run_name)
    run_manager.init_module_run_paths()
    run_title = f"RAG Query ({config_name})"

    rag = Rag(webpages_data_folder_path=config.webpages_data_folder_path)
    builder = RagBuilder(config)

    with (
        rag,
        save_logging_file(run_manager.log_path),
        log_run_time(run_title),
    ):
        # ----- 建立所有資源 -----
        log_session("Building All Resources", style="cyan")
        rebuild = False
        store_path = (
            config.milvus_uri
            if config.vector_store_type == "milvus"
            else config.qdrant_db_folder_path
        )
        if force_rebuild or not os.path.exists(store_path):
            rebuild = True

        # * Milvus Vector Store 必須重建
        if rebuild or config.vector_store_type == "milvus":
            if config.vector_store_type == "qdrant":
                builder.clean_vector_store(rag)
            elif config.vector_store_type == "milvus":
                builder.clean_vector_store(rag)
            builder.build_nodes(rag)
            builder.build_vector_store(rag)
            builder.build_index(rag)
        else:
            builder.build_vector_store(rag, overwrite=False)
            builder.load_index(rag)

        builder.build_retriever(rag)
        builder.build_query_engine(rag)

        # ----- Query -----
        faithfulness_pass = 0
        relevancy_pass = 0
        for i in range(query_times):
            # ----- 查詢與回應 -----
            log_session(f"Query & Response {i + 1}", style="cyan")
            response = rag.query(config.query, log_sources=True)

            # ----- 回應評估 -----
            # TODO: 改用 regas 或 deepeval 評估
            log_session("Evaluation", style="cyan")
            faithfulness_result, relevancy_result = rag.evaluate(
                query=config.query, response=response
            )
            if faithfulness_result.passing:
                faithfulness_pass += 1
            if relevancy_result.passing:
                relevancy_pass += 1

        faithfulness_pass_rate = faithfulness_pass / query_times * 100
        relevancy_pass_rate = relevancy_pass / query_times * 100

        # ----- 輸出評估結果 -----
        log_session("Evaluation Summary", style="green")
        print(f"Query times: {query_times}")
        print(
            f"Faithfulness: {faithfulness_pass_rate:.2f}% ({faithfulness_pass}/{query_times})"
        )
        print(f"Relevancy: {relevancy_pass_rate:.2f}% ({relevancy_pass}/{query_times})")

        # TODO: 制定 Query Response 的儲存方式
        # ----- 儲存設定和結果 -----
        save_module_config_as_toml(config, run_manager.module_config_toml_path)

        if rebuild or config.vector_store_type == "milvus":
            module_config_folder_path = ""
            if config.vector_store_type == "qdrant":
                module_config_folder_path = config.qdrant_db_folder_path
            elif config.vector_store_type == "milvus":
                module_config_folder_path = config.milvus_uri
            save_module_config_as_toml(
                config,
                os.path.join(module_config_folder_path, "module_config.toml"),
            )

        # ----- 輸出完成訊息 -----
        log_session("RAG Query Completed", style="cyan")
