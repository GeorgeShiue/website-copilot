"""站點設定（`configs/sites/{site_id}.yml`）：站點身分與爬取範圍，與模組參數分離。

模組 config（WebsiteCrawlerConfig 等）不含任何站點資訊；pipeline 依 `run_config.site`
以 `SiteConfig.from_yaml(site)` 載入站點。SiteConfig 共用模組 config 的 YAML loader
（支援 extends），但不是 BaseModuleConfig：沒有 config_name／run_name_fields。
"""

import re
from pathlib import Path
from typing import Annotated, ClassVar, Self

from pydantic import Field, field_validator

from website_copilot.config.base_config import (
    ConfigModel,
    LoadedConfigModel,
    NonEmptyStr,
    validate_loaded,
)
from website_copilot.config.yaml_helper import CONFIG_SUFFIX, load_config_dict
from website_copilot.utils.config_helper import ConfigValidationError

# Milvus collection 名稱與路徑皆可用的格式
SITE_ID_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class SiteCrawlConfig(ConfigModel):
    url: NonEmptyStr = Field(description="爬蟲起始網址")
    url_patterns: Annotated[list[str], Field(min_length=1)] | None = Field(
        default=None, description="允許爬取的網址 pattern（glob），null 為不過濾"
    )
    allowed_domains: Annotated[list[NonEmptyStr], Field(min_length=1)] | None = Field(
        default=None, description="允許爬取的網域，null 為不限制"
    )
    path_prefix: str | None = Field(
        default=None,
        description="只爬取此路徑前綴下的頁面，需以 / 開頭；null 時取起始網址的父路徑",
    )

    @field_validator("path_prefix")
    @classmethod
    def _check_path_prefix(cls, value: str | None) -> str | None:
        if value is not None and not value.startswith("/"):
            raise ValueError("path_prefix 必須以 / 開頭")
        return value


class SiteDocumentsConfig(ConfigModel):
    url_patterns: list[NonEmptyStr] = Field(
        default_factory=list,
        description="站點專屬的文件 URL 樣式（glob，如無副檔名的下載 API）；"
        "與通用副檔名一同被爬蟲排除、被文件收集器辨識",
    )


class SiteConfig(LoadedConfigModel):
    """站點身分：site_id 同時作為 data/ 與 runs/ 的資料夾名稱及 Milvus collection 名稱。"""

    _CONFIG_FOLDER_PATH: ClassVar[str] = "configs/sites"

    site_id: str = Field(description="站點識別碼，須與設定檔名稱一致")
    sample_query: NonEmptyStr | None = Field(
        default=None, description="rag-query 未指定 --run.query 時使用的查詢"
    )
    crawl: SiteCrawlConfig
    documents: SiteDocumentsConfig = Field(default_factory=SiteDocumentsConfig)

    @classmethod
    def available_sites(cls) -> list[str]:
        """`configs/sites/` 下的站點名稱。"""
        return sorted(
            path.stem
            for path in Path(cls._CONFIG_FOLDER_PATH).glob(f"*{CONFIG_SUFFIX}")
        )

    @classmethod
    def from_yaml(cls, site_id: str) -> Self:
        """載入 `configs/sites/{site_id}.yml`（展開 extends）並檢查 site_id 與檔名一致。"""
        path = Path(cls._CONFIG_FOLDER_PATH) / f"{site_id}{CONFIG_SUFFIX}"
        if not path.is_file():
            available = ", ".join(cls.available_sites()) or "（無）"
            raise FileNotFoundError(
                f"Site config not found: {path}（可用的站點：{available}）"
            )

        loaded = load_config_dict(cls._CONFIG_FOLDER_PATH, site_id)
        site = validate_loaded(cls, loaded.data, loaded.source)
        if site.site_id != site_id:
            raise ConfigValidationError(
                f"{loaded.source}: site_id 必須與檔名一致（{site.site_id} ≠ {site_id}）"
            )
        site._source = loaded.source
        return site

    @field_validator("site_id")
    @classmethod
    def _check_site_id(cls, value: str) -> str:
        if not SITE_ID_PATTERN.fullmatch(value):
            raise ValueError(
                "site_id 只能包含英數字與底線，且不可以數字開頭（Milvus collection 名稱規則）"
            )
        return value
