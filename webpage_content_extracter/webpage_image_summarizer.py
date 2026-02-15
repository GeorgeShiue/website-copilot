import base64
import logging
import os
import random
import re
import threading
import time
import urllib.request

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from dotenv import load_dotenv
from litellm import completion
from typing import Any


os.environ.setdefault("LITELLM_LOG", "ERROR")
load_dotenv()


@dataclass(frozen=True)
class _ImageSummarizeParameters:
    """VLM 圖片摘要用參數，供內部方法共用"""

    model: str
    prompt: str | None
    api_key: str | None
    caption_heading: str | None
    vlm_max_workers: int | None
    litellm_kwargs: dict[str, Any]


class WebpageImageSummarizerConstants:
    """VLM 圖片摘要用常數：圖片 URL 正則、預設提示詞、支援的模型對照。"""

    VLM_MODELS: dict[str, tuple[str, str]] = {
        "openai": ("gpt-4.1-mini", "OPENAI_WEBPAGE_SUMMARIZER_VLM_API_KEY"),
        "gemini": ("gemini-2.5-flash", "GEMINI_WEBPAGE_SUMMARIZER_VLM_API_KEY"),
    }
    DEFAULT_VLM_MODEL: str = "openai"
    DEFAULT_VLM_MAX_WORKERS: int = 10

    IMAGE_URL_PATTERN = re.compile(
        r"!\[[^\]]*\]\s*\(\s*(https?://[^)\s]+)\s*\)",
        re.IGNORECASE,
    )
    IMAGE_CAPTION_PROMPT = (
        "請描述這張圖片中的文字與版面內容。"
        "以結構化、易讀的純文字輸出，方便作為網頁內容的補充說明。"
    )
    CAPTION_HEADING = "**圖片說明：**"

    # 成功率低於此比例時觸發指數退避重試（視為可能被擋）
    MIN_SUCCESS_RATE_THRESHOLD: float = 0.8
    # 至少嘗試下載次數達此值才判斷是否需重試（避免少數失敗就重試）
    MIN_DOWNLOAD_ATTEMPTS_TO_CONSIDER_RETRY: int = 10
    # 指數退避秒數：第 1 次 30s、第 2 次 60s、第 3 次 2min，之後 5～10min，上限 15min
    BACKOFF_SECONDS: tuple[float, ...] = (30, 60, 120, 300, 600)
    BACKOFF_CAP_SECONDS: float = 900.0  # 15 分鐘
    BACKOFF_JITTER_FRACTION: float = 0.2  # ±20% 隨機
    MAX_RETRIES: int = 6  # 對應 BACKOFF_SECONDS 長度 + 最後一次用 cap


class WebpageImageSummarizer:
    """可初始化的網頁 Markdown 圖片摘要器，統計資訊封裝於實例內。"""

    def __init__(self) -> None:
        self.Constants = WebpageImageSummarizerConstants
        self._lock = threading.Lock()
        self.retry_count = 0
        self.download_stats: dict[str, int] = {
            "success": 0,
            "failure": 0,
            "cache_reuse": 0,
        }

    def _backoff_seconds(self, retry_index: int) -> float:
        """依重試次數回傳等待秒數（含 jitter），不超過 BACKOFF_CAP_SECONDS。"""
        bases = self.Constants.BACKOFF_SECONDS
        base = bases[min(retry_index, len(bases) - 1)] if bases else 30
        jitter = 1.0 + random.uniform(
            -self.Constants.BACKOFF_JITTER_FRACTION,
            self.Constants.BACKOFF_JITTER_FRACTION,
        )
        return min(base * jitter, self.Constants.BACKOFF_CAP_SECONDS)

    def _success_rate_for_retry(self) -> float | None:
        """若下載嘗試數足夠則回傳成功率（success/(success+failure)），否則回傳 None。"""
        s, f = self.download_stats["success"], self.download_stats["failure"]
        total = s + f
        if total < self.Constants.MIN_DOWNLOAD_ATTEMPTS_TO_CONSIDER_RETRY:
            return None
        return s / total

    # ----- 圖片下載 -----
    def _download_image_as_base64_data_url(
        self,
        url: str,
        timeout: float = 15.0,
        referer: str | None = None,
    ) -> str | None:
        """從 URL 下載圖片並轉成 data URL，供 VLM 使用。若下載失敗回傳 None。"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        if referer:
            headers["Referer"] = referer
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
                content_type = (
                    resp.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
                )
                if not content_type.startswith("image/"):
                    content_type = "image/jpeg"
                b64 = base64.standard_b64encode(data).decode("ascii")
                with self._lock:
                    self.download_stats["success"] += 1
                log.info("圖片下載成功 (url=%s)", url)
                return f"data:{content_type};base64,{b64}"
        except Exception as e:
            with self._lock:
                self.download_stats["failure"] += 1
            log.warning("圖片下載失敗 (url=%s): %s", url, e)
            return None

    # ----- 圖片 URL 提取 -----
    def _find_image_matches(self, markdown: str) -> list[tuple[int, int, str]]:
        """回傳 (start, end, url) 列表，供後續插入補充文本。"""
        out: list[tuple[int, int, str]] = []
        for m in self.Constants.IMAGE_URL_PATTERN.finditer(markdown):
            out.append((m.start(), m.end(), m.group(1)))
        return out

    # ----- VLM 呼叫（LiteLLM） -----
    def _get_image_caption(
        self, image_url: str, params: _ImageSummarizeParameters
    ) -> str:
        """呼叫支援視覺的模型取得圖片描述，失敗時回傳空字串。"""
        try:
            provider_config = self.Constants.VLM_MODELS.get(
                params.model
            ) or self.Constants.VLM_MODELS.get(self.Constants.DEFAULT_VLM_MODEL)
            model_name, api_key_name = provider_config
            effective_api_key = (
                params.api_key
                if params.api_key is not None
                else os.getenv(api_key_name)
            )
        except Exception as e:
            logging.getLogger(__name__).warning("VLM 模型配置錯誤: %s", e)
            return ""

        prompt = params.prompt or self.Constants.IMAGE_CAPTION_PROMPT
        image_input_url = self._download_image_as_base64_data_url(image_url)
        if not image_input_url:
            return ""

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_input_url},
                    },
                ],
            }
        ]

        try:
            options: dict[str, Any] = {}
            if effective_api_key:
                options["api_key"] = effective_api_key
            options.update(params.litellm_kwargs)
            response = completion(model=model_name, messages=messages, **options)
            content = response.choices[0].message.content
            return (content or "").strip()
        except Exception as e:
            logging.getLogger(__name__).warning("圖片描述 API 呼叫失敗: %s", e)
            return ""

    def _get_captions_for_urls(
        self,
        urls: list[str],
        caption_cache: dict[str, str],
        params: _ImageSummarizeParameters,
    ) -> dict[str, str]:
        """對一組 URL 並行取得說明（ThreadPoolExecutor）；已存在 caption_cache 的 URL 直接重用。"""
        url_to_caption: dict[str, str] = {}
        with self._lock:
            uncached = [u for u in urls if u not in caption_cache]
            for u in urls:
                if u in caption_cache:
                    self.download_stats["cache_reuse"] += 1
                    url_to_caption[u] = caption_cache[u]
        if not uncached:
            return url_to_caption

        max_workers = (
            params.vlm_max_workers
            if params.vlm_max_workers is not None
            else self.Constants.DEFAULT_VLM_MAX_WORKERS
        )

        def fetch_caption(url: str) -> tuple[str, str]:
            return (url, self._get_image_caption(url, params))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(fetch_caption, url) for url in uncached]
            for future in as_completed(futures):
                url, caption = future.result()
                with self._lock:
                    caption_cache[url] = caption
                    url_to_caption[url] = caption
        return url_to_caption

    # ----- 單頁 Markdown 圖片摘要 -----
    def _summarize_markdown_with_captions(
        self,
        content: str,
        caption_cache: dict[str, str],
        matches: list[tuple[int, int, str]],
        params: _ImageSummarizeParameters,
    ) -> str:
        """對單一 Markdown 字串：並行呼叫 VLM、在每張圖後插入補充文本；共用 caption_cache 避免跨頁重複。"""
        unique_urls = list(dict.fromkeys(m[2] for m in matches))
        url_to_caption = self._get_captions_for_urls(
            unique_urls, caption_cache=caption_cache, params=params
        )
        heading = params.caption_heading or self.Constants.CAPTION_HEADING

        parts: list[str] = []
        last_end = 0
        for start, end, url in matches:
            parts.append(content[last_end:start])
            parts.append(content[start:end])
            caption = url_to_caption.get(url, "")
            if caption:
                parts.append(
                    f"\n\n> {heading}\n>\n> {caption.replace(chr(10), chr(10) + '> ')}"
                )
            last_end = end
        parts.append(content[last_end:])
        return "".join(parts)

    def _one_pass_summarize(
        self,
        markdown_contents: list[str],
        skip_pages_without_images: bool,
        caption_cache: dict[str, str],
        params: _ImageSummarizeParameters,
    ) -> list[str]:
        """執行一輪多頁 Markdown 圖片摘要，回傳摘要後的列表。"""
        result: list[str] = []
        for content in markdown_contents:
            matches = self._find_image_matches(content)
            if skip_pages_without_images and not matches:
                result.append(content)
                continue
            summarized = self._summarize_markdown_with_captions(
                content, caption_cache=caption_cache, matches=matches, params=params
            )
            result.append(summarized)
        return result

    # ----- 對外 API -----
    def summarize_webpage_markdown_images(
        self,
        markdown_contents: list[str],
        *,
        model: str | None = None,
        prompt: str | None = None,
        api_key: str | None = None,
        caption_heading: str | None = None,
        skip_pages_without_images: bool = True,
        caption_cache: dict[str, str] | None = None,
        vlm_max_workers: int | None = None,
        **litellm_kwargs: Any,
    ) -> tuple[list[str], int, dict[str, int]]:
        """
        對多頁 Markdown 做 VLM 圖片摘要，回傳 (摘要後的列表, 重試次數, 下載統計)。
        若一輪後圖片下載成功率 < 80% 且嘗試數足夠，視為可能被擋，依指數退避自動重試（僅重試失敗的 URL）。
        - model: 模型商名稱（WebpageImageSummarizerConstants.VLM_MODELS 的 key），
          傳入後會自動對應模型型號與 .env 中的 API key；未傳則使用 Constants.DEFAULT_VLM_MODEL（'openai'）。
        - prompt: 送給 VLM 的提示詞，未設則用內建 IMAGE_CAPTION_PROMPT。
        - api_key: 若提供則覆寫該次呼叫的 API key，否則依模型商使用 VLM_MODELS 對應的環境變數。
        - skip_pages_without_images: 若為 True，沒有圖片的頁面直接原樣回傳，不呼叫 API。
        - caption_cache: 可選。若提供則會在此 dict 中累積 url -> 圖片說明，同一次呼叫內跨頁共用；下次呼叫可傳入同一 dict 以跨次重用。
        - vlm_max_workers: VLM 並行數上限，未設則用 Constants.DEFAULT_VLM_MAX_WORKERS，避免觸發 API rate limit。
        - **litellm_kwargs: 其他傳給 litellm.completion 的參數。
        """
        self.download_stats = {"success": 0, "failure": 0, "cache_reuse": 0}
        caption_cache = caption_cache if caption_cache is not None else {}
        params = _ImageSummarizeParameters(
            model=model,
            prompt=prompt,
            api_key=api_key,
            caption_heading=caption_heading,
            vlm_max_workers=vlm_max_workers,
            litellm_kwargs=litellm_kwargs,
        )
        log = logging.getLogger(__name__)
        result = self._one_pass_summarize(
            markdown_contents, caption_cache, params, skip_pages_without_images
        )
        self.retry_count = 0
        min_success_rate = self.Constants.MIN_SUCCESS_RATE_THRESHOLD
        max_retries = self.Constants.MAX_RETRIES
        while self.retry_count < max_retries:
            success_rate = self._success_rate_for_retry()
            if success_rate is None or success_rate >= min_success_rate:
                break
            to_remove = [url for url, cap in caption_cache.items() if cap == ""]
            for url in to_remove:
                del caption_cache[url]
            if not to_remove:
                break
            wait_sec = self._backoff_seconds(self.retry_count)
            log.warning(
                "圖片下載成功率 %.0f%% (< %.0f%%)，可能被擋；%s 個 URL 將於 %.1f 秒後重試（第 %s 次）",
                success_rate * 100,
                min_success_rate * 100,
                len(to_remove),
                wait_sec,
                self.retry_count + 1,
            )
            log.info("-" * 100)
            time.sleep(wait_sec)
            self.download_stats = {"success": 0, "failure": 0, "cache_reuse": 0}
            result = self._one_pass_summarize(
                markdown_contents, caption_cache, params, skip_pages_without_images
            )
            self.retry_count += 1
        return result, self.retry_count, self.download_stats


if __name__ == "__main__":
    import logging
    import time

    from website_crawler.crawl4ai_crawler import WebsiteCrawler
    from webpage_content_extracter.webpage_cleaner import WebpageCleaner
    from webpage_content_extracter.md_file_manager import MdFileManager

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    log = logging.getLogger(__name__)
    t0 = time.perf_counter()

    start_url = "https://sites.google.com/site/nculab/labintro"
    webpage_markdowns = WebsiteCrawler.crawl_website(
        url=start_url,
        max_depth=3,
        include_external=False,
        url_prefix="https://sites.google.com/site/nculab",
        concurrent_requests=15,
        text_mode=False,
        light_mode=True,
        verbose=True,
    )
    t1 = time.perf_counter()
    log.info("爬取 %s 個網頁, 耗時 %.3f 秒", len(webpage_markdowns), t1 - t0)
    log.info("-" * 100)

    cleaned_webpage_markdowns = WebpageCleaner.clean_webpage_markdown(
        webpage_markdowns, include_frontmatter=True
    )
    t2 = time.perf_counter()
    log.info(
        "清理後剩餘 %s 個網頁, 耗時 %.3f 秒",
        len(cleaned_webpage_markdowns),
        t2 - t1,
    )
    log.info("-" * 100)

    # cleaned_webpage_markdowns = MdFileManager.load_md_files(
    #     directory="data/webpage_markdown",
    #     limit=10,
    # )
    # log.info("已讀取 %s 個網頁", len(cleaned_webpage_markdowns))

    image_summarizer = WebpageImageSummarizer()
    markdown_contents_with_image_summary, retry_count, download_stats = (
        image_summarizer.summarize_webpage_markdown_images(
            cleaned_webpage_markdowns,
            model="openai",
            skip_pages_without_images=True,
        )
    )
    t3 = time.perf_counter()
    log.info(
        "加註 %s 個網頁的圖片, 重試 %s 次, 耗時 %.3f 秒",
        len(markdown_contents_with_image_summary),
        retry_count,
        t3 - t2,
    )
    log.info(
        "- 圖片下載資訊: 成功 %s 次, 失敗 %s 次, 跨頁重用快取 %s 次",
        download_stats["success"],
        download_stats["failure"],
        download_stats["cache_reuse"],
    )
    log.info("-" * 100)

    md_file_paths = MdFileManager.save_md_files(
        directory="./data/webpage_markdown_with_image_summary",
        markdown_contents=markdown_contents_with_image_summary,
    )
    t4 = time.perf_counter()
    log.info("已存成 %s 個 .md 檔, 耗時 %.3f 秒", len(md_file_paths), t4 - t3)
    log.info("-" * 100)

    log.info("總耗時 %.3f 秒", t4 - t0)
