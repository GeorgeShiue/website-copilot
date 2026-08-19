# 開發實作紀錄 (2026/08/18–08/26)

> 本文檔彙整 `docs/work/2026_0826/` 中所有規劃文件的**實作規格、程式碼設計、資料流變更、測試策略**。
> 各規劃文件保留動機、目標、風險、決策等規劃面內容，實作細節集中於此。

---

## 1. HTML 日期擷取（來源：`2026_0818-html_date_extraction.md`）

### 1-1. `website_crawler.py` — 新增 `_extract_date_from_html()`

從 `CrawlResult.html` 解析結構化日期標籤，回傳 `{"published_date": "...", "modified_date": "..."}`。

**解析優先級（由高到低）**：

| 優先級 | 來源 | 選擇器 / 正則 | 輸出格式 |
|--------|------|--------------|---------|
| 1 | JSON-LD `datePublished` | `soup.select('script[type="application/ld+json"]')` → parsed JSON 中的 `datePublished` | ISO 8601 |
| 2 | OG `article:published_time` | `soup.select('meta[property="article:published_time"]')` | ISO 8601 |
| 3 | `<time datetime>` (itemprop) | `soup.select('time[itemprop="datePublished"]')` 或 `time[datetime]` | ISO 8601 |
| 4 | Generic meta `date` / `pubdate` | `soup.select('meta[name*="date"], meta[name*="pubdate"]')` | 標準化為 ISO 8601 |
| 5 | Dublin Core `dc.date` | `soup.select('meta[name="dc.date"], meta[name="DC.date"]')` | ISO 8601 |
| 6 | HTTP `Last-Modified` | `response_headers.get("Last-Modified")` | ISO 8601 |

**主函數**：

```python
from bs4 import BeautifulSoup
from datetime import datetime

def _extract_date_from_html(
    html: str,
    response_headers: dict[str, str] | None = None,
) -> dict[str, str | None]:
    """從 HTML 原始碼 + HTTP 標頭擷取發佈/修改日期。

    回傳 ISO 8601 格式（YYYY-MM-DDTHH:MM:SS±HH:MM 或 YYYY-MM-DD）。
    無法擷取時對應值為 None。
    """
    published_date: str | None = None
    modified_date: str | None = None

    soup = BeautifulSoup(html, "html.parser")

    # --- Priority 1: JSON-LD datePublished / dateModified ---
    if published_date is None:
        published_date, modified_date = _extract_from_jsonld(soup)

    # --- Priority 2: <meta property="article:published_time"> ---
    if published_date is None:
        published_date = _extract_meta_property(soup, "article:published_time")

    # --- Priority 3: <time datetime> elements ---
    if published_date is None:
        published_date = _extract_time_element(soup)

    # --- Priority 4: Generic meta date tags ---
    if published_date is None:
        published_date = _extract_meta_name(soup, ("date", "pubdate", "publish_date"))

    # --- Priority 5: Dublin Core dc.date ---
    if published_date is None:
        published_date = _extract_meta_name(soup, ("dc.date", "dc.date.created"))

    # --- Priority 6: HTTP Last-Modified ---
    if published_date is None and response_headers:
        published_date = _parse_http_date(response_headers.get("Last-Modified"))

    # modified_date 從 JSON-LD 或 article:modified_time 補充
    if modified_date is None:
        modified_date = _extract_meta_property(soup, "article:modified_time")

    return {
        "published_date": _normalize_to_iso8601(published_date),
        "modified_date": _normalize_to_iso8601(modified_date),
    }
```

**輔助函數**：

```python
def _extract_from_jsonld(soup: BeautifulSoup) -> tuple[str | None, str | None]:
    """從 JSON-LD 擷取 datePublished / dateModified。"""
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            data = json.loads(script.string or "")
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict):
                    pub = item.get("datePublished") or item.get("dateCreated")
                    mod = item.get("dateModified")
                    if pub or mod:
                        return pub, mod
        except (json.JSONDecodeError, TypeError):
            continue
    return None, None

def _extract_meta_property(soup: BeautifulSoup, prop: str) -> str | None:
    tag = soup.select_one(f'meta[property="{prop}"]')
    return tag.get("content") if tag else None

def _extract_time_element(soup: BeautifulSoup) -> str | None:
    """從 <time> 元素擷取 datetime 屬性。"""
    for selector in (
        'time[itemprop="datePublished"]',
        'time[datetime]',
    ):
        tag = soup.select_one(selector)
        if tag and tag.get("datetime"):
            return tag["datetime"]
    return None

def _extract_meta_name(soup: BeautifulSoup, names: tuple[str, ...]) -> str | None:
    for name in names:
        tag = soup.select_one(f'meta[name="{name}" i]')
        if tag and tag.get("content"):
            return tag["content"]
    return None

def _parse_http_date(date_str: str | None) -> str | None:
    """解析 HTTP 日期格式（RFC 7231）。"""
    if not date_str:
        return None
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_str).isoformat()
    except (ValueError, TypeError):
        return None

def _normalize_to_iso8601(date_str: str | None) -> str | None:
    """嘗試將各種日期格式標準化為 ISO 8601。"""
    if not date_str:
        return None
    # 已經是 ISO 格式
    if re.match(r"\d{4}-\d{2}-\d{2}", date_str):
        return date_str[:10]  # 取 YYYY-MM-DD
    # 嘗試 dateutil / 手動解析
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None
```

### 1-2. `_extract_metadata()` 簽名變更

```python
# 現狀
@staticmethod
def _extract_metadata(url: str, raw_metadata: dict) -> dict:

# 改為
@staticmethod
def _extract_metadata(
    url: str,
    raw_metadata: dict,
    html: str | None = None,
    response_headers: dict[str, str] | None = None,
) -> dict:
```

新增邏輯（在現有 `description` + `page_type` 之後）：

```python
# --- HTML 日期擷取 ---
if html:
    date_info = _extract_date_from_html(html, response_headers)
    if date_info["published_date"]:
        metadata["published_date"] = date_info["published_date"]
    if date_info["modified_date"]:
        metadata["modified_date"] = date_info["modified_date"]
```

### 1-3. `_extract_crawl_results_data()` 呼叫端變更

```python
# 現狀
metadata: self._extract_metadata(url, raw_metadata),

# 改為
metadata: self._extract_metadata(
    url,
    raw_metadata,
    html=getattr(crawl_result, "html", None),
    response_headers=getattr(crawl_result, "response_headers", None),
),
```

### 1-4. `rag_factory.py` — `_build_file_metadata()` 變更

```python
# 現狀
return {
    "page_title": page_title,
    "page_url": page_info.get("url", ""),
    "page_type": page_metadata.get("page_type", "general"),
    "description": page_metadata.get("description", ""),
}

# 改為
file_metadata: dict[str, Any] = {
    "page_title": page_title,
    "page_url": page_info.get("url", ""),
    "page_type": page_metadata.get("page_type", "general"),
    "description": page_metadata.get("description", ""),
}

# 傳遞 HTML 擷取的日期，供下游 MarkdownDateExtractor 優先使用
if published_date := page_metadata.get("published_date"):
    file_metadata["published_date"] = published_date

return file_metadata
```

### 1-5. `rag_helper.py` — `_extract_date()` 優先級變更

```python
def _extract_date(self, node: BaseNode) -> Dict[str, Any]:
    # --- Strategy 0: HTML metadata 優先 ---
    published_date = node.metadata.get("published_date")
    if published_date:
        parts = published_date.split("-")
        result: dict[str, int] = {"year": int(parts[0])}
        if len(parts) >= 2:
            result["month"] = int(parts[1])
        if len(parts) >= 3:
            result["day"] = int(parts[2])
        return result

    # --- Strategy 1–4: 原有內容推斷（不變） ---
    content = node.get_content()
    # ... 原有四層策略 ...
```

### 1-6. 資料流變更

```
[改動前]
HTML → crawl4ai → CrawlResult.html (未使用)
                 → CrawlResult.metadata (僅 title/description)
                 → _extract_metadata() → results.json (無日期)
                 → MarkdownDateExtractor (從 Markdown 文字推斷)

[改動後]
HTML → crawl4ai → CrawlResult.html ──→ _extract_date_from_html()
                                      → results.json (published_date)
                                      → _build_file_metadata() → node metadata
                                      → MarkdownDateExtractor (優先使用 published_date)
                                                          ↓ (無 HTML date 時)
                                              原有四層策略（fallback）
```

### 1-7. results.json 變更前後對比

```json
// [改動前]
"metadata": {
    "description": "【Research Interests】",
    "page_type": "general"
}

// [改動後]
"metadata": {
    "description": "【Research Interests】",
    "page_type": "general",
    "published_date": "2024-10-17",
    "modified_date": "2024-10-20"
}
```

### 1-8. 測試策略

| 測試類型 | 對象 | 驗證內容 |
|---------|------|---------|
| **單元測試** | `_extract_date_from_html()` | 各種 HTML 結構的日期擷取正確性 |
| **單元測試** | `_normalize_to_iso8601()` | 各種日期格式的標準化 |
| **單元測試** | `_extract_date()` (MarkdownDateExtractor) | 有/無 `published_date` 時的行為 |
| **整合測試** | `_extract_metadata()` | 傳入 HTML + headers 後 metadata 包含日期 |
| **端到端** | 完整爬蟲流程 | `results.json` 中有有效 `published_date` |

關鍵測試案例：

```python
# HTML 有 JSON-LD datePublished
html_jsonld = '''
<html><head>
<script type="application/ld+json">
{"@type":"Article","datePublished":"2024-01-15T10:00:00Z","dateModified":"2024-06-20"}
</script>
</head></html>'''

# HTML 有 article:published_time
html_og = '''
<html><head>
<meta property="article:published_time" content="2024-03-20T08:30:00+08:00">
</head></html>'''

# HTML 有 <time> 元素
html_time = '''
<html><body>
<time datetime="2024-05-10" itemprop="datePublished">May 10, 2024</time>
</body></html>'''

# HTML 無日期標籤，fallback 到 Last-Modified
html_empty = '<html><head></head><body></body></html>'
headers = {"Last-Modified": "Wed, 15 Jan 2025 12:00:00 GMT"}

# HTML 完全無日期
html_no_date = '<html><head></head><body>No dates here</body></html>'
```

### 1-9. 實作順序

```
Step 1: website_crawler.py — 新增 _extract_date_from_html() 及輔助函數
Step 2: website_crawler.py — 修改 _extract_metadata() 簽名與邏輯
Step 3: website_crawler.py — 修改 _extract_crawl_results_data() 呼叫端
Step 4: rag_factory.py    — 修改 _build_file_metadata() 傳遞 published_date
Step 5: rag_helper.py     — 修改 MarkdownDateExtractor._extract_date() 優先級
Step 6: 寫單元測試
Step 7: 重新爬取 nculab 驗證 results.json 有日期
```

> ⚠️ Step 7 前置依賴：重新爬取的結果需寫入多站目錄結構 `data/webpages/nculab/`（而非舊的平坦結構），須等 RunManager Refactor Phase 2 完成後執行。

---

## 2. 多站 RAG — 代碼設計（來源：`2026_0818-multi_site_RAG.md`）

### 2-1. RAGRegistry 設計

```python
class RAGRegistry:
    """依 site_id 管理多個 RAG 實例，避免重複建立向量庫。"""

    def __init__(self, config_names: dict[str, str]):
        """config_names: {"nculab": "rag_nculab", "nctu": "rag_nctu"}"""
        self._configs = config_names
        self._instances: dict[str, Rag] = {}

    def get(self, site_id: str) -> Rag:
        if site_id not in self._instances:
            config = RagConfig.from_toml(self._configs[site_id])
            self._instances[site_id] = RAGBuilder(config).build_reusable()
        return self._instances[site_id]

    def list_sites(self) -> list[str]:
        return list(self._configs.keys())

    def close(self):
        for rag in self._instances.values():
            rag.close()
```

### 2-2. Tool 簽名（擴充後）

```python
class WebpageRetrieverInput(BaseModel):
    query: str
    site_id: str  # 新增：目標網站（如 "nculab"、"nctu"）
    filter_dict: dict | None = None
    top_k: int = 10

webpage_retriever = StructuredTool.from_function(
    func=retrieve,
    name="webpage_retriever",
    description="從指定網站的知識庫檢索相關網頁內容",
    args_schema=WebpageRetrieverInput,
)
```

---

## 3. RunManager Refactor

### 3-1. RunManager 新增屬性與方法

```python
class RunManager:
    def __init__(self, module_name="", base_folder="runs"):
        # ... 現有屬性 ...
        self.site_id: str = ""
        self.site_path: str = ""

    def set_site_path(self, site_id: str) -> None:
        """設定 site 路徑（可選）。不呼叫時 run_path 直接掛在 module_path 下。"""
        if not self.module_name:
            raise ValueError("Module name must be set before setting site path.")
        self.site_id = site_id
        self.site_path = os.path.join(self.module_path, site_id)
        os.makedirs(self.site_path, exist_ok=True)
```

### 3-2. RunManager `set_run_path()` 變更

```python
def set_run_path(self, run_name: str) -> None:
    if not self.module_name:
        raise ValueError("Module name must be set before setting run path.")
    if not run_name:
        raise ValueError("Run name must be provided to set run path.")

    self.run_name = run_name
    base = self.site_path if self.site_path else self.module_path
    run_path = os.path.join(base, self.run_name)
    os.makedirs(run_path, exist_ok=True)
    self.run_path = run_path
```

### 3-3. RunManager `_filter_run_folders()` 變更

```python
def _filter_run_folders(self) -> list[str]:
    """篩選出符合實驗資料夾命名規則的資料夾名稱列表。"""
    folder_names = os.listdir(self.base_folder)  # 改用 self.base_folder（原本硬編碼 RUNS_FOLDER_PATH）
    run_folder_names = []
    for folder_name in folder_names:
        if folder_name.startswith("20") and len(folder_name) == 15:
            run_folder_names.append(folder_name)
    if not run_folder_names:
        raise FileNotFoundError(f"No run folders found in {self.base_folder}.")
    return run_folder_names
```

### 3-4. 路徑結構變化

```
# 現在（三層）
set_module_path("website_crawler")  → runs/<ts>/website_crawler/
set_run_path("default")             → runs/<ts>/website_crawler/default/

# 多站（四層，set_site_path 可選）
set_module_path("website_crawler")  → runs/<ts>/website_crawler/
set_site_path("nculab")             → runs/<ts>/website_crawler/nculab/
set_run_path("default")             → runs/<ts>/website_crawler/nculab/default/

# 單站（不呼叫 set_site_path，向後相容）
set_module_path("website_crawler")  → runs/<ts>/website_crawler/
set_run_path("default")             → runs/<ts>/website_crawler/default/
```

### 3-5. DataManager 介面設計

```python
class DataManager:
    """管理 data/ 目錄下的持久化發布結果。

    職責：
    - publish：將 runs/ 中的執行結果覆蓋發布至 data/
    - discover：掃描 data/ 目錄，提供 site 列表與路徑
    - 不負責 runs/ 的建立或發現（那是 RunManager 的職責）
    """

    def __init__(self, data_folder: str = "data") -> None:
        self.data_folder = data_folder

    # ──────── Publish（寫入 data/）──────

    def publish_crawl_results(self, site_id: str, results: dict) -> None:
        """將爬取結果覆蓋發布至 data/webpages/{site_id}/。"""
        site_path = self._webpages_site_path(site_id)
        os.makedirs(os.path.join(site_path, "results"), exist_ok=True)
        with open(os.path.join(site_path, "results.json"), "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

    def publish_markdown(self, site_id: str, results: dict, markdown_type: str) -> None:
        """將 Markdown 結果覆蓋發布至 data/webpages/{site_id}/results/。"""
        site_path = self._webpages_site_path(site_id)
        results_dir = os.path.join(site_path, "results")
        os.makedirs(results_dir, exist_ok=True)
        for page_title, result in results.items():
            md_file_path = os.path.join(results_dir, page_title + ".md")
            with open(md_file_path, "w", encoding="utf-8") as f:
                f.write(result[markdown_type])

    def publish_vector_store(self, site_id: str, source_db_path: str) -> None:
        """將向量庫從 runs/ 複製至 data/rag/{site_id}/。"""
        dest_dir = self.get_vector_store_path(site_id)
        os.makedirs(dest_dir, exist_ok=True)
        # 複製 milvus.db 或 qdrant_db/ 至 dest_dir

    # ──────── Discover（掃描 data/）──────

    def list_sites(self) -> list[str]:
        """掃描 data/webpages/ 目錄，回傳所有已發佈的 site_id。"""
        webpages_path = os.path.join(self.data_folder, "webpages")
        if not os.path.isdir(webpages_path):
            return []
        return sorted(
            d for d in os.listdir(webpages_path)
            if os.path.isdir(os.path.join(webpages_path, d))
        )

    def get_webpages_path(self, site_id: str) -> str:
        """回傳 data/webpages/{site_id}/ 路徑（供 RAG 讀取）。"""
        return self._webpages_site_path(site_id)

    def get_vector_store_path(self, site_id: str) -> str:
        """回傳 data/rag/{site_id}/ 路徑（供 RAGRegistry 讀取）。"""
        return os.path.join(self.data_folder, "rag", site_id)

    # ──────── 內部方法 ────────

    def _webpages_site_path(self, site_id: str) -> str:
        return os.path.join(self.data_folder, "webpages", site_id)
```

安放位置：`src/app/workflow/data_manager.py`，與 `workflow_manager.py` 同層。

### 3-6. Workflow 函式簽名變化

所有 `run_*` 函式加入 `site_id` 和 `data_manager` 參數（可選），`site_id` 為空時所有新邏輯跳過，向後相容：

```python
def run_website_crawler(
    run_manager: RunManager | None = None,
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    site_id: str = "",                            # 新增（可選）
    data_manager: DataManager | None = None,       # 新增（可選）
    **config_overrides,
) -> dict[str, dict] | None:
```

### 3-7. `run_website_crawler` 完整改動

```python
def run_website_crawler(
    run_manager: RunManager | None = None,
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    site_id: str = "",
    data_manager: DataManager | None = None,
    **config_overrides,
) -> dict[str, dict] | None:
    # ----- 初始化設定和路徑 -----
    website_crawler = WebsiteCrawler()
    config = WebsiteCrawlerConfig.from_toml(config_name, **config_overrides)
    if run_manager is None:
        run_manager = RunManager("website_crawler")
    if site_id:
        run_manager.set_site_path(site_id)
    if run_name_use_config_name:
        run_manager.set_run_path(config_name)
    else:
        run_manager.set_run_path(config.run_name)
    run_manager.init_module_run_paths()

    # ... 現有爬蟲邏輯（不動）...

    # ----- 儲存至 runs/（歷史紀錄）-----
    save_module_config_as_toml(config, run_manager.module_config_toml_path)
    run_manager.save_results_as_json(crawl_results)
    run_manager.save_results_as_md(crawl_results, "fit_markdown")

    # ----- 發佈至 data/（持久化）-----
    if data_manager and site_id:
        data_manager.publish_crawl_results(site_id, crawl_results)
        data_manager.publish_markdown(site_id, crawl_results, "fit_markdown")

    log_session("Website Crawling Completed", style="cyan")
    return crawl_results
```

### 3-8. `run_webpage_image_summarizer` 改動

```python
def run_webpage_image_summarizer(
    run_manager: RunManager | None = None,
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    crawl_results: dict[str, dict] | None = None,
    site_id: str = "",
    data_manager: DataManager | None = None,
    **config_overrides,
) -> dict[str, dict] | None:
    # ... 初始化（含 set_site_path）...

    # ... 現有摘要邏輯（不動）...

    # ----- 儲存至 runs/ -----
    run_manager.save_results_as_json(enhanced_results)
    run_manager.save_results_as_md(enhanced_results, "enhanced_markdown")

    # ----- 發佈至 data/（覆蓋爬取結果為增強版本）-----
    if data_manager and site_id:
        data_manager.publish_crawl_results(site_id, enhanced_results)
        data_manager.publish_markdown(site_id, enhanced_results, "enhanced_markdown")

    return enhanced_results
```

### 3-9. `run_rag_build` 改動

```python
def run_rag_build(
    run_manager: RunManager | None = None,
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    webpages_data_use_latest_results: bool = False,
    save_vector_store_to_runs: bool = False,
    site_id: str = "",
    data_manager: DataManager | None = None,
    **config_overrides,
) -> None:
    config = RAGConfig.from_toml(config_name, **config_overrides)

    # ── 多站模式：DataManager 提供路徑 ──
    if site_id and data_manager:
        config.webpages_data_folder_path = data_manager.get_webpages_path(site_id)
        config.milvus_uri = os.path.join(
            data_manager.get_vector_store_path(site_id), "milvus.db"
        )
    # ── 單站 fallback：沿用現有邏輯 ──
    elif webpages_data_use_latest_results:
        webpages_data_folder_path = run_manager.load_latest_summarizer_run_path()
        config.webpages_data_folder_path = webpages_data_folder_path

    # ... 現有 RAG build 邏輯（不動）...

    # ----- publish 向量庫至 data/ -----
    if data_manager and site_id:
        data_manager.publish_vector_store(site_id, config.milvus_uri)
```

### 3-10. CLI 與 main.py 改動

**CLI dataclass 新增 `site_id`**：

```python
@dataclass
class WebsiteCrawlerRunConfig:
    run_name: str = "default"
    run_name_use_config_name: bool = False
    site_id: str = ""

# 其他 RunConfig 類比新增
```

**cli.py 分派邏輯**：

```python
# 現在
elif isinstance(cli_arg, WebsiteCrawlerCLI):
    run_manager.set_module_path("website_crawler")
    run_website_crawler(run_manager, **vars(cli_arg.run), **module_config_overrides)

# 多站後
elif isinstance(cli_arg, WebsiteCrawlerCLI):
    run_manager.set_module_path("website_crawler")
    run_website_crawler(
        run_manager,
        data_manager=data_manager,
        **vars(cli_arg.run),    # 含 site_id
        **module_config_overrides,
    )
```

**main.py**：

```python
def main() -> None:
    run_manager = RunManager()
    data_manager = DataManager()

    run_manager.set_module_path("website_crawler")
    crawl_results = run_website_crawler(
        run_manager=run_manager,
        site_id="nculab",
        data_manager=data_manager,
        **vars(website_crawler_run_config),
    )
```

### 3-11. 設定檔結構變化

**RAG 設定檔**（`webpages_data_folder_path` 不再硬編碼，由 DataManager 動態提供）：

```toml
# configs/rag/nculab.toml
[vector_store]
vector_store_type = "milvus"
collection_name = "webpages_nculab"

[index]
embedding_name = "text-embedding-3-small"

[retriever]
query_mode = "hybrid"
similarity_top_k = 10
hybrid_top_k = 10
```

### 3-12. Agent 整合

**Site Discovery 工具**：

```python
def create_site_discovery_tool(data_manager: DataManager) -> StructuredTool:
    """掃描 data/rag/ 目錄，回傳所有已建庫的 site_id 列表。"""

    def _list_sites() -> str:
        sites = data_manager.list_sites()
        return "\n".join(f"- {s}" for s in sites) if sites else "No sites available."

    return StructuredTool(
        name="list_knowledge_bases",
        description="列出所有可用的知識庫 site_id 列表。",
        func=_list_sites,
    )
```

**RAGRegistry（整合版）**：

```python
class RAGRegistry:
    """依 site_id 管理多個 RAG 實例。"""

    def __init__(self, data_manager: DataManager) -> None:
        self._data_manager = data_manager
        self._instances: dict[str, RAG] = {}

    def get(self, site_id: str, config_name: str = "default") -> RAG:
        if site_id not in self._instances:
            config = RAGConfig.from_toml(config_name)
            config.webpages_data_folder_path = self._data_manager.get_webpages_path(site_id)
            config.milvus_uri = os.path.join(
                self._data_manager.get_vector_store_path(site_id), "milvus.db"
            )
            self._instances[site_id] = RAGBuilder(config).build()
        return self._instances[site_id]

    def close(self) -> None:
        for rag in self._instances.values():
            rag.close()
```

### 3-13. 目錄結構（重構後）

```
data/
├── webpages/
│   ├── nculab/
│   │   ├── results.json
│   │   └── results/
│   │       └── *.md
│   └── nctu/
│       ├── results.json
│       └── results/
├── rag/
│   ├── nculab/
│   │   └── milvus.db
│   └── nctu/
│       └── milvus.db

runs/<ts>/
├── website_crawler/
│   └── nculab/
│       └── default/
│           ├── results.json
│           ├── results/*.md
│           ├── module_config.toml
│           └── terminal.log
├── webpage_image_summarizer/
│   └── nculab/
│       └── default/
├── rag_build/
│   └── nculab/
│       └── default/
├── rag_query/
│   └── nculab/
│       └── default/
└── agent/
    └── nculab/
        └── default/
```

### 3-14. 遷移路徑

```bash
# Phase 2 的目錄搬移
data/webpages/results.json       → data/webpages/nculab/results.json
data/webpages/results/           → data/webpages/nculab/results/
data/rag/results/milvus.db       → data/rag/nculab/milvus.db
```

### 3-15. site_id 完整流動路徑

```
                    ┌─────────────────────────────┐
                    │  來源（二擇一或兩者）         │
                    │  1. CLI: --site-id nculab    │
                    │  2. TOML: site_id = "nculab" │
                    └──────────┬──────────────────┘
                               │
                    ┌──────────▼──────────────────┐
                    │  WorkflowConfig / CLI dataclass│
                    │  site_id: str                 │
                    └──────────┬──────────────────┘
                               │
               ┌───────────────┼───────────────┐
               ▼               ▼               ▼
    ┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
    │ RunManager       │ │ DataManager  │ │ RAG Config       │
    │ .set_site_path() │ │ .publish_*() │ │ .webpages_data   │
    │ → runs/.../site/ │ │ → data/.../  │ │   = dynamical    │
    └──────────────────┘ └──────────────┘ └──────────────────┘
```

---

## 4. Engines 重構 — Import 變更（來源：`engines_restructure_analysis.md`）

### 4-1. 純函數搬移 import 變更

| 原 import | 新 import | 受影響檔案 |
|-----------|-----------|-----------|
| `app.engines.html_date_extractor` | `utils.html_date_extractor` | `website_crawler.py`、`test/test_html_date_extraction.py` |
| `app.engines.markdown_cleaner` | `utils.markdown_cleaner` | `website_crawler.py` |

共 **3 個 import 語句**需修改。

### 4-2. RAG 子資料夾 import 變更

| 原路徑 | 新路徑（有 `__init__.py` 匯出後） |
|--------|----------------------------------|
| `app.engines.rag.RAG` | `app.engines.rag.RAG`（不變） |
| `app.engines.rag_factory.RAGBuilder` | `app.engines.rag.RAGBuilder` |
| `app.engines.rag_eval_prompts.FAITHFULNESS_*` | `app.engines.rag.rag_eval_prompts.*` |

受影響的 consumer：

| 檔案 | 變更 |
|------|------|
| `app/workflow/workflow.py` | `from app.engines.rag import RAG`（不變）+ `from app.engines.rag_factory` → `from app.engines.rag` |
| `app/tools/webpage_retriever.py` | 同上 |
| `app/engines/rag_factory.py`（內部） | `from app.engines.rag import RAG`（不變）+ `from app.engines.rag_eval_prompts` → `from app.engines.rag.rag_eval_prompts`（或相對 import） |

共約 **4–5 個 import 語句**需修改。

---

## 5. engines/ 內部依賴圖

```
workflow.py ──→ RAG / RAGBuilder / WebsiteCrawler / WebpageImageSummarizer
tools/      ──→ RAG / RAGBuilder
test/       ──→ WebsiteCrawler, resolve_dedup_key, html_date_extractor

rag_factory ──→ RAG, rag_eval_prompts
website_crawler ──→ html_date_extractor, markdown_cleaner
```
