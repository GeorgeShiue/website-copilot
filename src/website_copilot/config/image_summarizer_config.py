from typing import Any, ClassVar, Literal

from pydantic import Field, NonNegativeInt, PositiveFloat, PositiveInt

from website_copilot.config.base_config import (
    BaseModuleConfig,
    ConfigModel,
    NonEmptyStr,
)
from website_copilot.config.prompts import IMAGE_SUMMARY_PROMPT


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
    _DEFAULT_RUN_NAME_FIELDS: ClassVar[tuple[str, ...]] = ("summarize.model",)

    init: SummarizerInitConfig = Field(default_factory=SummarizerInitConfig)
    summarize: SummarizeConfig = Field(default_factory=SummarizeConfig)
    litellm_kwargs: dict[str, Any] = Field(
        default_factory=dict, description="直接傳給 litellm 的額外參數"
    )

    def _post_process_run_name(self, run_name: str) -> str:
        return run_name.replace("/", "-")
