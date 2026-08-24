import logging
from dataclasses import dataclass
from typing import Any, ClassVar, Pattern

from app.configs.base_config import BaseModuleConfig
from utils.config_helper import ConfigValidationError

logger = logging.getLogger(__name__)

KEEP_TITLE_CONTENT_THRESHOLD = 0.45
KEEP_IMAGE_CONTENT_THRESHOLD = 0.25
DEFAULT_INIT_CONFIG_SECTION = "init"
DEFAULT_CRAWL_CONFIG_SECTION = "crawl"
INIT_KEYS = {
    "site_id",
    "max_depth",
    "max_pages",
    "content_threshold",
    "light_mode",
    "wait_for_images",
}
CRAWL_KEYS = {
    "url",
    "url_patterns",
    "allowed_domains",
    "exclude_words",
    "path_prefix",
}
SECTIONS_TO_KEYS = {
    DEFAULT_INIT_CONFIG_SECTION: INIT_KEYS,
    DEFAULT_CRAWL_CONFIG_SECTION: CRAWL_KEYS,
}


@dataclass
class WebsiteCrawlerConfig(BaseModuleConfig):
    _CONFIG_FOLDER_PATH: ClassVar[str] = "configs/website_crawler"
    sections_to_keys: ClassVar[dict[str, set[str]]] = SECTIONS_TO_KEYS

    # ----- crawl config (no default values) -----
    url: str
    # ----- init config -----
    max_depth: int | None = None
    max_pages: int | None = None
    content_threshold: float = KEEP_IMAGE_CONTENT_THRESHOLD
    light_mode: bool = True
    wait_for_images: bool = True
    # ----- crawl config -----
    url_patterns: str | Pattern | list[str | Pattern] | None = None
    allowed_domains: str | list[str] | None = None
    exclude_words: list[str] | None = None
    path_prefix: str | None = None

    def __post_init__(self) -> None:
        _validate_config(vars(self))


def _validate_config(config: dict[str, Any]) -> None:
    # ----- metadata -----
    BaseModuleConfig.validate_site_id(config.get("site_id", ""))

    # ----- init config -----
    max_depth = config.get("max_depth")
    max_pages = config.get("max_pages")
    content_threshold = config.get("content_threshold")
    light_mode = config.get("light_mode")
    wait_for_images = config.get("wait_for_images")

    if max_depth is not None:
        if not isinstance(max_depth, int):
            raise ConfigValidationError("max_depth 必須是整數或 None")
        if max_depth < 0:
            raise ConfigValidationError("max_depth 不可小於 0")

    if max_pages is not None:
        if not isinstance(max_pages, int):
            raise ConfigValidationError("max_pages 必須是整數")
        if max_pages <= 0:
            raise ConfigValidationError("max_pages 必須大於 0")

    if not isinstance(content_threshold, (int, float)):
        raise ConfigValidationError("content_threshold 必須是數字")
    if not 0 <= content_threshold <= 1:
        raise ConfigValidationError("content_threshold 必須介於 0 到 1")

    if not isinstance(light_mode, bool):
        raise ConfigValidationError("light_mode 必須是布林值")

    if not isinstance(wait_for_images, bool):
        raise ConfigValidationError("wait_for_images 必須是布林值")

    # ----- crawl config -----
    url = config.get("url")
    url_patterns = config.get("url_patterns")
    allowed_domains = config.get("allowed_domains")
    exclude_words = config.get("exclude_words")

    if not isinstance(url, str) or not url.strip():
        raise ConfigValidationError("url 必須是非空字串")

    if url_patterns is not None:
        if not isinstance(url_patterns, (str, Pattern, list)):
            raise ConfigValidationError(
                "url_patterns 必須是字串、正則表達式或字串/正則表達式列表"
            )
        if isinstance(url_patterns, list):
            if not url_patterns:
                raise ConfigValidationError("url_patterns 列表不可為空")
            for pattern in url_patterns:
                if not isinstance(pattern, (str, Pattern)):
                    raise ConfigValidationError(
                        "url_patterns 列表中的每個元素必須是字串或正則表達式"
                    )

    if allowed_domains is not None:
        if not isinstance(allowed_domains, (str, list)):
            raise ConfigValidationError("allowed_domains 必須是字串或字串列表")
        if isinstance(allowed_domains, list):
            if not allowed_domains:
                raise ConfigValidationError("allowed_domains 列表不可為空")
        for domain in allowed_domains:
            if not isinstance(domain, str) or not domain.strip():
                raise ConfigValidationError(
                    "allowed_domains 列表中的每個元素必須是非空字串"
                )

    if exclude_words is not None:
        if not isinstance(exclude_words, list):
            raise ConfigValidationError("exclude_words 必須是字串列表")
        if not exclude_words:
            raise ConfigValidationError("exclude_words 列表不可為空")
        for word in exclude_words:
            if not isinstance(word, str) or not word.strip():
                raise ConfigValidationError(
                    "exclude_words 列表中的每個元素必須是非空字串"
                )

    path_prefix = config.get("path_prefix")
    if path_prefix is not None:
        if not isinstance(path_prefix, str):
            raise ConfigValidationError("path_prefix 必須是字串")
        if not path_prefix.startswith("/"):
            raise ConfigValidationError("path_prefix 必須以 / 開頭")
