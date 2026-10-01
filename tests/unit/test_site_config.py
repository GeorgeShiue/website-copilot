"""SiteConfig（configs/sites/{site_id}.yml）測試。

- configs/sites/ 下所有站點皆能載入，site_id 與檔名一致。
- site_id 格式（Milvus collection 名稱規則）、與檔名不一致、找不到站點時的錯誤。
- crawl 欄位的驗證（path_prefix、allowed_domains 只接受 list）。
- save_site_config 往返。
"""

from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from website_copilot.config.site_config import SiteConfig, SiteCrawlConfig
from website_copilot.utils.config_helper import (
    ConfigValidationError,
    dump_yaml,
    save_site_config,
)

SITE_FILES = sorted(Path("configs/sites").glob("*.yml"))


def _site_dict(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "site_id": "demo",
        "sample_query": "q",
        "crawl": {"url": "https://example.com/"},
    }
    data.update(overrides)
    return data


@pytest.fixture
def sites_folder(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(SiteConfig, "_CONFIG_FOLDER_PATH", str(tmp_path))
    return tmp_path


@pytest.mark.parametrize("path", SITE_FILES, ids=lambda p: p.stem)
def test_all_site_files_load(path: Path) -> None:
    site = SiteConfig.from_yaml(path.stem)

    assert site.site_id == path.stem
    assert site.sample_query
    assert site.source == str(path)


def test_site_files_found() -> None:
    assert SiteConfig.available_sites() == ["claudecode", "ncucsie", "nculab"]


def test_crawl_optional_fields_default_to_none() -> None:
    crawl = SiteCrawlConfig(url="https://example.com/")

    assert (crawl.url_patterns, crawl.allowed_domains, crawl.path_prefix) == (
        None,
        None,
        None,
    )


@pytest.mark.parametrize("site_id", ["ncu-csie", "1lab", "nculab ", ""])
def test_invalid_site_id_rejected(site_id: str) -> None:
    with pytest.raises(ValidationError, match="site_id"):
        SiteConfig.model_validate(_site_dict(site_id=site_id))


@pytest.mark.parametrize("site_id", ["nculab", "_lab2", "NCU_csie"])
def test_valid_site_id(site_id: str) -> None:
    assert SiteConfig.model_validate(_site_dict(site_id=site_id)).site_id == site_id


def test_site_id_must_match_file_name(sites_folder: Path) -> None:
    dump_yaml(_site_dict(site_id="other"), sites_folder / "demo.yml")

    with pytest.raises(ConfigValidationError, match="site_id 必須與檔名一致"):
        SiteConfig.from_yaml("demo")


def test_missing_site_lists_available(sites_folder: Path) -> None:
    dump_yaml(_site_dict(), sites_folder / "demo.yml")

    with pytest.raises(FileNotFoundError, match="可用的站點：demo"):
        SiteConfig.from_yaml("missing")


def test_validation_error_includes_path(sites_folder: Path) -> None:
    dump_yaml(_site_dict(crawl={"url": " "}), sites_folder / "demo.yml")

    with pytest.raises(ConfigValidationError) as exc_info:
        SiteConfig.from_yaml("demo")

    assert str(exc_info.value) == (
        f"{sites_folder / 'demo.yml'}: crawl.url: 不可為空白字串"
    )


def test_site_extends(sites_folder: Path) -> None:
    """SiteConfig 共用模組 config 的 YAML loader，支援 extends。"""
    dump_yaml(_site_dict(), sites_folder / "base.yml")
    dump_yaml({"extends": "base", "site_id": "demo2"}, sites_folder / "demo2.yml")

    site = SiteConfig.from_yaml("demo2")

    assert site.site_id == "demo2"
    assert site.crawl.url == "https://example.com/"
    assert site.source == f"{sites_folder / 'demo2.yml'} (extends: base)"


def test_unknown_key_rejected() -> None:
    with pytest.raises(ValidationError, match="max_pages"):
        SiteConfig.model_validate(_site_dict(max_pages=10))


def test_allowed_domains_string_rejected() -> None:
    """字串會被逐字元檢查而通過的舊 bug：現在只接受 list。"""
    crawl = {"url": "https://example.com/", "allowed_domains": "example.com"}

    with pytest.raises(ValidationError, match="crawl.allowed_domains"):
        SiteConfig.model_validate(_site_dict(crawl=crawl))


def test_path_prefix_must_start_with_slash() -> None:
    crawl = {"url": "https://example.com/", "path_prefix": "site/nculab"}

    with pytest.raises(ValidationError, match="path_prefix 必須以 / 開頭"):
        SiteConfig.model_validate(_site_dict(crawl=crawl))


def test_save_site_config_round_trip(tmp_path: Path) -> None:
    site = SiteConfig.from_yaml("ncucsie")
    path = tmp_path / "site_config.yml"

    save_site_config(site, str(path))
    text = path.read_text(encoding="utf-8")

    assert text.startswith("# source: configs/sites/ncucsie.yml\n")
    assert (
        SiteConfig.model_validate(yaml.safe_load(text)).model_dump()
        == site.model_dump()
    )
