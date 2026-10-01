"""module config（pydantic）載入與驗證測試。

- configs/ 下所有設定檔皆能載入並通過驗證。
- strict 型別、未知 key、跨欄位規則、validate_assignment。
- ConfigValidationError 的訊息包含設定檔路徑與欄位路徑。
- run_name_fields 與 run_name 組成；扁平 overrides 放入所屬 section。
- save_module_config 往返：寫出後讀回驗證，model_dump 不變；檔頭註解記錄來源。

extends 的合併規則見 test_config_extends.py。
"""

from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from website_copilot.config.agent_config import AgentConfig
from website_copilot.config.base_config import BaseModuleConfig
from website_copilot.config.image_summarizer_config import ImageSummarizerConfig
from website_copilot.config.rag_config import RAGConfig
from website_copilot.config.website_crawler_config import WebsiteCrawlerConfig
from website_copilot.config.yaml_helper import load_config_dict
from website_copilot.utils.config_helper import (
    ConfigValidationError,
    dump_yaml,
    save_module_config,
)

MODULE_CONFIGS: dict[str, type[BaseModuleConfig]] = {
    "website_crawler": WebsiteCrawlerConfig,
    "image_summarizer": ImageSummarizerConfig,
    "rag": RAGConfig,
    "agent": AgentConfig,
}

CONFIG_FILES = sorted(Path("configs").glob("*/*.yml"))


def _load_dict(module: str, name: str = "test") -> dict[str, Any]:
    """extends 展開後、移除 run_name_fields 的設定內容（可直接 model_validate）。"""
    data = load_config_dict(f"configs/{module}", name).data
    data.pop("run_name_fields", None)
    return data


# ---------- configs/ 下所有設定檔 ----------


@pytest.mark.parametrize(
    "path", CONFIG_FILES, ids=lambda p: f"{p.parent.name}/{p.stem}"
)
def test_all_config_files_load(path: Path) -> None:
    config_cls = MODULE_CONFIGS[path.parent.name]
    config = config_cls.from_yaml(path.stem)

    assert config.config_name == path.stem
    assert config.run_name


def test_config_files_found() -> None:
    assert {p.parent.name for p in CONFIG_FILES} == set(MODULE_CONFIGS)
    assert not list(Path("configs").glob("**/*.toml"))


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
    config = RAGConfig.from_yaml("test")

    with pytest.raises(ValidationError, match="similarity_top_k"):
        config.retriever.similarity_top_k = 0
    with pytest.raises(ValidationError, match="milvus_uri"):
        config.milvus_uri = "x"  # type: ignore[attr-defined]  # 頂層無此欄位

    config.vector_store.milvus_uri = "runs/x/milvus.db"
    assert config.vector_store.milvus_uri == "runs/x/milvus.db"


def test_rag_default_paths_follow_site_id() -> None:
    config = RAGConfig.from_yaml("test", {"site_id": "ncucsie"})

    assert config.webpages_data_folder_path == "data/webpages/ncucsie"
    assert config.vector_store.milvus_uri == "data/rag/ncucsie/milvus.db"


# ---------- from_yaml：錯誤訊息與 overrides ----------


@pytest.fixture
def tmp_rag_folder(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(RAGConfig, "_CONFIG_FOLDER_PATH", str(tmp_path))
    return tmp_path


def test_validation_error_includes_config_path(tmp_rag_folder: Path) -> None:
    data = _load_dict("rag")
    data["retriever"]["similarity_top_k"] = 0
    dump_yaml(data, tmp_rag_folder / "bad.yml")

    with pytest.raises(ConfigValidationError) as exc_info:
        RAGConfig.from_yaml("bad")

    assert str(exc_info.value) == (
        f"{tmp_rag_folder / 'bad.yml'}: retriever.similarity_top_k: "
        "Input should be greater than 0"
    )


def test_validation_error_includes_extends_chain(tmp_rag_folder: Path) -> None:
    """錯誤值可能來自鏈上任一檔，訊息列出實際載入的檔案與繼承鏈。"""
    dump_yaml(_load_dict("rag"), tmp_rag_folder / "base.yml")
    dump_yaml({"extends": "base"}, tmp_rag_folder / "mid.yml")
    dump_yaml(
        {"extends": "mid", "retriever": {"similarity_top_k": 0}},
        tmp_rag_folder / "child.yml",
    )

    with pytest.raises(ConfigValidationError) as exc_info:
        RAGConfig.from_yaml("child")

    assert str(exc_info.value) == (
        f"{tmp_rag_folder / 'child.yml'} (extends: mid → base): "
        "retriever.similarity_top_k: Input should be greater than 0"
    )


def test_custom_validator_error_message(tmp_rag_folder: Path) -> None:
    """自訂 validator 的訊息不帶 pydantic 的 "Value error, " 前綴。"""
    data = _load_dict("rag")
    data["nodes"]["chunk_overlap"] = 900
    dump_yaml(data, tmp_rag_folder / "bad.yml")

    with pytest.raises(ConfigValidationError) as exc_info:
        RAGConfig.from_yaml("bad")

    assert str(exc_info.value) == (
        f"{tmp_rag_folder / 'bad.yml'}: nodes: chunk_overlap 必須小於 chunk_size"
    )


@pytest.mark.parametrize(
    ("text", "field"),
    [
        ("alpha: 1e-3", "retriever.alpha"),  # YAML 1.1：1e-3 為字串
        ("alpha: yes", "retriever.alpha"),  # YAML 1.1：yes 為 bool
        ("query: 2026-09-30", "query_engine.query"),  # 日期
    ],
)
def test_yaml_11_pitfalls_rejected_by_strict(
    tmp_rag_folder: Path, text: str, field: str
) -> None:
    """PyYAML（YAML 1.1）的型別陷阱由 strict 模式攔截，而非靜默轉型。"""
    dump_yaml(_load_dict("rag"), tmp_rag_folder / "base.yml")
    section = field.split(".")[0]
    (tmp_rag_folder / "bad.yml").write_text(
        f"extends: base\n{section}:\n  {text}\n", encoding="utf-8"
    )

    with pytest.raises(ConfigValidationError, match=field):
        RAGConfig.from_yaml("bad")


def test_missing_config_file(tmp_rag_folder: Path) -> None:
    with pytest.raises(FileNotFoundError, match="missing.yml"):
        RAGConfig.from_yaml("missing")


def test_nested_overrides_deep_merged() -> None:
    """overrides 以 deep merge 疊在 extends 展開結果上，未指定的欄位保留設定檔的值。"""
    config = RAGConfig.from_yaml(
        "test",
        {
            "retriever": {"similarity_top_k": 20},
            "query_engine": {"cutoff": 0.3},
            "vector_store": {"hybrid_ranker_params": {"weights": [1.0, 0.3]}},
        },
    )

    assert config.retriever.similarity_top_k == 20
    assert config.retriever.hybrid_top_k == 10
    assert config.query_engine.cutoff == 0.3
    assert config.query_engine.query_llm_name == "gpt-5.6-luna"
    params = config.vector_store.hybrid_ranker_params
    assert params is not None and params.weights == [1.0, 0.3]
    assert config.source.endswith(" + overrides")


def test_empty_overrides_keep_source() -> None:
    assert RAGConfig.from_yaml("test", {}).source == RAGConfig.from_yaml("test").source


@pytest.mark.parametrize(
    "overrides",
    [{"unknown_key": 1}, {"retriever": {"unknown_key": 1}}, {"run_name_fields": []}],
)
def test_unknown_override_rejected(overrides: dict[str, Any]) -> None:
    with pytest.raises(ConfigValidationError, match="unknown_key|run_name_fields"):
        RAGConfig.from_yaml("test", overrides)


def test_invalid_override_rejected() -> None:
    """override 的值同樣經過驗證，錯誤訊息標示有套用 overrides。"""
    with pytest.raises(ConfigValidationError) as exc_info:
        RAGConfig.from_yaml("test", {"retriever": {"alpha": 2.0}})

    message = str(exc_info.value)
    assert "+ overrides: retriever.alpha:" in message


def test_override_triggers_cross_field_rule() -> None:
    """只改 hybrid_ranker 時，合併後仍帶有設定檔的 weights，被跨欄位規則擋下。"""
    with pytest.raises(ConfigValidationError, match="RRFRanker"):
        RAGConfig.from_yaml("test", {"vector_store": {"hybrid_ranker": "RRFRanker"}})


# ---------- run name ----------


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
    assert MODULE_CONFIGS[module].from_yaml(name).run_name == expected


def test_run_name_skips_none_value() -> None:
    config = WebsiteCrawlerConfig.from_yaml("test")
    config._run_name_fields = ["init.max_depth", "init.max_pages"]
    assert config.run_name == "max_depth-2_max_pages-40"

    config.init.max_pages = None

    assert config.run_name == "max_depth-2"


@pytest.mark.parametrize(
    ("fields", "match"),
    [
        ("init.max_pages", "必須是 dotted path 字串的 list"),
        ("[init.unknown]", "找不到欄位 init.unknown"),
        ("[init.max_pages.x]", "找不到欄位 init.max_pages.x"),
        ("[max_pages]", "找不到欄位 max_pages"),
    ],
)
def test_invalid_run_name_fields_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fields: str, match: str
) -> None:
    monkeypatch.setattr(WebsiteCrawlerConfig, "_CONFIG_FOLDER_PATH", str(tmp_path))
    dump_yaml(_load_dict("website_crawler"), tmp_path / "base.yml")
    (tmp_path / "c.yml").write_text(f"extends: base\nrun_name_fields: {fields}\n")

    with pytest.raises(ConfigValidationError, match=match):
        WebsiteCrawlerConfig.from_yaml("c")


def test_private_attrs_not_dumped() -> None:
    config = RAGConfig.from_yaml("test")

    assert "config_name" not in config.model_dump()
    assert "run_name_fields" not in config.model_dump()
    assert config.run_name_fields == ["vector_store.vector_store_type"]


# ---------- save_module_config 往返 ----------


@pytest.mark.parametrize("module", list(MODULE_CONFIGS))
def test_save_module_config_round_trip(module: str, tmp_path: Path) -> None:
    config_cls = MODULE_CONFIGS[module]
    config = config_cls.from_yaml("test")
    path = tmp_path / "module_config.yml"

    save_module_config(config, str(path))
    with open(path, encoding="utf-8") as f:
        saved = yaml.safe_load(f)

    assert config_cls.model_validate(saved).model_dump() == config.model_dump()


def test_saved_module_config_header(tmp_path: Path) -> None:
    """附加資訊只寫在檔頭註解，不含 extends 與 run_name_fields key。"""
    path = tmp_path / "module_config.yml"
    save_module_config(RAGConfig.from_yaml("test"), str(path))
    text = path.read_text(encoding="utf-8")

    assert text.startswith(
        "# source: configs/rag/test.yml (extends: test_nculab → nculab → default)\n"
        "# run_name_fields: [vector_store.vector_store_type]\n"
    )
    saved = yaml.safe_load(text)
    assert "extends" not in saved and "run_name_fields" not in saved
    # None 輸出為 null；只有換行的字串以雙引號輸出
    assert "    k: null\n" in text
    assert '  paragraph_separator: "\\n\\n"\n' in text


def test_saved_multiline_prompt_is_block_scalar(tmp_path: Path) -> None:
    path = tmp_path / "module_config.yml"
    config = ImageSummarizerConfig.from_yaml("test")
    save_module_config(config, str(path))

    assert "  prompt: |\n" in path.read_text(encoding="utf-8")


@pytest.mark.parametrize("module", list(MODULE_CONFIGS))
def test_saved_module_config_sections(module: str, tmp_path: Path) -> None:
    """存檔的 key 與設定檔（extends 展開後）相同。"""
    path = tmp_path / "module_config.yml"
    save_module_config(MODULE_CONFIGS[module].from_yaml("test"), str(path))
    with open(path, encoding="utf-8") as f:
        saved = yaml.safe_load(f)
    source = _load_dict(module)

    assert set(saved) == set(source)
    for key, value in source.items():
        if isinstance(value, dict):
            assert set(value) <= set(saved[key])
