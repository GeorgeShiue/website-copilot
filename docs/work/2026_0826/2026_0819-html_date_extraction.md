# HTML 日期擷取規劃 (2026/08/19)

> 目標：在爬蟲階段從 HTML 結構化標籤擷取發佈日期，輔以 HTTP `Last-Modified` 標頭，
> 並將結果寫入 `results.json` → node metadata → 向量庫，讓下游檢索可利用時間資訊。

---

## 1. 變更範圍總覽

```
website_crawler.py          ← 新增 _extract_date_from_html()，改 _extract_metadata() 簽名
rag_factory.py              ← _build_file_metadata() 傳遞 published_date
rag_helper.py               ← MarkdownDateExtractor 優先使用 HTML metadata 日期
```

> 具體實作規格、程式碼設計、測試策略等，請參閱 [dev_log.md](dev_log.md) §1。

---

## 2. 模組一：`website_crawler.py` — HTML 日期解析

從 `CrawlResult.html` 解析結構化日期標籤，支援六層優先級解析（JSON-LD → OG meta → `<time>` 元素 → Generic meta → Dublin Core → HTTP Last-Modified），回傳 ISO 8601 格式的 `published_date` / `modified_date`。

主要變更：
- 新增 `_extract_date_from_html()` 及其輔助函數
- 修改 `_extract_metadata()` 簽名，新增 `html` 與 `response_headers` 參數
- 修改 `_extract_crawl_results_data()` 呼叫端，傳入 HTML 原始碼

---

## 3. 模組二：`rag_factory.py` — 傳遞日期到 Node Metadata

修改 `_build_file_metadata()`，將 HTML 擷取的 `published_date` 注入 node metadata，供下游 `MarkdownDateExtractor` 優先使用。

---

## 4. 模組三：`rag_helper.py` — MarkdownDateExtractor 降級改進

修改 `_extract_date()` 優先級：node metadata 中已有 `published_date` 時直接注入，跳過內容推斷；無 HTML metadata 時才走原有四層策略（完全向後相容）。

---

## 5. 資料流變更概要

```
[改動前]
HTML → crawl4ai → CrawlResult.metadata (無日期)
                 → MarkdownDateExtractor (從 Markdown 文字推斷)

[改動後]
HTML → crawl4ai → _extract_date_from_html() → results.json (published_date)
                                              → node metadata
                                              → MarkdownDateExtractor (優先使用 published_date)
                                                          ↓ (無 HTML date 時)
                                              原有四層策略（fallback）
```

---

## 6. results.json 變更預期

`metadata` 欄位新增 `published_date` 與 `modified_date`（ISO 8601 格式 `YYYY-MM-DD`）。

---

## 7. 測試策略概要

| 測試類型 | 對象 | 驗證內容 |
|---------|------|---------|
| **單元測試** | `_extract_date_from_html()` | 各種 HTML 結構的日期擷取正確性 |
| **單元測試** | `_normalize_to_iso8601()` | 各種日期格式的標準化 |
| **單元測試** | `_extract_date()` (MarkdownDateExtractor) | 有/無 `published_date` 時的行為 |
| **整合測試** | `_extract_metadata()` | 傳入 HTML + headers 後 metadata 包含日期 |
| **端到端** | 完整爬蟲流程 | `results.json` 中有有效 `published_date` |

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

> ⚠️ Step 7 前置依賴：重新爬取的結果需寫入多站目錄結構 `data/webpages/nculab/`（而非舊的平坦結構），須等 RunManager Refactor Phase 2 完成後執行。

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

### 問題背景

在測試 csie 網站爬取時，發現 `_filter_crawl_results()` 的去重邏輯使用 `<title>` 標籤作為去重鍵，但 csie 網站所有頁面共用相同的標題，導致多個頁面被誤判為重複而丟棄。

### 解決方案

將去重鍵從 `<title>` 改為 **URL relative path**，透過 TOML 設定 `path_prefix` 指定要截掉的路徑前綴。

> 具體實作、設定檔格式、測試結果等，請參閱 [dev_log.md](dev_log.md) §4。

---

## 11. 實作成果 (2026/08/19)

### 已完成變更

| 檔案 | 變更內容 | 狀態 |
|------|---------|------|
| `website_crawler.py` | 新增 `_extract_date_from_html()` 及 6 個輔助函數；修改 `_extract_metadata()` 簽名加入 `html`/`response_headers` 參數 | ✅ |
| `rag_factory.py` | `_build_file_metadata()` 新增 `published_date` 傳遞 | ✅ |
| `rag_helper.py` | `MarkdownDateExtractor` 新增 Strategy 0：優先使用 HTML metadata 日期 | ✅ |
| `test_html_date_extraction.py` | 35 個單元測試（JSON-LD、OG meta、`<time>` 元素、generic meta、Dublin Core、HTTP Last-Modified、無日期 fallback、損壞 HTML 容錯） | ✅ 35/35 通過 |

### 端到端驗證結果

**nculab（Google Sites）**與**csie（自架 PHP 站）**的所有頁面均無法從 HTML 擷取到日期，`published_date` 和 `modified_date` 皆為 `None`。

根本原因：
- Google Sites 為 SPA 架構，HTML 中完全沒有 JSON-LD、OG meta、`<time>` 元素等結構化日期標籤
- csie 網站同樣無結構化日期標籤，伺服器也不回傳 `Last-Modified` 標頭
- HTML 日期擷取的有效性高度依賴網站平台（WordPress、Medium 等有 SEO 套件的網站才有效）

### 後續建議

針對 nculab 和 csie，應以 **MarkdownDateExtractor 內容推斷**為主要日期來源，而非依賴 HTML 結構化標籤。詳細的替代方法評估請參閱 [alternative_date_methods_evaluation.md](2026_0819-alternative_date_methods_evaluation.md)。
