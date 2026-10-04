from typing import Annotated, Any, ClassVar, Literal

from pydantic import Field, NonNegativeInt, PositiveFloat, PositiveInt

from website_copilot.config.base_config import (
    BaseModuleConfig,
    ConfigModel,
    NonEmptyStr,
)
from website_copilot.config.prompts import IMAGE_SUMMARY_PROMPT


class DownloadConfig(ConfigModel):
    timeout: PositiveFloat = Field(default=10.0, description="單次請求逾時秒數")
    max_concurrency: PositiveInt = Field(
        default=40, description="同時下載的請求數（所有頁面共用）"
    )
    max_retries: NonNegativeInt = Field(
        default=2,
        description="單一請求遇到逾時、連線錯誤、5xx、429 時的重試次數（不含第一次）",
    )
    max_bytes: PositiveInt = Field(
        default=50 * 1024 * 1024,
        description="單一檔案的大小上限（bytes），超過即視為失敗",
    )


class RetryConfig(ConfigModel):
    success_threshold: float = Field(
        default=0.8,
        ge=0,
        le=1,
        description="成功率（成功 ÷ (成功 + 可恢復失敗)）低於此值則啟動整輪重試機制",
    )
    max_retries: NonNegativeInt = Field(
        default=6,
        description="整輪處理的最大輪數（含第一輪），對應指數退避的長度 + 最後一次用 cap",
    )


class ImagesConfig(ConfigModel):
    enabled: bool = Field(
        default=True, description="是否處理頁面圖片；false 時不呼叫 VLM（不產生費用）"
    )
    model: NonEmptyStr = Field(default="gpt-5.6-luna", description="VLM 模型名稱")
    prompt: NonEmptyStr = Field(
        default=IMAGE_SUMMARY_PROMPT,
        description="圖片摘要 prompt（見 config/prompts.py）",
    )
    source: Literal["images", "markdown"] = Field(
        default="markdown",
        description="圖片來源：爬蟲結果的 images 欄位或 markdown 中的圖片連結",
    )
    max_concurrency: PositiveInt = Field(
        default=50, description="同時呼叫 VLM 摘要圖片的請求數（所有頁面共用）"
    )
    min_size: NonNegativeInt = Field(
        default=100,
        description="圖片長邊小於此像素值不送 VLM、不產生描述（圖示、表情符號等）；0 為不過濾",
    )


class DocumentsConfig(ConfigModel):
    enabled: bool = Field(default=True, description="是否處理網站連結的文件")
    caption_images: bool = Field(
        default=True,
        description="文件內嵌圖片是否交給 VLM 描述並插回文件內容（需 images.enabled）",
    )
    formats: Annotated[
        list[Literal["pdf", "docx", "doc", "odt"]], Field(min_length=1)
    ] = Field(
        default_factory=lambda: ["pdf", "docx", "doc", "odt"],
        description="要下載並解析的文件格式；其餘格式只記統計，不下載（或下載後略過）",
    )


class AugmenterConfig(BaseModuleConfig):
    _CONFIG_FOLDER_PATH: ClassVar[str] = "configs/augmenter"
    _DEFAULT_RUN_NAME_FIELDS: ClassVar[tuple[str, ...]] = ("images.model",)

    download: DownloadConfig = Field(default_factory=DownloadConfig)
    retry: RetryConfig = Field(default_factory=RetryConfig)
    images: ImagesConfig = Field(default_factory=ImagesConfig)
    documents: DocumentsConfig = Field(default_factory=DocumentsConfig)
    litellm_kwargs: dict[str, Any] = Field(
        default_factory=dict, description="直接傳給 litellm 的額外參數"
    )

    def _post_process_run_name(self, run_name: str) -> str:
        return run_name.replace("/", "-")
