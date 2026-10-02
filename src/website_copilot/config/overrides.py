"""由 module config 自動產生 CLI 覆寫用的 partial model（`{Config}Overrides`）。

規則：
- 巢狀 section（含 `Model | None` 的可選 section）→ 巢狀 partial model，以預設實例作為預設值
  （避免 tyro 把 `Model | None` 變成子命令）。
- 葉欄位 → `X | None = None`，`None` 代表「未指定」；因此 CLI 無法把欄位設為 null
  （需要時另寫 extends 設定檔）。
- `dict[str, Any]` 欄位（如 `litellm_kwargs`）tyro 無法處理，排除在 CLI 之外，只能寫在設定檔。
- 複製 `Field(description=...)`，讓 `--help` 顯示欄位說明。
- `--help` 以 `(default: X)` 顯示 config class 的預設值（必填欄位標示「必填，來自設定檔」），
  並以 metavar 隱藏 `None` 選項；實際執行時 `--run.config` 設定檔的值優先於此預設。

partial model 只負責收集 CLI 的值；型別、範圍與跨欄位規則在 `from_yaml()` 合併後統一驗證。
"""

import types
from typing import Annotated, Any, Literal, Union, get_args, get_origin

import tyro
import yaml
from pydantic import BaseModel, ConfigDict, Field, create_model
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from website_copilot.config.base_config import ConfigModel
from website_copilot.utils.config_helper import truncate_config_value

REQUIRED_HINT = "(必填，來自設定檔)"
HINT_VALUE_MAX_CHARS = 60


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


def _strip_optional(annotation: Any) -> Any:
    """去除 `X | None` 的 None 與 Annotated 包裝，回傳 X。"""
    if get_origin(annotation) is Annotated:
        return _strip_optional(get_args(annotation)[0])
    if get_origin(annotation) in (Union, types.UnionType):
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if len(args) == 1:
            return _strip_optional(args[0])
    return annotation


def _metavar(annotation: Any) -> str | None:
    """不含 None 選項的 metavar（如 INT、{hybrid,default}、FLOAT [FLOAT ...]）；無法判斷時交給 tyro。"""
    base = _strip_optional(annotation)
    if get_origin(base) is Literal:
        return "{" + ",".join(str(arg) for arg in get_args(base)) + "}"
    if base is bool:
        return "{True,False}"
    if base in (int, float, str):
        return base.__name__.upper()
    if get_origin(base) is list:
        item = _metavar(get_args(base)[0])
        return f"{item} [{item} ...]" if item else None
    return None


def _format_default(value: Any) -> str:
    if isinstance(value, str):
        return truncate_config_value(value, HINT_VALUE_MAX_CHARS)
    if isinstance(value, BaseModel):
        value = value.model_dump()
    return (
        yaml.safe_dump(value, default_flow_style=True)
        .strip()
        .removesuffix("...")
        .strip()
    )


def _field_default(info: FieldInfo) -> Any:
    """欄位預設值；必填欄位回傳 PydanticUndefined。"""
    if info.default_factory is not None:
        return info.default_factory()  # type: ignore[call-arg]
    return info.default


def make_overrides_model(
    model: type[BaseModel], defaults: BaseModel | None = None
) -> type[OverridesModel]:
    """遞迴產生 `{Model}Overrides`：所有葉欄位皆為可選，未指定時為 None。

    defaults 為 section 在上層的預設實例（如 `hybrid_ranker_params` 的預設為
    `HybridRankerParams(weights=[1.0, 0.5])`，與 HybridRankerParams 本身的欄位預設不同），
    用來顯示 help 中的預設值；None 時使用欄位本身的預設值。
    """
    fields: dict[str, Any] = {}
    for name, info in model.model_fields.items():
        annotation = info.annotation
        if defaults is not None:
            default = getattr(defaults, name)
        else:
            default = _field_default(info)

        section = _section_type(annotation)
        if section is not None:
            section_defaults = default if isinstance(default, BaseModel) else None
            section_overrides = make_overrides_model(section, section_defaults)
            fields[name] = (
                section_overrides,
                Field(default_factory=section_overrides, description=info.description),
            )
        elif _is_dict(annotation):
            continue
        else:
            assert annotation is not None
            hint = (
                REQUIRED_HINT
                if default is PydanticUndefined
                else f"(default: {_format_default(default)})"
            )
            arg = tyro.conf.arg(help_behavior_hint=hint, metavar=_metavar(annotation))
            fields[name] = (
                Annotated[annotation | None, arg],
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
