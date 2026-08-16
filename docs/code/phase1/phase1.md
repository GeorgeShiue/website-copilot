# Survey
> [docs/code/phase1/survey/data_process_method.md](survey/data_process_method.md)

# 1. 資料獲取
> [docs/code/phase1/modules/data_collect.md](modules/data_collect.md)

## 實作進度
- [x] **網站爬蟲**
    - [x] **網頁轉Markdown**
    - [x] **篩選網域**、**雜訊**
    - [x] **平行處理**

## 已知問題
- [ ] **HTML** 可包含更多**結構化資訊**

## 未來規劃
- [ ] 爬取**網站地圖**
- [ ] 讀取網站**後端資料庫**

# 2. 資料前處理
> [docs/code/phase1/modules/data_preprocess.md](modules/data_preprocess.md)

## 實作進度
- [x] **圖片處理**
	- [x] **下載圖片**
	- [x] **VLM 摘要圖片資訊**
	- [x] **平行處理**、**快取**
	- [x] **自動重試**
	- [x] **VLM Prompt 調整**
		- [x] **prompt-v1**
		- [x] **prompt-v2**
		- [x] **prompt-v3**
    - [ ] **下載和摘要拆成兩個模組**

## 已知問題
- [ ] **圖片摘要**可能喪失資訊
    1. 將圖片加入**多模態RAG**
    2. 保留**原始圖片**給**Agent**

## 未來規劃
- [ ] **表格處理**（對應多欄位→資料庫策略）
- [ ] **文件處理**（對應長文本→RAG 策略延伸）

# 3. 資料查詢 (當前進度)
> [docs/code/phase1/modules/data_retrieve.md](modules/data_retrieve.md)

## 實作進度
- [x] **RAG 檢索-長文本資料**
    - [x] **載入資料**（SimpleDirectoryReader + results.json）
    - [x] **轉換資料**（MarkdownNodeParser / SentenceSplitter / MarkdownHeadingMergeParser / MarkdownImageExtractor）
    - [x] **向量索引**（OpenAI **text-embedding-3-small** + **Qdrant** / **Milvus** 本地持久化）
    - [x] **Metadata Filter**（爬蟲 URL 解析 `page_type`；`MarkdownDateExtractor` 自內容萃取 `year`/`month`/`day`，注入節點 metadata 供檢索前過濾）
    - [x] **Metadata 時間範圍過濾**（以 `filter_dict={"year": (2024, ">=")}` 等條件進行時間區間過濾）
    - [x] **Hybrid Search**（**Milvus BGE-M3** 或 **Qdrant BM25** 稠密稀疏雙軌檢索，WeightedRanker / RRFRanker 融合）
    - [x] **查詢引擎**（RetrieverQueryEngine + **Gemini** / **GPT** 回答生成）
    - [x] **RAG Retriever Tool**（LangChain `StructuredTool` 封裝，供 Agent 動態呼叫）
    - [x] **成效評估**（FaithfulnessEvaluator + RelevancyEvaluator）
    - [x] **Query 結果落盤**（結構化 `results.json` + 每次 query 一份 `results/query_{index}.md`）
    - [x] **向量庫存至 run 內**（`save_vector_store_to_runs`，避免實驗互相覆寫 `data/rag/results/`）
- [ ] **知識圖譜檢索（網站結構）** — 規劃中
- [ ] **資料庫檢索（多欄位資料）** — 規劃中

## 已知問題
- [ ] **特定頁面類型需依靠 Metadata Filter**：部分頁面類型（如論文）語意相似度不足，若無 metadata filter 輔助，Dense Search 可能完全召回不到；需仰賴 Agent 在查詢意圖判斷後主動傳入 `filter_dict` 參數。
- [ ] **日期萃取依賴內容格式**：時間 metadata 由 `MarkdownDateExtractor` 依內容中的日期樣式推斷（含「內容年份回落」），若頁面無明顯日期資訊，萃取結果可能不精確。

## 未來規劃
- [ ] **資料類型分類器**：判斷查詢/資料類型，自動路由至適當檢索策略
- [ ] **知識圖譜檢索工具**：處理網站結構與頁面關聯性查詢
- [ ] **資料庫檢索工具**：處理表格與多欄位結構化資料
