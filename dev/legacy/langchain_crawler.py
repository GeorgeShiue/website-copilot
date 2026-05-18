"""
網站遞迴爬蟲模組。

使用 LangChain 的 RecursiveUrlLoader 從首頁進入，
遞迴爬取整個網站的每個網頁，並可選擇將 HTML 萃取為純文字。
"""

import re
from typing import Iterator

from bs4 import BeautifulSoup
from langchain_community.document_loaders import RecursiveUrlLoader
from langchain_core.documents import Document


def _default_extractor(html: str) -> str:
    """使用 BeautifulSoup 將 HTML 萃取為適合閱讀的純文字。"""
    soup = BeautifulSoup(html, "lxml")
    # 移除 script、style 等標籤
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    # 合併多餘換行
    return re.sub(r"\n\n+", "\n\n", text).strip()


def crawl_website(
    url: str,
    *,
    max_depth: int | None = 3,
    use_async: bool = False,
    extract_text: bool = True,
    exclude_dirs: list[str] | None = None,
    prevent_outside: bool = True,
    base_url: str | None = None,
    timeout: int = 10,
    check_response_status: bool = True,
    continue_on_failure: bool = True,
    headers: dict | None = None,
) -> list[Document]:
    """
    從給定的首頁 URL 遞迴爬取整個網站。

    Args:
        url: 要爬取的網站首頁 URL。
        max_depth: 遞迴爬取的最大深度，None 表示不限制（慎用）。
        use_async: 是否使用非同步載入。
        extract_text: 是否用 BeautifulSoup 將 HTML 萃取為純文字；False 則保留原始 HTML。
        exclude_dirs: 要排除的 URL 路徑前綴列表（例如 ['https://example.com/logout']）。
        prevent_outside: 是否只爬取與 base_url 同網域內的連結。
        base_url: 用來判斷「站內」的基準 URL；未指定時以 url 的網域為準。
        timeout: 每個請求的超時秒數。
        check_response_status: 是否跳過 HTTP 4xx/5xx 的頁面。
        continue_on_failure: 單一頁面失敗時是否繼續爬取。
        headers: 自訂 HTTP 請求標頭。

    Returns:
        每個網頁對應的 Document 列表（page_content 與 metadata）。
    """
    extractor = _default_extractor if extract_text else None
    loader = RecursiveUrlLoader(
        url=url,
        max_depth=max_depth,
        use_async=use_async,
        extractor=extractor,
        exclude_dirs=exclude_dirs or (),
        prevent_outside=prevent_outside,
        base_url=base_url,
        timeout=timeout,
        check_response_status=check_response_status,
        continue_on_failure=continue_on_failure,
        headers=headers or {},
    )
    return loader.load()


def crawl_website_lazy(
    url: str,
    *,
    max_depth: int | None = 3,
    use_async: bool = False,
    extract_text: bool = True,
    exclude_dirs: list[str] | None = None,
    prevent_outside: bool = True,
    base_url: str | None = None,
    timeout: int = 10,
    check_response_status: bool = True,
    continue_on_failure: bool = True,
    headers: dict | None = None,
) -> Iterator[Document]:
    """
    以懶加載方式遞迴爬取網站，適合大型網站以節省記憶體。

    參數與 crawl_website 相同；回傳為逐頁 yield 的 Document 迭代器。
    """
    extractor = _default_extractor if extract_text else None
    loader = RecursiveUrlLoader(
        url=url,
        max_depth=max_depth,
        use_async=use_async,
        extractor=extractor,
        exclude_dirs=exclude_dirs or (),
        prevent_outside=prevent_outside,
        base_url=base_url,
        timeout=timeout,
        check_response_status=check_response_status,
        continue_on_failure=continue_on_failure,
        headers=headers or {},
    )
    yield from loader.lazy_load()


if __name__ == "__main__":
    # 範例：從首頁遞迴爬取整個網站（可改成你要的 URL）
    url = "https://sites.google.com/site/nculab/labintro?authuser=0"
    docs = crawl_website(url, max_depth=2, extract_text=True)
    print(f"共爬取 {len(docs)} 個網頁")
    for doc in docs[:5]:
        source = doc.metadata.get("source", "?")
        preview = (doc.page_content or "")[:300].replace("\n", " ")
        print(f"  - {source}\n    {preview}...")
