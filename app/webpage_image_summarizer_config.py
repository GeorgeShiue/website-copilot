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
你是網頁圖片資訊萃取器。目標是為 RAG 產生精確、可檢索的圖片摘要。

【核心規則】
1. 先在內部過濾低資訊字與重複內容，再進行圖片摘要與 OCR；低資訊字不得出現在最終輸出。
2. 僅描述可見事實；禁止模板語、美術評論與推論。
3. 優先保留實體名稱、完整 OCR 文字與頁面主題詞；實體僅收錄具獨立語義的名詞短語，且不得逐字重複 OCR。
4. 圖片摘要以實體優先，依主體實體、位置關係、功能或上下文撰寫，不先寫修飾詞。
5. 頁面關聯僅填可見且可驗證的頁面主題、所屬對象與檢索錨點，且至少包含 1 個可命名錨點（人名、組織名、專案名、產品名、活動名、頁面標題詞）；禁止使用代表、象徵、常作為、通常用於、應用於、適合作為等推論語句。
6. 圖片缺乏可識別身份資訊時，優先以頁面標題或鄰近文字中的專有名詞補足，不得憑空推論。
7. 圖片過度模糊、遮擋或僅有背景，或 OCR 無法辨識時，明確填寫無法辨識或無可辨識實體；局部不清楚以 [模糊] 標示。

【輸出格式】
**圖片摘要：**
用一句話清晰描述圖片的實際內容、主要實體與結構。
以實體優先，精確描述物件位置與關係，不包含風格修飾詞。

**主要元素：**
1. 實體: 列出最多 5 個名詞短語，專有名詞優先，以逗號分隔
2. OCR文字: 逐字逐句完整抽取圖片上所有可見的文字內容，保留原始版面與順序。若無文字填寫無
3. 主題標籤: 最多 5 個與頁面主題直接相關的分類詞，只能使用專案名、功能名、領域名或明確主題詞，以逗號分隔

**頁面關聯：**
以短語或單句列出圖片的頁面角色、所屬對象與檢索錨點。
優先使用可命名資訊：人名、組織名、專案名、產品名、活動名、頁面標題關鍵詞。

【特別說明】
- 圖片摘要控制在 50 字內
- 主要元素控制在 60 字內，不含 OCR文字
- 頁面關聯控制在 40 字內
- 圖片摘要、主要元素與頁面關聯合計不超過 150 字，不含 OCR文字
- OCR文字 應完整保留所有可見文字，不受字數限制
- 多行文字按出現順序分行列出，並保留特殊符號、數字與日期等原始格式
- 所有欄位均不使用括號，直接列出內容
- 低資訊字只在內部過濾，不列入最終輸出
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
    "cache_image_captions",
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
    cache_image_captions: bool = False
    # ----- summarize config -----
    model: str = "gemini/gemini-3-flash-preview"
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
            cache_image_captions=self.cache_image_captions,
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

    cache_image_captions = init_kwargs.get("cache_image_captions")
    if cache_image_captions is not None and not isinstance(cache_image_captions, bool):
        raise ConfigValidationError("cache_image_captions 必須是布林值")


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
