# 獲取網站資料

## 方案 A：網站爬蟲
- 原則：從網站首頁啟動非同步爬取，遍歷網站內頁並將每一頁轉成 Markdown 格式。
- 核心實作：`app/website_crawler.py`
- 設定管理：`app/website_crawler_config.py`
- 使用套件：`crawl4ai`，主要包含 `AsyncWebCrawler`、`BFSDeepCrawlStrategy`、`PruningContentFilter`。

### 實作流程
1. 可調整的爬取範圍與過濾
   - `max_depth`：爬取最深層級。
   - `max_pages`：限制最多回傳頁數。
   - `url_patterns` / `allowed_domains`：可用字串、正則或列表限制只爬特定範圍。

2. 內容過濾與 Markdown 生成
   - 使用 `PruningContentFilter(threshold=content_threshold)` 控制保留的內容量。
   - 將每頁內容轉成 `fit_markdown`。

3. 後處理：排除、去重與檔名生成
   - `exclude_words`：剔除含指定字詞的行。
   - 移除隱藏錨點空連結：`[](...#h...)`。
   - 將空標題行提升為下一個可用文字標題。
   - 取第一個 Markdown 標題作為檔名，非法字元移除並將空白轉成底線。
   - 相同檔名視為重複，僅保留第一筆結果。

4. 輸出與統計
   - 每頁輸出包含 `md_file_name`、`url`、`fit_markdown`、`images`。
   - 統計項目包括 `success_pages`、`error_pages`、`repeat_pages`。

5. 設定驗證與執行選項
   - `app/website_crawler_config.py` 讀取 `./config/website_crawler/{name}.toml`。
   - 驗證 `max_depth`、`max_pages`、`content_threshold`、`light_mode`、`wait_for_images`。
   - 驗證 `url`、`url_patterns`、`allowed_domains`、`exclude_words`。
   - 若 `exclude_words` 以列表提供，會自動轉為 tuple。

###  補充說明
- `WebsiteCrawler.crawl_website()` 會先執行 `_crawl_website_async()` 再做 `_filter_crawl_results()`。
- `_crawl_website_async()` 中可根據 `max_pages` 決定是否將 `max_pages` 傳入 `BFSDeepCrawlStrategy`。
- `BrowserConfig` 目前預設 headless 模式，可透過註解調整為可視瀏覽器模式。
- 目前程式碼已保留 `images` 內容，但 `image_count` 統計尚未啟用。

## 方案B：上傳資料
> 待更新

# 當前進度

- [x] 獲取網站資料
  - [x] 網站爬蟲
  - [x] 篩選網域、雜訊
  - [x] 平行處理

# 未來規劃
- 獲取網站地圖
