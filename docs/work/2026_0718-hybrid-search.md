# Hybrid Search (2026/7/18)
> 對應 `2026_0708-RAG_Upgrade.md` 第二部分（二、混合檢索與重排序）

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
| `[retriever]` | `similarity_top_k` | `int` | `10` | 最終回傳的節點數 + dense 候選數 |
| `[retriever]` | `query_mode` | `str` | `"hybrid"` | `"hybrid"` 或 `"default"` |
| `[retriever]` | `hybrid_top_k` | `int` | `10` | sparse 分支候選數（原 `sparse_top_k`） |
| `[retriever]` | `alpha` | `float` | `0.5` | 稠密/稀疏權重（僅 Qdrant Weighted 有效） |

> **命名演進**：
> - `top_k` → `similarity_top_k`（對應 LlamaIndex `VectorStoreQuery.similarity_top_k`）
> - `sparse_top_k` → `hybrid_top_k`（對應 LlamaIndex `VectorStoreQuery.hybrid_top_k`）
> - `enable_hybrid` 與 `fastembed_sparse_model` 已從 config 層移除，於 `build_vector_store()` 中硬編碼

### Config keys 定義

```python
RETRIEVER_KEYS = {
    "similarity_top_k",
    "query_mode",
    "hybrid_top_k",
    "alpha",
}
```

### `_validate_config()` 新增驗證

```python
# query_mode: 僅接受 "hybrid" 或 "default"
# alpha: 必須為數值且介於 0.0 到 1.0 之間
# similarity_top_k / hybrid_top_k: 必須為大於 0 的整數
```

### 設定檔範例（`configs/rag/test-qdrant.toml`）

```toml
[retriever]
similarity_top_k = 10  # run name
query_mode = "hybrid"
hybrid_top_k = 10
alpha = 0.5
```

## 1.4 Vector Store 改造：啟用 Hybrid 索引

**位置**：`app/modules/rag.py` → `build_vector_store()`

```python
def build_vector_store(
    self,
    vector_store_type: str = DEFAULT_VECTOR_STORE_TYPE,
    qdrant_db_folder_path: str = DEFAULT_QDRANT_DB_FOLER_PATH,
    ...
) -> None:
    if vector_store_type == "qdrant":
        os.makedirs(qdrant_db_folder_path, exist_ok=True)
        self.qdrant_client = QdrantClient(path=qdrant_db_folder_path)
        self.vector_store = QdrantVectorStore(
            collection_name,
            self.qdrant_client,
            index_doc_id=False,
            enable_hybrid=True,                     # 硬編碼永遠啟用
            fastembed_sparse_model="Qdrant/bm25",   # 硬編碼 BM25 模型
        )
```

### 關鍵考量

- `enable_hybrid=True` 硬編碼，新建立的 collection 會同時包含稠密向量 + BM25 稀疏向量
- `Qdrant/bm25` 是 Qdrant 官方預訓練的 BM25 稀疏向量模型，不需額外訓練
- 既有 collection 無 sparse vectors 需重建索引（詳見 §Workflow, `--run.force-rebuild`）

## 1.5 Retriever 改造：混合檢索 + Metadata Filter 共存

**位置**：`app/modules/rag.py` → `build_retriever()`

```python
def build_retriever(
    self,
    query_mode: str = "hybrid",
    filter_dict: dict[str, str | int | tuple] | None = None,
    similarity_top_k: int = 10,
    hybrid_top_k: int = 10,
    alpha: float = 0.5,
) -> None:
```

### 內部邏輯

1. **Metadata filter 轉換邏輯不變**（`filter_dict` → `MetadataFilters`）
2. **判斷檢索模式**：
   - `"hybrid"` → 傳入 `VectorStoreQueryMode.HYBRID`、`hybrid_top_k`、`alpha`
   - `"default"` → 傳入 `VectorStoreQueryMode.DEFAULT`，退化為純稠密檢索
3. **解包傳入 `VectorIndexRetriever`**

### 重要說明

- Metadata filter 與 hybrid mode **可同時作用**（filter 在 Qdrant 層級 pre-filter）
- `alpha=0.5` 平衡稠密/稀疏；可依 Paper 低分現象實驗調整（如 `alpha=0.3` 增大稀疏權重）
- Qdrant 使用 **Weighted 線性融合**：`final = alpha × dense + (1-alpha) × sparse`

## 1.6 實測成效

在 `query_mode="hybrid"` 下以 Qdrant force-rebuild 測試「實驗室的成員有哪些人？」：

| 指標 | 結果 |
|---|---|
| Top-1 Score | 0.499（cosine similarity） |
| 成員覆蓋 | 12 位 ✅ |
| Faithfulness | 100% ✅ |
| Relevancy | 100% ✅ |
| 執行時間 | ~12 秒 |

## 1.7 已知限制：BM25 中文支援不足

Qdrant 內建的 `Qdrant/bm25` 模型對中文的 tokenization 效果有限，主要針對英文語料設計。部分中文關鍵字匹配可能不如預期，這也是引入 Milvus + BGE-M3 的關鍵動機（詳見 Part 2）。

---

# Part 2 — Milvus Hybrid Search

## 2.1 動機

Qdrant + BM25 對中文語料的關鍵字匹配效果有限，因此引入 Milvus + BGE-M3 作為替代方案。BGE-M3 是 BAAI 推出的多語言 embedding 模型，原生支援中文稀疏編碼，可同時產生 dense、sparse、ColBERT 三種向量。

## 2.2 依賴套件

| 套件 | 用途 | 安裝指令 |
|---|---|---|
| `llama-index-vector-stores-milvus>=1.1.0` | LlamaIndex Milvus 整合 | `uv add llama-index-vector-stores-milvus` |
| `FlagEmbedding>=1.3.0` | BGE-M3 模型（含 BGEM3FlagModel） | `uv add FlagEmbedding` |

`FlagEmbedding` 首次使用時會自動下載 BGE-M3 模型（約 2.2GB）至 `~/.cache/huggingface/`。

## 2.3 Vector Store 改造

**位置**：`app/modules/rag.py` → `build_vector_store()`

```python
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.vector_stores.milvus.utils import BGEM3SparseEmbeddingFunction

def build_vector_store(
    self,
    vector_store_type: str = DEFAULT_VECTOR_STORE_TYPE,
    ...
) -> None:
    if vector_store_type == "milvus":
        dim = EMBEDDING_DIM_MAP.get(embedding_name)

        self.vector_store = MilvusVectorStore(
            milvus_uri,
            collection_name=collection_name,
            overwrite=overwrite,
            dim=dim,
            output_fields=["_node_content", "_node_type"],
            enable_sparse=True,                                      # 永遠啟用
            sparse_embedding_function=BGEM3SparseEmbeddingFunction(),  # BGE-M3
        )
```

### 關鍵參數

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `enable_sparse` | `True`（硬編碼） | 啟用 sparse 向量欄位 |
| `sparse_embedding_function` | `BGEM3SparseEmbeddingFunction()` | 使用 BGE-M3 產生稀疏編碼 |
| `overwrite` | `True` | 是否清除既有 collection 重建 |
| `output_fields` | `["_node_content", "_node_type"]` | MilvusLite 須明確指定才能回傳完整節點資料 |
| `hybrid_ranker` | `"RRFRanker"` | 融合演算法（詳見 §2.5） |
| `hybrid_ranker_params` | `{}` | ranker 細部參數 |

## 2.4 BGEM3SparseEmbeddingFunction

此為 LlamaIndex 內建類別，封裝了 `BGEM3FlagModel`：

```python
class BGEM3SparseEmbeddingFunction(BaseSparseEmbeddingFunction):
    def __init__(self) -> None:
        from FlagEmbedding import BGEM3FlagModel
        self.model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=False)

    def encode_queries(self, queries: List[str]):
        outputs = self.model.encode(
            queries, return_dense=False, return_sparse=True,
            return_colbert_vecs=False,
        )["lexical_weights"]
        return [self._to_standard_dict(o) for o in outputs]

    def encode_documents(self, documents: List[str]):
        return self.encode_queries(documents)
```

### 自訂 sparse function

若要調整 `use_fp16` 或改用其他模型，可繼承 `BaseSparseEmbeddingFunction` 自訂。

## 2.5 融合演算法：RRF vs WeightedRanker

Milvus 支援兩種 hybrid 融合策略：

### RRFRanker（預設）

```
score = 1/(k + rank_dense) + 1/(k + rank_sparse)
```

| 特性 | 說明 |
|---|---|
| 只看排名，不看 similarity 分數 | 分數範圍固定 0~0.033（k=60 時） |
| `alpha` 無效 | 因為融合過程不使用分數 |
| `k` 控制 | `k` 越小 sparse 影響力越大 |

```python
MilvusVectorStore(
    hybrid_ranker="RRFRanker",
    hybrid_ranker_params={"k": 60},  # 預設 60
)
```

### WeightedRanker

```
score = w_dense × dense_score + w_sparse × sparse_score
```

| 特性 | 說明 |
|---|---|
| 分數保留 cosine similarity 特性 | 範圍 0~1，直觀可解讀 |
| 使用 `weights` 語法 | `[w_dense, w_sparse]`，非 `alpha` |
| 建議實驗值 | `[1.0, 0.3]`（dense 為主，sparse 為輔） |

```python
MilvusVectorStore(
    hybrid_ranker="WeightedRanker",
    hybrid_ranker_params={"weights": [1.0, 0.3]},
)
```

## 2.6 Score 特性與 SimilarityPostprocessor

RRF 分數極低（0.01~0.03），若 `build_query_engine()` 使用 `SimilarityPostprocessor(cutoff=0.4)` 會全數誤殺。

**解法**：hybrid 模式跳過 `SimilarityPostprocessor`：

```python
def build_query_engine(self, ..., query_mode: str = "hybrid") -> None:
    node_postprocessors = []
    if query_mode != "hybrid":
        node_postprocessors.append(SimilarityPostprocessor(similarity_cutoff=cutoff))
    self.query_engine = RetrieverQueryEngine(
        self.retriever, response_synthesizer,
        node_postprocessors=node_postprocessors,
    )
```

## 2.7 Retriever 參數

| 參數 | 預設值 | 說明 | 建議調整 |
|---|---|---|---|
| `similarity_top_k` | `10` | 最終輸出數 + dense 候選數 | 依需求增減 |
| `hybrid_top_k` | `10` | sparse 分支候選數 | **建議 20~30**，讓 sparse 有更多優質候選 |
| `alpha` | `0.5` | ⚠️ **RRF 下無效** | 改用 WeightedRanker 後用 `weights` |

## 2.8 持久化與重用

MilvusLite 使用本機檔案作為儲存後端。關鍵注意事項：

| 問題 | 說明 | 解法 |
|---|---|---|
| **`overwrite=True` 清空資料** | 每次 `build_vector_store()` 呼叫都會清除 collection | 非重建路徑傳入 `overwrite=False` |
| **`from_vector_store()` index 不完整** | `VectorStoreIndex.from_vector_store()` 建立空的 `nodes_dict`，無法解析檢索結果 | 非重建路徑也需 `build_nodes()` + `build_index()`，不可省略 |
| **collection released** | 第二次載入時 collection 停留在 `released` 狀態 | `load_index()` 中加入 `client.load_collection()` |

目前 `run_rag_query()` 的邏輯為 Milvus 每次強制走完整重建路徑（`build_nodes` → `build_vector_store` → `build_index`），確保 index struct 正確。

## 2.9 實測成效

在 `query_mode="hybrid"` 下以 Milvus force-rebuild 測試「實驗室的成員有哪些人？」：

| 指標 | RRFRanker（預設） | WeightedRanker `[1.0, 0.5]`（估算） |
|---|---|---|
| Top-1 Score | 0.033（RRF 排名分數） | ~0.4~0.5（保留 cosine） |
| 成員覆蓋 | 7 位（漏列多人） | 預期接近 Qdrant 水準 🔍 |
| Faithfulness | 100% ✅ | — |
| Relevancy | 100% ✅ | — |
| 執行時間 | ~34 秒（含模型載入） | 同左 |

> **預設 RRF 下 sparse 干擾過大**，建議改用 `WeightedRanker` 搭配 `weights=[1.0, 0.3]`。

## 2.10 Qdrant vs Milvus 比較

| 面向 | Qdrant (BM25 + Weighted) | Milvus (BGE-M3 + RRF) |
|---|---|---|
| **Sparse model** | `Qdrant/bm25`（純 BM25） | `BAAI/bge-m3`（神經稀疏編碼） |
| **中文支援** | ⚠️ 有限 | ✅ **原生支援** |
| **融合演算法** | Weighted: `alpha × dense + (1-alpha) × sparse` | RRF: rank-based（預設） |
| **Score 可讀性** | ✅ Cosine 0.4~0.5 | ❌ RRF 0.01~0.03 |
| **Sparse 實際影響** | 較低（dense 主導） | 較高（RRF 只看排名） |
| **執行時間** | ~12 秒（無模型載入） | ~34 秒（含 BGE-M3 載入） |
| **持久化** | ✅ 支援 Qdrant 本機檔案 | ⚠️ MilvusLite 有限 |
| **`alpha` 參數** | ✅ 有效 | ❌ 無效（需改用 `weights`） |

### 適用場景建議

| 場景 | 建議 |
|---|---|
| 快速穩定，中英文混合 | **Qdrant + hybrid default** |
| 中文為主，需進階 sparse 匹配 | **Milvus + WeightedRanker** |
| 實驗與調參 | 兩者皆保留，切換 `vector_store_type` |

## 2.11 調參建議

針對「Milvus RRF sparse 干擾過強」的問題，依序嘗試：

### Step 1：改用 WeightedRanker（最直接）

```python
MilvusVectorStore(
    hybrid_ranker="WeightedRanker",
    hybrid_ranker_params={"weights": [1.0, 0.3]},
)
```

### Step 2：拉高 hybrid_top_k

```python
rag.build_retriever(similarity_top_k=10, hybrid_top_k=30, query_mode="hybrid")
```

### Step 3：若仍不理想，調整 RRF k 值

```python
MilvusVectorStore(
    hybrid_ranker="RRFRanker",
    hybrid_ranker_params={"k": 100},  # 降低 sparse 干擾
)
```

### 參數交互關係

```
hybrid_top_k ↑     → sparse 候選越多 → 多樣性 ↑ → recall 可能 ↑
RRF k ↓           → sparse 權重 ↑   → 關鍵字更有影響力
Weighted w ↑sparse → sparse 權重 ↑   → 同 alpha 效果（但用 weights 語法）
similarity_top_k ↑ → 最終輸出 ↑     → LLM context 更長
```

---

# Part 3 — Node Re-ranking

## 3.1 概念：Cross-Encoder Reranker

Hybrid Search 檢索回來的候選節點數量較多（`similarity_top_k=10`），其中可能混入部分低相關結果。**Reranker** 採用 Cross-Encoder 架構，同時將 query 與候選節點餵入模型進行深度比對，產出比向量餘弦相似度更精準的相關性分數，進而重新排序並截斷。

### 管線定位

```
Hybrid Retrieval (similarity_top_k=10) → SimilarityPostprocessor(cutoff=0.0)
    → SentenceTransformerRerank(top_n=5) → LLM Generation
```

## 3.2 依賴套件：sentence-transformers

| 套件 | 用途 | 安裝指令 |
|---|---|---|
| `sentence-transformers>=3.4.0` | 載入 BGE Cross-Encoder Reranker 模型 | `uv add sentence-transformers` |

## 3.3 Config Schema：Reranker 相關擴充

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
    DEFAULT_RERANKER_CONFIG_SECTION: RERANKER_KEYS,
}
```

### 設定檔範例（`configs/rag/default.toml`）

```toml
[reranker]
reranker_model = "BAAI/bge-reranker-v2-m3"
reranker_top_n = 5
```

## 3.4 放寬 cutoff 的動機（0.4 → 0.0）

- Phase 1 已證明 Paper 節點 cosine 僅 0.37–0.38
- `SimilarityPostprocessor(cutoff=0.4)` 會誤殺所有 paper 節點
- BM25 稀疏檢索雖可輔助召回這些低分節點，但 **cutoff=0.4 仍在後處理階段將它們過濾掉**
- **改為 `cutoff=0.0`**：讓所有 hybrid 檢索結果通過初步過濾，由 BGE Reranker 進行精準二次排序
- ⚠️ **注意**：Milvus + RRFRanker 下分數為 0.01~0.03，即使 cutoff=0.0 也無法改善，需跳過 SimilarityPostprocessor（詳見 §2.6）

## 3.5 Query Engine 改造：加入 Reranker

**位置**：`app/modules/rag.py` → `build_query_engine()`

### 方法簽章

```python
def build_query_engine(
    self,
    llm_name: str = "gemini-3.1-flash-lite",
    cutoff: float = 0.0,
    query_mode: str = "hybrid",
    reranker_model: str = "BAAI/bge-reranker-v2-m3",
    reranker_top_n: int = 5,
) -> None:
```

### 內部邏輯

1. **LLM 初始化**邏輯不變（依 `llm_name` 判斷 Gemini 或 OpenAI）
2. **建立 `node_postprocessors` 列表**：
   - hybrid 模式跳過 `SimilarityPostprocessor`（詳見 §2.6）
   - 若 `reranker_model` 非空字串，追加 `SentenceTransformerRerank(model=reranker_model, top_n=reranker_top_n)`
3. **建立 `RetrieverQueryEngine`**：傳入 `self.retriever`、`response_synthesizer`、`node_postprocessors`

### 完整管線示意

```
Retrieval Stage (Part 1 / Part 2):
  VectorIndexRetriever (hybrid)
    ├── Dense vectors (語意)
    └── Sparse vectors (BM25 / BGE-M3)
        │
Post-processing Stage (Part 3):
  SimilarityPostprocessor (cutoff=0.0, 跳過 hybrid)
    │
  SentenceTransformerRerank (BGE, top_n=5)
    ↓
Generation Stage:
  LLM + 防幻覺 Prompt → 附來源連結的回應
```

## 3.6 Reranker 模型選擇分析

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

## 3.7 Prompt 模板 — 防幻覺 + 強制溯源

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
| `fastembed` | `>=0.6.0` | Qdrant BM25 稀疏向量本地生成 | Part 1 | `uv add fastembed` |
| `FlagEmbedding` | `>=1.3.0` | BGE-M3 稀疏編碼模型 | Part 2 | `uv add FlagEmbedding` |
| `sentence-transformers` | `>=3.4.0` | BGE Cross-Encoder Reranker 模型 | Part 3 | `uv add sentence-transformers` |

## Workflow Pipeline 更新

### `run_rag_build()` — 將新參數傳入對應方法

| 呼叫方法 | 傳入的新參數 |
|---------|-------------|
| `build_vector_store()` | `vector_store_type`、`overwrite`、`enable_sparse`（硬編碼） |
| `build_retriever()` | `config.similarity_top_k`、`config.query_mode`、`config.hybrid_top_k`、`config.alpha` |
| `build_query_engine()` | `config.cutoff`、`config.query_mode`、`config.reranker_model`、`config.reranker_top_n` |

### `run_rag_query()` — 重建策略

| 情境 | 策略 |
|---|---|
| Qdrant + `force_rebuild` 或路徑不存在 | `clean_vector_store()` + 完整重建 |
| Qdrant + 路徑存在 + `overwrite=False` | `build_nodes()` + `build_vector_store(overwrite=False)` + `load_index()` |
| Milvus（任何情況） | 強制完整重建（因 `from_vector_store()` 無法建立完整 index struct） |

## 向後相容策略

| 場景 | 處理方式 |
|---|---|
| 既有 collection 無 sparse vectors | 偵測後自動 clean + rebuild，或提示使用者執行 `--run.force-rebuild` |
| `reranker_model=""` | 跳過 reranker 初始化，只保留 SimilarityPostprocessor |
| `query_mode="default"` | 使用傳統 dense-only 檢索 |
| 舊 config TOML 無 hybrid/reranker section | 透過 `RagConfig` 預設值自動補齊 |
| 舊 config 使用 `top_k` / `sparse_top_k` | 需手動更新為 `similarity_top_k` / `hybrid_top_k` |

## 測試計畫

### 測試檔：`test/test_hybrid_rerank.py`

| 測試類別 | 所屬 | 數量 | 核心驗證 |
|---------|------|------|---------|
| `TestQdrantHybridRetrieval` | Part 1 | 3 | Qdrant hybrid mode 召回率 > dense-only |
| `TestMilvusHybridRetrieval` | Part 2 | 3 | Milvus hybrid mode 召回率 > dense-only |
| `TestRerankerOrdering` | Part 3 | 2 | Reranker 後 top-5 均為真正相關節點 |
| `TestFilterCompatibility` | Part 1+2 | 2 | Metadata filter + hybrid mode 同時運作 |
| `TestRegression` | 共同 | 2 | Hybrid + filter + reranker 不破壞既有通過條件 |
| `TestEdgeCases` | 共同 | 1 | 退化模式：`reranker_model=""` |

### 預期評估指標

| 指標 | Phase 1 (dense-only) | Part 1+2 (hybrid) | Part 3 (+reranker) |
|------|---------------------|-------------------|---------------------|
| Q5 Relevancy | ✅ | ✅（維持） | ✅（維持） |
| Paper 節點召回 | 需 `cutoff=0.0` | BM25/BGE-M3 自然召回 | 同左 |
| Faithfulness | 100% | 維持 100% | 維持 100% |
| Sources 多樣性 | 僅語意相近 | 語意 + 關鍵字補充 | 同左 |
| Top-N 相關性 | 向量分數排序 | 同左 | BGE Cross-Encoder 二次排序 |

## 實作步驟優先序

```
Part 1 — Qdrant Hybrid:
  [Step 1] 依賴安裝:     pyproject.toml 新增 fastembed
  [Step 2] Config 擴充:  rag_config.py 新增 hybrid 參數（query_mode, similarity_top_k, hybrid_top_k, alpha）
  [Step 3] Vector Store: rag.py build_vector_store 硬編碼 enable_hybrid=True
  [Step 4] Retriever:    rag.py build_retriever 新增 hybrid 檢索模式
  [Step 5] 設定檔:       test-qdrant.toml 加入 hybrid 參數
  [Step 6] Workflow:     workflow.py 將新參數傳入對應方法

Part 2 — Milvus Hybrid:
  [Step 7] 依賴安裝:     pyproject.toml 新增 FlagEmbedding + llama-index-vector-stores-milvus
  [Step 8] Vector Store: rag.py build_vector_store 新增 milvus 分支（enable_sparse + BGEM3SparseEmbeddingFunction）
  [Step 9] 設定檔:       test-milvus.toml 建立
  [Step 10] 調參:       Milvus WeightedRanker + hybrid_top_k 實驗

Part 3 — Reranker:
  [Step 11] 依賴安裝:    pyproject.toml 新增 sentence-transformers
  [Step 12] Reranker:    rag.py build_query_engine 新增 SentenceTransformerRerank
  [Step 13] Prompt:      rag.py 加入 HYBRID_TEXT_QA_TEMPLATE
  [Step 14] 測試:        test/test_hybrid_rerank.py 撰寫

跨領域:
  [Step 15] 回歸測試:   確保既有 20 項 metadata filter 測試不受影響
  [Step 16] 評估記錄:   執行 hybrid+reranker 評估，記錄結果至 docs/work/
```

## 風險評估

| 風險 | 影響 | 所屬 | 緩解方式 |
|------|------|------|---------|
| `fastembed` CUDA 衝突 | 環境安裝失敗 | Part 1 | 使用 CPU-only 安裝 `fastembed[cpu]` |
| BGE-M3 模型下載耗時 (~2.2GB) | 首次建 index 延遲 | Part 2 | 首次執行時自動下載 |
| MilvusLite 非同步限制 | 搜尋前須 `load_collection()` | Part 2 | 已在 `load_index()` 中處理 |
| Milvus 非重建路徑不完整 | index struct 為空 | Part 2 | 目前強制走重建路徑 |
| BGE reranker 模型下載耗時 (~2.4GB) | 首次 query 延遲 | Part 3 | 首次執行時自動下載；可考慮 lightweight 版本 |
| Hybrid 索引儲存空間倍增 | 磁碟用量上升 | Part 1+2 | 定期清理舊 collection |
| Reranker 增加 latency (~0.5–2s) | 查詢變慢 | Part 3 | 控制 `reranker_top_n` |

## 成果價值鏈

```
Phase 1 Metadata Filter (隔離非論文)
    ↓
Part 1: Qdrant BM25 稀疏檢索 (英文關鍵字補回)
  OR Part 2: Milvus BGE-M3 神經稀疏編碼 (中文關鍵字補回)
    ↓
Part 1+2: Metadata Filter + Hybrid 同時作用 (分類 + 檢索)
    ↓
Part 3: BGE Cross-Encoder Reranker (精準截斷)
    ↓
Part 3: 防幻覺 Prompt + 強制溯源 (品質把關)
    ↓
LLM Response (高品質、有來源引用)
```

最終目標：**讓論文查詢不僅 filter 隔離了非論文內容，還透過 hybrid search 找回被 cutoff 誤殺的節點，再經 reranker 精準排序後餵給 LLM，產生高品質且有來源引用的回答。**
