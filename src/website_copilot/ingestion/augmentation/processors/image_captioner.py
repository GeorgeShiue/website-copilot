"""圖片解析：下載結果 → base64 data URL（格式白名單），再以 VLM 產生描述。"""

import asyncio
import base64
import io
import logging
from typing import Any

from litellm import acompletion, completion_cost
from PIL import Image

from website_copilot.utils.http_downloader import DownloadResult
from website_copilot.utils.llm_provider import get_api_key, resolve_provider
from website_copilot.utils.log_helper import TaskCountProgress

logger = logging.getLogger(__name__)

# VLM（OpenAI）僅支援 png / jpeg / gif / webp
SUPPORTED_IMAGE_CONTENT_TYPES = frozenset(
    {"image/png", "image/jpeg", "image/gif", "image/webp"}
)


def to_image_data_url(result: DownloadResult) -> tuple[str | None, str]:
    """下載成功的圖片轉成 VLM 用的 base64 data URL；Content-Type 不在白名單時回傳 (None, 原因)。"""
    assert result.content is not None
    content_type = result.headers.get("content-type", "").split(";")[0].strip()
    if content_type not in SUPPORTED_IMAGE_CONTENT_TYPES:
        logger.warning(
            "Unsupported image content-type (url=%s, content_type=%s)",
            result.url,
            content_type or "<empty>",
        )
        return None, f"unsupported content-type {content_type or '<empty>'}"

    b64 = base64.standard_b64encode(result.content).decode("ascii")
    return f"data:{content_type};base64,{b64}", ""


def to_data_url(image: Any) -> str | None:
    """文件內嵌圖片 → VLM 用的 base64 data URL；格式不在白名單時先嘗試以 Pillow 轉成 PNG，仍不行回傳 None。"""
    media_type = image.media_type.split(";")[0].strip().lower()
    content = image.content
    if media_type not in SUPPORTED_IMAGE_CONTENT_TYPES:
        try:
            with Image.open(io.BytesIO(content)) as converted:
                buffer = io.BytesIO()
                converted.convert("RGBA").save(buffer, format="PNG")
        except Exception as e:  # noqa: BLE001 -- Pillow 轉檔失敗的例外型別繁多；統一降級為略過此圖
            logger.warning(
                "Image conversion to PNG failed (media_type=%s): %s", media_type, e
            )
            return None
        media_type, content = "image/png", buffer.getvalue()
    return (
        f"data:{media_type};base64,{base64.standard_b64encode(content).decode('ascii')}"
    )


def caption_block(index: int, caption: str) -> str:
    """圖片描述區塊（頁面圖片與文件內嵌圖片共用的格式）；index 為圖片在頁面／文件內的序號。"""
    return f"> # Image-{index}\n>\n> {caption.replace(chr(10), chr(10) + '> ')}\n"


class ImageCaptioner:
    def __init__(
        self,
        *,
        model: str,
        prompt: str,
        max_concurrency: int,  # 同時呼叫 VLM 的請求數（一次 caption 呼叫內所有頁面共用）
        litellm_kwargs: dict[str, Any] | None = None,
    ) -> None:
        self.model = model
        self.prompt = prompt
        self.max_concurrency = max_concurrency
        self.litellm_kwargs = litellm_kwargs or {}
        # 建構時解析一次：無法判斷供應商或缺 API key 時直接失敗，不逐張圖報錯
        provider = resolve_provider(model)
        self._litellm_model = f"{provider.litellm_prefix}{model}"
        self._api_key = get_api_key(provider)

    def caption(self, images: dict[str, str]) -> list[tuple[str, str, str, float]]:
        """同步版：url → base64 data URL 的圖片批次摘要，回傳 (url, caption, status, cost)。"""
        if not images:
            return []
        return asyncio.run(self._agenerate_image_captions(images))

    async def _agenerate_image_captions(
        self,
        images: dict[str, str],
    ) -> list[tuple[str, str, str, float]]:
        """對圖片批次平行摘要，回傳 (url, caption, status, cost)。"""
        # 同一批 task 共用一個 semaphore 才能限制並行數（event loop 隨 asyncio.run 建立，不可跨呼叫保存）
        semaphore = asyncio.Semaphore(self.max_concurrency)
        tasks: list[asyncio.Task[tuple[str, str, str, float]]] = []
        for image_url, image_base64_url in images.items():
            task = asyncio.create_task(
                self._agenerate_image_caption_task(
                    semaphore, image_url, image_base64_url
                )
            )
            tasks.append(task)

        results: list[tuple[str, str, str, float]] = []
        with TaskCountProgress() as progress:
            task_id = progress.add_task("Generating captions...", total=len(tasks))

            for completed_task in asyncio.as_completed(tasks):
                try:
                    results.append(await completed_task)
                except Exception as e:
                    logger.warning(
                        "Image summarization task failed unexpectedly: %s",
                        e,
                        exc_info=True,
                    )
                finally:
                    progress.update(task_id, advance=1)

        return results

    async def _agenerate_image_caption_task(
        self,
        semaphore: asyncio.Semaphore,
        image_url: str,
        image_base64_url: str,
    ) -> tuple[str, str, str, float]:
        async with semaphore:
            (
                image_caption,
                summarize_status,
                cost_usd,
            ) = await self._agenerate_image_caption(image_base64_url)
            return image_url, image_caption, summarize_status, cost_usd

    async def _agenerate_image_caption(
        self,
        image_base64_url: str,
    ) -> tuple[str, str, float]:
        """呼叫 VLM 取得圖片描述。"""
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": self.prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_base64_url},
                    },
                ],
            }
        ]
        litellm_kwargs: dict[str, Any] = {"api_key": self._api_key}  # 避免 api key 洩漏
        litellm_kwargs.update(self.litellm_kwargs)
        image_caption = ""

        try:
            response = await acompletion(
                model=self._litellm_model,
                messages=messages,
                stream=False,
                **litellm_kwargs,
            )
        except Exception as e:
            logger.warning("Image summarization failed: %s", e, exc_info=True)
            return image_caption, "failed", 0.0

        cost_usd = completion_cost(completion_response=response)
        self._log_caption_generation(response=response, cost_usd=cost_usd)

        choices = getattr(response, "choices", None)
        if choices and isinstance(choices, (list, tuple)) and len(choices) > 0:
            choice = choices[0]
            message = getattr(choice, "message", None)
            if message:
                msg_content = getattr(message, "content", None)
                if isinstance(msg_content, str):
                    image_caption = msg_content.strip()

        return image_caption, "success", cost_usd

    @staticmethod
    def _log_caption_generation(response=None, cost_usd=None) -> None:
        caption_generation_log = "Caption generation succeeded"

        if response is not None and cost_usd is not None:
            usage = getattr(response, "usage", None)
            prompt_tokens = getattr(usage, "prompt_tokens", None) if usage else None
            completion_tokens = (
                getattr(usage, "completion_tokens", None) if usage else None
            )
            total_tokens = getattr(usage, "total_tokens", None) if usage else None
            cost_usd_string = f"${cost_usd:.6f}"
            caption_generation_log += f" (cost_usd={cost_usd_string} prompt_tokens={prompt_tokens} completion_tokens={completion_tokens} total_tokens={total_tokens})"

        logger.debug(caption_generation_log)
