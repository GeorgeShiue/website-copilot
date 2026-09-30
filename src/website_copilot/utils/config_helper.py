import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml
from pydantic import BaseModel
from rich.table import Table

from website_copilot.utils.log_helper import log_session, print_log

if TYPE_CHECKING:
    from website_copilot.config.base_config import BaseModuleConfig

logger = logging.getLogger(__name__)


class ConfigValidationError(ValueError):
    """設定驗證錯誤。"""


class EnvironmentVariableError(ValueError):
    """環境變數相關錯誤。"""


class _ConfigDumper(yaml.SafeDumper):
    """多行字串輸出為 `|` block scalar 的 SafeDumper。"""


def _represent_str(dumper: yaml.SafeDumper, data: str) -> yaml.ScalarNode:
    style = None
    if "\n" in data:
        # 只有換行、沒有其他內容的字串（如 paragraph_separator）以雙引號寫成 "\n\n"
        style = "|" if data.strip() else '"'
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)


_ConfigDumper.add_representer(str, _represent_str)


def dump_yaml(
    data: dict[str, Any], path: str | Path, header: list[str] | None = None
) -> None:
    """以自訂 dumper 寫出 YAML：多行字串為 `|` block scalar、保留中文、保持 key 順序、
    `None` 為 `null`；header 每行寫成檔頭的 `# ` 註解。"""
    text = yaml.dump(
        data,
        Dumper=_ConfigDumper,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    )
    comments = "".join(f"# {line}\n" for line in header or [])
    Path(path).write_text(comments + text, encoding="utf-8")


def save_module_config(config: "BaseModuleConfig", file_path: str) -> None:
    """將 extends 展開後的完整 config（model_dump）寫成 module_config.yml。

    config_name／run_name_fields 不是設定內容，只寫在檔頭註解（來源與 run name 欄位）。
    """
    header = []
    if config.source:
        header.append(f"source: {config.source}")
    header.append(f"run_name_fields: [{', '.join(config.run_name_fields)}]")
    dump_yaml(config.model_dump(), file_path, header=header)


def save_run_config(config: object, file_path: str) -> None:
    """將 run dataclass 的所有欄位寫成 run_config.yml（None 為 null）。"""
    dump_yaml(dict(vars(config)), file_path)


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
