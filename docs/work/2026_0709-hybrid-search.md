# Hybrid Search + Node Re-ranking 實作計畫

> 對應 `2026_0708-RAG_Upgrade.md` 第二部分（二、混合檢索與重排序）
> 建立日期：2026/07/09 | 最後修正：2026/07/16（根據 Qdrant Hybrid Search 官方 API 文件校正、重組為兩大部分）

## 前置回顧：Phase 1 對 Phase 2 的關鍵影響

| Phase 1 發現 | Phase 2 策略 |
|---|---|
| Paper 節點 cosine score 僅 0.37–0.38，容易被 `cutoff=0.4` 誤殺 | BM25 關鍵字匹配可補回語意檢索的漏網之魚 |
| Q5 回歸驗證通過（filter 隔離非 paper）但向量分數仍低 | Reranker 二次排序：放寬初步撈取量後精準截斷 |
| 日期萃取四層策略驗證通過，`year` metadata 可用於後續過濾 | Hybrid Retriever 可合併使用 metadata filter + hybrid mode |

---

# Part 1 — Qdrant Hybrid Search

## 1.1 概念：Dense vs Sparse 向量

| 向量類型 | 說明 | 範例模型 |
|---|---|---|
| **Dense Vectors**（稠密向量） | 透過嵌入模型將整段文字壓縮為固定長度的數值向量，捕捉語義關聯 | OpenAI Embeddings, BGE, SentenceTransformers |
| **Sparse Vectors**（稀疏向量） | 大部分元素為零的高維向量，每個維度對應詞彙表中的一個詞，擅長關鍵字比對 | TF-IDF, BM25, SPLADE |

Hybrid Search 的核心優勢在於同時利用兩者的互補性：語義理解（dense）用於捕捉同義詞與上下文，關鍵字匹配（sparse）用於確保特定術語不被遺漏。

## 1.2 依賴套件：fastembed

| 套件 | 用途 | 安裝指令 |
|---|---|---|
| `fastembed>=0.6.0` | Qdrant BM25 稀疏向量本地生成，與 `enable_hybrid=True` 無縫整合 | `uv add fastembed` |

`fastembed` 是 Qdrant 官方推薦的稀疏向量生成引擎，可在本機端執行 BM25/SPLADE 模型，不需外部 API。

## 1.3 Config Schema：Hybrid 相關擴充

### RagConfig dataclass — Hybrid 欄位

| Section | 欄位 | 類型 | 預設值 | 說明 |
|---------|------|------|--------|------|
| `[vector_store]` | `batch_size` | `int` | `20` | 稀疏向量批次編碼的節點數 |
| `[retriever]` | `top_k` | `int` | `15` | 最終回傳的節點數（fusion 後） |
| `[retriever]` | `vector_store_query_mode` | `str` | `"hybrid"` | `"hybrid"` 或 `"default"` |
| `[retriever]` | `sparse_top_k` | `int` | `15` | 每種向量各取回 N 筆候選 |
| `[retriever]` | `alpha` | `float` | `0.5` | 稠密/稀疏權重（數值越低越偏稀疏） |
| `[retriever]` | `enable_hybrid` | `bool` | `True` | 是否啟用 hybrid 索引 |

> **API 校正**：官方 `QdrantVectorStore` **無** `hybrid_top_k` 參數。候選總數由 `sparse_top_k`（各取 N 筆）控制，最終輸出由 `similarity_top_k`（即 `top_k`）控制。

### Config keys 定義

```python
VECTOR_STORE_KEYS = {
    # ...既有 keys...
    "batch_size",  # 新增
}

RETRIEVER_KEYS = {
    "top_k",
    "vector_store_query_mode",  # 新增
    "sparse_top_k",             # 新增
    "alpha",                    # 新增
    "enable_hybrid",            # 新增
}
```

### `_validate_config()` 新增驗證

```python
# vector_store_query_mode: 僅接受 "hybrid" 或 "default"
# alpha: 必須為數值且介於 0.0 到 1.0 之間
# enable_hybrid: 必須為布林值
# sparse_top_k: 必須為大於 0 的整數
# batch_size: 必須為大於 0 的整數
```

### 設定檔範例（`configs/rag/default.toml`）

```toml
[vector_store]
batch_size = 20

[retriever]
top_k = 15
vector_store_query_mode = "hybrid"
sparse_top_k = 15
alpha = 0.5
enable_hybrid = true
```

## 1.4 Vector Store 改造：啟用 Hybrid 索引

**位置**：`app/modules/rag.py` → `build_vector_store()`

```python
def build_vector_store(
    self,
    qdrant_db_folder_path: str = DEFAULT_QDRANT_DB_FOLER_PATH,
    collection_name: str = "webpages",
    enable_hybrid: bool = True,
    fastembed_sparse_model: str = "Qdrant/bm25",
    batch_size: int = 20,
) -> None:
    self.qdrant_client = QdrantClient(path=qdrant_db_folder_path)
    self.aqdrant_client = AsyncQdrantClient(path=qdrant_db_folder_path)
    self.vector_store = QdrantVectorStore(
        collection_name,
        self.qdrant_client,
        aclient=self.aqdrant_client,
        index_doc_id=False,
        enable_hybrid=enable_hybrid,
        fastembed_sparse_model=fastembed_sparse_model,
        batch_size=batch_size,
    )
    logger.info(f"Successfully built vector store (hybrid={enable_hybrid})")
```

### 關鍵考量

- `enable_hybrid=True` 後，**新建立的 collection** 會同時包含稠密向量 + BM25 稀疏向量
- `batch_size` 控制每次傳入稀疏向量模型的節點數，防止大資料集 OOM
- `Qdrant/bm25` 是 Qdrant 官方預訓練的 BM25 稀疏向量模型，不需額外訓練
- `AsyncQdrantClient`（`aclient`）支援非同步查詢（`await query_engine.aquery()`）
- 既有 collection 無 sparse vectors 需重建索引（詳見 §Workflow）

## 1.5 Retriever 改造：混合檢索 + Metadata Filter 共存

**位置**：`app/modules/rag.py` → `build_retriever()`

```python
def build_retriever(
    self,
    top_k: int = 5,
    filter_dict: dict[str, str | int | tuple] | None = None,
    vector_store_query_mode: str = "hybrid",
    sparse_top_k: int = 15,
    alpha: float = 0.5,
) -> None:
```

### 內部邏輯

1. **Metadata filter 轉換邏輯不變**（Phase 1 的 `filter_dict` → `MetadataFilters`）
2. **判斷檢索模式**：
   - `"hybrid"` → 傳入 `vector_store_query_mode="hybrid"`、`sparse_top_k`、`alpha`
   - `"default"` → 只設 `vector_store_query_mode="default"`，退化為純稠密檢索
3. **解包傳入 `VectorIndexRetriever`**，並 log 輸出檢索模式與所有參數值

### 重要說明

- Metadata filter 與 hybrid mode **可同時作用**（filter 在 Qdrant 層級 pre-filter，不受檢索模式影響）
- `alpha=0.5` 平衡稠密/稀疏；可依 Paper 低分現象實驗調整（如 `alpha=0.3` 增大稀疏權重）

---

# Part 2 — Node Re-ranking

## 2.1 概念：Cross-Encoder Reranker

Hybrid Search 檢索回來的候選節點數量較多（`top_k=15`），其中可能混入部分低相關結果。**Reranker** 採用 Cross-Encoder 架構，同時將 query 與候選節點餵入模型進行深度比對，產出比向量餘弦相似度更精準的相關性分數，進而重新排序並截斷。

### 管線定位

```
Hybrid Retrieval (top_k=15) → SimilarityPostprocessor(cutoff=0.0)
    → SentenceTransformerRerank(top_n=5) → LLM Generation
```

## 2.2 依賴套件：sentence-transformers

| 套件 | 用途 | 安裝指令 |
|---|---|---|
| `sentence-transformers>=3.4.0` | 載入 BGE Cross-Encoder Reranker 模型 | `uv add sentence-transformers` |

## 2.3 Config Schema：Reranker 相關擴充

### RagConfig dataclass — Reranker 欄位

全新 `[reranker]` section：

| 欄位 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `reranker_model` | `str` | `"BAAI/bge-reranker-v2-m3"` | 設為空字串表不啟用 |
| `reranker_top_n` | `int` | `5` | 最終保留的節點數 |

### Config keys 定義

```python
DEFAULT_RERANKER_CONFIG_SECTION = "reranker"
RERANKER_KEYS = {"reranker_model", "reranker_top_n"}
SECTIONS_TO_KEYS = {
    # ...既有對應...
    DEFAULT_RERANKER_CONFIG_SECTION: RERANKER_KEYS,  # 新增
}
```

### `__post_init__` 預設值補齊

```python
def __post_init__(self) -> None:
    if not hasattr(self, "reranker_model"):
        self.reranker_model = "BAAI/bge-reranker-v2-m3"
    if not hasattr(self, "reranker_top_n"):
        self.reranker_top_n = 5
    _validate_config(vars(self))
```

### 設定檔範例（`configs/rag/default.toml`）

```toml
[reranker]
reranker_model = "BAAI/bge-reranker-v2-m3"
reranker_top_n = 5
```

## 2.4 放寬 cutoff 的動機（0.4 → 0.0）

- Phase 1 已證明 Paper 節點 cosine 僅 0.37–0.38
- `SimilarityPostprocessor(cutoff=0.4)` 會誤殺所有 paper 節點
- BM25 稀疏檢索雖可輔助召回這些低分節點，但 **cutoff=0.4 仍在後處理階段將它們過濾掉**
- **改為 `cutoff=0.0`**：讓所有 hybrid 檢索結果通過初步過濾，由 BGE Reranker 進行精準二次排序

## 2.5 Query Engine 改造：加入 Reranker

**位置**：`app/modules/rag.py` → `build_query_engine()`

### 方法簽章

```python
def build_query_engine(
    self,
    llm_name: str = "gemini-3.1-flash-lite",
    cutoff: float = 0.0,              # 放寬至 0.0
    reranker_model: str = "BAAI/bge-reranker-v2-m3",
    reranker_top_n: int = 5,
) -> None:
```

### 內部邏輯

1. **LLM 初始化**邏輯不變（依 `llm_name` 判斷 Gemini 或 OpenAI）
2. **建立 `node_postprocessors` 列表**：
   - 第一個元素：`SimilarityPostprocessor(similarity_cutoff=cutoff)`
   - 若 `reranker_model` 非空字串，追加 `SentenceTransformerRerank(model=reranker_model, top_n=reranker_top_n)`
3. **建立 response synthesizer**：`get_response_synthesizer(llm=llm, text_qa_template=HYBRID_TEXT_QA_TEMPLATE)`
4. **建立 `RetrieverQueryEngine`**：傳入 `self.retriever`、`response_synthesizer`、`node_postprocessors`

### 完整管線示意

```
Retrieval Stage (Part 1):
  VectorIndexRetriever (hybrid, top_k=15)
    ├── Dense vectors (語意, alpha=0.5)
    └── Sparse vectors (BM25 關鍵字, alpha=0.5)
        │
Post-processing Stage (Part 2):
  SimilarityPostprocessor (cutoff=0.0, 最低限度過濾)
    │
  SentenceTransformerRerank (BGE, top_n=5)
    ↓
Generation Stage:
  LLM + 防幻覺 Prompt → 附來源連結的回應
```

## 2.6 Reranker 模型選擇分析

| 模型 | 中文支援 | 大小 | 速度 | 推薦場景 |
|---|---|---|---|---|
| **`BAAI/bge-reranker-v2-m3`** | ✅ **優良（多語言）** | ~2.4GB | 中等 | **首選**：中英混合語料 |
| `BAAI/bge-reranker-v2.5-gemma2-lightweight` | ✅ 良好 | 輕量 | 快 | 資源受限場景 |
| `cross-encoder/ms-marco-MiniLM-L6-v2` | ❌ 僅英文 | ~0.4GB | 極快 | 快取驗證用 |
| `CohereRerank`（API） | ✅ 良好 | N/A | 極快 | 有 API key 且可接受外部呼叫 |

採用 **BAAI/bge-reranker-v2-m3** 的原因：
1. 原生支援中英文混合語料（實驗室網站為中英夾雜）
2. 本地運行，無外部 API 呼叫與費用
3. 開源社群活躍，持續維護

## 2.7 Prompt 模板 — 防幻覺 + 強制溯源

**位置**：`app/modules/rag.py`（全域常量）

```python
HYBRID_TEXT_QA_TEMPLATE = PromptTemplate(
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "請嚴格遵守以下規則回答問題：\n"
    "1. 只能使用上述 Context 的內容回答，不足時須明確告知使用者。\n"
    "2. 回答事實問題（如發表年份、論文名稱、實驗室成員等）須附上來源連結，"
    "格式為 [頁面名稱](url)。\n"
    "3. 嚴禁推測編造，特別是名單、年份、數量等具體數字。\n"
    "4. 名單不完整或不確定時須明確告知使用者。\n"
    "5. 以繁體中文回答。\n\n"
    "Query: {query_str}\n"
    "Answer: "
)
```

---

# 跨領域共用章節

## 依賴套件總表

| 套件 | 版本 | 用途 | 所屬 | 安裝指令 |
|------|------|------|------|---------|
| `fastembed` | `>=0.6.0` | Qdrant BM25 稀疏向量本地生成 | Part 1 Hybrid | `uv add fastembed` |
| `sentence-transformers` | `>=3.4.0` | BGE Cross-Encoder Reranker 模型 | Part 2 Reranker | `uv add sentence-transformers` |

## Workflow Pipeline 更新

### `run_rag_build()` — 將新參數傳入對應方法

| 呼叫方法 | 傳入的新參數 |
|---------|-------------|
| `build_vector_store()` | `config.enable_hybrid`（啟用 hybrid 索引） |
| `build_retriever()` | `config.top_k`、`config.vector_store_query_mode`、`config.sparse_top_k`、`config.alpha` |
| `build_query_engine()` | `config.cutoff`、`config.reranker_model`、`config.reranker_top_n` |

`build_index()` 不需更動 — 稠密向量由 `embed_model` 處理，稀疏向量由 `QdrantVectorStore` 內部處理。

### `run_rag_query()` — Hybrid 重建偵測

當 `enable_hybrid=True` 且 collection 已存在但無 sparse vectors 時觸發重建。實作輔助方法 `_collection_has_sparse_vectors()`，透過 `QdrantClient.get_collection()` 檢查 collection 的向量配置。簡單策略：hybrid mode 啟用時一律強制 `clean_vector_store()` + 重新 build_nodes/build_index。

## 向後相容策略

| 場景 | 處理方式 |
|---|---|
| 既有 collection 無 sparse vectors | 偵測後自動 clean + rebuild，或提示使用者執行 force_rebuild |
| `enable_hybrid=False` | 完全退化為目前 dense-only 行為，零破損 |
| `reranker_model=""` | 跳過 reranker 初始化，只保留 SimilarityPostprocessor |
| `vector_store_query_mode="default"` | 跳過 hybrid 參數，使用傳統 dense-only 檢索 |
| 舊 config TOML 無 hybrid/reranker section | 透過 `RagConfig` 預設值自動補齊 |
| `top_k` 維持既有值（5） | 仍可正常執行，僅無 hybrid+reranker 帶來的效益 |
| `batch_size` 不存在於舊版 config | 透過 `RagConfig.__post_init__` 補上預設值 `20` |

## 測試計畫

### 測試檔：`test/test_hybrid_rerank.py`

| 測試類別 | 所屬 | 數量 | 核心驗證 |
|---------|------|------|---------|
| `TestHybridRetrieval` | Part 1 | 3 | Hybrid mode 召回率 > dense-only，Paper 低分節點被 BM25 補回 |
| `TestRerankerOrdering` | Part 2 | 2 | Reranker 後 top-5 均為真正相關節點，分數重新排序正確 |
| `TestFilterCompatibility` | Part 1 | 2 | Metadata filter + hybrid mode 同時運作 |
| `TestRegression` | 共同 | 2 | Hybrid + filter + reranker 不破壞 Q5 既有通過條件 |
| `TestEdgeCases` | 共同 | 2 | 退化模式：`reranker_model=""`、`enable_hybrid=False` |

### 預期評估指標

| 指標 | Phase 1 (dense-only) | Phase 2 目標 (hybrid+reranker) |
|------|---------------------|-------------------------------|
| Q5 Relevancy | **PASSING** ✅ | **PASSING** ✅（維持） |
| Paper 節點召回 | 需 `cutoff=0.0` 才召回 | BM25 自然召回，無需降 threshold |
| Faithfulness | 100% | 維持 100%（prompt 強制約束） |
| Sources 多樣性 | 僅語意相近 | 語意 + 關鍵字相互補充 |
| Top-5 相關性 | 向量分數排序 | BGE Cross-Encoder 二次排序 |

## 實作步驟優先序

```
[Step 1] 依賴安裝: pyproject.toml 新增 fastembed + sentence-transformers
[Step 2] Config 擴充: rag_config.py 新增 hybrid + reranker 參數與驗證
[Step 3] Vector Store: rag.py build_vector_store 新增 enable_hybrid
[Step 4] Retriever:    rag.py build_retriever 新增 hybrid 檢索模式           ← Part 1
[Step 5] Query Engine: rag.py build_query_engine 新增 Reranker + Prompt     ← Part 2
[Step 6] 設定檔:      default.toml / test.toml 擴充
[Step 7] Workflow:    workflow.py 將新參數傳入對應方法
[Step 8] 測試:        test/test_hybrid_rerank.py 撰寫
[Step 9] 回歸測試:    確保既有 20 項 metadata filter 測試不受影響
[Step 10] 評估記錄:   執行 hybrid+reranker 評估，記錄結果至 docs/work/
```

## 風險評估

| 風險 | 影響 | 所屬 | 緩解方式 |
|------|------|------|---------|
| `fastembed` CUDA 衝突 | 環境安裝失敗 | Part 1 | 使用 CPU-only 安裝 `fastembed[cpu]` |
| BGE reranker 模型下載耗時 (~2.4GB) | 首次 query 延遲 | Part 2 | 首次執行時自動下載；可考慮 lightweight 版本 |
| Hybrid 索引導致儲存空間倍增 | 磁碟用量上升 | Part 1 | Qdrant 儲存在本地，可接受；定期清理舊 collection |
| Reranker 增加 latency (~0.5–2s) | 查詢變慢 | Part 2 | 評估 latency 影響，必要時控制 `reranker_top_n` |
| `fastembed` 與既有 embedding 衝突 | ImportError | Part 1 | 確認 `fastembed` 不干擾 `OpenAIEmbedding`；隔離在 vector store 層 |

## 成果價值鏈

```
Phase 1 Metadata Filter (隔離非論文)
    ↓
Part 1: BM25 稀疏檢索 (找回低 cosine 論文節點)
    ↓
Part 1: Metadata Filter + Hybrid 同時作用 (分類 + 檢索)
    ↓
Part 2: BGE Cross-Encoder Reranker (15→5 精準截斷)
    ↓
Part 2: 防幻覺 Prompt + 強制溯源 (品質把關)
    ↓
LLM Response (高品質、有來源引用)
```

最終目標：**讓 Q5 類型的論文查詢不僅 filter 隔離了非論文內容，還透過 BM25 找回被 cutoff 誤殺的論文節點，再經 reranker 精準排序後餵給 LLM，產生高品質且有來源引用的回答。**
