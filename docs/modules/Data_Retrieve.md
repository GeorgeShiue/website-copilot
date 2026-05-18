# 向量資料庫檢索

## rag.py

### 1. 載入資料
- 使用 LlamaIndex 的 `SimpleDirectoryReader` 讀取 `data/webpages/prompt-v3/results`。
- 只處理副檔名為 `.md` 的檔案，確保輸入內容來自爬蟲生成的 Markdown 成果。
- 透過 `file_metadata` 補充文件 metadata，讓後續節點保留來源資訊。

### 2. 轉換資料
- `MarkdownNodeParser` 先解析 Markdown 結構，並保留標題路徑 metadata。
- `SentenceSplitter` 以 `chunk_size=800`、`chunk_overlap=100` 進行切塊，這組參數目前表現最平衡。
- `MarkdownHeadingMergeParser` 會把純標題節點併入下一個有實質內容的節點。
- `MarkdownImageExtractor` 會將 Markdown 圖片抽出到 `metadata["images"]`，並把內容中的圖片標記替換成 `alt` 文字。
- 這樣可讓圖片摘要、OCR 與頁面關聯保留在同一個 Node 中，避免資訊斷裂。

### 3. 建立索引
- Embedding 使用 `OpenAIEmbedding(model="text-embedding-3-small")`，並透過 `.env` 讀取 `OPENAI_RAG_EMBEDDING_API_KEY`。
- 向量資料庫使用 `QdrantVectorStore`，collection 名稱為 `webpages`，持久化路徑為 `data/rag/qdrant_db`。
- 若向量資料庫已存在，會直接從既有 Qdrant 載入並以 `VectorStoreIndex.from_vector_store(...)` 建立索引。
- 若向量資料庫不存在，則會以處理後的 `nodes` 建立新索引並寫入 Qdrant。

### 4. 查詢引擎
- 查詢引擎使用 `GoogleGenAI(model="gemini-3.1-flash-lite")`，並透過 `GEMINI_RAG_QUERY_ENGINE_API_KEY` 載入金鑰。
- 檢索器採用 `VectorIndexRetriever(index=index, similarity_top_k=5)`，每次回傳前 5 筆相關節點。
- 回答生成器使用 `get_response_synthesizer(llm=llm)`，將檢索到的節點組合成回應。
- 後處理加入 `SimilarityPostprocessor(similarity_cutoff=0.5)`，過濾相似度過低的節點。
- 最後由 `RetrieverQueryEngine` 串接 retriever、response synthesizer 與 node postprocessors，形成完整查詢流程。

### 5. 成效評估
- LlamaIndex
- Ragas

