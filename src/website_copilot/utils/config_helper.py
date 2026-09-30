import logging
from pathlib import Path
from typing import Any

from rich.table import Table
from pydantic import BaseModel
from tomlkit import document, dump, inline_table, table

from website_copilot.utils.log_helper import log_session, print_log

logger = logging.getLogger(__name__)


class ConfigValidationError(ValueError):
    """設定驗證錯誤。"""


class EnvironmentVariableError(ValueError):
    """環境變數相關錯誤。"""


def _drop_none(value: Any) -> Any:
    """遞迴移除 dict 中值為 None 的 key（TOML 無 null）。"""
    if isinstance(value, dict):
        return {k: _drop_none(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
        return [_drop_none(v) for v in value]
    return value


def save_module_config_as_toml(
    config: BaseModel,
    toml_file_path: str,
) -> None:
    """將 module config 以 model_dump() 寫成 TOML：頂層欄位在前，巢狀 section 為 [table]。"""
    config_dict = _drop_none(config.model_dump())
    toml_doc = document()

    # TOML 規定頂層 key 必須在所有 [table] 之前
    for key, value in config_dict.items():
        if not isinstance(value, dict):
            toml_doc[key] = value
    for key, value in config_dict.items():
        if isinstance(value, dict):
            section_table = table()
            for section_key, section_value in value.items():
                if isinstance(section_value, dict):
                    nested = inline_table()
                    nested.update(section_value)
                    section_value = nested
                section_table[section_key] = section_value
            toml_doc[key] = section_table

    with Path(toml_file_path).open("w") as file:
        dump(toml_doc, file)


def save_run_config_as_toml(
    config: object,
    toml_file_path: str,
) -> None:
    """Persist all config values into a flat run config TOML document."""
    config_dict = vars(config)
    toml_doc = document()

    for key, value in config_dict.items():
        if value is not None:
            toml_doc[key] = value

    with Path(toml_file_path).open("w") as file:
        dump(toml_doc, file)


def filter_commented_configs(config_path: str, comment_keyword: str) -> list[str]:
    """找出 TOML 中以註解（如 `# run name`）標記的欄位，回傳 dotted path（如 init.max_depth）。

    頂層欄位（在任何 [section] 之前）回傳欄位名本身。
    """
    text = Path(config_path).read_text(encoding="utf-8")
    result: list[str] = []
    section = ""

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("[") and not line.startswith("[["):
            section = line[1 : line.index("]")].strip()
            continue

        in_single = False
        in_double = False
        comment_index = -1
        for idx, ch in enumerate(raw_line):
            if ch == '"' and not in_single:
                in_double = not in_double
            elif ch == "'" and not in_double:
                in_single = not in_single
            elif ch == "#" and not in_single and not in_double:
                comment_index = idx
                break

        if comment_index < 0:
            continue

        comment = raw_line[comment_index + 1 :].strip()
        if comment_keyword not in comment:
            continue

        code_part = raw_line[:comment_index].strip()
        if "=" not in code_part:
            continue

        key_part, _ = code_part.split("=", 1)
        key = key_part.strip()
        if not key:
            continue

        result.append(f"{section}.{key}" if section else key)

    return result


CONFIG_VALUE_MAX_CHARS = 100


def truncate_config_value(value: str, max_chars: int = CONFIG_VALUE_MAX_CHARS) -> str:
    """將換行轉成 `\\n` 並截斷過長字串（超過 max_chars 加 `…`），供 config 表顯示。"""
    display_value = value.replace("\n", "\\n")
    if len(display_value) > max_chars:
        return display_value[:max_chars] + "…"
    return display_value


def _log_config_table(title: str, values: dict[str, Any]) -> None:
    table = Table(
        title=f"[bold cyan]{title}[/bold cyan]",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Config", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")

    for key, value in values.items():
        if isinstance(value, BaseModel):
            value = value.model_dump(exclude_none=True)
        display_value = value
        if isinstance(display_value, str):
            display_value = truncate_config_value(display_value)
        table.add_row(str(key), str(display_value))

    print_log(table)


def log_config(title: str, config: BaseModel) -> None:
    """以 Rich 表格逐 section 輸出 config：頂層欄位一張表，每個巢狀 section 一張表。"""
    top_level: dict[str, Any] = {}
    sections: dict[str, BaseModel] = {}
    for key in type(config).model_fields:
        value = getattr(config, key)
        if isinstance(value, BaseModel):
            sections[key] = value
        else:
            top_level[key] = value

    log_session(title, style="cyan")
    if top_level:
        _log_config_table(type(config).__name__, top_level)
    for section, section_config in sections.items():
        _log_config_table(
            section,
            {
                key: getattr(section_config, key)
                for key in type(section_config).model_fields
            },
        )
