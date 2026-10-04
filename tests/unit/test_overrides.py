"""config/overrides.py 測試：由 module config 自動產生的 partial model、prune_empty 與 --help 顯示。"""

from typing import Any, Literal

import pytest
from pydantic import BaseModel

from website_copilot.config.agent_config import AgentConfig
from website_copilot.config.augmenter_config import AugmenterConfig
from website_copilot.config.overrides import (
    _format_default,
    _metavar,
    make_overrides_model,
    overrides_to_dict,
    prune_empty,
)
from website_copilot.config.rag_config import RAGConfig, RetrieverConfig
from website_copilot.config.website_crawler_config import WebsiteCrawlerConfig

RAGOverrides = make_overrides_model(RAGConfig)


def _field(model: type[BaseModel], dotted_path: str) -> Any:
    """以 dotted path 取得巢狀 partial model 的 FieldInfo。"""
    *sections, name = dotted_path.split(".")
    for section in sections:
        annotation = model.model_fields[section].annotation
        assert isinstance(annotation, type) and issubclass(annotation, BaseModel)
        model = annotation
    return model.model_fields[name]


def test_model_name() -> None:
    assert RAGOverrides.__name__ == "RAGConfigOverrides"


@pytest.mark.parametrize(
    "config_cls", [WebsiteCrawlerConfig, AugmenterConfig, RAGConfig, AgentConfig]
)
def test_all_leaf_fields_default_to_none(config_cls: type[BaseModel]) -> None:
    """未指定任何值時，overrides 為空 dict（不會以 None 覆蓋設定檔）。"""
    overrides = make_overrides_model(config_cls)()

    assert overrides_to_dict(overrides) == {}


def test_sections_are_nested_models() -> None:
    retriever = _field(RAGOverrides, "retriever")

    assert retriever.annotation.__name__ == "RetrieverConfigOverrides"
    assert set(retriever.annotation.model_fields) == set(RetrieverConfig.model_fields)


def test_optional_section_is_nested_model() -> None:
    """`HybridRankerParams | None` 也展開成巢狀 partial model（避免 tyro 變成子命令）。"""
    params = _field(RAGOverrides, "vector_store.hybrid_ranker_params")

    assert params.annotation.__name__ == "HybridRankerParamsOverrides"
    assert set(params.annotation.model_fields) == {"weights", "k"}


def test_leaf_type_becomes_optional() -> None:
    assert _field(RAGOverrides, "retriever.similarity_top_k").annotation == int | None
    assert (
        _field(RAGOverrides, "retriever.query_mode").annotation
        == Literal["hybrid", "default"] | None
    )


def test_dict_field_excluded() -> None:
    """dict[str, Any]（litellm_kwargs）tyro 無法處理，排除在 CLI 之外。"""
    overrides_cls = make_overrides_model(AugmenterConfig)

    assert "litellm_kwargs" not in overrides_cls.model_fields
    assert "images" in overrides_cls.model_fields


def test_description_copied() -> None:
    assert (
        _field(RAGOverrides, "retriever.alpha").description
        == RetrieverConfig.model_fields["alpha"].description
    )


def test_unknown_field_rejected() -> None:
    with pytest.raises(ValueError, match="unknown"):
        RAGOverrides.model_validate({"retriever": {"unknown": 1}})


def test_overrides_to_dict_keeps_only_specified_values() -> None:
    overrides = RAGOverrides.model_validate(
        {
            "retriever": {"similarity_top_k": 20},
            "vector_store": {"hybrid_ranker_params": {"weights": [1.0, 0.3]}},
        }
    )

    assert overrides_to_dict(overrides) == {
        "retriever": {"similarity_top_k": 20},
        "vector_store": {"hybrid_ranker_params": {"weights": [1.0, 0.3]}},
    }


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ({"a": None, "b": 1}, {"b": 1}),
        ({"a": {}, "b": {"c": None}}, {}),
        ({"a": {"b": {"c": {}}, "d": 0}}, {"a": {"d": 0}}),
        ({"a": [], "b": False, "c": ""}, {"a": [], "b": False, "c": ""}),
    ],
)
def test_prune_empty(data: dict[str, Any], expected: dict[str, Any]) -> None:
    assert prune_empty(data) == expected


# ---------- --help 顯示（help hint、metavar） ----------


@pytest.mark.parametrize(
    ("annotation", "expected"),
    [
        (int | None, "INT"),
        (float, "FLOAT"),
        (Literal["hybrid", "default"] | None, "{hybrid,default}"),
        (bool, "{True,False}"),
        (list[float] | None, "FLOAT [FLOAT ...]"),
        (dict[str, Any], None),
    ],
)
def test_metavar(annotation: Any, expected: str | None) -> None:
    assert _metavar(annotation) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (10, "10"),
        (None, "null"),
        (True, "true"),
        ([1.0, 0.5], "[1.0, 0.5]"),
        ("gpt-5.6-luna", "gpt-5.6-luna"),
        ("a\nb", "a\\nb"),
    ],
)
def test_format_default(value: Any, expected: str) -> None:
    assert _format_default(value) == expected


def test_format_default_truncates_long_string() -> None:
    assert _format_default("x" * 100) == "x" * 60 + "…"
