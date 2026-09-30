import logging
from typing import Any, ClassVar, Literal

from pydantic import Field, NonNegativeInt, PositiveFloat, PositiveInt

from website_copilot.config.base_config import (
    BaseModuleConfig,
    ConfigModel,
    NonEmptyStr,
)

logger = logging.getLogger(__name__)

VLM_MODEL_TO_API_KEY: dict[str, str] = {
    "gpt": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
}


class SummarizerInitConfig(ConfigModel):
    download_timeout: PositiveFloat = Field(description="單張圖片下載逾時秒數")
    success_threshold: float = Field(
        ge=0, le=1, description="圖片下載成功率低於此值則啟動重試機制"
    )
    max_retries: NonNegativeInt = Field(
        description="最大重試次數，對應指數退避的長度 + 最後一次用 cap"
    )
    cache_download_images: bool = Field(
        description="快取已下載圖片，適用於同一批網頁重複實驗"
    )
    cache_image_captions: bool = Field(
        description="快取圖片摘要，適用於同一批網頁重複實驗"
    )


class SummarizeConfig(ConfigModel):
    model: NonEmptyStr = Field(description="VLM 模型名稱")
    prompt: NonEmptyStr
    image_source: Literal["images", "markdown"] = Field(
        description="圖片來源：爬蟲結果的 images 欄位或 markdown 中的圖片連結"
    )
    vlm_max_workers: PositiveInt


class ImageSummarizerConfig(BaseModuleConfig):
    _CONFIG_FOLDER_PATH: ClassVar[str] = "configs/image_summarizer"

    site_id: NonEmptyStr
    init: SummarizerInitConfig
    summarize: SummarizeConfig
    litellm_kwargs: dict[str, Any] = Field(
        default_factory=dict, description="直接傳給 litellm 的額外參數"
    )

    def _post_process_run_name(self, run_name: str) -> str:
        return run_name.replace("/", "-")
