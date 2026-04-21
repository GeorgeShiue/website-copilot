import logging
from dataclasses import dataclass
from typing import Any, Pattern, Self

from utils.config_manager import (
    ConfigValidationError,
    load_config_section_from_toml,
    save_config_as_toml,
)

logger = logging.getLogger(__name__)

KEEP_TITLE_CONTENT_THRESHOLD = 0.45
KEEP_IMAGE_CONTENT_THRESHOLD = 0.25
DEFAULT_CONFIG_PATH = "./config/website_crawler.toml"
DEFAULT_INIT_CONFIG_SECTION = "init"
DEFAULT_CRAWL_CONFIG_SECTION = "crawl"
INIT_KEYS = {
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
}
SECTIONS_TO_KEYS = {
    DEFAULT_INIT_CONFIG_SECTION: INIT_KEYS,
    DEFAULT_CRAWL_CONFIG_SECTION: CRAWL_KEYS,
}


@dataclass
class WebsiteCrawlerConfig:
    # ----- init config (no default values)-----
    max_depth: int

    # ----- crawl config (no default values)-----
    url: str

    # ----- init config -----
    max_pages: int | None = None
    content_threshold: float = KEEP_IMAGE_CONTENT_THRESHOLD
    light_mode: bool = True
    wait_for_images: bool = True

    # ----- crawl config -----
    url_patterns: str | Pattern | list[str | Pattern] | None = None
    allowed_domains: str | list[str] | None = None
    exclude_words: tuple[str, ...] | None = None

    @classmethod
    def from_config(
        cls,
        config_path: str = DEFAULT_CONFIG_PATH,
        init_config_section: str = DEFAULT_INIT_CONFIG_SECTION,
        crawl_config_section: str = DEFAULT_CRAWL_CONFIG_SECTION,
    ) -> Self:
        """從 TOML 設定檔建立 WebsiteCrawlerConfig。"""
        init_config = _load_init_config_from_toml(config_path, init_config_section)
        crawl_config = _load_crawl_config_from_toml(config_path, crawl_config_section)
        return cls(**init_config, **crawl_config)

    def __post_init__(self) -> None:
        _validate_init_config(
            max_depth=self.max_depth,
            max_pages=self.max_pages,
            content_threshold=self.content_threshold,
            light_mode=self.light_mode,
            wait_for_images=self.wait_for_images,
        )
        _validate_crawl_config(
            url=self.url,
            url_patterns=self.url_patterns,
            allowed_domains=self.allowed_domains,
            exclude_words=self.exclude_words,
        )

    def override_init_config(self, **overrides) -> None:
        """覆寫 init 參數並驗證。"""
        _override_init_config(vars(self), **overrides)

    def override_crawl_config(self, **overrides) -> None:
        """覆寫 crawl 參數並驗證。"""
        _override_crawl_config(vars(self), **overrides)


def _validate_init_config(
    init_config: dict[str, Any] = {},
    **init_kwargs,
) -> None:
    if init_config:
        max_depth = init_config.get("max_depth")
        max_pages = init_config.get("max_pages")
        content_threshold = init_config.get("content_threshold")
        light_mode = init_config.get("light_mode")
        wait_for_images = init_config.get("wait_for_images")
    else:
        max_depth = init_kwargs.get("max_depth")
        max_pages = init_kwargs.get("max_pages")
        content_threshold = init_kwargs.get("content_threshold")
        light_mode = init_kwargs.get("light_mode")
        wait_for_images = init_kwargs.get("wait_for_images")

    if not isinstance(max_depth, int):
        raise ConfigValidationError("max_depth 必須是整數")
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


def _validate_crawl_config(
    crawl_config: dict[str, Any] = {},
    **crawl_kwargs,
) -> None:
    if crawl_config:
        url = crawl_config.get("url")
        url_patterns = crawl_config.get("url_patterns")
        allowed_domains = crawl_config.get("allowed_domains")
        exclude_words = crawl_config.get("exclude_words")
    else:
        url = crawl_kwargs.get("url")
        url_patterns = crawl_kwargs.get("url_patterns")
        allowed_domains = crawl_kwargs.get("allowed_domains")
        exclude_words = crawl_kwargs.get("exclude_words")

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
        if not isinstance(exclude_words, tuple):
            raise ConfigValidationError("exclude_words 必須是字串元組")
        for word in exclude_words:
            if not isinstance(word, str) or not word.strip():
                raise ConfigValidationError(
                    "exclude_words 元組中的每個元素必須是非空字串"
                )


def _load_init_config_from_toml(
    config_path: str = DEFAULT_CONFIG_PATH,
    config_section: str = DEFAULT_INIT_CONFIG_SECTION,
) -> dict[str, Any]:
    """從 TOML 讀取 init 參數。"""
    init_config = load_config_section_from_toml(
        config_path=config_path,
        config_section=config_section,
        allowed_keys=INIT_KEYS,
        unknown_keys_warning="Unknown init config keys will be ignored: %s",
    )

    return init_config


def _load_crawl_config_from_toml(
    config_path: str = DEFAULT_CONFIG_PATH,
    config_section: str = DEFAULT_CRAWL_CONFIG_SECTION,
) -> dict[str, Any]:
    """從 TOML 讀取 crawl 參數。"""
    crawl_config = load_config_section_from_toml(
        config_path=config_path,
        config_section=config_section,
        allowed_keys=CRAWL_KEYS,
        unknown_keys_warning="Unknown crawl config keys will be ignored: %s",
    )

    exclude_words = crawl_config.get("exclude_words")
    if isinstance(exclude_words, list):
        crawl_config["exclude_words"] = tuple(exclude_words)

    return crawl_config


def _override_init_config(
    init_config: dict[str, Any],
    **overrides: dict[str, Any],
) -> dict[str, Any]:
    """套用 overrides 並驗證 init 參數。"""
    for key, value in overrides.items():
        if key in INIT_KEYS:
            init_config[key] = value

    _validate_init_config(init_config)
    return init_config


def _override_crawl_config(
    crawl_config: dict[str, Any],
    **overrides: dict[str, Any],
) -> dict[str, Any]:
    """套用 overrides 並驗證 crawl 參數。"""
    for key, value in overrides.items():
        if key in CRAWL_KEYS:
            crawl_config[key] = value

    exclude_words = crawl_config.get("exclude_words")
    if isinstance(exclude_words, list):
        crawl_config["exclude_words"] = tuple(exclude_words)

    _validate_crawl_config(crawl_config)
    return crawl_config


def save_crawler_config_as_toml(
    config: WebsiteCrawlerConfig, toml_file_path: str
) -> None:
    """將 WebsiteCrawlerConfig 儲存為 TOML 檔案。"""
    save_config_as_toml(config, SECTIONS_TO_KEYS, toml_file_path)
