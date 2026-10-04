"""module config（pydantic）載入與驗證測試。

- configs/ 下所有設定檔皆能載入並通過驗證。
- class 預設值：不經設定檔即可建立、預設值本身通過驗證、設定檔省略的欄位使用預設值、
  `default` 設定檔可省略。模組 config 不含站點資訊（站點設定見 test_site_config.py）。
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
from pydantic import PositiveInt, ValidationError

from website_copilot.config.agent_config import AgentConfig
from website_copilot.config.base_config import BaseModuleConfig, ConfigModel
from website_copilot.config.augmenter_config import AugmenterConfig
from website_copilot.config.prompts import AGENT_SYSTEM_PROMPT
from website_copilot.config.rag_config import RAGConfig, RetrieverConfig
from website_copilot.config.website_crawler_config import WebsiteCrawlerConfig
from website_copilot.config.yaml_helper import load_config_dict
from website_copilot.utils.config_helper import (
    ConfigValidationError,
    dump_yaml,
    save_module_config,
)

MODULE_CONFIGS: dict[str, type[BaseModuleConfig]] = {
    "website_crawler": WebsiteCrawlerConfig,
    "augmenter": AugmenterConfig,
    "rag": RAGConfig,
    "agent": AgentConfig,
}

# 模組設定檔（configs/sites/ 的站點設定見 test_site_config.py）
CONFIG_FILES = sorted(
    path
    for module in MODULE_CONFIGS
    for path in Path(f"configs/{module}").glob("*.yml")
)


def _load_dict(module: str, name: str = "test") -> dict[str, Any]:
    """repo 中 configs/ 的設定載入後的完整內容（含 class 預設值，可直接 model_validate 或寫成
    設定檔）；固定讀取 repo 的 configs/，不受測試中 monkeypatch 的 _CONFIG_FOLDER_PATH 影響。"""
    data = load_config_dict(f"configs/{module}", name).data
    data.pop("run_name_fields", None)
    return MODULE_CONFIGS[module].model_validate(data).model_dump()


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
    assert {p.name for p in Path("configs").iterdir() if p.is_dir()} == {
        *MODULE_CONFIGS,
        "sites",
    }
    assert not list(Path("configs").glob("**/*.toml"))


# ---------- class 預設值 ----------


@pytest.mark.parametrize("module", list(MODULE_CONFIGS))
def test_build_without_config_file(module: str) -> None:
    """全部欄位都有 class 預設值，不經設定檔即可建立（含跨欄位規則的驗證）。"""
    config = MODULE_CONFIGS[module]()

    assert config.run_name


@pytest.mark.parametrize("module", ["website_crawler", "augmenter", "rag"])
def test_module_config_has_no_site_fields(module: str) -> None:
    """站點資訊在 SiteConfig，模組 config 不含 site_id／crawl／query 等站點欄位。"""
    fields = MODULE_CONFIGS[module].model_fields

    assert "site_id" not in fields and "crawl" not in fields
    with pytest.raises(ValidationError, match="site_id"):
        MODULE_CONFIGS[module].model_validate({"site_id": "nculab"})


def test_section_defaults() -> None:
    assert RetrieverConfig().similarity_top_k == 10
    config = RAGConfig()
    assert config.retriever == RetrieverConfig()
    params = config.vector_store.hybrid_ranker_params
    assert params is not None and params.weights == [1.0, 0.5]
    assert AgentConfig().system_prompt == AGENT_SYSTEM_PROMPT


def test_mutable_defaults_not_shared() -> None:
    a = RAGConfig()
    b = RAGConfig()
    a.retriever.similarity_top_k = 20
    assert a.vector_store.hybrid_ranker_params is not None
    a.vector_store.hybrid_ranker_params.weights = [0.1, 0.9]

    assert b.retriever.similarity_top_k == 10
    assert b.vector_store.hybrid_ranker_params is not None
    assert b.vector_store.hybrid_ranker_params.weights == [1.0, 0.5]


def test_invalid_default_rejected() -> None:
    """validate_default：誤寫的預設值在建立時即報錯。"""

    class _Bad(ConfigModel):
        count: PositiveInt = 0

    with pytest.raises(ValidationError, match="count"):
        _Bad()


def test_omitted_field_uses_class_default() -> None:
    data = _load_dict("rag")
    del data["retriever"]["alpha"]
    del data["index"]

    config = RAGConfig.model_validate(data)

    assert config.retriever.alpha == RetrieverConfig().alpha
    assert config.index.embedding_name == "text-embedding-3-small"


@pytest.mark.parametrize("module", list(MODULE_CONFIGS))
def test_default_config_file_optional(module: str) -> None:
    """`default` 沒有設定檔時等於 class 預設值（各模組皆已無 default.yml）。"""
    config_cls = MODULE_CONFIGS[module]
    assert not Path(f"configs/{module}/default.yml").exists()

    config = config_cls.from_yaml("default")

    assert config.model_dump() == config_cls().model_dump()
    assert config.source == (
        f"{config_cls.__name__} 預設值（configs/{module}/default.yml 不存在）"
    )


def test_missing_non_default_config_file_rejected() -> None:
    with pytest.raises(FileNotFoundError, match="missing.yml"):
        AgentConfig.from_yaml("missing")


# ---------- strict 型別與未知 key ----------


def test_bool_rejected_for_int_field() -> None:
    data = _load_dict("website_crawler")
    data["init"]["max_depth"] = True

    with pytest.raises(ValidationError, match="init.max_depth"):
        WebsiteCrawlerConfig.model_validate(data)


def test_numeric_string_rejected() -> None:
    data = _load_dict("augmenter")
    data["retry"]["max_retries"] = "6"

    with pytest.raises(ValidationError, match="retry.max_retries"):
        AugmenterConfig.model_validate(data)


def test_int_accepted_for_float_field() -> None:
    data = _load_dict("augmenter")
    data["download"]["timeout"] = 10

    config = AugmenterConfig.model_validate(data)

    assert config.download.timeout == 10.0


@pytest.mark.parametrize("section", [None, "retriever"])
def test_unknown_key_rejected(section: str | None) -> None:
    data = _load_dict("rag")
    (data if section is None else data[section])["unknown_key"] = 1

    with pytest.raises(ValidationError, match="unknown_key"):
        RAGConfig.model_validate(data)


def test_blank_string_rejected() -> None:
    data = _load_dict("agent")
    data["system_prompt"] = "  \n "

    with pytest.raises(ValidationError, match="不可為空白字串"):
        AgentConfig.model_validate(data)


def test_non_empty_str_keeps_whitespace() -> None:
    """NonEmptyStr 只檢查不改寫：prompt 的前後換行原樣保留。"""
    data = _load_dict("augmenter")
    data["images"]["prompt"] = "\nprompt\n"

    config = AugmenterConfig.model_validate(data)

    assert config.images.prompt == "\nprompt\n"


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
        config.milvus_uri = "x"  # type: ignore[attr-defined]  # 位置改由 RAGTarget 提供

    config.retriever.similarity_top_k = 20
    assert config.retriever.similarity_top_k == 20


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
        ("query_llm_name: 2026-09-30", "query_engine.query_llm_name"),  # 日期
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


def test_extends_missing_default_rejected(tmp_rag_folder: Path) -> None:
    """`default` 可省略只適用於直接載入；extends 指向不存在的 default.yml 照舊報錯。"""
    (tmp_rag_folder / "child.yml").write_text("extends: default\n")

    with pytest.raises(ConfigValidationError, match="繼承鏈：child → default"):
        RAGConfig.from_yaml("child")


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
        ("website_crawler", "default", "max_depth-2"),
        ("website_crawler", "test", "max_pages-40"),
        ("augmenter", "default", "model-gpt-5.6-luna"),
        ("augmenter", "test", "model-gpt-5.6-luna"),
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


def test_rag_run_name_keeps_gemini_model_name() -> None:
    """RAG run name 只把 "/" 換成 "-"，不刪除模型名稱中的 "-gemini"。"""
    config = RAGConfig.from_yaml(
        "test", {"query_engine": {"query_llm_name": "models/gemini-2.5-flash"}}
    )
    config._run_name_fields = [
        "vector_store.vector_store_type",
        "query_engine.query_llm_name",
    ]

    assert (
        config.run_name
        == "vector_store_type-milvus_query_llm_name-models-gemini-2.5-flash"
    )


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


def test_run_name_fields_class_default(tmp_rag_folder: Path) -> None:
    """設定檔未寫 run_name_fields 時使用 class 預設；寫 [] 時明確清空。"""
    dump_yaml(_load_dict("rag"), tmp_rag_folder / "plain.yml")
    dump_yaml({"extends": "plain", "run_name_fields": []}, tmp_rag_folder / "empty.yml")

    assert RAGConfig.from_yaml("plain").run_name == "vector_store_type-milvus"
    assert RAGConfig.from_yaml("empty").run_name_fields == []
    assert RAGConfig.from_yaml("empty").run_name == "default"


def test_run_name_without_loader() -> None:
    config = RAGConfig()

    assert config.run_name_fields == ["vector_store.vector_store_type"]
    assert config.run_name == "vector_store_type-milvus"


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
        "# source: configs/rag/test.yml\n"
        "# run_name_fields: [vector_store.vector_store_type]\n"
    )
    saved = yaml.safe_load(text)
    assert "extends" not in saved and "run_name_fields" not in saved
    # None 輸出為 null；只有換行的字串以雙引號輸出
    assert "    k: null\n" in text
    assert '  paragraph_separator: "\\n\\n"\n' in text


def test_saved_multiline_prompt_is_block_scalar(tmp_path: Path) -> None:
    path = tmp_path / "module_config.yml"
    config = AugmenterConfig.from_yaml("test")
    save_module_config(config, str(path))

    assert "  prompt: |\n" in path.read_text(encoding="utf-8")


@pytest.mark.parametrize("module", list(MODULE_CONFIGS))
def test_saved_module_config_has_all_fields(module: str, tmp_path: Path) -> None:
    """存檔包含所有欄位（含 class 預設值與 null），不只設定檔寫到的部分。"""
    config_cls = MODULE_CONFIGS[module]
    path = tmp_path / "module_config.yml"
    save_module_config(config_cls.from_yaml("test"), str(path))
    with open(path, encoding="utf-8") as f:
        saved = yaml.safe_load(f)

    assert list(saved) == list(config_cls.model_fields)
    for name, value in saved.items():
        annotation = config_cls.model_fields[name].annotation
        if isinstance(annotation, type) and issubclass(annotation, ConfigModel):
            assert list(value) == list(annotation.model_fields)
