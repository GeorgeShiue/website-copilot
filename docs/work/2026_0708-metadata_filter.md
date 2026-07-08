# Metadata Filter (2026/07/08)

## 一、網頁爬蟲端的屬性萃取 (Data Extraction)

### 規劃

**目標**：在純文字 Markdown 之外，利用 URL 結構與 HTML 原始碼特徵，精準萃取出可用於分類的結構化標籤。

1. **URL 路徑解析**：這是最穩定、成本最低的分類法。透過解析 URL 的 sub-path 來定義 `page_type`。
   * 例如：包含 `/news` 標記為 `announcement`；包含 `/publication` 或 `/paper` 標記為 `paper`；包含 `/members` 標記為 `personnel`。
2. ~~HTML 標籤萃取 (DOM Parsing)~~ — **已放棄**。目標網站 Google Sites 無標準 `<meta name="date">` 或 `<time datetime>`，BeautifulSoup 等 DOM 解析工具無用武之地。未來若有其他網站源可重新評估。
3. **定義標準輸出 Schema**：確保爬蟲輸出的 `results.json` 中，每一筆資料除了 `content`，都強制包含標準化的 `metadata` 字典（如 `description`、`page_type`）。

### 進度

- **page_type** — 從 URL sub-path 匹配（`/news` → `announcement`、`/members` → `personnel`、`/publication` → `paper` 等），內建於 `_extract_metadata` 中
- **輸出 Schema 重整** — `results.json` 單頁結構拆分為三層：
  - `metadata`：內容屬性（`description`、`page_type`），給 LLM 閱讀 + DB pre-filter
  - `crawl_info`：爬蟲環境（`depth`、`parent_url`），僅供除錯，不進 LlamaIndex
  - top-level：`url`、`fit_markdown`、`images`（`[{url, caption}]`）
- **頁面標題萃取方式變更** — 從原本的 heading regex 改為 `crawl_result.metadata.get("title")`，取 ` - ` 分隔的最後一段作為檔名，更穩定且避免中文 heading 檔名不一致問題
- **日期提取已全面移除** — 歷經以下探索後判定 cost/benefit 不足而放棄：
  - ¹ 嘗試 regex 從 `description`/`title` 提取年份 → 覆蓋率極低（Google Sites 無標準 meta）
  - ² 嘗試多層次 fallback（HTML meta tag → response_headers Last-Modified → URL path）→ 三層全數落空（Google Sites 平台限制）
  - ³ 嘗試 crawl4ai `LLMExtractionStrategy`，每頁以 Gemini 2.5 Flash Lite 判斷發布日期 → **僅 54%（25/46 頁）成功萃取**，其餘頁面無足夠線索。每個頁面花費約 1-2s LLM call，成本與延遲不成比例
  - ❌ **最終決定：2026/7/4 移除整個 LLM 日期萃取機制**
- **方法提取** — 影像 URL 提取獨立為 `_extract_images`；`_filter_crawl_results` 僅負責過濾（404、重複）與頁面標題萃取，`_extract_metadata` 專注 URL-based page_type，符合單一職責原則


## 二、LlamaIndex 節點注入與權限控制 (Data Ingestion)

### 規劃

**目標**：將爬蟲萃取出的標籤（目前僅 `page_type`），無縫綁定到 LlamaIndex 的 `Document` 與切塊後的 `Node` 中，同時避免不必要的標籤浪費大模型的 Token。

1. **載入與綁定**：在讀取 `results.json` 建立 LlamaIndex `Document` 物件時，將爬蟲的 `metadata` 字典傳入 `Document` 的 `metadata` 參數。目前僅有 `page_type` 與 `description` 兩個欄位。
2. **設定 Metadata 可見度 (極度重要)**：LlamaIndex 允許您設定哪些 Metadata 是給「資料庫過濾」用的，哪些是給「LLM 閱讀」用的。
   * **給資料庫用的 (過濾鍵)**：`page_type`（如 `"personnel"`、`"paper"`），這對 LLM 閱讀無意義，建議加入 `excluded_llm_metadata_keys` 中，避免浪費 Token。
   * **給 LLM 閱讀的 (上下文鍵)**：`year`、`month`、`day`（由 `MarkdownDateExtractor` 從 heading / post date / trailing date 萃取），保留給 LLM 閱讀，對理解節點時間背景有助益，不建議排除。
3. **切塊繼承**：執行 Text Splitter 時，確認這些 Metadata 都有正確地被所有子 `Node` 繼承。

> **`year` 替代方案實作歷程**：爬蟲端已放棄日期萃取，後改以 ingestion 階段的 `MarkdownDateExtractor` 自訂 Extractor 從 Markdown 內容補償。詳見下方進度。

### 進度

- **`_file_metadata()` 注入 `page_type` 與 `description`**（2026/7/8）— 從 `results.json` 的巢狀 `metadata` 子物件提取兩個欄位，寫入 Document metadata，再透過 IngestionPipeline 自動繼承給所有 child Node
- **`page_type` 保留給 LLM** — 不設 `excluded_llm_metadata_keys`，因僅 1–3 tokens，且對 `general` 類型邊界案例有助益；反而不建議排除
- **`MarkdownDateExtractor`**（2026/7/8）— 在 `utils/rag_helper.py` 新增，作為 `IngestionPipeline` 中 `SentenceSplitter` 的前置 Extractor，確保 child chunks 繼承日期 metadata。支援四層遞減優先級：

  | 優先 | 策略 | 正則 | 輸出 |
  |:----:|------|------|------|
  | **1** | Section heading 年份 | `### 2026` | `year=2026` |
  | **2** | Post date 行 | `Post date: Feb 15, 2011 3:16:55 AM` | `year=2011, month=2, day=15` |
  | **3** | 列表結尾日期標記 | `— Dec. 5, 2024` | `year=2024, month=12, day=5` |
  | **4** | 內容年份回落 | 第一個 `20\d{2}`（如 `TAAI 2024`） | `year=2024` |

  Pipeline 順序：
  ```
  MarkdownNodeParser
      ↓ 產生 heading-based nodes
  MarkdownDateExtractor   ← HERE
      ↓ 每個 node 帶有 year/month/day metadata
  SentenceSplitter
      ↓ child chunks 自動繼承
  MarkdownHeadingMergeParser
  MarkdownImageExtractor
  ```

## 三、Qdrant 向量庫掛載與檢索過濾 (Retrieval with Pre-filtering)

### 規劃

**目標**：在接收到帶有明確條件的查詢時，透過 LlamaIndex 介面驅動 Qdrant 進行底層的硬性篩選。

1. **Filter 參數設計**：`build_retriever()` 接受 `filters_dict: list[dict[str, str]] | None`，每個 dict 包含 `key` 與 `value`。內部自動轉換為 `MetadataFilters` 與 `ExactMatchFilter` 物件，傳入 `VectorIndexRetriever`。
   * 例：`filters_dict=[{"key": "page_type", "value": "paper"}]`
   * 支援多條件：`filters_dict=[{"key": "page_type", "value": "paper"}, {"key": "year", "value": "2024"}]`
   * **日期範圍查詢**：`MetadataFilter` 支援 `FilterOperator`（`GTE`、`LTE`、`GT`、`LT`、`IN` 等），可對整數型 `year`/`month`/`day` 進行範圍篩選。
     * 例：`year >= 2024` → `MetadataFilter(key="year", value=2024, operator=FilterOperator.GTE)`
     * 例：`year IN [2023, 2024, 2025]` → `MetadataFilter(key="year", value=[2023, 2024, 2025], operator=FilterOperator.IN)`
2. ~~搜尋封裝函數~~ — **已放棄**。Filter 是 `build_retriever()` 的參數，不是 `query()` 的參數。Agent 只需在呼叫 `build_retriever()` 時傳入 `filters_dict`，`query()` 完全不需要知道 filter 的存在。
3. ~~`build_retrieval_engine()` 合併方法~~ — **已放棄**。維持既有 `build_retriever()` + `build_query_engine()` 二階段呼叫，filter 只存在於 retriever 層級。
4. **重要結論**：LlamaIndex 的 `RetrieverQueryEngine` 不需要知道 filter 的存在。只要 retriever 帶有 filters，query engine 在內部呼叫 `retriever.retrieve()` 時就會自動套用 Qdrant 端的 pre-filter。

### 進度

- **`build_retriever()` 支援 `filters_dict`**（2026/7/8）— 參數從 `filters: MetadataFilters | None` 改為 `filters_dict: list[dict[str, str]] | None`，內部自動轉換為 `MetadataFilters`。保留 `ExactMatchFilter` 供未來擴充
- **`query()` 維持不變** — 不移入 filter 邏輯、不重建 retriever/query engine。Agent 使用流程為：`build_retriever(filters_dict=...)` → `build_query_engine()` → `query()`
- **`page_type` 僅是 filter key 之一** — 不設專用參數，所有 filter 條件統一透過 `filters_dict` 傳入
- **日期範圍查詢就緒**（2026/7/8）— `MetadataFilter` 底層支援 `FilterOperator.GTE` / `LTE` / `GT` / `LT` / `IN`，可對 `year` 做數值範圍篩選。惟 `build_retriever()` 預設使用 `EQ` 比對，若要啟用 `GTE` 等範圍操作，需手動建構 `MetadataFilter(key="year", value=2024, operator=FilterOperator.GTE)` 傳入。使用範例：

  ```python
  from llama_index.core.vector_stores import MetadataFilter, FilterOperator

  # year >= 2024 且 page_type == "paper"
  rag.build_retriever(
      top_k=10,
      filter_dict={
          "page_type": "paper",
          "year": 2024,
          # 注意：預設為 EQ，範圍查詢需手動建構 MetadataFilter
      },
  )
  ```

## 四、孤立驗證與邊界測試 (Validation)

**目標**：在進入下一階段（混合檢索與重排序）之前，確認預篩選機制 100% 生效。

1. ~~防漏測試 (Recall Check)~~ — **可執行**。此測試需 `page_type` + `year` 雙重 filter 才能驗證召回完整性。`MarkdownDateExtractor` 已實作 node-level 日期萃取，可設定 `page_type="paper"` + `year >= 2024`，確認所有回傳節點皆有 `year >= 2024` 且無遺漏。
2. **防穿透測試 (Isolation Check)**（可立即執行）：設定 `filters` 為 `page_type = "announcement"`，但強行在 Query 中搜尋「只有在論文區才有的專有名詞」。

* **預期結果**：系統應該回傳「查無資料」或空陣列，因為 Qdrant 的預篩選已經把論文區的資料隔絕在外。如果這時候還能撈到論文區的資料，代表 Metadata 注入或過濾器設定有瑕疵，必須回頭除錯。
