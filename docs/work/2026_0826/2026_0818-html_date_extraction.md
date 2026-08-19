# 實作計畫：HTML 日期擷取 (2026/08/18)

> 目標：在爬蟲階段從 HTML 結構化標籤擷取發佈日期，輔以 HTTP `Last-Modified` 標頭，
> 並將結果寫入 `results.json` → node metadata → 向量庫，讓下游檢索可利用時間資訊。

---

## 1. 變更範圍總覽

```
website_crawler.py          ← 新增 _extract_date_from_html()，改 _extract_metadata() 簽名
rag_factory.py              ← _build_file_metadata() 傳遞 published_date
rag_helper.py               ← MarkdownDateExtractor 優先使用 HTML metadata 日期
```

---

## 2. 模組一：`website_crawler.py` — HTML 日期解析

### 2-1. 新增 `_extract_date_from_html(html: str) -> dict[str, str | None]`

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

**實作要點**：

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

### 2-2. 修改 `_extract_metadata()` 簽名

**現狀**：
```python
@staticmethod
def _extract_metadata(url: str, raw_metadata: dict) -> dict:
```

**改為**：
```python
@staticmethod
def _extract_metadata(
    url: str,
    raw_metadata: dict,
    html: str | None = None,
    response_headers: dict[str, str] | None = None,
) -> dict:
```

**新增邏輯**（在現有 `description` + `page_type` 之後）：

```python
# --- HTML 日期擷取 ---
if html:
    date_info = _extract_date_from_html(html, response_headers)
    if date_info["published_date"]:
        metadata["published_date"] = date_info["published_date"]
    if date_info["modified_date"]:
        metadata["modified_date"] = date_info["modified_date"]
```

### 2-3. 修改 `_extract_crawl_results_data()` 呼叫端

**現狀**（第 286–293 行）：
```python
raw_metadata: dict = crawl_result.metadata

enriched_results[page_title] = {
    ...
    "metadata": self._extract_metadata(url, raw_metadata),
    ...
}
```

**改為**：
```python
raw_metadata: dict = crawl_result.metadata

enriched_results[page_title] = {
    ...
    "metadata": self._extract_metadata(
        url,
        raw_metadata,
        html=getattr(crawl_result, "html", None),
        response_headers=getattr(crawl_result, "response_headers", None),
    ),
    ...
}
```

使用 `getattr` 以防 `crawl_result` 缺少這些欄位（向後相容）。

---

## 3. 模組二：`rag_factory.py` — 傳遞日期到 Node Metadata

### 3-1. 修改 `_build_file_metadata()`

**現狀**（第 80–90 行）：
```python
return {
    "page_title": page_title,
    "page_url": page_info.get("url", ""),
    "page_type": page_metadata.get("page_type", "general"),
    "description": page_metadata.get("description", ""),
}
```

**改為**：
```python
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

---

## 4. 模組三：`rag_helper.py` — MarkdownDateExtractor 降級改進

### 4-1. 修改 `_extract_date()` 優先級

**核心邏輯**：node metadata 中已有 `published_date`（來自 HTML 解析）時直接注入，跳過內容推斷。

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

**變更影響**：
- 有 HTML metadata 的頁面 → 直接使用，精確到年月日
- 無 HTML metadata 的頁面 → 退回原有四層策略（完全向後相容）

---

## 5. 資料流變更示意

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

---

## 6. results.json 變更前後對比

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

---

## 7. 測試策略

| 測試類型 | 對象 | 驗證內容 |
|---------|------|---------|
| **單元測試** | `_extract_date_from_html()` | 各種 HTML 結構的日期擷取正確性 |
| **單元測試** | `_normalize_to_iso8601()` | 各種日期格式的標準化 |
| **單元測試** | `_extract_date()` (MarkdownDateExtractor) | 有/無 `published_date` 時的行為 |
| **整合測試** | `_extract_metadata()` | 傳入 HTML + headers 後 metadata 包含日期 |
| **端到端** | 完整爬蟲流程 | `results.json` 中有有效 `published_date` |

### 關鍵測試案例

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

---

## 8. 實作順序

```
Step 1: website_crawler.py — 新增 _extract_date_from_html() 及輔助函數
Step 2: website_crawler.py — 修改 _extract_metadata() 簽名與邏輯
Step 3: website_crawler.py — 修改 _extract_crawl_results_data() 呼叫端
Step 4: rag_factory.py    — 修改 _build_file_metadata() 傳遞 published_date
Step 5: rag_helper.py     — 修改 MarkdownDateExtractor._extract_date() 優先級
Step 6: 寫單元測試
Step 7: 重新爬取 nculab 驗證 results.json 有日期
```

> **⚠️ Step 7 前置依賴**：Step 7（重新爬取 nculab）必須在
> [RunManager Refactor Phase 2](docs/work/2026_0819/2026_0819-RunManager_refactor.md)
> 完成後才執行。理由：重新爬取的結果需直接寫入多站目錄結構
> `data/webpages/nculab/`（而非舊的平坦結構 `data/webpages/`），
> 避免額外的遷移步驟。Step 1–6 與 Refactor 可並行，互不阻塞。

---

## 9. 風險與緩解

| 風險 | 影響 | 緩解 |
|------|------|------|
| HTML 結構異常導致 BeautifulSoup 解析失敗 | 該頁面無日期 | try/except 包裹，回傳空 dict |
| 標準化失敗（未知日期格式） | published_date 為 None | 退回 MarkdownDateExtractor 內容推斷 |
| crawl4ai 版本升級改變 html 欄位 | 擷取失敗 | 用 getattr 保護，向後相容 |
| Google Sites 的 JSON-LD 結構不同 | 日期擷取不到 | 有多層 fallback，不影響現有功能 |

---

## 10. 附帶實作：URL path 去重機制 (`path_prefix`)

### 10-1. 問題背景

在測試 csie 網站爬取時，發現 `_filter_crawl_results()` 的去重邏輯使用 `<title>` 標籤作為去重鍵，但 csie 網站所有頁面共用相同的標題（`國立中央大學資訊工程學系`），導致 10 個頁面爬取後只剩 1 個被保留，其餘 9 個被誤判為重複頁面而丟棄。

| 頁面 | `<title>` | 舊去重鍵 | 結果 |
|------|----------|---------|------|
| `/` | `國立中央大學資訊工程學系` | `國立中央大學資訊工程學系` | ✅ 保留 |
| `/department` | `系所介紹 - 國立中央大學資訊工程學系` | `國立中央大學資訊工程學系` | ❌ 丟棄 |
| `/department/member` | `系所介紹 - 國立中央大學資訊工程學系` | `國立中央大學資訊工程學系` | ❌ 丟棄 |
| `/admission` | `招生資訊 - 國立中央大學資訊工程學系` | `國立中央大學資訊工程學系` | ❌ 丟棄 |

### 10-2. 解決方案：URL path 作為去重鍵

將去重鍵從 `<title>` 改為 **URL relative path**，透過 TOML 設定 `path_prefix` 指定要截掉的路徑前綴。

**去重鍵生成邏輯**：

```python
def _resolve_dedup_key(self, url: str) -> str:
    """從 URL 產生去重鍵：截去 path_prefix 後的相對路徑。"""
    full_path = urlparse(url).path
    base = self.path_prefix.rstrip("/")
    relative = full_path[len(base):].strip("/") if base else full_path.strip("/")
    return relative.replace("/", "_") or "index"
```

### 10-3. TOML 設定檔新增 `path_prefix`

```toml
# nculab.toml
[crawl]
url = "https://sites.google.com/site/nculab/labintro"
path_prefix = "/site/nculab"

# ncucsie.toml
[crawl]
url = "https://www.csie.ncu.edu.tw/"
path_prefix = "/"
```

**Fallback**：`path_prefix` 未設定時，自動取起始 URL 的父路徑。

### 10-4. 各網站走讀

| 網站 | URL | path_prefix | relative | dedup_key |
|------|-----|-------------|----------|-----------|
| nculab 首頁 | `/site/nculab/labintro` | `/site/nculab` | `labintro` | `labintro` |
| nculab 校內奬項 | `/site/nculab/news/校內奬項` | `/site/nculab` | `news/校內奬項` | `news_校內奬項` |
| csie 首頁 | `/` | `/` | `` → `index` | `index` |
| csie 系所介紹 | `/department` | `/` | `department` | `department` |
| csie 系所成員 | `/department/member` | `/` | `department/member` | `department_member` |
| csie 公告 | `/announcement/016e98cf...` | `/` | `announcement/016e98cf...` | `announcement_016e98cf...` |

### 10-5. 已完成的變更

| 檔案 | 變更內容 | 狀態 |
|------|---------|------|
| `src/app/configs/website_crawler_config.py` | 新增 `path_prefix` 到 `CRAWL_KEYS`、dataclass 欄位、驗證邏輯 | ✅ 完成 |
| `src/app/engines/website_crawler.py` | 新增 `path_prefix` 參數到 `crawl_website()`；重寫 `_filter_crawl_results()` 使用 URL path 去重；新增 `_resolve_dedup_key()` | ✅ 完成 |
| `src/app/workflow/workflow.py` | 傳遞 `path_prefix` 從設定檔到爬蟲 | ✅ 完成 |
| `configs/website_crawler/nculab.toml` | 新增 `path_prefix = "/site/nculab"` | ✅ 完成 |
| `configs/website_crawler/ncucsie.toml` | 新增 `path_prefix = "/"` | ✅ 完成 |
| `configs/website_crawler/test.toml` | 新增 `path_prefix = "/site/nculab"` | ✅ 完成 |
| `src/test/test_dedup_key.py` | 12 個去重邏輯單元測試 | ✅ 12/12 通過 |

### 10-6. 端到端驗證結果

#### csie.ncu.edu.tw（改動前 vs 改動後）

| 指標 | 改動前 | 改動後 |
|------|--------|--------|
| 爬取頁面數 | 10 | 10 |
| 保留頁面數 | 1（9 個被去重） | **9** |
| .md 檔名風格 | `國立中央大學資訊工程學系.md` | `department_member.md` |

#### 改動後的 .md 檔名結構

```
runs/20260819_113704/website_crawler/max_pages-10/results/
├── index.md                          ← /
├── department.md                     ← /department
├── department_area.md                ← /department/area
├── department_introduction.md        ← /department/introduction
├── department_lab.md                 ← /department/lab
├── department_member.md              ← /department/member
├── admission.md                      ← /admission
├── admission_master.md               ← /admission/master
└── admission_undergraduate.md        ← /admission/undergraduate
```

#### nculab（改動前 vs 改動後）

| 指標 | 改動前 | 改動後 |
|------|--------|--------|
| 保留頁面數 | 4 | 4（不變） |
| .md 檔名 | `校內奬項.md` | `news_校內奬項.md` |

### 10-7. 單元測試結果

```bash
uv run pytest src/test/test_dedup_key.py -v

TestResolveDedupKey::test_nculab_child_page       PASSED
TestResolveDedupKey::test_nculab_root             PASSED
TestResolveDedupKey::test_csie_child_page         PASSED
TestResolveDedupKey::test_csie_root               PASSED
TestResolveDedupKey::test_csie_deep_path          PASSED
TestResolveDedupKey::test_no_path_prefix_fallback PASSED
TestResolveDedupKey::test_no_path_prefix_domain_root PASSED
TestFilterCrawlResults::test_different_pages_not_deduped PASSED
TestFilterCrawlResults::test_same_url_deduped     PASSED
TestFilterCrawlResults::test_404_skipped          PASSED
TestFilterCrawlResults::test_nculab_pages_not_deduped PASSED
TestFilterCrawlResults::test_stats_tracking       PASSED

============================== 12 passed ==============================
```

---

## 11. 實作結果 (2026/08/19) — HTML 日期擷取

### 10-1. 已完成的變更

| 檔案 | 變更內容 | 狀態 |
|------|---------|------|
| `src/app/engines/website_crawler.py` | 新增 `_extract_date_from_html()` 及 6 個輔助函數；修改 `_extract_metadata()` 簽名加入 `html`/`response_headers` 參數；修改 `_extract_crawl_results_data()` 呼叫端 | ✅ 完成 |
| `src/app/engines/rag_factory.py` | `_build_file_metadata()` 新增 `published_date` 傳遞 | ✅ 完成 |
| `src/utils/rag_helper.py` | `MarkdownDateExtractor` 新增 Strategy 0：優先使用 HTML metadata 日期 | ✅ 完成 |
| `src/test/test_html_date_extraction.py` | 35 個單元測試（JSON-LD、OG meta、`<time>` 元素、generic meta、Dublin Core、HTTP Last-Modified、無日期 fallback、損壞 HTML 容錯） | ✅ 35/35 通過 |

### 10-2. 端到端驗證結果

#### Google Sites (nculab)

| 頁面 | published_date | modified_date |
|------|---------------|---------------|
| Web Intelligence and Data Mining Lab | ❌ 無 | ❌ 無 |
| 校內奬項 | ❌ 無 | ❌ 無 |
| News | ❌ 無 | ❌ 無 |
| 研討會 | ❌ 無 | ❌ 無 |

**原因**：Google Sites HTML 中完全沒有結構化日期標籤。

#### csie.ncu.edu.tw

| 頁面 | published_date | modified_date |
|------|---------------|---------------|
| index (首頁) | ❌ 無 | ❌ 無 |
| department | ❌ 無 | ❌ 無 |
| department_member | ❌ 無 | ❌ 無 |
| admission | ❌ 無 | ❌ 無 |

**原因**：csie 網站 HTML 中也完全沒有結構化日期標籤。

### 10-3. HTML 日期來源分析

| 來源 | Google Sites | csie.ncu.edu.tw | WordPress | Medium |
|------|-------------|----------------|-----------|--------|
| JSON-LD `datePublished` | ❌ 無 | ❌ 無 | ✅ 有 | ✅ 有 |
| `<meta property="article:published_time">` | ❌ 無 | ❌ 無 | ✅ 有 | ✅ 有 |
| `<time datetime>` 元素 | ❌ 無 | ❌ 無 | ⚠️ 部分有 | ❌ 無 |
| Generic meta `date` / `pubdate` | ❌ 無 | ❌ 無 | ⚠️ 部分有 | ❌ 無 |
| Dublin Core `dc.date` | ❌ 無 | ❌ 無 | ⚠️ 部分有 | ❌ 無 |
| HTTP `Last-Modified` | ❌ 無 | ❌ 無 | ✅ 有 | ✅ 有 |

---

## 12. 遇到的阻礙（HTML 日期擷取）

### 阻礙一：Google Sites 與 csie 網站不提供結構化日期

**問題**：這兩個網站的 HTML 中完全沒有所需的日期標籤（JSON-LD、OG meta、`<time>` 元素、Dublin Core），HTTP 回應標頭也沒有 `Last-Modified`。

**影響**：所有 6 個優先級都無法命中，`published_date` 和 `modified_date` 均為 None。

**根本原因**：
- Google Sites 作為 SPA（Single Page Application），不生成傳統的 SEO 日期標籤
- csie 網站（自架站）也沒有實作結構化日期 meta 標籤
- 兩個網站的伺服器都不回傳 `Last-Modified` 標頭

### 阻礙二：MarkdownDateExtractor 的內容推斷精度有限

**問題**：當 HTML 日期擷取失敗時，退回到 `MarkdownDateExtractor` 的四層策略，但這些策略依賴頁面內容中的特定文字格式：

| 策略 | 依賴格式 | 命中率 |
|------|---------|--------|
| Strategy 1 | `### 2026`（Section heading 年份） | 低 |
| Strategy 2 | `Post date: Mon DD, YYYY`（Google Sites 專用） | 中 |
| Strategy 3 | `— Mon. DD, YYYY`（Google Sites 專用） | 中 |
| Strategy 4 | 第一個 `20\d{2}`（年份回落） | 高但不精確 |

**影響**：
- 非 Google Sites 的網站（如 csie）幾乎不會命中 Strategy 2 和 3
- Strategy 4 只能取得年份，無法取得月日
- 某些頁面完全沒有日期文字，四層策略全部失效

### 阻礙三：HTTP `Last-Modified` 標頭不可靠

**問題**：即使某些網站提供 `Last-Modified` 標頭，它反映的是**伺服器檔案修改時間**，不一定是**頁面發佈時間**。

**影響**：
- CDN 快取可能導致 `Last-Modified` 反映快取時間而非發佈時間
- 動態生成的頁面（如 SPA）可能每次請求都產生新的 `Last-Modified`
- 某些伺服器根本不提供此標頭（如 Google Sites、csie）

---

## 13. 後續可採用的方法（HTML 日期擷取）

### 方法一：RSS/Atom Feed 擷取（推薦）

**概念**：從網站的 RSS 或 Atom feed 中擷取每篇文章的發佈日期。

**優點**：
- RSS/Atom feed 是專門為內容分發設計的，通常包含精確的發佈日期
- 格式標準化（`<pubDate>` / `<updated>`），解析簡單
- 適合部落格、新聞網站、公告系統

**缺點**：
- 需要先找到 feed URL（通常在 `<link rel="alternate">` 中）
- 不是所有網站都有 feed（如 Google Sites、csie）
- Feed 中的日期可能與實際發佈時間有出入

**實作方式**：
```python
# 1. 從 HTML 中找 feed URL
feed_link = soup.select_one('link[type="application/rss+xml"]')
feed_url = feed_link.get("href") if feed_link else None

# 2. 下載 feed 並解析
import feedparser
feed = feedparser.parse(feed_url)

# 3. 從 feed entries 中擷取日期
for entry in feed.entries:
    published = entry.get("published_parsed")  # time.struct_time
    # 轉換為 ISO 8601
```

### 方法二：Wayback Machine API（歷史快照）

**概念**：使用 Internet Archive 的 Wayback Machine API 查詢頁面的歷史快照時間。

**優點**：
- 可以取得頁面的首次收錄時間和最後更新時間
- 適合任何被 Wayback Machine 收錄的網站
- 不依賴網站本身的日期標籤

**缺點**：
- 查詢速度慢（每次請求需要網路往返）
- 某些頁面可能未被收錄
- 快照時間不等於發佈時間

**實作方式**：
```python
import httpx

def get_wayback_dates(url: str) -> dict[str, str | None]:
    """從 Wayback Machine 取得頁面的首次和最後快照時間。"""
    api_url = f"https://web.archive.org/web/timemap/json/{url}"
    response = httpx.get(api_url, timeout=10)
    if response.status_code == 200:
        data = response.json()
        # 取得最早和最晚的快照時間
        timestamps = [entry[1] for entry in data[1:]]  # 跳過標題列
        return {
            "earliest": timestamps[0] if timestamps else None,
            "latest": timestamps[-1] if timestamps else None,
        }
    return {"earliest": None, "latest": None}
```

### 方法三：Sitemap.xml `<lastmod>` 擷取

**概念**：從網站的 sitemap.xml 中擷取每個頁面的 `<lastmod>` 時間。

**優點**：
- sitemap.xml 通常包含 `<lastmod>` 欄位
- 格式標準化（ISO 8601）
- 適合大型網站

**缺點**：
- `<lastmod>` 反映的是最後修改時間，不一定是發佈時間
- 某些網站的 `<lastmod` 不準確或不更新
- 需要先找到 sitemap.xml 的位置

**實作方式**：
```python
import xml.etree.ElementTree as ET

def extract_dates_from_sitemap(sitemap_url: str) -> dict[str, str]:
    """從 sitemap.xml 中擷取 URL 和 lastmod。"""
    response = httpx.get(sitemap_url, timeout=10)
    root = ET.fromstring(response.text)

    dates = {}
    for url_elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
        loc = url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        lastmod = url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
        if loc is not None and lastmod is not None:
            dates[loc.text] = lastmod.text
    return dates
```

### 方法四：LLM 日期推斷（進階）

**概念**：使用 LLM 從頁面內容中推斷發佈日期。

**優點**：
- 可以理解自然語言中的日期描述（如「昨天」、「上週五」）
- 適合沒有結構化日期標籤的網站
- 可以結合上下文判斷最可能的發佈日期

**缺點**：
- 成本高（每次推斷需要 API 呼叫）
- 速度慢
- 推斷結果可能不準確

**實作方式**：
```python
from llama_index.llms.openai import OpenAI

def infer_date_with_llm(content: str) -> str | None:
    """使用 LLM 從內容中推斷發佈日期。"""
    llm = OpenAI(model="gpt-4")
    prompt = f"""
    從以下內容中推斷最可能的發佈日期。
    如果無法推斷，回傳 None。
    只回傳 ISO 8601 格式（YYYY-MM-DD），不要其他文字。

    內容：
    {content[:2000]}  # 限制長度避免 token 過多
    """
    response = llm.complete(prompt)
    date_str = response.text.strip()

    # 驗證格式
    if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        return date_str
    return None
```

### 方法五：混合策略（推薦的長期方案）

**概念**：結合多種方法，根據網站類型選擇最適合的日期擷取策略。

**策略選擇邏輯**：
```
1. 嘗試 HTML 結構化標籤（現有實作）
   ↓ 失敗
2. 嘗試 RSS/Atom Feed
   ↓ 失敗
3. 嘗試 Sitemap.xml <lastmod>
   ↓ 失敗
4. 嘗試 Wayback Machine API
   ↓ 失敗
5. 退回到 MarkdownDateExtractor 內容推斷
   ↓ 失敗
6. 回傳 None（無日期）
```

**優點**：
- 最大化日期擷取的成功率
- 根據網站類型自動選擇最適合的方法
- 有明確的 fallback 鏈

**缺點**：
- 實作複雜度高
- 需要為每種方法實作對應的解析邏輯
- 某些方法需要額外的網路請求或 API 呼叫

---

## 14. 建議的下一步（HTML 日期擷取）

| 優先級 | 行動 | 預期效益 |
|--------|------|---------|
| **高** | 實作方法五（混合策略）的 RSS/Atom Feed 擷取 | 提升有 feed 的網站的日期擷取率 |
| **中** | 實作 Sitemap.xml `<lastmod>` 擷取 | 提升有 sitemap 的網站的日期擷取率 |
| **中** | 為 csie 網站實作專用的日期推斷邏輯（從 URL 結構或頁面內容推斷） | 提升 csie 的日期擷取率 |
| **低** | 實作 Wayback Machine API 整合 | 作為最後的 fallback 手段 |
| **低** | 評估 LLM 日期推斷的成本效益 | 考慮是否值得為特定網站使用 |

---

## 15. 結論

### 已達成的目標

1. ✅ **HTML 日期擷取框架已建置**：6 層優先級的解析邏輯已實作並測試
2. ✅ **資料流已串接**：`results.json` → node metadata → 向量庫的完整鏈路已建立
3. ✅ **Fallback 機制已完善**：無 HTML date 時退回 `MarkdownDateExtractor` 內容推斷
4. ✅ **向後相容**：不影響既有網站（如 Google Sites）的運作

### 未達成的目標

1. ❌ **csie 和 Google Sites 的日期擷取**：這兩個網站不提供結構化日期標籤，所有優先級都無法命中
2. ❌ **HTTP `Last-Modified` 的實用性**：這兩個網站的伺服器都不回傳此標頭

### 核心發現

**HTML 日期擷取的有效性高度依賴網站平台**：
- WordPress、Medium、自架站（有 SEO 套件）→ 高命中率
- Google Sites、csie（無 SEO 套件）→ 零命中率

**建議**：對於不提供結構化日期的網站，應採用混合策略（方法五），結合 RSS/Atom Feed、Sitemap.xml、Wayback Machine 等多種資料來源，最大化日期擷取的成功率。
