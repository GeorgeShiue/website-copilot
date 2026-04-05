import logging
import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = "config/webpage_image_summarizer.toml"
DEFAULT_CONFIG_SECTION = "webpage_image_summarizer"
INIT_KEYS = {
    "download_timeout",
    "model",
    "prompt",
    "vlm_max_workers",
    "image_source",
    "success_threshold",
    "max_retries",
}
VLM_MODEL_TO_API_KEY: dict[str, str] = {
    "gpt": "OPENAI_WEBPAGE_SUMMARIZER_VLM_API_KEY",
    "gemini": "GEMINI_WEBPAGE_SUMMARIZER_VLM_API_KEY",
}


class ConfigError(ValueError):
    """設定檔解析或驗證錯誤。"""


@dataclass(slots=True)
class WebpageImageSummarizerConfig:
    init_kwargs: dict[str, Any]
    litellm_kwargs: dict[str, Any]


def load_webpage_image_summarizer_args(
    config_path: str = DEFAULT_CONFIG_PATH,
    config_section: str = DEFAULT_CONFIG_SECTION,
    **overrides: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """從 TOML 讀取設定並套用 overrides，回傳建構子與 litellm 參數。"""
    config_obj = _load_webpage_image_summarizer_config(config_path, config_section)
    init_kwargs, litellm_kwargs = _build_init_and_litellm_kwargs(config_obj, overrides)
    return init_kwargs, litellm_kwargs


def _load_webpage_image_summarizer_config(
    config_path: str,
    config_section: str,
) -> WebpageImageSummarizerConfig:
    """從 TOML 讀取設定，並回傳結構化結果。"""
    with Path(config_path).open("rb") as f:
        raw = tomllib.load(f)

    cfg = raw.get(config_section)
    if cfg is None:
        raise ConfigError(f"找不到設定區段: {config_section}")
    if not isinstance(cfg, dict):
        raise ConfigError(f"{config_section} 必須是 table")

    litellm_kwargs = cfg.get("litellm_kwargs", {})
    if not isinstance(litellm_kwargs, dict):
        raise ConfigError("litellm_kwargs 必須是 table")

    unknown_top_level = {
        k: v for k, v in cfg.items() if k not in INIT_KEYS | {"litellm_kwargs"}
    }
    if unknown_top_level:
        logger.warning(
            "Unknown top-level config keys in config_section '%s' will be treated as litellm kwargs: %s",
            config_section,
            sorted(unknown_top_level.keys()),
        )

    init_kwargs = {k: cfg[k] for k in INIT_KEYS if k in cfg}
    merged_litellm_kwargs = {**unknown_top_level, **litellm_kwargs}

    _validate_init_kwargs(init_kwargs)

    return WebpageImageSummarizerConfig(
        init_kwargs=init_kwargs,
        litellm_kwargs=merged_litellm_kwargs,
    )


def _build_init_and_litellm_kwargs(
    config_obj: WebpageImageSummarizerConfig,
    overrides: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """套用 overrides 並輸出建構子與 litellm 參數。"""
    init_kwargs = dict(config_obj.init_kwargs)
    litellm_kwargs = dict(config_obj.litellm_kwargs)
    mutable_overrides = dict(overrides)

    override_litellm_kwargs = mutable_overrides.pop("litellm_kwargs", None)

    for key, value in mutable_overrides.items():
        if key in INIT_KEYS:
            init_kwargs[key] = value
        else:
            litellm_kwargs[key] = value

    if override_litellm_kwargs is not None:
        if not isinstance(override_litellm_kwargs, dict):
            raise ConfigError("overrides.litellm_kwargs 必須是 dict")
        litellm_kwargs.update(override_litellm_kwargs)

    _validate_init_kwargs(init_kwargs)

    return init_kwargs, litellm_kwargs


def _validate_init_kwargs(init_kwargs: dict[str, Any]) -> None:
    """驗證建構子參數型別與範圍。"""
    download_timeout = init_kwargs.get("download_timeout")
    if download_timeout is not None:
        if not isinstance(download_timeout, (int, float)):
            raise ConfigError("download_timeout 必須是數字")
        if download_timeout <= 0:
            raise ConfigError("download_timeout 必須大於 0")

    model = init_kwargs.get("model")
    if model is not None:
        if not isinstance(model, str):
            raise ConfigError("model 必須是字串")
        if not model.strip():
            raise ConfigError("model 不可為空字串")

    prompt = init_kwargs.get("prompt")
    if prompt is not None and not isinstance(prompt, str):
        raise ConfigError("prompt 必須是字串")

    vlm_max_workers = init_kwargs.get("vlm_max_workers")
    if vlm_max_workers is not None:
        if not isinstance(vlm_max_workers, int):
            raise ConfigError("vlm_max_workers 必須是整數")
        if vlm_max_workers <= 0:
            raise ConfigError("vlm_max_workers 必須大於 0")

    image_source = init_kwargs.get("image_source")
    if image_source is not None:
        if image_source not in {"images", "markdown"}:
            raise ConfigError("image_source 只能是 'images' 或 'markdown'")

    success_threshold = init_kwargs.get("success_threshold")
    if success_threshold is not None:
        if not isinstance(success_threshold, (int, float)):
            raise ConfigError("success_threshold 必須是數字")
        if not 0 <= success_threshold <= 1:
            raise ConfigError("success_threshold 必須介於 0 到 1")

    max_retries = init_kwargs.get("max_retries")
    if max_retries is not None:
        if not isinstance(max_retries, int):
            raise ConfigError("max_retries 必須是整數")
        if max_retries < 0:
            raise ConfigError("max_retries 不可小於 0")


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
