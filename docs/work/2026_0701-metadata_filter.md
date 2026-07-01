# Metadata Filter (2026/07/01)

## 一、網頁爬蟲端的屬性萃取 (Data Extraction)

**目標**：在純文字 Markdown 之外，利用 URL 結構與 HTML 原始碼特徵，精準萃取出可用於分類的結構化標籤。

1. **URL 路徑解析**：這是最穩定、成本最低的分類法。透過解析 URL 的 sub-path 來定義 `page_type`。
   * 例如：包含 `/news/` 標記為 `announcement`；包含 `/publications/` 標記為 `paper`；包含 `/members/` 標記為 `personnel`。
2. **HTML 標籤萃取 (DOM Parsing)**：針對時間或特定屬性，使用 BeautifulSoup 等工具抓取隱藏標籤。
   * 抓取 `<meta name="date" content="...">` 或 `<time datetime="...">` 來精確提取 `year`。
   * 抓取網頁的麵包屑 (Breadcrumbs) 作為階層分類的備用依據。
3. **定義標準輸出 Schema**：確保爬蟲輸出的 `results.json` 中，每一筆資料除了 `content`，都強制包含標準化的 `metadata` 字典（如 `url`, `title`, `page_type`, `year`）。

## 二、LlamaIndex 節點注入與權限控制 (Data Ingestion)

**目標**：將爬蟲萃取出的標籤，無縫綁定到 LlamaIndex 的 `Document` 與切塊後的 `Node` 中，同時避免不必要的標籤浪費大模型的 Token。

1. **載入與綁定**：在讀取 `results.json` 建立 LlamaIndex `Document` 物件時，將字典直接塞入 `metadata` 參數中。
2. **設定 Metadata 可見度 (極度重要)**：LlamaIndex 允許您設定哪些 Metadata 是給「資料庫過濾」用的，哪些是給「LLM 閱讀」用的。
   * **給資料庫用的 (過濾鍵)**：例如 `page_type` 的內部代號（如 `doc_type_01`），這對 LLM 沒意義，請將其加入 `excluded_llm_metadata_keys` 中，LLM 就不會看到它。
   * **給 LLM 閱讀的 (上下文鍵)**：例如 `year` 或 `title`，這能幫助 LLM 了解當前段落的時空背景，請保留在 `Document` 的預設可見範圍內。
3. **切塊繼承**：執行 Text Splitter 時，確認這些 Metadata 都有正確地被所有子 `Node` 繼承。

## 三、Qdrant 向量庫掛載與檢索過濾 (Retrieval with Pre-filtering)

**目標**：在接收到帶有明確條件的查詢時，透過 LlamaIndex 介面驅動 Qdrant 進行底層的硬性篩選。

1. **建構 MetadataFilters 物件**：在呼叫 Retriever 之前，根據查詢需求動態組裝過濾條件。
   * 使用 `ExactMatchFilter` 處理絕對分類（例：`key="page_type", value="paper"`）。
   * 使用 `MetadataFilter` 配合運算子處理範圍（例：尋找 `key="year", operator=">=", value=2024`）。
2. **套用至 Retriever**：將組裝好的 `MetadataFilters` 物件傳入 `VectorIndexRetriever` 的 `filters` 參數中。
3. **封裝檢索介面**：寫一個 Python 封裝函數（例如 `search_with_filters(query, type=None, year=None)`），讓這個 Retriever 具備接收外部參數的能力，這是為了未來銜接 Agent 路由做準備。

## 四、孤立驗證與邊界測試 (Validation)

**目標**：在進入下一階段（混合檢索與重排序）之前，確認預篩選機制 100% 生效。

1. **防漏測試 (Recall Check)**：設定 `filters` 為特定年份的論文，查詢一組必然存在於該年份的生僻詞彙，確認是否能順利召回。
2. **防穿透測試 (Isolation Check)**：設定 `filters` 為「最新消息 (news)」，但強行在 Query 中搜尋「只有在論文區才有的專有名詞」。

* **預期結果**：系統應該回傳「查無資料」或空陣列，因為 Qdrant 的預篩選已經把論文區的資料隔絕在外。如果這時候還能撈到論文區的資料，代表 Metadata 注入或過濾器設定有瑕疵，必須回頭除錯。
