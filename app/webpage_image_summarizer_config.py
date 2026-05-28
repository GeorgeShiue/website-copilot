import logging
import os
from dataclasses import dataclass, field
from typing import Any, Literal, Self

from utils.config_helper import (
    ConfigValidationError,
    filter_commented_configs,
    load_config_from_toml,
    override_config,
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
DEFAULT_CONFIG_FOLDER_PATH = "./config/webpage_image_summarizer"
DEFAULT_CONFIG_NAME = "default"
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
LITELLM_KWARGS_KEYS: set[str] = set()
FIXED_SECTIONS_TO_KEYS = {
    DEFAULT_INIT_CONFIG_SECTION: INIT_KEYS,
    DEFAULT_SUMMARIZE_CONFIG_SECTION: SUMMARIZE_KEYS,
}
SECTIONS_TO_KEYS = {
    **FIXED_SECTIONS_TO_KEYS,
    DEFAULT_LITELLM_CONFIG_SECTION: LITELLM_KWARGS_KEYS,
}
VLM_MODEL_TO_API_KEY: dict[str, str] = {
    "gpt": "OPENAI_WEBPAGE_IMAGE_SUMMARIZER_VLM_API_KEY",
    "gemini": "GEMINI_WEBPAGE_IMAGE_SUMMARIZER_VLM_API_KEY",
}


@dataclass
class WebpageImageSummarizerConfig:
    # ----- metadata (no default values)-----
    config_name: str
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
        default_factory=lambda: {
            section: keys.copy() for section, keys in SECTIONS_TO_KEYS.items()
        }
    )

    def __post_init__(self) -> None:
        _validate_config(vars(self))

    @classmethod
    def from_toml(
        cls,
        config_name: str = DEFAULT_CONFIG_NAME,
        **overrides,
    ) -> Self:
        """從 TOML 設定檔建立 WebpageImageSummarizerConfig。"""
        config_path = os.path.join(DEFAULT_CONFIG_FOLDER_PATH, f"{config_name}.toml")
        config = load_config_from_toml(config_path, SECTIONS_TO_KEYS)
        config = override_config(config, overrides, SECTIONS_TO_KEYS)
        config["config_name"] = config_name
        return cls(**config)

    @property
    def run_name(self) -> str:
        """根據 config toml 中的註解生成 run name。"""
        config_path = os.path.join(
            DEFAULT_CONFIG_FOLDER_PATH, f"{self.config_name}.toml"
        )
        commented_configs = filter_commented_configs(config_path, "run name")

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


def _validate_config(config: dict[str, Any]) -> None:
    # ----- init config -----
    download_timeout = config.get("download_timeout")
    success_threshold = config.get("success_threshold")
    max_retries = config.get("max_retries")

    if download_timeout is not None:
        if download_timeout <= 0:
            raise ConfigValidationError("download_timeout 必須大於 0")

    if success_threshold is not None:
        if not 0 <= success_threshold <= 1:
            raise ConfigValidationError("success_threshold 必須介於 0 到 1")

    if max_retries is not None:
        if max_retries < 0:
            raise ConfigValidationError("max_retries 不可小於 0")

    # ----- summarize config -----
    model = config.get("model")
    image_source = config.get("image_source")
    vlm_max_workers = config.get("vlm_max_workers")

    if model is not None:
        if not model.strip():
            raise ConfigValidationError("model 不可為空字串")

    if vlm_max_workers is not None:
        if vlm_max_workers <= 0:
            raise ConfigValidationError("vlm_max_workers 必須大於 0")

    if image_source is not None and image_source not in {"images", "markdown"}:
        raise ConfigValidationError("image_source 只能是 'images' 或 'markdown'")

    # ----- litellm kwargs validation (type check only) -----
    litellm_config = config.get("litellm_kwargs")
    if litellm_config is not None and not isinstance(litellm_config, dict):
        raise ConfigValidationError("litellm_kwargs 必須是字典")
