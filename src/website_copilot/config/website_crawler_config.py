import logging
from typing import ClassVar

from pydantic import (
    Field,
    NonNegativeInt,
    PositiveInt,
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


class CleanConfig(ConfigModel):
    llm_model: NonEmptyStr = Field(
        default="gpt-5.6-luna", description="產生 exclude words 的 LLM"
    )
    sample_ratio: float = Field(default=0.1, gt=0, le=1, description="抽樣頁面比例")
    repeat: PositiveInt = Field(default=5, description="抽樣產生 exclude words 的次數")
    max_prompt_tokens: PositiveInt = Field(
        default=500_000, description="exclude words prompt 的 token 上限，超過時報錯"
    )
    seed: int | None = Field(default=None, description="抽樣亂數種子")


class WebsiteCrawlerConfig(BaseModuleConfig):
    """爬蟲參數；起始網址與爬取範圍屬於站點資訊，見 SiteConfig.crawl。"""

    _CONFIG_FOLDER_PATH: ClassVar[str] = "configs/website_crawler"
    _DEFAULT_RUN_NAME_FIELDS: ClassVar[tuple[str, ...]] = ("init.max_depth",)

    init: CrawlerInitConfig = Field(default_factory=CrawlerInitConfig)
    clean: CleanConfig = Field(default_factory=CleanConfig)
