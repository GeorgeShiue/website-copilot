from dataclasses import dataclass

from app.workflow.workflow_config import (
    RagBuildRunConfig,
    RagQueryRunConfig,
    WebpageImageSummarizerRunConfig,
    WebsiteCrawlerRunConfig,
)


@dataclass
class WebsiteCrawlerConfigCLI:
    # ----- init config -----
    max_pages: int | None = None


@dataclass
class WebpageImageSummarizerConfigCLI:
    # ----- init config -----
    model: str | None = None


@dataclass
class RagConfigCLI:
    # ----- retriever config -----
    similarity_top_k: int | None = None
    query_mode: str | None = None
    hybrid_top_k: int | None = None
    alpha: float | None = None
    # ----- query engine config -----
    cutoff: float | None = None
    query: str | None = None


@dataclass
class WebsiteCrawlerCLI:
    run: WebsiteCrawlerRunConfig
    module: WebsiteCrawlerConfigCLI


@dataclass
class WebpageImageSummarizerCLI:
    run: WebpageImageSummarizerRunConfig
    module: WebpageImageSummarizerConfigCLI


@dataclass
class RagBuildCLI:
    run: RagBuildRunConfig
    module: RagConfigCLI


@dataclass
class RagQueryCLI:
    run: RagQueryRunConfig
    module: RagConfigCLI


if __name__ == "__main__":
    import tyro

    from app.workflow.workflow import (
        run_rag_build,
        run_rag_query,
        run_webpage_image_summarizer,
        run_website_crawler,
    )
    from app.workflow.workflow_manager import RunManager
    from utils.config_helper import save_run_config_as_toml
    from utils.log_helper import setup_logging

    setup_logging("debug")

    run_manager = RunManager()

    cli_args_type = (
        WebsiteCrawlerCLI | WebpageImageSummarizerCLI | RagBuildCLI | RagQueryCLI
    )
    cli_arg = tyro.cli(cli_args_type)
    module_config_overrides = {}
    for key, value in vars(cli_arg.module).items():
        if value is not None:
            module_config_overrides[key] = value

    if isinstance(cli_arg, WebsiteCrawlerCLI):
        run_manager.set_module_path("website_crawler")
        run_website_crawler(
            run_manager,
            **vars(cli_arg.run),
            **module_config_overrides,
        )
    elif isinstance(cli_arg, WebpageImageSummarizerCLI):
        run_manager.set_module_path("webpage_image_summarizer")
        run_webpage_image_summarizer(
            run_manager,
            **vars(cli_arg.run),
            **module_config_overrides,
        )
    elif isinstance(cli_arg, RagBuildCLI):
        run_manager.set_module_path("rag_build")
        run_rag_build(
            run_manager,
            **vars(cli_arg.run),
            **module_config_overrides,
        )
    elif isinstance(cli_arg, RagQueryCLI):
        run_manager.set_module_path("rag_query")
        run_rag_query(
            run_manager,
            **vars(cli_arg.run),
            **module_config_overrides,
        )

    save_run_config_as_toml(cli_arg.run, run_manager.run_config_toml_path)
    run_manager.log_run_paths("complete")
