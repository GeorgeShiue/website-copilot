import logging
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from tomlkit import document, dump, load, table

logger = logging.getLogger(__name__)


class ConfigNotFoundError(ValueError):
    """設定未找到錯誤。"""


class ConfigInvalidTypeError(ValueError):
    """設定類型無效錯誤。"""


class ConfigValidationError(ValueError):
    """設定驗證錯誤。"""


class EnvironmentVariableError(ValueError):
    """環境變數相關錯誤。"""


def _load_toml_section(
    config_path: str,
    config_section: str,
) -> dict[str, Any]:
    """Load a TOML section and return it as a plain dict."""
    with Path(config_path).open("rb") as file:
        toml_content = load(file)

    config = toml_content.get(config_section)
    if config is None:
        raise ConfigNotFoundError(f"Config section not found: {config_section}")

    if not isinstance(config, Mapping):
        raise ConfigInvalidTypeError(f"Config section is not a table: {config_section}")

    return dict(config)


def _filter_allowed_config_keys(
    source_config: Mapping[str, Any],
    allowed_keys: set[str],
    *,
    unknown_keys_warning: str,
) -> dict[str, Any]:
    """Keep only allowed keys and warn for unknown keys if present."""
    unknown_keys = {
        key: value for key, value in source_config.items() if key not in allowed_keys
    }
    if unknown_keys:
        logger.warning(unknown_keys_warning, sorted(unknown_keys.keys()))

    return {key: source_config[key] for key in allowed_keys if key in source_config}


def load_config_section_from_toml(
    config_path: str,
    config_section: str,
    allowed_keys: set[str],
    *,
    unknown_keys_warning: str,
) -> dict[str, Any]:
    """Load one TOML section, then filter by allowed keys with unknown-key warnings."""
    config = _load_toml_section(
        config_path=config_path,
        config_section=config_section,
    )

    filtered_config = _filter_allowed_config_keys(
        source_config=config,
        allowed_keys=allowed_keys,
        unknown_keys_warning=unknown_keys_warning,
    )

    return filtered_config


def save_config_as_toml(
    config: object,
    section_to_keys: Mapping[str, set[str]],
    toml_file_path: str,
) -> None:
    """Persist config values into TOML sections based on key mapping."""
    config_dict = config.__dict__
    toml_doc = document()

    for section_name, section_keys in section_to_keys.items():
        section_table = table()
        for section_key in section_keys:
            config_value = config_dict.get(section_key)
            if config_value is not None:
                section_table[section_key] = config_value
        toml_doc[section_name] = section_table

    with Path(toml_file_path).open("w") as file:
        dump(toml_doc, file)


def log_config(title: str, config: Mapping[str, Any]) -> None:
    """Log config key-values with a section title."""
    if not config:
        return

    logger.info("%s", title)
    for key in config:
        logger.info("  %s: %s", key, config[key])
    logger.info("-" * 30)


def filter_commented_configs(config_path: str, comment_keyword: str) -> list[str]:
    text = Path(config_path).read_text(encoding="utf-8")
    result: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("[") and line.endswith("]") and not line.startswith("[["):
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

        result.append(key)

    return result
