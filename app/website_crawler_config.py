from dataclasses import dataclass
from typing import Pattern

KEEP_TITLE_CONTENT_THRESHOLD = 0.45
KEEP_IMAGE_CONTENT_THRESHOLD = 0.25


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


class ConfigError(ValueError):
    """爬蟲設定驗證錯誤。"""


def _validate_init_config(
    max_depth: int,
    max_pages: int | None,
    content_threshold: float,
    light_mode: bool,
    wait_for_images: bool,
) -> None:
    if not isinstance(max_depth, int):
        raise ConfigError("max_depth 必須是整數")
    if max_depth < 0:
        raise ConfigError("max_depth 不可小於 0")

    if max_pages is not None:
        if not isinstance(max_pages, int):
            raise ConfigError("max_pages 必須是整數")
        if max_pages <= 0:
            raise ConfigError("max_pages 必須大於 0")

    if not isinstance(content_threshold, (int, float)):
        raise ConfigError("content_threshold 必須是數字")
    if not 0 <= content_threshold <= 1:
        raise ConfigError("content_threshold 必須介於 0 到 1")

    if not isinstance(light_mode, bool):
        raise ConfigError("light_mode 必須是布林值")
    if not isinstance(wait_for_images, bool):
        raise ConfigError("wait_for_images 必須是布林值")


def _validate_crawl_config(
    url: str,
    url_patterns: str | Pattern | list[str | Pattern] | None,
    allowed_domains: str | list[str] | None,
    exclude_words: tuple[str, ...] | None,
) -> None:
    if not isinstance(url, str) or not url.strip():
        raise ConfigError("url 必須是非空字串")

    if url_patterns is not None:
        if not isinstance(url_patterns, (str, Pattern, list)):
            raise ConfigError(
                "url_patterns 必須是字串、正則表達式或字串/正則表達式列表"
            )
        if isinstance(url_patterns, list):
            if not url_patterns:
                raise ConfigError("url_patterns 列表不可為空")
            for pattern in url_patterns:
                if not isinstance(pattern, (str, Pattern)):
                    raise ConfigError(
                        "url_patterns 列表中的每個元素必須是字串或正則表達式"
                    )

    if allowed_domains is not None:
        if not isinstance(allowed_domains, (str, list)):
            raise ConfigError("allowed_domains 必須是字串或字串列表")
        if isinstance(allowed_domains, list):
            if not allowed_domains:
                raise ConfigError("allowed_domains 列表不可為空")
        for domain in allowed_domains:
            if not isinstance(domain, str) or not domain.strip():
                raise ConfigError("allowed_domains 列表中的每個元素必須是非空字串")

    if exclude_words is not None:
        if not isinstance(exclude_words, tuple):
            raise ConfigError("exclude_words 必須是字串元組")
        for word in exclude_words:
            if not isinstance(word, str) or not word.strip():
                raise ConfigError("exclude_words 元組中的每個元素必須是非空字串")
