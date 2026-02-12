import base64
import logging
import os
import re
import urllib.request
from typing import Any

# 在 import litellm 前關閉冗餘日誌，避免重複輸出 "Give Feedback / Get Help" 等
os.environ.setdefault("LITELLM_LOG", "ERROR")

from dotenv import load_dotenv
from litellm import completion

load_dotenv()

# 圖片下載統計：enrich_webpage_markdown 每次開始時重置，供 _fetch_image_as_base64_data_url 累加
_download_stats: dict[str, int] = {"success": 0, "failure": 0}
# 同一次 enrich 內跨頁重用同一圖片說明的次數（用 list 以便在函式內累加不需 global）
_cache_reuse_count: list[int] = [0]


class WebpageSummarizerConstants:
    """VLM 圖片增強用常數：圖片 URL 正則、預設提示詞、支援的模型對照。"""

    # 匹配 ![alt](url) 或 [![alt](url)](...) 中的圖片 URL
    IMAGE_URL_PATTERN = re.compile(
        r"!\[[^\]]*\]\s*\(\s*(https?://[^)\s]+)\s*\)",
        re.IGNORECASE,
    )

    IMAGE_CAPTION_PROMPT = (
        "請描述這張圖片中的文字與版面內容。"
        "以結構化、易讀的純文字輸出，方便作為網頁內容的補充說明。"
    )

    CAPTION_HEADING = "**圖片說明：**"

    # 模型商名稱 -> (LiteLLM model 字串, .env 中 API key 的環境變數名)
    VLM_PROVIDERS: dict[str, tuple[str, str]] = {
        "openai": ("gpt-4.1-mini", "OPENAI_WEBPAGE_SUMMARIZER_VLM_API_KEY"),
        "gemini": ("gemini-2.5-flash", "GEMINI_WEBPAGE_SUMMARIZER_VLM_API_KEY"),
    }


def _fetch_image_as_base64_data_url(
    url: str, timeout: float = 15.0, referer: str | None = None
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
            _download_stats["success"] += 1
            logging.getLogger(__name__).info("圖片下載成功 (url=%s)", url)
            return f"data:{content_type};base64,{b64}"
    except Exception as e:
        _download_stats["failure"] += 1
        logging.getLogger(__name__).warning("圖片下載失敗 (url=%s): %s", url, e)
        return None


class WebpageSummarizer:
    Constants = WebpageSummarizerConstants

    # ----- 圖片 URL 提取 -----
    @classmethod
    def _extract_image_urls(cls, markdown: str) -> list[str]:
        """從 Markdown 提取所有圖片 URL，保持出現順序並去重。"""
        urls = cls.Constants.IMAGE_URL_PATTERN.findall(markdown)
        return list(dict.fromkeys(urls))

    @classmethod
    def _find_image_matches(cls, markdown: str) -> list[tuple[int, int, str]]:
        """回傳 (start, end, url) 列表，供後續插入補充文本。"""
        out: list[tuple[int, int, str]] = []
        for m in cls.Constants.IMAGE_URL_PATTERN.finditer(markdown):
            out.append((m.start(), m.end(), m.group(1)))
        return out

    # ----- VLM 呼叫（LiteLLM） -----
    @classmethod
    def _get_image_caption(
        cls,
        image_url: str,
        model: str,
        prompt: str | None = None,
        api_key: str | None = None,
        **kwargs: Any,
    ) -> str:
        """呼叫支援視覺的模型取得圖片描述，失敗時回傳空字串。"""
        prompt = prompt or cls.Constants.IMAGE_CAPTION_PROMPT
        # 模型商名稱 -> 解析出 (model 字串, api_key)
        provider_config = cls.Constants.VLM_PROVIDERS.get(model)
        if provider_config is not None:
            model_name, api_key_name = provider_config
            effective_api_key = (
                api_key if api_key is not None else os.getenv(api_key_name)
            )
        else:
            model_name = model
            effective_api_key = api_key
        # 先由本地下載圖片並轉成 base64；若失敗（如 403）則不呼叫 API，直接跳過
        image_input_url = _fetch_image_as_base64_data_url(image_url)
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
            options.update(kwargs)
            response = completion(model=model_name, messages=messages, **options)
            content = response.choices[0].message.content
            return (content or "").strip()
        except Exception as e:
            logging.getLogger(__name__).warning("圖片描述 API 呼叫失敗: %s", e)
            return ""

    @classmethod
    def _get_captions_for_urls(
        cls,
        urls: list[str],
        model: str,
        caption_cache: dict[str, str],
        prompt: str | None = None,
        api_key: str | None = None,
        **kwargs: Any,
    ) -> dict[str, str]:
        """對一組 URL 逐一取得說明；已存在 caption_cache 的 URL 直接重用，不重複下載與呼叫 VLM。"""
        url_to_caption: dict[str, str] = {}
        for url in urls:
            if url in caption_cache:
                _cache_reuse_count[0] += 1
                url_to_caption[url] = caption_cache[url]
                continue
            caption = cls._get_image_caption(
                image_url=url,
                model=model,
                prompt=prompt,
                api_key=api_key,
                **kwargs,
            )
            caption_cache[url] = caption
            url_to_caption[url] = caption
        return url_to_caption

    # ----- 單頁 Markdown 增強 -----
    @classmethod
    def _enrich_markdown_with_captions(
        cls,
        content: str,
        model: str,
        caption_cache: dict[str, str],
        prompt: str | None = None,
        api_key: str | None = None,
        caption_heading: str | None = None,
        **kwargs: Any,
    ) -> str:
        """對單一 Markdown 字串：提取圖片 URL、呼叫 VLM、在每張圖後插入補充文本；共用 caption_cache 避免跨頁重複下載與重複呼叫。"""
        matches = cls._find_image_matches(content)
        if not matches:
            return content

        unique_urls = list(dict.fromkeys(m[2] for m in matches))
        url_to_caption = cls._get_captions_for_urls(
            unique_urls,
            model=model,
            caption_cache=caption_cache,
            prompt=prompt,
            api_key=api_key,
            **kwargs,
        )
        heading = caption_heading or cls.Constants.CAPTION_HEADING

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

    # ----- 對外 API -----
    @classmethod
    def enrich_webpage_markdown(
        cls,
        markdown_contents: list[str],
        *,
        model: str | None = None,
        prompt: str | None = None,
        api_key: str | None = None,
        caption_heading: str | None = None,
        skip_pages_without_images: bool = True,
        caption_cache: dict[str, str] | None = None,
        **litellm_kwargs: Any,
    ) -> list[str]:
        """對多頁 Markdown 做 VLM 圖片資訊增強，回傳補充文本後的列表。

        - model: 模型商名稱（WebpageSummarizerConstants.VLM_PROVIDERS 的 key），
          傳入後會自動對應模型型號與 .env 中的 API key；預設由環境變數 VLM_PROVIDER 決定，未設則用 'openai'。
        - prompt: 送給 VLM 的提示詞，未設則用內建 IMAGE_CAPTION_PROMPT。
        - api_key: 若提供則覆寫該次呼叫的 API key，否則依模型商使用 VLM_PROVIDERS 對應的環境變數。
        - skip_pages_without_images: 若為 True，沒有圖片的頁面直接原樣回傳，不呼叫 API。
        - caption_cache: 可選。若提供則會在此 dict 中累積 url -> 圖片說明，同一次呼叫內跨頁共用；下次呼叫可傳入同一 dict 以跨次重用。
        - **litellm_kwargs: 其他傳給 litellm.completion 的參數。
        """
        model = model or "openai"
        _download_stats["success"] = 0
        _download_stats["failure"] = 0
        _cache_reuse_count[0] = 0
        caption_cache = caption_cache if caption_cache is not None else {}
        enriched_markdown_contents: list[str] = []
        for content in markdown_contents:
            if skip_pages_without_images and not cls._extract_image_urls(content):
                enriched_markdown_contents.append(content)
                continue
            enriched_markdown_content = cls._enrich_markdown_with_captions(
                content,
                model=model,
                caption_cache=caption_cache,
                prompt=prompt,
                api_key=api_key,
                caption_heading=caption_heading,
                **litellm_kwargs,
            )
            enriched_markdown_contents.append(enriched_markdown_content)
        logging.getLogger(__name__).info(
            "圖片下載統計資訊: 成功 %s 次, 失敗 %s 次, 跨頁重用快取 %s 次",
            _download_stats["success"],
            _download_stats["failure"],
            _cache_reuse_count[0],
        )
        return enriched_markdown_contents


if __name__ == "__main__":
    import logging
    import time

    from website_crawler.crawl4ai_crawler import WebsiteCrawler
    from webpage_content_extracter.md_file_manager import MdFileManager

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    log = logging.getLogger(__name__)

    # t0 = time.perf_counter()
    # start_url = "https://sites.google.com/site/nculab/labintro"
    # webpage_markdowns = WebsiteCrawler.crawl_website(
    #     url=start_url,
    #     max_depth=3,
    #     include_external=False,
    #     # max_pages=100, # test
    #     url_prefix="https://sites.google.com/site/nculab",
    #     concurrent_requests=15,
    #     text_mode=False,
    #     light_mode=True,
    #     verbose=True,
    # )

    # t1 = time.perf_counter()
    # log.info("爬取 %s 個網頁, 耗時 %.3f 秒", len(webpage_markdowns), t1 - t0)

    # cleaned_webpage_markdowns = WebpageCleaner.clean_webpage_markdown(
    #     webpage_markdowns, include_frontmatter=True
    # )
    t2 = time.perf_counter()
    # log.info(
    #     "清理後剩餘 %s 個網頁, 耗時 %.3f 秒",
    #     len(cleaned_webpage_markdowns),
    #     t2 - t1,
    # )
    # for cleaned_webpage_markdown in cleaned_webpage_markdowns:
    #     print(cleaned_webpage_markdown)

    cleaned_webpage_markdowns = MdFileManager.load_md_files(
        directory="data/webpage_markdown",
        limit=10, # test first 10 webpages
    )
    # for cleaned_webpage_markdown in cleaned_webpage_markdowns:
    #     print(cleaned_webpage_markdown)
    log.info("已讀取 %s 個網頁", len(cleaned_webpage_markdowns))

    enriched_markdown_contents = WebpageSummarizer.enrich_webpage_markdown(
        cleaned_webpage_markdowns,
        model="openai",
        skip_pages_without_images=True,
    )

    # for enriched_webpage_markdown in enriched:
    #     print(enriched_webpage_markdown)
    #     print("-" * 100)

    t3 = time.perf_counter()
    log.info(
        "加註 %s 個網頁的圖片, 耗時 %.3f 秒", len(enriched_markdown_contents), t3 - t2
    )

    md_file_paths = MdFileManager.save_md_files(
        directory="./data/enriched_webpage_markdown",
        markdown_contents=enriched_markdown_contents,
    )
    t4 = time.perf_counter()
    log.info("已存成 %s 個 .md 檔, 耗時 %.3f 秒", len(md_file_paths), t4 - t3)
