# 向量資料庫檢索

## 模組總覽
此模組以**向量檢索**為核心，將爬蟲產生的 Markdown 網頁內容經過**解析**、**切塊**與**嵌入**後存入 **Qdrant 向量資料庫**，再以**語意檢索**找出最相關的段落，並由 **LLM** 生成回答。流程包含**索引建構**、**查詢引擎設定**與**成效評估**，形成完整的 RAG（Retrieval-Augmented Generation）管線。

- **模組實作**
	- `app/modules/rag.py`（主流程，包含**向量儲存**、**節點處理**、**索引建立**、**查詢引擎**與**評估**）
	- `app/configs/rag_config.py`（**設定載入**、**驗證**、**覆寫**與 **API key 推斷**）
	- `utils/rag_helper.py`（**自訂 Markdown Parser**、**圖片萃取**與**格式化工具**）

- **模組設定**
	- `./configs/rag/{name}.toml`（**檢索設定檔**，透過 `app/configs/rag_config.py` 載入）
	- 可在 `RagConfig` 或執行參數中覆寫 **embedding**、**chunk 參數**、**檢索設定**與 **LLM 模型**
	- API key 依用途分為三組獨立環境變數：`OPENAI_RAG_EMBEDDING_API_KEY`（Embedding）、`GEMINI_RAG_QUERY_ENGINE_API_KEY` / `OPENAI_RAG_QUERY_ENGINE_API_KEY`（查詢引擎）、`GEMINI_RAG_EVALUATOR_API_KEY` / `OPENAI_RAG_EVALUATOR_API_KEY`（評估）

- **模組環境**
	- `Python >= 3.10`（程式使用**現代型別語法**如 `Sequence[BaseNode]`）
	- **標準函式庫**：`json`、`os`、`shutil`、`logging`
	- **第三方套件**：`llama-index`（**核心檢索框架**）、`qdrant-client`（**向量資料庫**）、`llama-index-embeddings-openai`（**OpenAI Embedding**）、`llama-index-llms-google-genai` / `llama-index-llms-openai`（**查詢與評估 LLM**）

## rag.py

`Rag` 類別封裝了向量資料庫的完整生命週期，從初始化、建構到查詢與評估，各步驟有嚴格的呼叫順序。

### 使用流程總覽

```
Rag()
├── build_vector_store()     # (1) 建立 Qdrant 向量儲存
├── build_nodes()            # (2) 讀取 Markdown → Pipeline 產出節點
│   └── load_index()         # (3a) 既有 Qdrant 直接載入（跳過 build_nodes/build_index）
│   └── build_index()        # (3b) 從 nodes 新建索引並寫入 Qdrant
├── build_retriever()        # (4) 建立檢索器
├── build_query_engine()     # (5) 建立查詢引擎
├── query() / evaluate()     # (6) 執行查詢與評估
└── close()                  # (7) 釋放資源
```

其中 (2) → (3b) 用於首次建立索引，(3a) 則用於後續重複使用。

---

### 1. 載入資料

#### 初始化與 results.json
- 建構子會自動讀取 `data/webpages/prompt-v3/results.json`（由爬蟲產生的網頁清單），若檔案不存在則直接拋出 `FileNotFoundError`。
- `results.json` 的 key 為網頁標題（去除 `.md` 副檔名），value 包含 `url` 等資訊，後續 `file_metadata` 會以此補充每份文件的來源 URL。

#### 讀取 Markdown 文件
- `build_nodes()` 使用 LlamaIndex 的 `SimpleDirectoryReader` 讀取 `{webpages_data_folder_path}/results`（預設為 `data/webpages/prompt-v3/results`）。
- 只處理副檔名為 `.md` 的檔案，確保輸入內容來自爬蟲生成的 Markdown 成果。
- 透過 `self._file_metadata()` 回呼函式，根據 `results.json` 為每份文件注入 `page_title` 與 `page_url` metadata。

---

### 2. 轉換資料

`build_nodes()` 內部使用 `IngestionPipeline` 依序執行以下轉換：

1. **`MarkdownNodeParser`** — 解析 Markdown 結構，保留標題路徑 metadata。
2. **`SentenceSplitter`** — 以 `chunk_size=800`、`chunk_overlap=100`、`paragraph_separator="\n\n"` 進行切塊，這組參數目前表現最平衡。
3. **`MarkdownHeadingMergeParser`**（自訂）— 把純標題節點併入下一個有實質內容的節點，避免空洞的標題節點。
4. **`MarkdownImageExtractor`**（自訂）— 將 Markdown 圖片抽出到 `metadata["images"]`，並把內容中的圖片標記替換成 `alt` 文字。

這樣可讓圖片摘要、OCR 與頁面關聯保留在同一個 Node 中，避免資訊斷裂。

---

### 3. 建立索引

#### 3a. 建立向量儲存（必要前驟）
- `build_vector_store()` 透過 `QdrantClient(path=qdrant_db_folder_path)` 初始化 Qdrant，並以 `QdrantVectorStore(collection_name, client, index_doc_id=False)` 建立向量儲存。
- 預設 collection 名稱為 `webpages`，持久化路徑為 `data/rag/qdrant_db`。

#### 3b. 載入或新建索引
- **既有資料庫載入**：`load_index()` 使用 `VectorStoreIndex.from_vector_store(vector_store, embed_model)`，僅需提供 embedding 模型。
- **新建索引**：`build_index()` 需先完成 `build_nodes()` 產出 `self.nodes`，再以 `VectorStoreIndex(nodes, storage_context, embed_model)` 寫入 Qdrant。

#### Embedding 設定
- 使用 `OpenAIEmbedding(model="text-embedding-3-small", embed_batch_size=256)`，並透過 `.env` 讀取 `OPENAI_RAG_EMBEDDING_API_KEY`。

---

### 4. 查詢引擎

#### 檢索器
- `build_retriever()` 建立 `VectorIndexRetriever(index=self.index, similarity_top_k=5)`，每次回傳前 5 筆相關節點。

#### 查詢引擎
- `build_query_engine()` 將檢索器、回應合成器與後處理器串接成 `RetrieverQueryEngine`。
- 查詢 LLM 使用 `GoogleGenAI(model="gemini-3.1-flash-lite")`，API key 來自 `GEMINI_RAG_QUERY_ENGINE_API_KEY`（若使用 GPT 系列則來自 `OPENAI_RAG_QUERY_ENGINE_API_KEY`）。
- 回答生成器使用 `get_response_synthesizer(llm=llm)`。
- 後處理加入 `SimilarityPostprocessor(similarity_cutoff=0.45)`，過濾相似度過低的節點。

#### 執行查詢
- `query(query, log_sources=False)` 將字串查詢送入查詢引擎，回傳 `Response` 物件。
- 設 `log_sources=True` 時會以 `format_sources_text()`（來自 `utils.rag_helper`）輸出檢索到的來源節點摘要。

---

### 5. 成效評估

`evaluate(query, response, llm_name)` 使用兩項指標評估查詢結果：

#### Faithfulness（忠實度）
- `FaithfulnessEvaluator` 搭配自訂 `FAITHFULNESS_EVAL_TEMPLATE` 與 `FAITHFULNESS_REFINE_TEMPLATE`。
- 判斷回應內容是否被檢索到的 context 所支持，輸出 YES/NO 加上繁體中文原因。

#### Relevancy（相關性）
- `RelevancyEvaluator` 搭配自訂 `RELEVANCY_EVAL_TEMPLATE` 與 `RELEVANCY_REFINE_TEMPLATE`。
- 判斷查詢與回應是否與 context 一致，輸出 YES/NO 加上繁體中文原因。

#### Evaluator LLM
- 預設使用 `gpt-5.4`（因 `gemini-3.1-pro-preview` 每日限額太低）。
- API key 來自 `GEMINI_RAG_EVALUATOR_API_KEY`（Gemini）或 `OPENAI_RAG_EVALUATOR_API_KEY`（GPT）。
