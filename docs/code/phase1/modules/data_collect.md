# 網站爬蟲

## 模組總覽
此模組以**非同步方式**爬取網站頁面，依設定限制**爬取深度**與**頁數**，並將每頁內容整理成乾淨且格式化的**Markdown**。爬取後的資料會再經過**清理**、**標題整理**、**圖片連結擷取**與**去重**，最後以**頁面標題**作為識別，回傳整理後的頁面資訊並記錄**成功**、**錯誤**與**重複頁面**的統計。

- **模組實作**
	- `src/website_copilot/ingestion/crawling/website_crawler.py`（**主爬蟲實作**，包含**爬取**、**過濾**、**Markdown 清洗**與**輸出邏輯**）
	- `src/website_copilot/config/website_crawler_config.py`（**模組內部常數**與**預設設定**，例如**內容門檻**）
	- `src/website_copilot/utils/log_helper.py`（**日誌**與**統計輸出輔助**）

- **模組設定**
	- `./configs/website_crawler/{name}.yml`（**爬蟲模組參數**，只寫與 class 預設值不同的部分，透過 `src/website_copilot/config/website_crawler_config.py` 載入）
	- `./configs/sites/{site}.yml`（**站點設定**：`site_id`、`sample_query` 與 `crawl` 的 `url`／`url_patterns`／`allowed_domains`／`path_prefix`，以及 `documents.url_patterns`（站點專屬的文件 URL 樣式），透過 `config/site_config.py` 的 `SiteConfig` 載入）。文件 URL（通用副檔名 + `documents.url_patterns`）不進入 BFS（瀏覽器導航會觸發下載而失敗），改由 augmenter 處理；`success=False` 的頁面記錄實際錯誤訊息（統計項 `error_failed`）
	- 可在 `src/website_copilot/ingestion/crawling/website_crawler.py` 中調整 `BrowserConfig` 與 `CrawlerRunConfig` 選項以改變**執行行為**

- **模組環境**
	- `Python >= 3.13`（程式使用**現代型別語法**如 `int | None`）
	- **標準函式庫**：`asyncio`、`re`、`logging`
	- **第三方套件**：`crawl4ai`（**爬蟲與 Markdown 生成**）、`mdformat`（**Markdown 格式化**）、`rich`（**輸出統計表格**）

## website_crawler.py

### 1. 網站爬取設定
- 設定**爬取深度**與**頁數上限**。
- 限制**特定網域**或**網址模式**。
- 決定**實際爬取範圍**。

### 2. 爬取與內容整理
- 從首頁開始**非同步爬取**，並保留較有價值的內容。
- 將每頁轉成**Markdown**，並移除**雜訊**與不需要的**連結**。
- 以**頁面標題**作為檔名，並避免**重複輸出**。

### 3. 輸出與記錄結果
- 回傳每頁的**網址**、整理後**內容**、**圖片資訊**、**metadata** 與 **crawl_info**。
- Metadata 包含從 URL 解析出的 `page_type`（`"paper"` / `"announcement"` / `"personnel"` / `"general"` 等）與網頁 `description`，供後續 RAG 檢索時作為過濾標籤。
- 提供**成功**、**錯誤**與**重複頁面**的統計。
- 方便後續檢查**爬取品質**與**覆蓋範圍**。

## website_crawler_config.py

### 1. 讀取設定來源
- 從 `./configs/website_crawler/{name}.yml` 載入**爬蟲模組參數**（支援 `extends`，缺少的欄位使用 config class 預設值）；站點相關的網址與篩選條件由 `SiteConfig` 提供。
- 支援不同任務切換**不同設定檔**。
- 由 `src/website_copilot/config/website_crawler_config.py` 統一管理。

### 2. 檢查可用設定
- 驗證**爬取深度**、**頁數上限**與**內容門檻**。
- 檢查**網址**、**網域**與**排除字詞**等條件。
- 避免**設定格式不正確**而影響爬取。

### 3. 套用與轉換參數
- `exclude_words` 已不再是設定參數：由 LLM 產生並驗證（見 `[clean]` 與 `ingestion/crawling/markdown_cleaner.py`）。
- 可搭配 `ingestion/crawling/website_crawler.py` 調整**瀏覽**與**爬取行為**。
- 讓設定內容直接對應**實際執行需求**。

## 補充說明
- `WebsiteCrawler.crawl_website()` 先設定**網址**與**篩選條件**，再執行**非同步爬取**與**結果整理**；任一階段失敗都會直接回傳 `None`。
- `_crawl_website_async()` 組合**瀏覽器設定**、**內容過濾**、**網址/網域篩選**與**深層爬取策略**，並將結果整理成清單。
- `_extract_metadata()` 根據 URL sub-path 匹配 `PAGE_TYPE_PATTERNS` 規則（如 `/news` → `announcement`、`/publication` → `paper`），產出 `page_type` 與 `description` 供下游 metadata filter 使用。
- `_extract_crawl_results_data()` 產出最終結構，每個頁面包含 `url`、`fit_markdown`、`images`、`metadata` 與 `crawl_info` 五個子字典。
- `WebsiteCrawlerConfig.from_yaml(config_name, overrides=None)` 載入 `init` 與 `clean` 設定（extends 展開 → 疊上 CLI overrides → pydantic 驗證一次）；`default` 無檔案時等於 class 預設值。
- `run_name` 依 YAML 的 `run_name_fields` 組成，未寫時使用 class 的 `_DEFAULT_RUN_NAME_FIELDS`（`init.max_depth`）。- `init.content_threshold`（`PruningContentFilter` 的門檻，越高過濾越多內容）預設 `0.25`。曾有一組「保留標題」的對照值 `0.45`（原常數 `KEEP_TITLE_CONTENT_THRESHOLD`），程式中無人引用而已刪除；需要時以設定檔覆寫 `init.content_threshold` 即可。
