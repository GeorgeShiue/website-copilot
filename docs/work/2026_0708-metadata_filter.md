# Metadata Filter (2026/07/08)

## 待辦事項
- [x] 一、網頁爬蟲端的屬性萃取 (Data Extraction)
- [x] 二、LlamaIndex 節點注入與權限控制 (Data Ingestion)
- [x] 三、Qdrant 向量庫掛載與檢索過濾 (Retrieval with Pre-filtering)
- [x] 四、孤立驗證與邊界測試 (Validation)

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

1. **Filter 參數設計**：`build_retriever()` 接受 `filter_dict: dict[str, str | int] | None`，內部自動轉換為 `MetadataFilters` 與 `ExactMatchFilter` 物件，傳入 `VectorIndexRetriever`。
   * 例：`filter_dict={"page_type": "paper"}`
   * 支援多條件：`filter_dict={"page_type": "paper", "year": 2024}`
   * **⚠️ 已知侷限**：`build_retriever()` 目前僅支援 `EQ` 比對。範圍查詢（如 `year >= 2024`）需直接操作底層 `VectorIndexRetriever` + `MetadataFilter(key="year", value=2024, operator=FilterOperator.GTE)`。
2. ~~搜尋封裝函數~~ — **已放棄**。Filter 是 `build_retriever()` 的參數，不是 `query()` 的參數。Agent 只需在呼叫 `build_retriever()` 時傳入 `filters_dict`，`query()` 完全不需要知道 filter 的存在。
3. ~~`build_retrieval_engine()` 合併方法~~ — **已放棄**。維持既有 `build_retriever()` + `build_query_engine()` 二階段呼叫，filter 只存在於 retriever 層級。
4. **重要結論**：LlamaIndex 的 `RetrieverQueryEngine` 不需要知道 filter 的存在。只要 retriever 帶有 filters，query engine 在內部呼叫 `retriever.retrieve()` 時就會自動套用 Qdrant 端的 pre-filter。

### 進度

- **`build_retriever()` 支援 `filter_dict`**（2026/7/8）— 參數從 `filters: MetadataFilters | None` 改為 `filter_dict: dict[str, str | int] | None`，內部自動轉換為 `MetadataFilters`。所有條件皆使用 `EQ` 比對。
- **`query()` 維持不變** — 不移入 filter 邏輯、不重建 retriever/query engine。Agent 使用流程為：`build_retriever(filter_dict=...)` → `build_query_engine()` → `query()`
- **`page_type` 僅是 filter key 之一** — 不設專用參數，所有 filter 條件統一透過 `filter_dict` 傳入
- **日期範圍查詢標註為已知侷限** — `build_retriever()` 僅支援 EQ。若要 `year >= 2024` + `page_type == "paper"`，需直接操作底層 `VectorIndexRetriever` + `MetadataFilters`。

## 四、孤立驗證與邊界測試 (Validation)

**目標**：在進入下一階段（混合檢索與重排序）之前，確認預篩選機制 100% 生效。

> **🚨 設計修正**：驗證斷言不預期「穿透測試回空」，而是「所有回傳節點的 metadata 皆符合 filter 條件」。announcement 頁面可能包含論文關鍵字（如「賀！XXX 論文獲獎」），非空結果不代表 filter 失效。

### 規劃測試項目

| Phase | 測試類別 | 測試內容 | 核心斷言 |
|:-----:|----------|----------|----------|
| **1** | Metadata 注入完整性 | page_type 傳播、日期萃取四策略、description 完整性 | node metadata 與 `results.json` 一致 |
| **2** | Pre-filter 隔離正確性 | 單一 page_type / year filter、複合 filter | `∀ node → metadata[key] == value` |
| **3** | 穿透測試 | announcement filter + 論文術語；paper filter + 公告術語 | `∀ node → page_type 符合 filter` |
| **4** | 召回完整性 | paper / personnel 召回 | 回傳頁面涵蓋已知目標頁面 |
| **5** | 邊界案例 | 不存在的 page_type、None filter | 0 結果 / 退回無 filter |
| **6** | Q5 回歸測試 | `page_type=paper` + 論文年限查詢 | 無 leakage + 有召回 + Relevancy PASS |
| **7** | 實作 | `test/test_metadata_filter.py`，6 類別 20 項測試 | `pytest -v` 全部通過 |

### 測試執行結果

```
======================== 20 passed in 32.84s ========================
```

| Phase | 測試類別 | 結果 | 備註 |
|:-----:|----------|:----:|------|
| **1** | `TestMetadataInjection` | ✅ 6/6 | Advisor 實際為 `general`（爬蟲未 map `/advisor`→`personnel`）|
| **2** | `TestFilterIsolation` | ✅ 5/5 | 含 parametrize 四種 page_type、year、複合 filter |
| **3** | `TestFilterPenetration` | ✅ 2/2 | 雙向穿透確認 filter 依 metadata 而非語義 |
| **4** | `TestRecallCompleteness` | ✅ 2/2 | Paper 召回需 `cutoff=0.0` 避免誤殺（score 僅 0.37–0.38）|
| **5** | `TestEdgeCases` | ✅ 2/2 | 不存在 filter 回 0 筆；None filter 退化正常 |
| **6** | `TestRegression` | ✅ 3/3 | Q5 無 leakage + 有關聯性 → **原始動機驗證通過** |

### 測試重要發現

**測試套件：** `test/test_metadata_filter.py` — 6 類別 20 項測試全部通過（32.84s）

| 發現 | 說明 | 影響 |
|------|------|------|
| **Q5 回歸問題已解決** | 先前 `cutoff=0.4` + `top_k=10` 時，Q5 查詢「實驗室近三年發表過哪些論文？」因混入大量獎項與公告頁面，Relevancy evaluator 判定 **0%**。加入 `page_type=paper` filter 後，Qdrant pre-filter 在向量搜尋前就隔絕所有非 paper 節點，LLM 只看得到 Publication / Publication by Year / Thesis Advised 三頁的 chunks。Relevancy 判定為 **PASSING**。 | ✅ **原始動機驗證通過**。下一階段混合檢索的 filter 設計可直接沿用此機制。 |
| **Paper 節點向量相似度偏低** | Publication 三頁的 chunks 與一般查詢語句的 cosine similarity 僅 **0.37–0.38**，遠低於其他類型的節點（personnel 約 0.45–0.55，announcement 約 0.42–0.52）。預設 `cutoff=0.45` 在測試中導致 **query engine 回傳 Empty Response**，所有 paper 節點被相似度後處理器誤殺。 | ⚠️ **對混合檢索架構有直接設計意涵**：(1) Vector search 階段應使用低 cutoff（`0.0`）或乾脆禁用 cutoff，靠 filter 保證 metadata 正確性；(2) 須引入 BM25 稀疏檢索補償語義向量的不足；(3) 最終用 cross-encoder reranker 做二次排序，而非仰賴一次性的向量相似度截斷。 |
| **Crawler URL→page_type mapping 有 gap** | `_extract_metadata()` 目前僅處理 `/news`→`announcement`、`/publication`→`paper`、`/members`→`personnel` 三條路徑。`/advisor` 未列入 mapping 表，導致 Advisor 頁面被歸類為 `general`。若未來加入 `/labintro`、`/projects`、`/news/activities` 等路徑，需一併確認。 | 修復成本極低（一行 URL pattern），但若不及時修正，`personnel` 類別的召回完整性會長期缺漏 Advisor 內容。建議在 `_extract_metadata()` 中補上 `/advisor`，或將 mapping table 抽取為可設定的規則檔。 |
| **日期萃取四層策略皆正確觸發** | `MarkdownDateExtractor` 的四層遞減策略在測試中全數驗證通過：(1) heading 年份（`### 2026`→`year=2026`），(2) Post date 行（`Post date: Jul 20, 2015`→完整年月日），(3) trailing date（`— Dec. 10, 2022`→完整年月日），(4) 內容 fallback（內文 `20\d{2}`→`year=2026`）。無日期線索的頁面（實驗室首頁、專案頁）確實無 `year` metadata。 | 可放心用於實際 pipeline。注意 heading 策略最寬鬆（任何 `### 20xx` 都會觸發），若擔心誤判可考慮加入數值範圍驗證（如侷限 2000–2030）。 |
| **`build_retriever()` 高層 API 僅支援 EQ** | `build_retriever(filter_dict=...)` 內部將所有條件以 `MetadataFilter(key=..., value=..., operator=FilterOperator.EQ)` 處理。若要 `year >= 2024` 或 `year IN [2023, 2024]` 等範圍查詢，需繞過此方法，直接操作 `VectorIndexRetriever(index=..., filters=MetadataFilters(filters=[...]))` 並手動指定 `FilterOperator`。 | 短期內 EQ 已滿足大部分使用場景（`page_type` 篩選、特定年份篩選）。若未來 Agent 需要「近三年論文」這類動態範圍查詢，建議擴充 `build_retriever()` 或提供一個底層 helper 函數。 |

