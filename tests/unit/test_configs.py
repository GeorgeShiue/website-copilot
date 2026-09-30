"""module config（pydantic）載入與驗證測試。

- configs/ 下所有設定檔皆能載入並通過驗證。
- strict 型別、未知 key、跨欄位規則、validate_assignment。
- ConfigValidationError 的訊息包含設定檔路徑與欄位路徑。
- run name 註解解析（dotted path）與 run_name 組成；扁平 overrides 放入所屬 section。
- save_module_config_as_toml 往返：寫出後讀回驗證，model_dump 不變。
"""

import tomllib
from pathlib import Path
from typing import Any

import pytest
import tomlkit
from pydantic import ValidationError

from website_copilot.config.agent_config import AgentConfig
from website_copilot.config.base_config import BaseModuleConfig
from website_copilot.config.image_summarizer_config import ImageSummarizerConfig
from website_copilot.config.rag_config import RAGConfig
from website_copilot.config.website_crawler_config import WebsiteCrawlerConfig
from website_copilot.utils.config_helper import (
    ConfigValidationError,
    filter_commented_configs,
    save_module_config_as_toml,
)

MODULE_CONFIGS: dict[str, type[BaseModuleConfig]] = {
    "website_crawler": WebsiteCrawlerConfig,
    "image_summarizer": ImageSummarizerConfig,
    "rag": RAGConfig,
    "agent": AgentConfig,
}

CONFIG_FILES = sorted(Path("configs").glob("*/*.toml"))


def _load_dict(module: str, name: str = "test") -> dict[str, Any]:
    with open(f"configs/{module}/{name}.toml", "rb") as f:
        return tomllib.load(f)


# ---------- configs/ 下所有設定檔 ----------


@pytest.mark.parametrize(
    "path", CONFIG_FILES, ids=lambda p: f"{p.parent.name}/{p.stem}"
)
def test_all_config_files_load(path: Path) -> None:
    config_cls = MODULE_CONFIGS[path.parent.name]
    config = config_cls.from_toml(path.stem)

    assert config.config_name == path.stem
    assert config.run_name


def test_config_files_found() -> None:
    assert {p.parent.name for p in CONFIG_FILES} == set(MODULE_CONFIGS)


# ---------- strict 型別與未知 key ----------


def test_bool_rejected_for_int_field() -> None:
    data = _load_dict("website_crawler")
    data["init"]["max_depth"] = True

    with pytest.raises(ValidationError, match="init.max_depth"):
        WebsiteCrawlerConfig.model_validate(data)


def test_numeric_string_rejected() -> None:
    data = _load_dict("image_summarizer")
    data["init"]["max_retries"] = "6"

    with pytest.raises(ValidationError, match="init.max_retries"):
        ImageSummarizerConfig.model_validate(data)


def test_int_accepted_for_float_field() -> None:
    data = _load_dict("image_summarizer")
    data["init"]["download_timeout"] = 10

    config = ImageSummarizerConfig.model_validate(data)

    assert config.init.download_timeout == 10.0


def test_allowed_domains_string_rejected() -> None:
    """舊版字串會被逐字元檢查而通過；現在只接受 list。"""
    data = _load_dict("website_crawler")
    data["crawl"]["allowed_domains"] = "sites.google.com"

    with pytest.raises(ValidationError, match="crawl.allowed_domains"):
        WebsiteCrawlerConfig.model_validate(data)


@pytest.mark.parametrize("section", [None, "retriever"])
def test_unknown_key_rejected(section: str | None) -> None:
    data = _load_dict("rag")
    (data if section is None else data[section])["unknown_key"] = 1

    with pytest.raises(ValidationError, match="unknown_key"):
        RAGConfig.model_validate(data)


def test_missing_required_field_rejected() -> None:
    data = _load_dict("rag")
    del data["retriever"]["alpha"]

    with pytest.raises(ValidationError, match="retriever.alpha"):
        RAGConfig.model_validate(data)


def test_blank_string_rejected() -> None:
    data = _load_dict("agent")
    data["system_prompt"] = "  \n "

    with pytest.raises(ValidationError, match="不可為空白字串"):
        AgentConfig.model_validate(data)


def test_non_empty_str_keeps_whitespace() -> None:
    """NonEmptyStr 只檢查不改寫：prompt 的前後換行原樣保留。"""
    data = _load_dict("image_summarizer")
    data["summarize"]["prompt"] = "\nprompt\n"

    config = ImageSummarizerConfig.model_validate(data)

    assert config.summarize.prompt == "\nprompt\n"


def test_path_prefix_must_start_with_slash() -> None:
    data = _load_dict("website_crawler")
    data["crawl"]["path_prefix"] = "site/nculab"

    with pytest.raises(ValidationError, match="path_prefix 必須以 / 開頭"):
        WebsiteCrawlerConfig.model_validate(data)


# ---------- 跨欄位規則 ----------


def test_chunk_overlap_must_be_less_than_chunk_size() -> None:
    data = _load_dict("rag")
    data["nodes"]["chunk_overlap"] = data["nodes"]["chunk_size"]

    with pytest.raises(ValidationError, match="chunk_overlap 必須小於 chunk_size"):
        RAGConfig.model_validate(data)


@pytest.mark.parametrize(
    ("ranker", "params", "valid"),
    [
        ("WeightedRanker", {"weights": [1.0, 0.3]}, True),
        ("WeightedRanker", None, True),
        ("WeightedRanker", {"k": 60}, False),
        ("WeightedRanker", {"weights": [1.0, 0.3], "k": 60}, False),
        ("RRFRanker", {"k": 60}, True),
        ("RRFRanker", None, True),
        ("RRFRanker", {"weights": [1.0, 0.3]}, False),
    ],
)
def test_hybrid_ranker_params_rules(
    ranker: str, params: dict[str, Any] | None, valid: bool
) -> None:
    data = _load_dict("rag")
    data["vector_store"]["hybrid_ranker"] = ranker
    if params is None:
        del data["vector_store"]["hybrid_ranker_params"]
    else:
        data["vector_store"]["hybrid_ranker_params"] = params

    if valid:
        RAGConfig.model_validate(data)
    else:
        with pytest.raises(ValidationError, match="hybrid_ranker_params"):
            RAGConfig.model_validate(data)


def test_weights_length_must_be_two() -> None:
    data = _load_dict("rag")
    data["vector_store"]["hybrid_ranker_params"] = {"weights": [1.0]}

    with pytest.raises(ValidationError, match="weights"):
        RAGConfig.model_validate(data)


# ---------- validate_assignment ----------


def test_assignment_is_validated() -> None:
    config = RAGConfig.from_toml("test")

    with pytest.raises(ValidationError, match="similarity_top_k"):
        config.retriever.similarity_top_k = 0
    with pytest.raises(ValidationError, match="milvus_uri"):
        config.milvus_uri = "x"  # type: ignore[attr-defined]  # 頂層無此欄位

    config.vector_store.milvus_uri = "runs/x/milvus.db"
    assert config.vector_store.milvus_uri == "runs/x/milvus.db"


def test_rag_default_paths_follow_site_id() -> None:
    config = RAGConfig.from_toml("test", site_id="ncucsie")

    assert config.webpages_data_folder_path == "data/webpages/ncucsie"
    assert config.vector_store.milvus_uri == "data/rag/ncucsie/milvus.db"


# ---------- from_toml：錯誤訊息與 overrides ----------


@pytest.fixture
def tmp_rag_folder(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(RAGConfig, "_CONFIG_FOLDER_PATH", str(tmp_path))
    return tmp_path


def test_validation_error_includes_config_path(tmp_rag_folder: Path) -> None:
    data = _load_dict("rag")
    data["retriever"]["similarity_top_k"] = 0
    (tmp_rag_folder / "bad.toml").write_text(tomlkit.dumps(data))

    with pytest.raises(ConfigValidationError) as exc_info:
        RAGConfig.from_toml("bad")

    assert str(exc_info.value) == (
        f"{tmp_rag_folder / 'bad.toml'}: retriever.similarity_top_k: "
        "Input should be greater than 0"
    )


def test_custom_validator_error_message(tmp_rag_folder: Path) -> None:
    """自訂 validator 的訊息不帶 pydantic 的 "Value error, " 前綴。"""
    data = _load_dict("rag")
    data["nodes"]["chunk_overlap"] = 900
    (tmp_rag_folder / "bad.toml").write_text(tomlkit.dumps(data))

    with pytest.raises(ConfigValidationError) as exc_info:
        RAGConfig.from_toml("bad")

    assert str(exc_info.value) == (
        f"{tmp_rag_folder / 'bad.toml'}: nodes: chunk_overlap 必須小於 chunk_size"
    )


def test_missing_config_file(tmp_rag_folder: Path) -> None:
    with pytest.raises(FileNotFoundError, match="missing.toml"):
        RAGConfig.from_toml("missing")


def test_flat_overrides_go_to_their_section() -> None:
    config = RAGConfig.from_toml(
        "test",
        similarity_top_k=20,
        cutoff=0.3,
        hybrid_ranker_params={"weights": [1.0, 0.3]},
    )

    assert config.retriever.similarity_top_k == 20
    assert config.query_engine.cutoff == 0.3
    params = config.vector_store.hybrid_ranker_params
    assert params is not None and params.weights == [1.0, 0.3]


def test_unknown_override_rejected() -> None:
    with pytest.raises(ConfigValidationError, match="unknown_key"):
        RAGConfig.from_toml("test", unknown_key=1)


def test_invalid_override_rejected() -> None:
    with pytest.raises(ConfigValidationError, match="retriever.alpha"):
        RAGConfig.from_toml("test", alpha=2.0)


# ---------- run name ----------


def test_filter_commented_configs_returns_dotted_path(tmp_path: Path) -> None:
    path = tmp_path / "c.toml"
    path.write_text(
        'site_id = "a" # run name\n'
        "[init]\n"
        "max_depth = 2 # run name\n"
        'url = "http://x#y" # other\n'
        "[clean]\n"
        "seed = 1 # run name\n"
    )

    assert filter_commented_configs(str(path), "run name") == [
        "site_id",
        "init.max_depth",
        "clean.seed",
    ]


@pytest.mark.parametrize(
    ("module", "name", "expected"),
    [
        ("website_crawler", "default", "default"),
        ("website_crawler", "ncucsie", "max_depth-2"),
        ("website_crawler", "test", "max_pages-40"),
        ("image_summarizer", "test", "model-gpt-5.6-luna"),
        ("rag", "test", "vector_store_type-milvus"),
        ("agent", "test", "default"),
    ],
)
def test_run_name(module: str, name: str, expected: str) -> None:
    assert MODULE_CONFIGS[module].from_toml(name).run_name == expected


def test_run_name_skips_none_value(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(WebsiteCrawlerConfig, "_CONFIG_FOLDER_PATH", str(tmp_path))
    text = Path("configs/website_crawler/test.toml").read_text()
    (tmp_path / "c.toml").write_text(
        text.replace("max_depth = 2", "max_depth = 2 # run name")
    )
    config = WebsiteCrawlerConfig.from_toml("c")
    assert config.run_name == "max_depth-2_max_pages-40"

    config.init.max_pages = None

    assert config.run_name == "max_depth-2"


def test_private_attrs_not_dumped() -> None:
    config = RAGConfig.from_toml("test")

    assert "config_name" not in config.model_dump()
    assert "run_name_fields" not in config.model_dump()
    assert config.run_name_fields == ["vector_store.vector_store_type"]


# ---------- save_module_config_as_toml 往返 ----------


@pytest.mark.parametrize("module", list(MODULE_CONFIGS))
def test_save_module_config_round_trip(module: str, tmp_path: Path) -> None:
    config_cls = MODULE_CONFIGS[module]
    config = config_cls.from_toml("test")
    path = tmp_path / "module_config.toml"

    save_module_config_as_toml(config, str(path))
    with open(path, "rb") as f:
        saved = tomllib.load(f)

    assert config_cls.model_validate(saved).model_dump() == config.model_dump()


@pytest.mark.parametrize("module", list(MODULE_CONFIGS))
def test_saved_module_config_sections(module: str, tmp_path: Path) -> None:
    """存檔的 section 與設定檔相同；RAG 另含由 site_id 推導出的路徑欄位。"""
    path = tmp_path / "module_config.toml"
    save_module_config_as_toml(MODULE_CONFIGS[module].from_toml("test"), str(path))
    with open(path, "rb") as f:
        saved = tomllib.load(f)
    source = _load_dict(module)

    derived = {"webpages_data_folder_path"} if module == "rag" else set()
    assert set(saved) == set(source) | derived
    for key, value in source.items():
        if isinstance(value, dict):
            assert set(value) <= set(saved[key])
