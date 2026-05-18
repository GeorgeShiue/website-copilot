# 網站爬蟲

## 模組總覽
此模組以**非同步方式**爬取網站頁面，依設定限制**爬取深度**與**頁數**，並將每頁內容整理成乾淨且格式化的**Markdown**。爬取後的資料會再經過**清理**、**標題整理**、**圖片連結擷取**與**去重**，最後以**頁面標題**作為識別，回傳整理後的頁面資訊並記錄**成功**、**錯誤**與**重複頁面**的統計。

- **模組實作**
	- `app/website_crawler.py`（**主爬蟲實作**，包含**爬取**、**過濾**、**Markdown 清洗**與**輸出邏輯**）
	- `app/website_crawler_config.py`（**模組內部常數**與**預設設定**，例如**內容門檻**）
	- `utils/log_helper.py`（**日誌**與**統計輸出輔助**）

- **模組設定**
	- `./config/website_crawler/{name}.toml`（**爬蟲執行設定**，透過 `app/website_crawler_config.py` 載入）
	- 可在 `app/website_crawler.py` 中調整 `BrowserConfig` 與 `CrawlerRunConfig` 選項以改變**執行行為**

- **模組環境**
	- `Python >= 3.10`（程式使用**現代型別語法**如 `int | None`）
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
- 回傳每頁的**網址**、整理後**內容**與**圖片資訊**。
- 提供**成功**、**錯誤**與**重複頁面**的統計。
- 方便後續檢查**爬取品質**與**覆蓋範圍**。

## website_crawler_config.py

### 1. 讀取設定來源
- 從 `./config/website_crawler/{name}.toml` 載入**爬蟲設定**。
- 支援不同任務切換**不同設定檔**。
- 由 `app/website_crawler_config.py` 統一管理。

### 2. 檢查可用設定
- 驗證**爬取深度**、**頁數上限**與**內容門檻**。
- 檢查**網址**、**網域**與**排除字詞**等條件。
- 避免**設定格式不正確**而影響爬取。

### 3. 套用與轉換參數
- 將 `exclude_words` 由**列表**轉成 `tuple`。
- 可搭配 `app/website_crawler.py` 調整**瀏覽**與**爬取行為**。
- 讓設定內容直接對應**實際執行需求**。

## 補充說明
- `WebsiteCrawler.crawl_website()` 先設定**網址**與**篩選條件**，再執行**非同步爬取**與**結果整理**；任一階段失敗都會直接回傳 `None`。
- `_crawl_website_async()` 組合**瀏覽器設定**、**內容過濾**、**網址/網域篩選**與**深層爬取策略**，並將結果整理成清單。
- `WebsiteCrawlerConfig.from_toml()` 從 `./config/website_crawler/{name}.toml` 載入 `init` 與 `crawl` 設定，並在建立後立即驗證內容。
- `exclude_words` 若以**列表**提供會自動轉成 `tuple`，`run_name` 則依 TOML 註解標記的欄位組合而成。