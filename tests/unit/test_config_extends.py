"""YAML 設定檔 extends 繼承（config/yaml_helper.py）測試。

多層繼承、循環偵測、找不到父檔、合併規則（dict 遞迴合併、list／純量整個取代、
null 清除、{} 不清空 dict）、run_name_fields 的繼承與取代、非頂層保留 key 被拒。
"""

from pathlib import Path
from typing import Any

import pytest

from website_copilot.config.rag_config import RAGConfig
from website_copilot.config.yaml_helper import deep_merge, load_config_dict
from website_copilot.utils.config_helper import ConfigValidationError, dump_yaml


def _write(folder: Path, name: str, data: dict[str, Any]) -> None:
    dump_yaml(data, folder / f"{name}.yml")


# ---------- deep_merge ----------


@pytest.mark.parametrize(
    ("base", "override", "expected"),
    [
        ({"a": {"x": 1, "y": 2}}, {"a": {"y": 3}}, {"a": {"x": 1, "y": 3}}),
        ({"a": [1, 2]}, {"a": [3]}, {"a": [3]}),  # list 整個取代
        ({"a": {"x": 1}}, {"a": None}, {"a": None}),  # null 取代 dict
        ({"a": {"x": 1}}, {"a": {}}, {"a": {"x": 1}}),  # {} 不清空 dict
        ({"a": {"x": 1}}, {"a": {"x": None}}, {"a": {"x": None}}),  # 明確清除 key
        ({"a": 1}, {"a": {"x": 1}}, {"a": {"x": 1}}),  # 型別不同整個取代
        ({"a": 1}, {"b": 2}, {"a": 1, "b": 2}),
    ],
)
def test_deep_merge(
    base: dict[str, Any], override: dict[str, Any], expected: dict[str, Any]
) -> None:
    assert deep_merge(base, override) == expected


def test_deep_merge_does_not_mutate_inputs() -> None:
    base = {"a": {"x": 1}}
    override = {"a": {"y": 2}}

    deep_merge(base, override)

    assert base == {"a": {"x": 1}} and override == {"a": {"y": 2}}


# ---------- load_config_dict ----------


def test_multi_level_extends(tmp_path: Path) -> None:
    _write(tmp_path, "c", {"run_name_fields": [], "a": {"x": 1, "y": 1, "z": 1}})
    _write(tmp_path, "b", {"extends": "c", "a": {"y": 2}})
    _write(tmp_path, "a", {"extends": "b", "a": {"z": 3}})

    loaded = load_config_dict(tmp_path, "a")

    assert loaded.data == {"run_name_fields": [], "a": {"x": 1, "y": 2, "z": 3}}
    assert loaded.chain == ("a", "b", "c")
    assert loaded.source == f"{tmp_path / 'a.yml'} (extends: b → c)"


def test_no_extends_source(tmp_path: Path) -> None:
    _write(tmp_path, "a", {"x": 1})

    loaded = load_config_dict(tmp_path, "a")

    assert loaded.source == str(tmp_path / "a.yml")
    assert "extends" not in loaded.data


def test_cycle_detected(tmp_path: Path) -> None:
    _write(tmp_path, "a", {"extends": "b"})
    _write(tmp_path, "b", {"extends": "a"})

    with pytest.raises(ConfigValidationError, match="循環繼承：a → b → a"):
        load_config_dict(tmp_path, "a")


def test_self_extends_detected(tmp_path: Path) -> None:
    _write(tmp_path, "a", {"extends": "a"})

    with pytest.raises(ConfigValidationError, match="循環繼承：a → a"):
        load_config_dict(tmp_path, "a")


def test_missing_parent(tmp_path: Path) -> None:
    _write(tmp_path, "a", {"extends": "b"})
    _write(tmp_path, "b", {"extends": "missing"})

    with pytest.raises(ConfigValidationError) as exc_info:
        load_config_dict(tmp_path, "a")

    message = str(exc_info.value)
    assert str(tmp_path / "missing.yml") in message
    assert "繼承鏈：a → b → missing" in message


def test_missing_config_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="a.yml"):
        load_config_dict(tmp_path, "a")


def test_toml_not_accepted(tmp_path: Path) -> None:
    (tmp_path / "a.toml").write_text("x = 1\n")

    with pytest.raises(FileNotFoundError):
        load_config_dict(tmp_path, "a")


@pytest.mark.parametrize("value", ["''", "'  '", "[a, b]", "1", "null"])
def test_invalid_extends_value(tmp_path: Path, value: str) -> None:
    (tmp_path / "a.yml").write_text(f"extends: {value}\n")

    with pytest.raises(ConfigValidationError, match="extends 必須是"):
        load_config_dict(tmp_path, "a")


def test_top_level_must_be_mapping(tmp_path: Path) -> None:
    (tmp_path / "a.yml").write_text("- 1\n- 2\n")

    with pytest.raises(ConfigValidationError, match="最上層必須是 mapping"):
        load_config_dict(tmp_path, "a")


def test_empty_file_extends_nothing(tmp_path: Path) -> None:
    (tmp_path / "a.yml").write_text("")

    assert load_config_dict(tmp_path, "a").data == {}


# ---------- 搭配 config model ----------


@pytest.fixture
def rag_folder(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """tmp 的 configs/rag：base.yml 為 configs/rag/test.yml 載入後的完整內容（含 class 預設值
    與 run_name_fields），讓子檔的合併規則可以對所有欄位測試。"""
    config = RAGConfig.from_yaml("test")
    base = {"run_name_fields": config.run_name_fields, **config.model_dump()}
    monkeypatch.setattr(RAGConfig, "_CONFIG_FOLDER_PATH", str(tmp_path))
    _write(tmp_path, "base", base)
    return tmp_path


def test_run_name_fields_inherited(rag_folder: Path) -> None:
    _write(rag_folder, "child", {"extends": "base"})

    assert RAGConfig.from_yaml("child").run_name_fields == [
        "vector_store.vector_store_type"
    ]


def test_run_name_fields_replaced(rag_folder: Path) -> None:
    _write(
        rag_folder,
        "child",
        {"extends": "base", "run_name_fields": ["retriever.similarity_top_k"]},
    )

    config = RAGConfig.from_yaml("child")

    assert config.run_name_fields == ["retriever.similarity_top_k"]
    assert config.run_name == "similarity_top_k-10"


def test_run_name_fields_omitted_uses_class_default(rag_folder: Path) -> None:
    data = load_config_dict(rag_folder, "base").data
    del data["run_name_fields"]
    _write(rag_folder, "plain", data)

    config = RAGConfig.from_yaml("plain")

    assert config.run_name_fields == ["vector_store.vector_store_type"]


@pytest.mark.parametrize("key", ["extends", "run_name_fields"])
def test_reserved_key_rejected_below_top_level(rag_folder: Path, key: str) -> None:
    _write(rag_folder, "child", {"extends": "base", "retriever": {key: "base"}})

    with pytest.raises(ConfigValidationError, match=f"retriever.{key}"):
        RAGConfig.from_yaml("child")


def test_null_clears_optional_field(rag_folder: Path) -> None:
    _write(
        rag_folder,
        "child",
        {"extends": "base", "vector_store": {"hybrid_ranker_params": None}},
    )

    assert RAGConfig.from_yaml("child").vector_store.hybrid_ranker_params is None


def test_null_on_required_field_rejected(rag_folder: Path) -> None:
    _write(rag_folder, "child", {"extends": "base", "retriever": {"alpha": None}})

    with pytest.raises(ConfigValidationError, match="retriever.alpha"):
        RAGConfig.from_yaml("child")


def test_switch_ranker_requires_clearing_weights(rag_folder: Path) -> None:
    """dict 遞迴合併：繼承鏈中已寫 weights 時，改用 RRFRanker 需明確寫 weights: null。"""
    _write(
        rag_folder,
        "rrf_bad",
        {
            "extends": "base",
            "vector_store": {
                "hybrid_ranker": "RRFRanker",
                "hybrid_ranker_params": {"k": 60},
            },
        },
    )
    _write(
        rag_folder,
        "rrf_ok",
        {
            "extends": "base",
            "vector_store": {
                "hybrid_ranker": "RRFRanker",
                "hybrid_ranker_params": {"weights": None, "k": 60},
            },
        },
    )

    with pytest.raises(ConfigValidationError, match="RRFRanker"):
        RAGConfig.from_yaml("rrf_bad")
    params = RAGConfig.from_yaml("rrf_ok").vector_store.hybrid_ranker_params
    assert params is not None and params.k == 60 and params.weights is None


def test_switch_ranker_without_weights_in_chain(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """class 預設值不會與設定檔給的 dict 逐欄合併：繼承鏈未寫 weights 時，只寫 k 即可。"""
    monkeypatch.setattr(RAGConfig, "_CONFIG_FOLDER_PATH", str(tmp_path))
    _write(
        tmp_path,
        "rrf",
        {
            "site_id": "s",
            "query_engine": {"query": "q"},
            "vector_store": {
                "hybrid_ranker": "RRFRanker",
                "hybrid_ranker_params": {"k": 60},
            },
        },
    )

    params = RAGConfig.from_yaml("rrf").vector_store.hybrid_ranker_params

    assert params is not None and params.k == 60 and params.weights is None


def test_empty_dict_does_not_clear_section(rag_folder: Path) -> None:
    _write(rag_folder, "child", {"extends": "base", "retriever": {}})

    assert RAGConfig.from_yaml("child").retriever.similarity_top_k == 10
