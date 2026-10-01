import logging
from typing import Any, ClassVar, Literal

from pydantic import Field, NonNegativeInt, PositiveFloat, PositiveInt

from website_copilot.config.base_config import (
    BaseModuleConfig,
    ConfigModel,
    NonEmptyStr,
)
from website_copilot.config.prompts import IMAGE_SUMMARY_PROMPT

logger = logging.getLogger(__name__)

VLM_MODEL_TO_API_KEY: dict[str, str] = {
    "gpt": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
}


class SummarizerInitConfig(ConfigModel):
    download_timeout: PositiveFloat = Field(
        default=10.0, description="單張圖片下載逾時秒數"
    )
    success_threshold: float = Field(
        default=0.8, ge=0, le=1, description="圖片下載成功率低於此值則啟動重試機制"
    )
    max_retries: NonNegativeInt = Field(
        default=6, description="最大重試次數，對應指數退避的長度 + 最後一次用 cap"
    )
    cache_download_images: bool = Field(
        default=True, description="快取已下載圖片，適用於同一批網頁重複實驗"
    )
    cache_image_captions: bool = Field(
        default=True, description="快取圖片摘要，適用於同一批網頁重複實驗"
    )


class SummarizeConfig(ConfigModel):
    model: NonEmptyStr = Field(default="gpt-5.6-luna", description="VLM 模型名稱")
    prompt: NonEmptyStr = Field(
        default=IMAGE_SUMMARY_PROMPT,
        description="圖片摘要 prompt（見 config/prompts.py）",
    )
    image_source: Literal["images", "markdown"] = Field(
        default="markdown",
        description="圖片來源：爬蟲結果的 images 欄位或 markdown 中的圖片連結",
    )
    vlm_max_workers: PositiveInt = 20


class ImageSummarizerConfig(BaseModuleConfig):
    _CONFIG_FOLDER_PATH: ClassVar[str] = "configs/image_summarizer"

    site_id: NonEmptyStr  # Phase D 移除，改由 SiteConfig 提供
    init: SummarizerInitConfig = Field(default_factory=SummarizerInitConfig)
    summarize: SummarizeConfig = Field(default_factory=SummarizeConfig)
    litellm_kwargs: dict[str, Any] = Field(
        default_factory=dict, description="直接傳給 litellm 的額外參數"
    )

    def _post_process_run_name(self, run_name: str) -> str:
        return run_name.replace("/", "-")
