import logging
import os
from dataclasses import dataclass, field
from typing import Any, Literal, Self

from dotenv import load_dotenv

from utils.config_helper import (
    ConfigValidationError,
    EnvironmentVariableError,
    filter_commented_configs,
    load_config_section_from_toml,
)

logger = logging.getLogger(__name__)

DEFAULT_PROMPT = """
用繁體中文描述圖片，作為網頁補充說明。

依序輸出：
    - 圖片摘要：1 句（20-40 字）。
    - 可觀察元素：列出 3-5 點可直接看見的內容（物件、顏色、位置、構圖）。
    - 可讀文字：列出圖片中的文字；若沒有請寫「無」。
    - 場景功能：1 句，描述圖片中場景可能的用途或功能。

規則：
    - 只寫可觀察事實，避免主觀形容詞。
    - 不確定就寫「不確定」，不要臆測細節。
    - 若需列點，一律使用「*」作為 Markdown 列點符號。
"""
DEFAULT_CONFIG_FODER_PATH = "./config/webpage_image_summarizer"
DEFAULT_INIT_CONFIG_SECTION = "init"
DEFAULT_SUMMARIZE_CONFIG_SECTION = "summarize"
DEFAULT_LITELLM_CONFIG_SECTION = "litellm_kwargs"
INIT_KEYS = {
    "download_timeout",
    "success_threshold",
    "max_retries",
    "cache_download_images",
}
SUMMARIZE_KEYS = {
    "prompt",
    "model",
    "image_source",
    "vlm_max_workers",
}
SECTIONS_TO_KEYS = {
    "init": INIT_KEYS,
    "summarize": SUMMARIZE_KEYS,
}
VLM_MODEL_TO_API_KEY: dict[str, str] = {
    "gpt": "OPENAI_WEBPAGE_IAMGE_SUMMARIZER_VLM_API_KEY",
    "gemini": "GEMINI_WEBPAGE_IMAGE_SUMMARIZER_VLM_API_KEY",
}


# arg parse 可以改用 tyro
@dataclass
class WebpageImageSummarizerConfig:
    # ----- metadata (no default values)-----
    config_path: str
    # ----- init config -----
    download_timeout: float = 10.0
    success_threshold: float = 0.8  # 圖片下載成功率低於此值則啟動重試機制
    max_retries: int = 6  # 最大重試次數，對應指數退避的長度 + 最後一次用 cap
    cache_download_images: bool = False
    # ----- summarize config -----
    model: str = "gpt-5-mini"
    prompt: str = DEFAULT_PROMPT
    image_source: Literal["images", "markdown"] = "markdown"
    vlm_max_workers: int = 10
    litellm_kwargs: dict[str, Any] = field(default_factory=dict)
    # ----- metadata -----
    sections_to_keys: dict[str, set[str]] = field(
        default_factory=lambda: SECTIONS_TO_KEYS
    )

    def __post_init__(self):
        _validate_init_config(
            download_timeout=self.download_timeout,
            success_threshold=self.success_threshold,
            max_retries=self.max_retries,
            cache_download_images=self.cache_download_images,
        )
        _validate_summarize_config(
            prompt=self.prompt,
            model=self.model,
            image_source=self.image_source,
            vlm_max_workers=self.vlm_max_workers,
            litellm_kwargs=self.litellm_kwargs,
        )

    @classmethod
    def from_toml(
        cls,
        config_name: str = "default",
        init_config_section: str = DEFAULT_INIT_CONFIG_SECTION,
        summarize_config_section: str = DEFAULT_SUMMARIZE_CONFIG_SECTION,
    ) -> Self:
        """從 TOML 設定檔建立 WebpageImageSummarizerConfig。"""
        config_path = os.path.join(DEFAULT_CONFIG_FODER_PATH, f"{config_name}.toml")
        cls.config_path = config_path
        init_config = _load_init_config_from_toml(config_path, init_config_section)
        summarize_config = _load_summarize_config_from_toml(
            config_path, summarize_config_section
        )
        return cls(**init_config, **summarize_config, config_path=config_path)

    def override_init_config(self, **overrides) -> None:
        """覆寫建構子參數並驗證。"""
        _override_init_config(vars(self), **overrides)

    def override_summarize_config(self, **overrides) -> None:
        """覆寫 summarize 參數並驗證。"""
        _override_summarize_config(vars(self), **overrides)

    @property
    def run_name(self) -> str:
        """根據 config toml 中的註解生成 run name。"""
        commented_configs = filter_commented_configs(self.config_path, "run name")

        if not commented_configs:
            return "default"

        run_name = ""
        for config in commented_configs:
            value = getattr(self, config, None)
            if value is not None:
                run_name += f"{config}-{value}_"
        run_name = run_name.rstrip("_").replace("/", "-")

        # 刪除模型名稱中多餘的 "-gemini"
        if run_name.find("-gemini") > 1:
            run_name = run_name.replace("-gemini", "", 1)

        return run_name


def _validate_init_config(init_config: dict[str, Any] = {}, **init_kwargs) -> None:
    """驗證建構子參數型別與範圍。"""
    if init_config:
        download_timeout = init_config.get("download_timeout")
        success_threshold = init_config.get("success_threshold")
        max_retries = init_config.get("max_retries")
    else:
        download_timeout = init_kwargs.get("download_timeout")
        success_threshold = init_kwargs.get("success_threshold")
        max_retries = init_kwargs.get("max_retries")

    if download_timeout is not None:
        if not isinstance(download_timeout, (int, float)):
            raise ConfigValidationError("download_timeout 必須是數字")
        if download_timeout <= 0:
            raise ConfigValidationError("download_timeout 必須大於 0")

    if success_threshold is not None:
        if not isinstance(success_threshold, (int, float)):
            raise ConfigValidationError("success_threshold 必須是數字")
        if not 0 <= success_threshold <= 1:
            raise ConfigValidationError("success_threshold 必須介於 0 到 1")

    if max_retries is not None:
        if not isinstance(max_retries, int):
            raise ConfigValidationError("max_retries 必須是整數")
        if max_retries < 0:
            raise ConfigValidationError("max_retries 不可小於 0")

    cache_download_images = init_kwargs.get("cache_download_images")
    if cache_download_images is not None and not isinstance(
        cache_download_images, bool
    ):
        raise ConfigValidationError("cache_download_images 必須是布林值")


def _validate_summarize_config(
    summarize_config: dict[str, Any] = {}, **summarize_kwargs
) -> None:
    """驗證 summarize 參數型別與範圍。"""
    if summarize_config:
        model = summarize_config.get("model")
        prompt = summarize_config.get("prompt")
        vlm_max_workers = summarize_config.get("vlm_max_workers")
        image_source = summarize_config.get("image_source")
        litellm_kwargs = summarize_config.get("litellm_kwargs")
    else:
        model = summarize_kwargs.get("model")
        prompt = summarize_kwargs.get("prompt")
        vlm_max_workers = summarize_kwargs.get("vlm_max_workers")
        image_source = summarize_kwargs.get("image_source")
        litellm_kwargs = summarize_kwargs.get("litellm_kwargs")

    if model is not None:
        if not isinstance(model, str):
            raise ConfigValidationError("model 必須是字串")
        if not model.strip():
            raise ConfigValidationError("model 不可為空字串")

    if prompt is not None and not isinstance(prompt, str):
        raise ConfigValidationError("prompt 必須是字串")

    if vlm_max_workers is not None:
        if not isinstance(vlm_max_workers, int):
            raise ConfigValidationError("vlm_max_workers 必須是整數")
        if vlm_max_workers <= 0:
            raise ConfigValidationError("vlm_max_workers 必須大於 0")

    if image_source is not None:
        if image_source not in {"images", "markdown"}:
            raise ConfigValidationError("image_source 只能是 'images' 或 'markdown'")

    if litellm_kwargs is not None and not isinstance(litellm_kwargs, dict):
        raise ConfigValidationError("litellm_kwargs 必須是 dict")


def _load_init_config_from_toml(
    config_path: str,
    config_section: str,
) -> dict[str, Any]:
    """從 TOML 讀取建構子參數。"""
    return load_config_section_from_toml(
        config_path=config_path,
        config_section=config_section,
        allowed_keys=INIT_KEYS,
        unknown_keys_warning="Unknown init config keys will be ignored: %s",
    )


def _load_summarize_config_from_toml(
    config_path: str,
    config_section: str,
) -> dict[str, Any]:
    """從 TOML 讀取 summarize 參數。"""
    summarize_cfg = load_config_section_from_toml(
        config_path=config_path,
        config_section=config_section,
        allowed_keys=SUMMARIZE_KEYS,
        unknown_keys_warning="Unknown summarize config keys will be treated as litellm kwargs: %s",
    )

    litellm_kwargs = load_config_section_from_toml(
        config_path=config_path,
        config_section=DEFAULT_LITELLM_CONFIG_SECTION,
        allowed_keys=set(),  # 允許所有 key
        unknown_keys_warning="",
    )

    summarize_cfg["litellm_kwargs"] = {
        **summarize_cfg.get("litellm_kwargs", {}),
        **litellm_kwargs,
    }

    return summarize_cfg


def _override_init_config(
    init_config: dict[str, Any],
    **overrides: dict[str, Any],
) -> dict[str, Any]:
    """套用 overrides 並輸出建構子參數。"""
    for key, value in overrides.items():
        if key in INIT_KEYS:
            init_config[key] = value

    _validate_init_config(init_config)
    return init_config


def _override_summarize_config(
    summarize_config: dict[str, Any], **overrides: dict[str, Any]
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
            raise ConfigValidationError("overrides.summarize 必須是 dict")
        for key, value in override_summarize_config.items():
            if key in SUMMARIZE_KEYS:
                summarize_config[key] = value
            elif key == "litellm_kwargs":
                if not isinstance(value, dict):
                    raise ConfigValidationError(
                        "overrides.summarize.litellm_kwargs 必須是 dict"
                    )
                summarize_config["litellm_kwargs"].update(value)
            else:
                summarize_config["litellm_kwargs"][key] = value

    if override_litellm_kwargs is not None:
        if not isinstance(override_litellm_kwargs, dict):
            raise ConfigValidationError("overrides.litellm_kwargs 必須是 dict")
        summarize_config["litellm_kwargs"].update(override_litellm_kwargs)

    _validate_summarize_config(summarize_config)
    return summarize_config


def get_summarizer_model_api_key(model: str) -> str:
    """根據模型名稱推斷環境變數，並傳回有效的 API 金鑰。"""
    api_key_name: str | None = None
    for keyword, key_var in VLM_MODEL_TO_API_KEY.items():
        if keyword.lower() in model.lower():
            api_key_name = key_var
            break

    if api_key_name is None:
        raise EnvironmentVariableError(
            f"無法根據模型名稱 '{model}' 推斷 API key 變數。"
            f"請確保模型名稱包含 {list(VLM_MODEL_TO_API_KEY.keys())}"
        )

    load_dotenv()
    api_key = os.getenv(api_key_name)
    if api_key is None:
        raise EnvironmentVariableError(
            f"環境變數 {api_key_name} 未設定。請檢查 .env 或系統環境變數。"
        )

    return api_key
