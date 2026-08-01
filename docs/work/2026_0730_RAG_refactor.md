# # RAG Refactor (2026/07/30)

## 重構規劃：`Rag`（runtime）+ `RagBuilder`（build）

### 0. 現狀問題

rag.py 目前是一個 ~615 行的類別，混合了三種職責：

```
rag.py (615 行)
├── 4 個評估模板 (80 行)
├── __init__ / close / context manager (50 行)
├── override_init_config / _load_results_json (30 行)
├── build / build_to_retriever / _require_config (70 行)  ← 建構編排
├── build_nodes / build_vector_store / clean_vector_store (50 行)  ← 建構步驟
├── build_index / load_index (30 行)  ← 建構步驟
├── build_retriever / _build_filters (40 行)  ← 建構步驟
├── build_query_engine / _set_embed_model / _set_llm (50 行)  ← 建構步驟
├── query / retrieve / evaluate / _log_sources / _log_evaluation_result (120 行)  ← runtime
└── imports (35 行, 混合 build 與 runtime)
```

### 1. 目標架構

```
rag.py (runtime)               rag_factory.py (build)
┌──────────────────────┐       ┌──────────────────────────────┐
│ class Rag:            │       │ class RagBuilder:             │
│   __init__(path)      │       │   __init__(config)           │
│   close()             │       │   build() → Rag             │
│   query()             │       │   build_to_retriever() → Rag │
│   retrieve()          │       │   build_nodes(rag)          │
│   evaluate()          │       │   build_vector_store(rag)   │
│                       │       │   build_index(rag)          │
│   _file_metadata()    │◄──────┤   load_index(rag)           │
│   _load_results_json()│callback│   build_retriever(rag)      │
│                       │       │   build_query_engine(rag)   │
│ ── shared ──          │       │   clean_vector_store(rag)   │
│ @static build_filters │◄──────►   _set_embed_model()        │
│ @static create_llm    │ shared│                              │
└──────────────────────┘       │ class NodePipelineBuilder    │
                               │ class VectorStoreBuilder     │
                               └──────────────────────────────┘
```

### 2. rag.py — 只留 Runtime 方法

**保留的方法**（~200 行）：

```python
class Rag:
    def __init__(self, webpages_data_folder_path: str = ...):
        # 只存路徑 + 載入 results_json
        # ❌ 不再接受 RagConfig
        # ❌ 不再有 self.config
        self.webpages_data_folder_path = ...
        self.md_docs_folder_path = ...
        self.results_json_path = ...
        self.results_json = self._load_results_json()
        # internal state (由 Builder 填入)
        self.qdrant_client = None
        self.vector_store = None
        self.index = None
        self.nodes = None
        self.retriever = None
        self.query_engine = None
        self._closed = False

    def close(self) -> None: ...
    def __enter__ / __exit__ / __del__ ...

    def query(self, ...) -> Response: ...
    def retrieve(self, ...) -> list[dict]: ...
    def evaluate(self, ...) -> tuple: ...

    def _file_metadata(self, file_path) -> dict: ...  # callback for Builder
    def _load_results_json(self, ...) -> dict: ...     # init helper

    # ── 跨域共用工具（不依賴任何 build 邏輯）──
    @staticmethod
    def build_filters(filter_dict) -> MetadataFilters | None: ...
    @staticmethod
    def create_llm(llm_name, api_key_name) -> LLM: ...
```

**移除的 import**（全移到 rag_factory.py）：
- `RagConfig`, `NodePipelineBuilder`, `VectorStoreBuilder`
- `StorageContext`, `VectorStoreIndex`, `get_response_synthesizer`
- `VectorIndexRetriever`, `RetrieverQueryEngine`
- `VectorStoreQueryMode`, `FilterOperator`, `MetadataFilter`, `MetadataFilters`
- `OpenAIEmbedding`, `SimilarityPostprocessor`

**刪除的方法**：
- `build()`, `build_to_retriever()`, `_require_config()`
- `build_nodes()`, `build_vector_store()`, `clean_vector_store()`
- `build_index()`, `load_index()`
- `build_retriever()`, `build_query_engine()`
- `_set_embed_model()`, `override_init_config()`

**保留的 import**：
- `gc`, `json`, `logging`, `os`, `typing`
- `Response`, `EvaluationResult`, `NodeWithScore`, `truncate_text`
- `MilvusVectorStore`, `QdrantVectorStore`, `QdrantClient`
- `WEBPAGES_DATA_FOLDER_PATH`
- `extract_sources_info`, `log_session`, `log_source_title`
- `FaithfulnessEvaluator`, `RelevancyEvaluator`, 4 個 `PromptTemplate`
- `GoogleGenAI`, `OpenAI`（`create_llm` 需要）

### 3. rag_factory.py — 新增 `RagBuilder`

```python
class RagBuilder:
    """負責 RAG 管線的 5 步驟建構流程。

    封裝 NodePipelineBuilder、VectorStoreBuilder 以及所有建構邏輯。
    提供完整建構 (build) 與部分建構 (build_to_retriever) 兩種模式，
    也公開每個步驟的方法供條件式建構使用。
    """

    def __init__(self, config: RagConfig) -> None:
        self.config = config

    # ── 高階編排 ──

    def build(self) -> Rag:
        """完整 5 步驟建構，回傳就緒的 Rag 實例。"""
        rag = self._create_rag()
        self.build_nodes(rag)
        self.build_vector_store(rag)
        self.build_index(rag)
        self.build_retriever(rag)
        self.build_query_engine(rag)
        return rag

    def build_to_retriever(self) -> Rag:
        """只建到 retriever，不回傳 query engine。"""
        rag = self._create_rag()
        self.build_nodes(rag)
        self.build_vector_store(rag)
        self.build_index(rag)
        self.build_retriever(rag)
        return rag

    # ── 個別建構步驟（公開，供 run_rag_query 條件式使用）──

    def build_nodes(self, rag: Rag) -> None: ...
        # 讀取 self.config.chunk_size 等
        # builder = NodePipelineBuilder(...)
        # rag.nodes = builder.build(..., file_metadata_fn=rag._file_metadata)

    def build_vector_store(self, rag: Rag, overwrite: bool = True) -> None: ...
        # VectorStoreBuilder.build(...) 寫入 rag.qdrant_client / rag.vector_store

    def build_index(self, rag: Rag) -> None: ...
        # 自己呼叫 _set_embed_model + VectorStoreIndex(...)

    def load_index(self, rag: Rag) -> None: ...
        # 自己呼叫 _set_embed_model + VectorStoreIndex.from_vector_store(...)

    def build_retriever(self, rag: Rag, filter_dict=None) -> None: ...
        # Rag.create_llm → VectorIndexRetriever(...)

    def build_query_engine(self, rag: Rag) -> None: ...
        # Rag.create_llm → RetrieverQueryEngine(...)

    def clean_vector_store(self, rag: Rag) -> None: ...
        # 清除 rag.qdrant_client / rag.vector_store 的資料

    # ── 私有輔助 ──

    @staticmethod
    def _set_embed_model(embedding_name: str) -> OpenAIEmbedding: ...
        # 從 env 讀取 OPENAI_RAG_EMBEDDING_API_KEY

    def _create_rag(self) -> Rag:
        return Rag(webpages_data_folder_path=self.config.webpages_data_folder_path)
```

### 4. `Rag.build_filters()` 和 `Rag.create_llm()` — 跨域設計

這兩個方法同時被 Builder（建構階段）和 Rag（執行階段）使用。

**方案選擇**：放在 `Rag` 上作為 `@staticmethod`，而非放在 rag_factory.py 或獨立工具函式。

理由：
- `build_filters()` 和 `create_llm()` 屬於 RAG 領域的概念，放在 `Rag` 上語義合理
- `Rag` 不需要 import rag_factory.py，保持單向依賴（`rag_factory` → `Rag`）
- Builder 透過 `Rag.build_filters()` / `Rag.create_llm()` 呼叫，不需額外 import

### 5. 呼叫端修改對照

#### `run_rag_build`（workflow.py）
```python
# 當前
rag = Rag(config=config).build()

# 之後
from app.modules.rag_factory import RagBuilder
rag = RagBuilder(config).build()
```

#### `run_rag_query`（workflow.py）
```python
# 當前
with Rag(config=config) as rag:
    rag.clean_vector_store(...)
    rag.build_nodes(...)
    ...

# 之後
rag = Rag(webpages_data_folder_path=config.webpages_data_folder_path)
builder = RagBuilder(config)
with rag:
    if rebuild:
        builder.clean_vector_store(rag, ...)
        builder.build_nodes(rag, ...)
        builder.build_vector_store(rag, ...)
        builder.build_index(rag, ...)
    else:
        builder.build_vector_store(rag, overwrite=False, ...)
        builder.load_index(rag, ...)
    builder.build_retriever(rag, ...)
    builder.build_query_engine(rag, ...)
```

注意：`builder` 不需要進入 `with` 區塊，只有 `rag` 需要。

#### webpage_retriever.py
```python
# 當前
rag = Rag(config=config).build_to_retriever()

# 之後
rag = RagBuilder(config).build_to_retriever()
```

### 6. 檔案變更總表

| 檔案 | 變更 |
|---|---|
| rag.py | 縮減為 ~200 行；刪除所有 build 方法；加入 `build_filters()` / `create_llm()` static |
| rag_factory.py | 新增 `RagBuilder` 類別（~120 行）；`NodePipelineBuilder` / `VectorStoreBuilder` 不變 |
| workflow.py | import 改為 `RagBuilder`；`run_rag_query` 改為 builder + rag 雙變數 |
| webpage_retriever.py | import 改為 `RagBuilder` |
| test_rag_builder.py | import 改為 `RagBuilder` |
| test_vector_store_builder.py | 不變 |
| test_node_pipeline_builder.py | 不變 |

### 7. 注意事項

1. **`override_init_config` 可刪除**：當年是為了解決「先 `Rag()` 再改路徑」的 workaround。重構後 Builder 直接 `Rag(config_path)`，不需要它。

2. **`_build_filters` 改名為 `build_filters`**：從 private 變 public static，因為跨域共用。

3. **`_set_llm` 改名為 `create_llm`**：語義更清楚，且避免誤會是 setter。

4. **單向依賴**：rag_factory.py → rag.py，rag.py 不再回頭 import rag_factory.py。

5. **評估模板不變**：4 個 `PromptTemplate` 留在 rag.py，因為只有 `evaluate()` 使用它們。