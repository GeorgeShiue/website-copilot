"""由 module config 自動產生 CLI 覆寫用的 partial model（`{Config}Overrides`）。

規則：
- 巢狀 section（含 `Model | None` 的可選 section）→ 巢狀 partial model，以預設實例作為預設值
  （避免 tyro 把 `Model | None` 變成子命令）。
- 葉欄位 → `X | None = None`，`None` 代表「未指定」；因此 CLI 無法把欄位設為 null
  （需要時另寫 extends 設定檔）。
- `dict[str, Any]` 欄位（如 `litellm_kwargs`）tyro 無法處理，排除在 CLI 之外，只能寫在設定檔。
- 複製 `Field(description=...)`，讓 `--help` 顯示欄位說明。

partial model 只負責收集 CLI 的值；型別、範圍與跨欄位規則在 `from_yaml()` 合併後統一驗證。
"""

import types
from typing import Any, Union, get_args, get_origin

from pydantic import BaseModel, ConfigDict, Field, create_model

from website_copilot.config.base_config import ConfigModel


class OverridesModel(BaseModel):
    """所有 `{Config}Overrides` 的共用基底。"""

    model_config = ConfigDict(extra="forbid")


def _section_type(annotation: Any) -> type[ConfigModel] | None:
    """annotation 為 `Model` 或 `Model | None` 時回傳 Model，否則回傳 None。"""
    if isinstance(annotation, type) and issubclass(annotation, ConfigModel):
        return annotation
    if get_origin(annotation) in (Union, types.UnionType):
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if len(args) == 1:
            return _section_type(args[0])
    return None


def _is_dict(annotation: Any) -> bool:
    return annotation is dict or get_origin(annotation) is dict


def make_overrides_model(model: type[BaseModel]) -> type[OverridesModel]:
    """遞迴產生 `{Model}Overrides`：所有葉欄位皆為可選，未指定時為 None。"""
    fields: dict[str, Any] = {}
    for name, info in model.model_fields.items():
        annotation = info.annotation
        section = _section_type(annotation)
        if section is not None:
            section_overrides = make_overrides_model(section)
            fields[name] = (
                section_overrides,
                Field(default_factory=section_overrides, description=info.description),
            )
        elif _is_dict(annotation):
            continue
        else:
            assert annotation is not None
            fields[name] = (
                annotation | None,
                Field(default=None, description=info.description),
            )
    return create_model(f"{model.__name__}Overrides", __base__=OverridesModel, **fields)


def prune_empty(data: dict[str, Any]) -> dict[str, Any]:
    """遞迴移除值為 None 的 key 與清空後的 dict（未指定的 section）。"""
    pruned: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, dict):
            value = prune_empty(value)
            if not value:
                continue
        elif value is None:
            continue
        pruned[key] = value
    return pruned


def overrides_to_dict(overrides: BaseModel) -> dict[str, Any]:
    """將 CLI 解析出的 partial model 轉成只含已指定欄位的巢狀 dict。"""
    return prune_empty(overrides.model_dump(exclude_none=True))
