"""文字清洗工具。"""

import html
import re

# description 會被放進每個 chunk 的 metadata，必須遠小於 chunk_size
# （SentenceSplitter 要求 metadata 長度小於 chunk_size）。
MAX_DESCRIPTION_CHARS = 300

# Markdown 內的圖片連結（只取 http(s) 網址），爬蟲萃取 images 與圖片摘要共用
MARKDOWN_IMAGE_PATTERN = re.compile(r"!\[.*?\]\((https?://[^\s)]+)\)")

_HTML_TAG_RE = re.compile(r"<[^>]*>")
_WHITESPACE_RE = re.compile(r"\s+")


def clean_description(description: str | None) -> str:
    """把 meta description 清成純文字摘要。

    部分網站的 description／og:description 會塞進整段 HTML（例如嵌入的社群貼文），
    這裡移除 HTML 標籤、解碼 HTML entity、壓縮空白，並截斷到 MAX_DESCRIPTION_CHARS。
    """
    if not description:
        return ""
    text = html.unescape(_HTML_TAG_RE.sub(" ", description))
    text = _WHITESPACE_RE.sub(" ", text).strip()
    if len(text) > MAX_DESCRIPTION_CHARS:
        text = text[:MAX_DESCRIPTION_CHARS].rstrip() + "…"
    return text
