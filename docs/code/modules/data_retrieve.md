# RAG 檢索-長文本資料

## 模組總覽
此模組實作**多策略知識庫中的 RAG 路徑**。針對長文本類型的網頁內容（文章、公告、部落格），將爬蟲產生的 Markdown 經過**解析**、**切塊**與**嵌入**後存入 **Qdrant** 或 **Milvus** 向量資料庫，再以**語意檢索**（Dense）與**關鍵字檢索**（Sparse/Hybrid）找出最相關段落，由 **LLM** 生成回答。

流程包含**索引建構**、**查詢引擎設定**與**成效評估**，形成完整的 RAG 管線。進階功能包含：

- **Metadata Filter** — 從爬蟲 URL 解析出 `page_type`（paper / announcement / personnel），注入節點 metadata 以供檢索前過濾
- **Hybrid Search** — 透過 Milvus BGE-M3 或 Qdrant BM25 進行稠密+稀疏雙軌檢索，以 WeightedRanker 或 RRFRanker 融合分數
- **RAG Retriever Tool** — 將檢索能力包裝為 LangChain `StructuredTool`，供下游 Agent 動態呼叫

與此並行的尚有**知識圖譜檢索（網站結構）**、**資料庫檢索（多欄位資料）** 兩條策略路徑，依資料類型分流選用。

- **模組實作**
	- `src/app/modules/rag.py`（**runtime 執行**：`query`、`retrieve`、`evaluate` 與資源釋放）
	- `src/app/modules/rag_factory.py`（**建構流程**：`RAGBuilder` 編排 + `NodePipelineBuilder` / `VectorStoreBuilder`）
	- `src/app/modules/rag_eval_prompts.py`（**評估 Prompt 模板**：Faithfulness / Relevancy 的 eval 與 refine）
	- `src/app/configs/rag_config.py`（**設定載入**、**驗證**、**覆寫**與 **API key 推斷**）
	- `src/utils/rag_helper.py`（**自訂 Markdown Parser**、**圖片萃取**、**格式化工具**、共用 `build_filters` / `create_llm`，與 **Query 結果序列化** `extract_sources_list` / `evaluation_result_to_dict` / `response_to_dict`）
	- `src/app/tools/webpage_retriever.py`（**RAG Retriever Tool** — 將 retriever 包裝為 LangChain `StructuredTool`）

- **模組設定**
	- `./configs/rag/{name}.toml`（**檢索設定檔**，透過 `src/app/configs/rag_config.py` 載入）
	- 可在 `RagConfig` 或執行參數中覆寫 **embedding**、**vector store 類型**、**hybrid ranker**、**chunk 參數**、**檢索設定**與 **LLM 模型**
	- API key 依用途分為三組獨立環境變數：`OPENAI_RAG_EMBEDDING_API_KEY`（Embedding）、`GEMINI_RAG_QUERY_ENGINE_API_KEY` / `OPENAI_RAG_QUERY_ENGINE_API_KEY`（查詢引擎）、`GEMINI_RAG_EVALUATOR_API_KEY` / `OPENAI_RAG_EVALUATOR_API_KEY`（評估）

- **模組環境**
	- `Python >= 3.10`（程式使用**現代型別語法**如 `Sequence[BaseNode]`）
	- **標準函式庫**：`json`、`os`、`shutil`、`logging`
	- **第三方套件**：`llama-index`（**核心檢索框架**）、`qdrant-client` / `pymilvus`（**向量資料庫**）、`llama-index-vector-stores-milvus`（**Milvus 整合**）、`llama-index-embeddings-openai`（**OpenAI Embedding**）、`llama-index-llms-google-genai` / `llama-index-llms-openai`（**查詢與評估 LLM**）、`langchain-core`（**StructuredTool**）

## rag.py

`Rag` 類別封裝了向量資料庫的完整生命週期，從初始化、建構到查詢與評估，各步驟有嚴格的呼叫順序。

### 使用流程總覽

```
RAGBuilder(config)
├── build_nodes()            # (1) 讀取 Markdown → Pipeline 產出節點
├── build_vector_store()     # (2) 建立向量儲存（Qdrant / Milvus，支援 Hybrid）
│   └── load_index()         # (3a) 既有向量庫直接載入（跳過 build_nodes/build_index）
│   └── build_index()        # (3b) 從 nodes 新建索引並寫入向量庫
├── build_retriever()        # (4) 建立檢索器（支援 filter_dict 動態過濾）
├── build_query_engine()     # (5) 建立查詢引擎
└── build_reusable()         # 依需求自動選擇「重建」或「載入」路徑（run_rag_query 使用）

RAG（runtime）
├── query() / evaluate()     # (6) 執行查詢與評估
├── retrieve()               # (7) 僅檢索不回覆（回傳結構化 dict，供 Tool 使用）
└── close()                  # (8) 釋放資源
```

其中 (1) → (3b) 用於首次建立索引，(3a) 則用於後續重複使用。

---

### 1. 載入資料

#### 初始化與 results.json
- 建構子會自動讀取 `{webpages_data_folder_path}/results.json`（由爬蟲產生的網頁清單），若檔案不存在則直接拋出 `FileNotFoundError`。
- `results.json` 的 key 為網頁標題（去除 `.md` 副檔名），value 包含 `url`、`metadata`（含 `page_type`、`description`）、`images`、`crawl_info` 等資訊。

#### 讀取 Markdown 文件
- `RAGBuilder.build_nodes()` 使用 LlamaIndex 的 `SimpleDirectoryReader` 讀取 `{webpages_data_folder_path}/results`。
- 只處理副檔名為 `.md` 的檔案，確保輸入內容來自爬蟲生成的 Markdown 成果。
- 透過 `NodePipelineBuilder._build_file_metadata()` 回呼函式，根據 `results.json` 為每份文件注入以下 metadata：
  - `page_title` — 頁面標題
  - `page_url` — 原始 URL
  - `page_type` — 頁面類型（爬蟲從 URL 解析：`"paper"` / `"announcement"` / `"personnel"` / `"general"` 等）
  - `description` — 頁面描述
  - `year` / `month` / `day` — 由管線中的 `MarkdownDateExtractor` 依內容萃取，支援時間範圍過濾（見下方「轉換資料」）

這些 metadata 在 `RAGBuilder.build_nodes()` 階段即寫入每個 LlamaIndex Document，後續經由 IngestionPipeline 傳遞給 child nodes，最終持久化到向量儲存中，同時供 **pre-filtering**（檢索前過濾）與 **LLM context**（檢索後附加上下文）使用。

---

### 2. 轉換資料

`RAGBuilder.build_nodes()` 內部使用 `IngestionPipeline` 依序執行以下轉換：

1. **`MarkdownNodeParser`** — 解析 Markdown 結構，保留標題路徑 metadata。
2. **`MarkdownDateExtractor`**（自訂）— 從節點內容萃取 `year` / `month` / `day` 寫入 metadata（四層遞減優先：section heading 年份 → `Post date` 行 → 列表結尾日期標記 → 內容年份回落），需置於 `SentenceSplitter` 之前讓 child chunks 繼承日期 metadata。
3. **`SentenceSplitter`** — 以 `chunk_size=800`、`chunk_overlap=100`、`paragraph_separator="\n\n"` 進行切塊，這組參數目前表現最平衡。
4. **`MarkdownHeadingMergeParser`**（自訂）— 把純標題節點併入下一個有實質內容的節點，避免空洞的標題節點。
5. **`MarkdownImageExtractor`**（自訂）— 將 Markdown 圖片抽出到 `metadata["images"]`，並把內容中的圖片標記替換成 `alt` 文字。

這樣可讓圖片摘要、OCR 與頁面關聯保留在同一個 Node 中，避免資訊斷裂。

---

### 3. 建立索引

#### 3a. 建立向量儲存（必要前驟）
`RAGBuilder.build_vector_store()` 支援兩種向量儲存後端，透過 `vector_store_type` 切換：

**Qdrant（純 BM25 Hybrid）**
- 以 `QdrantClient(path=qdrant_db_folder_path)` 初始化，`QdrantVectorStore(collection_name, client, index_doc_id=False, enable_hybrid=True, fastembed_sparse_model="Qdrant/bm25")`。
- 集合名稱預設 `webpages`，持久化路徑預設 `data/rag/results/qdrant_db`。
- Dense + Sparse 融合使用加權公式：`score = alpha × dense + (1-alpha) × sparse`。

**Milvus（BGE-M3 Hybrid）**
- 以 `MilvusVectorStore(milvus_uri, collection_name, enable_sparse=True, sparse_embedding_function=BGEM3SparseEmbeddingFunction())` 初始化。
- Sparse 編碼使用 `BAAI/bge-m3` 神經稀疏模型，**原生支援中文**。
- 融合演算法可選：
  - `RRFRanker`（預設參數 `k=60`）：只看排名 `score = 1/(k+rank_dense) + 1/(k+rank_sparse)`
  - `WeightedRanker`（預設權重 `[1.0, 0.5]`）：加權原始分數 `score = w_dense × dense_score + w_sparse × sparse_score`
- 須明確指定 `output_fields=["_node_content", "_node_type"]` 確保節點完整回傳。

#### 3b. 載入或新建索引
- **既有資料庫載入**：`RAGBuilder.load_index()` 使用 `VectorStoreIndex.from_vector_store(vector_store, embed_model)`，僅需提供 embedding 模型。
- **新建索引**：`RAGBuilder.build_index()` 需先完成 `build_nodes()` 產出 `rag.nodes`，再以 `VectorStoreIndex(nodes, storage_context, embed_model)` 寫入向量庫。

#### Embedding 設定
- 使用 `OpenAIEmbedding(model="text-embedding-3-small", embed_batch_size=256)`，並透過 `.env` 讀取 `OPENAI_RAG_EMBEDDING_API_KEY`。

---

### 4. 查詢引擎

#### 檢索器
`RAGBuilder.build_retriever()` 建立 `VectorIndexRetriever`，支援以下參數：

- `query_mode`：`"default"`（純 Dense）或 `"hybrid"`（Dense + Sparse 混合）。Hybrid 模式會設定 `vector_store_query_mode=VectorStoreQueryMode.HYBRID`。
- `similarity_top_k`：回傳的前 k 筆結果（預設 `10`）。
- `hybrid_top_k`：Hybrid 模式下各通道（dense/sparse）各自取前 k 筆再融合（預設 `10`）。
- `alpha`：Qdrant Hybrid 模式下 dense 與 sparse 的加權係數（預設 `0.5`）。
- `filter_dict`：**可選的 metadata 過濾條件**，支援動態傳入。例如：
  - `{"page_type": "paper"}` — 只回傳論文頁面
  - `{"page_type": (["paper", "announcement"], "in")}` — 論文或公告
  - `{"year": (2024, ">=")}` — 年份 ≥ 2024

若未傳入 `filter_dict`，沿用既有 retriever 的 filter 設定（若無則不過濾）。

#### 查詢引擎
`RAGBuilder.build_query_engine()` 將檢索器、回應合成器與後處理器串接成 `RetrieverQueryEngine`。

- **Hybrid 模式**：跳過 `SimilarityPostprocessor`，因為 hybrid 分數已由 ranker 融合，不再適用 similarity cutoff。
- **Dense 模式**：加入 `SimilarityPostprocessor(similarity_cutoff=cutoff)`（預設 `cutoff=0.0`，通常設定 `0.4`）。
- 查詢 LLM 使用 `GoogleGenAI(model="gemini-3.1-flash-lite")`，API key 來自 `GEMINI_RAG_QUERY_ENGINE_API_KEY`（若使用 GPT 系列則來自 `OPENAI_RAG_QUERY_ENGINE_API_KEY`）。
- 回答生成器使用 `get_response_synthesizer(llm=llm)`。

#### 執行查詢
- `query(query, log_sources=False)` 將字串查詢送入查詢引擎，回傳 `Response` 物件。
- 設 `log_sources=True` 時以 `_log_sources()` 輸出檢索到的來源節點摘要（含 `page_title`、`score`、`page_type`、內容片段）。

#### 僅檢索不回覆
- `retrieve(query, filter_dict=None, similarity_top_k=None)` 是 `query()` 的輕量版，不回傳 LLM 生成結果。
- 回傳結構化 `list[dict]`（`page_title`、`score`、`page_type`、`content`、`url`），而非 LlamaIndex 的 `NodeWithScore`，便於序列化與工具層使用。
- 支援執行期動態 `filter_dict` 與 `similarity_top_k` 覆寫（暫時重建 retriever）。

---

### 5. 成效評估

`evaluate(query, response)` 使用兩項指標評估查詢結果（Prompt 模板定義於 `app/modules/rag_eval_prompts.py`）：

#### Faithfulness（忠實度）
- `FaithfulnessEvaluator` 搭配自訂 `FAITHFULNESS_EVAL_TEMPLATE` 與 `FAITHFULNESS_REFINE_TEMPLATE`。
- 判斷回應內容是否被檢索到的 context 所支持，輸出 YES/NO 加上繁體中文原因。

#### Relevancy（相關性）
- `RelevancyEvaluator` 搭配自訂 `RELEVANCY_EVAL_TEMPLATE` 與 `RELEVANCY_REFINE_TEMPLATE`。
- 判斷查詢與回應是否與 context 一致，輸出 YES/NO 加上繁體中文原因。

#### Evaluator LLM
- 預設使用 `gpt-5.4`（因 `gemini-3.1-pro-preview` 每日限額太低）。
- API key 來自 `GEMINI_RAG_EVALUATOR_API_KEY`（Gemini）或 `OPENAI_RAG_EVALUATOR_API_KEY`（GPT）。

---

### 6. Metadata Filter（頁面類型過濾）

Metadata filter 允許在檢索前預先隔離跨類別雜訊，避免語義重疊導致的幻覺。

#### 過濾機制
- `RAGBuilder.build_retriever(filter_dict=...)` 在建置檢索器時即設定過濾條件。
- `retrieve(filter_dict=...)` 支援**執行期動態覆寫**，暫時重建 retriever 以套用新 filter。
- filter_dict 支援 `FilterOperator`：`EQ`（等於）、`GT` / `GTE` / `LT` / `LTE`（比較）、`IN`（包含）、`TEXT_MATCH`（文字匹配）。

#### 效果
- **無 filter**：Top-10 可能混入 personnel pages（Score 0.95–0.98），論文頁面（Score 0.62–0.63）被淹沒。
- **加 filter** `{"page_type": "paper"}`：Top-10 100% 為論文頁面，Faithfulness 100%。

---

### 7. Hybrid Search（混合檢索）

Hybrid Search 同時以 Dense Vector 與 Sparse Vector 檢索，再將兩者分數融合排序，補回低語義相似度但高關鍵字匹配的節點。

#### Vector Store 對照

| Vector Store | Sparse Model | 中文支援 | 融合演算法 |
|---|---|---|---|
| **Qdrant** | `Qdrant/bm25`（純 BM25） | ❌ 不支援 | Weighted: `alpha × dense + (1-alpha) × sparse` |
| **Milvus** | `BAAI/bge-m3`（神經稀疏編碼） | ✅ 原生支援 | RRF → WeightedRanker（`w_d × dense + w_s × sparse`） |

#### 使用時機
- Dense Search 設定的 `cutoff` 排除所有低分節點（如 paper 節點分數 0.37–0.38）時，Hybrid Search 可透過關鍵字匹配補回。
- 建議同時搭配 Metadata Filter 使用，避免 Hybrid 拉回不相關的跨類型頁面。

---

## webpage_retriever.py

將 RAG retriever 包裝為 LangChain `StructuredTool`，使下游 Agent 可直接呼叫檢索。

### RetrieverInputSchema
Pydantic v2 schema，定義三個參數供 LLM 填寫：
- `query`：搜尋查詢字串
- `filter_dict`：可選的 metadata 過濾條件（範例：`{"page_type": "paper"}`）
- `similarity_top_k`：回傳數量上限

### create_webpage_retriever_tool()
高層工廠函數，接受 `run_manager`（可選）、`config_name`、`run_name_use_config_name` 與 `**config_overrides`，流程：
1. 載入 TOML 設定 → 建立 `RunManager` 並初始化 run 路徑
2. 呼叫 `RAGBuilder(config).build_to_retriever()`（建立 Nodes → Vector Store → Index → Retriever，**不建 Query Engine**）
3. 包裝為 `StructuredTool(name="webpage_retriever")`
4. 將 RAG 實例綁定為 `tool.rag` 屬性（結束後呼叫 `tool.rag.close()` 釋放資源）
5. 在 run 路徑寫出 `module_config.toml`（與其他 workflow 一致的留檔行為）

### 使用方式
```python
tool = create_webpage_retriever_tool()  # config_name 預設 "default"（Milvus hybrid）
agent = create_agent(model, [tool])
# Agent 執行期間自主呼叫 tool(retriever_input)
tool.rag.close()  # 釋放向量儲存資源
```

---

## 未來規劃
- [ ] **知識圖譜檢索工具**：處理網站結構與頁面關聯性查詢
- [ ] **資料庫檢索工具**：處理表格與多欄位結構化資料
- [ ] **資料類型分流路由**：統一入口自動判斷查詢類型，導向對應策略路徑
