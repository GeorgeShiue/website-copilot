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
        default=None,
        description="最大爬取深度，未設定時不限制（crawl4ai 的 0 代表只爬首頁）",
    )
    max_pages: PositiveInt | None = None
    content_threshold: float = Field(
        ge=0,
        le=1,
        description="PruningContentFilter 的門檻，越高過濾越多內容",
    )
    light_mode: bool
    wait_for_images: bool


class CrawlConfig(ConfigModel):
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
    llm_model: NonEmptyStr = Field(description="產生 exclude words 的 LLM")
    sample_ratio: float = Field(gt=0, le=1, description="抽樣頁面比例")
    repeat: PositiveInt = Field(description="抽樣產生 exclude words 的次數")
    max_prompt_tokens: PositiveInt = Field(
        description="exclude words prompt 的 token 上限，超過時報錯"
    )
    seed: int | None = Field(default=None, description="抽樣亂數種子")


class WebsiteCrawlerConfig(BaseModuleConfig):
    _CONFIG_FOLDER_PATH: ClassVar[str] = "configs/website_crawler"

    site_id: NonEmptyStr
    init: CrawlerInitConfig
    crawl: CrawlConfig
    clean: CleanConfig
