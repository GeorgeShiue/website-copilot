import logging
import os
import tomllib
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = "config/webpage_image_summarizer.toml"
DEFAULT_INIT_CONFIG_SECTION = "init"
DEFAULT_SUMMARIZE_CONFIG_SECTION = "summarize"
DEFAULT_LITELLM_CONFIG_SECTION = "litellm_kwargs"
INIT_KEYS = {
    "download_timeout",
    "success_threshold",
    "max_retries",
}
SUMMARIZE_KEYS = {
    "prompt",
    "model",
    "image_source",
    "vlm_max_workers",
}
VLM_MODEL_TO_API_KEY: dict[str, str] = {
    "gpt": "OPENAI_WEBPAGE_SUMMARIZER_VLM_API_KEY",
    "gemini": "GEMINI_WEBPAGE_SUMMARIZER_VLM_API_KEY",
}


class ConfigError(ValueError):
    """設定檔解析或驗證錯誤。"""


def load_init_config_from_toml(
    config_path: str = DEFAULT_CONFIG_PATH,
    config_section: str = DEFAULT_INIT_CONFIG_SECTION,
) -> dict[str, Any]:
    """從 TOML 讀取建構子參數。"""
    init_cfg = _load_config_section_from_toml(config_path, config_section)

    unknown_init_level = {k: v for k, v in init_cfg.items() if k not in INIT_KEYS}
    if unknown_init_level:
        logger.warning(
            "Unknown init config keys will be ignored: %s",
            sorted(unknown_init_level.keys()),
        )

    init_config = {k: init_cfg[k] for k in INIT_KEYS if k in init_cfg}
    validate_init_config(init_config)
    logger.info("Init config from toml validation passed")
    return init_config


def override_init_config(
    init_config: dict[str, Any],
    **overrides: dict[str, Any],
) -> dict[str, Any]:
    """套用 overrides 並輸出建構子參數。"""
    for key, value in overrides.items():
        if key in INIT_KEYS:
            init_config[key] = value

    validate_init_config(init_config)
    logger.info("Init config override validation passed")
    return init_config


def load_summarize_config_from_toml(
    config_path: str = DEFAULT_CONFIG_PATH,
    config_section: str = DEFAULT_SUMMARIZE_CONFIG_SECTION,
) -> dict[str, Any]:
    """從 TOML 讀取 summarize 參數。"""
    summarize_cfg = _load_config_section_from_toml(config_path, config_section)
    litellm_kwargs = _load_config_section_from_toml(
        config_path, DEFAULT_LITELLM_CONFIG_SECTION
    )

    summarize_config = {
        k: summarize_cfg[k] for k in SUMMARIZE_KEYS if k in summarize_cfg
    }

    unknown_summarize_level = {
        k: v for k, v in summarize_cfg.items() if k not in SUMMARIZE_KEYS
    }
    if unknown_summarize_level:
        logger.warning(
            "Unknown summarize config keys will be treated as litellm kwargs: %s",
            sorted(unknown_summarize_level.keys()),
        )

    summarize_config["litellm_kwargs"] = {
        **unknown_summarize_level,
        **litellm_kwargs,
    }

    validate_summarize_config(summarize_config)
    logger.info("Summarize config from toml validation passed")
    return summarize_config


def override_summarize_config(
    summarize_config: dict[str, Any], **overrides: Any
) -> dict[str, Any]:
    """套用 overrides 並輸出 summarize 參數。"""
    summarize_config["litellm_kwargs"] = dict(
        summarize_config.get("litellm_kwargs", {})
    )

    override_summarize_config = overrides.pop("summarize", None)
    override_litellm_kwargs = overrides.pop("litellm_kwargs", None)

    for key, value in overrides.items():
        if key in SUMMARIZE_KEYS:
            summarize_config[key] = value
        else:
            summarize_config["litellm_kwargs"][key] = value

    if override_summarize_config is not None:
        if not isinstance(override_summarize_config, dict):
            raise ConfigError("overrides.summarize 必須是 dict")
        for key, value in override_summarize_config.items():
            if key in SUMMARIZE_KEYS:
                summarize_config[key] = value
            elif key == "litellm_kwargs":
                if not isinstance(value, dict):
                    raise ConfigError("overrides.summarize.litellm_kwargs 必須是 dict")
                summarize_config["litellm_kwargs"].update(value)
            else:
                summarize_config["litellm_kwargs"][key] = value

    if override_litellm_kwargs is not None:
        if not isinstance(override_litellm_kwargs, dict):
            raise ConfigError("overrides.litellm_kwargs 必須是 dict")
        summarize_config["litellm_kwargs"].update(override_litellm_kwargs)

    validate_summarize_config(summarize_config)
    logger.info("Summarize config override validation passed")
    return summarize_config


def _load_config_section_from_toml(
    config_path: str,
    config_section: str,
) -> dict[str, Any]:
    with Path(config_path).open("rb") as f:
        raw = tomllib.load(f)

    scoped_cfg = raw.get(config_section)
    if scoped_cfg is None:
        raise ConfigError(f"找不到設定區段: {config_section}")
    if not isinstance(scoped_cfg, dict):
        raise ConfigError(f"{config_section} 必須是 table")
    return scoped_cfg


# TODO: 若沒有提供 config dict 可用 override 方式動態建立
def validate_init_config(init_config: dict[str, Any]) -> None:
    """驗證建構子參數型別與範圍。"""
    download_timeout = init_config.get("download_timeout")
    if download_timeout is not None:
        if not isinstance(download_timeout, (int, float)):
            raise ConfigError("download_timeout 必須是數字")
        if download_timeout <= 0:
            raise ConfigError("download_timeout 必須大於 0")

    success_threshold = init_config.get("success_threshold")
    if success_threshold is not None:
        if not isinstance(success_threshold, (int, float)):
            raise ConfigError("success_threshold 必須是數字")
        if not 0 <= success_threshold <= 1:
            raise ConfigError("success_threshold 必須介於 0 到 1")

    max_retries = init_config.get("max_retries")
    if max_retries is not None:
        if not isinstance(max_retries, int):
            raise ConfigError("max_retries 必須是整數")
        if max_retries < 0:
            raise ConfigError("max_retries 不可小於 0")


def validate_summarize_config(summarize_config: dict[str, Any]) -> None:
    """驗證 summarize 參數型別與範圍。"""

    model = summarize_config.get("model")
    if model is not None:
        if not isinstance(model, str):
            raise ConfigError("model 必須是字串")
        if not model.strip():
            raise ConfigError("model 不可為空字串")

    prompt = summarize_config.get("prompt")
    if prompt is not None and not isinstance(prompt, str):
        raise ConfigError("prompt 必須是字串")

    vlm_max_workers = summarize_config.get("vlm_max_workers")
    if vlm_max_workers is not None:
        if not isinstance(vlm_max_workers, int):
            raise ConfigError("vlm_max_workers 必須是整數")
        if vlm_max_workers <= 0:
            raise ConfigError("vlm_max_workers 必須大於 0")

    image_source = summarize_config.get("image_source")
    if image_source is not None:
        if image_source not in {"images", "markdown"}:
            raise ConfigError("image_source 只能是 'images' 或 'markdown'")

    litellm_kwargs = summarize_config.get("litellm_kwargs")
    if litellm_kwargs is not None and not isinstance(litellm_kwargs, dict):
        raise ConfigError("litellm_kwargs 必須是 dict")


def log_config(title: str, config: dict[str, Any]) -> None:
    if config:
        logger.info("%s", title)
        for k in config.keys():
            logger.info("  %s: %s", k, config[k])
        logger.info("-" * 30)


def get_vlm_api_key(model: str) -> str:
    """根據 VLM 模型名稱推斷環境變數，並傳回有效的 API 金鑰。"""
    api_key_name: str | None = None
    for keyword, key_var in VLM_MODEL_TO_API_KEY.items():
        if keyword.lower() in model.lower():
            api_key_name = key_var
            break

    if api_key_name is None:
        raise ConfigError(
            f"無法根據模型名稱 '{model}' 推斷 API key 變數。"
            f"請確保模型名稱包含 {list(VLM_MODEL_TO_API_KEY.keys())}"
        )

    load_dotenv()
    api_key = os.getenv(api_key_name)
    if api_key is None:
        raise ConfigError(
            f"環境變數 {api_key_name} 未設定。請檢查 .env 或系統環境變數。"
        )

    return api_key
