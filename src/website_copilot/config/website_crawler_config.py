import logging
from typing import Annotated, ClassVar

from pydantic import (
    Field,
    NonNegativeInt,
    PositiveInt,
    field_validator,
)

from website_copilot.config.base_config import (
    BaseModuleConfig,
    ConfigModel,
    NonEmptyStr,
)

logger = logging.getLogger(__name__)

KEEP_TITLE_CONTENT_THRESHOLD = 0.45
KEEP_IMAGE_CONTENT_THRESHOLD = 0.25


class CrawlerInitConfig(ConfigModel):
    max_depth: NonNegativeInt | None = Field(
        default=2,
        description="最大爬取深度，null 為不限制（crawl4ai 的 0 代表只爬首頁）",
    )
    max_pages: PositiveInt | None = None
    content_threshold: float = Field(
        default=KEEP_IMAGE_CONTENT_THRESHOLD,
        ge=0,
        le=1,
        description="PruningContentFilter 的門檻，越高過濾越多內容",
    )
    light_mode: bool = True
    wait_for_images: bool = True


class CrawlConfig(ConfigModel):
    """站點資訊（Phase D 移到 SiteConfig），不以特定站點的值作為預設。"""

    url: NonEmptyStr = Field(description="爬蟲起始網址")
    url_patterns: Annotated[list[str], Field(min_length=1)] | None = Field(
        default=None, description="允許爬取的網址 pattern（glob）"
    )
    allowed_domains: Annotated[list[NonEmptyStr], Field(min_length=1)] | None = None
    path_prefix: str | None = Field(
        default=None, description="只爬取此路徑前綴下的頁面，需以 / 開頭"
    )

    @field_validator("path_prefix")
    @classmethod
    def _check_path_prefix(cls, value: str | None) -> str | None:
        if value is not None and not value.startswith("/"):
            raise ValueError("path_prefix 必須以 / 開頭")
        return value


class CleanConfig(ConfigModel):
    llm_model: NonEmptyStr = Field(
        default="gpt-5.6-luna", description="產生 exclude words 的 LLM"
    )
    sample_ratio: float = Field(default=0.1, gt=0, le=1, description="抽樣頁面比例")
    repeat: PositiveInt = Field(default=5, description="抽樣產生 exclude words 的次數")
    max_prompt_tokens: PositiveInt = Field(
        default=200_000, description="exclude words prompt 的 token 上限，超過時報錯"
    )
    seed: int | None = Field(default=None, description="抽樣亂數種子")


class WebsiteCrawlerConfig(BaseModuleConfig):
    _CONFIG_FOLDER_PATH: ClassVar[str] = "configs/website_crawler"

    site_id: NonEmptyStr  # Phase D 移除，改由 SiteConfig 提供
    init: CrawlerInitConfig = Field(default_factory=CrawlerInitConfig)
    crawl: CrawlConfig
    clean: CleanConfig = Field(default_factory=CleanConfig)
