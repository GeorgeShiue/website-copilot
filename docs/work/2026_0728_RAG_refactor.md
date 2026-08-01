# RAG Refactor (2026/07/28)

## 目錄

1. 現狀分析與重構策略
2. 重構範圍與邊界
3. Phase 1：抽取 `NodePipelineBuilder`
4. Phase 2：抽取 `VectorStoreBuilder`
5. Phase 3：建立 `RagBuilder` Facade
6. [Phase 4：輕量化 `Rag` 類別](#6-phase-4輕量化-rag-類別)
7. 驗證策略
8. 回歸測試矩陣
9. 風險與緩解

---

## 1. 現狀分析與重構策略

### 現有問題

| 問題 | 描述 | 影響端 |
|------|------|--------|
| **God Class** | `Rag` 管理 7+ 個職責（節點、向量儲存、索引、檢索器、查詢引擎、評估、資源清理） | 所有呼叫端 |
| **建構序列重複** | workflow.py（2處）與 webpage_retriever.py（1處）手動重複相同 5 步驟 | 3 個呼叫點 |
| **測試需要完整基礎設施** | 需完整的 Milvus/Qdrant 才能測試任一環節 | 測試困難 |
| **單一檔案過大** | rag.py ~650 行，載入 20+ 個第三方匯入 | 可維護性 |

### 重構目標

```
重構前：
workflow.py ──→ Rag (God Class, 650 行)
webpage_retriever.py ──→ Rag (God Class, 650 行)

重構後：
workflow.py ──→ RagBuilder Facade ──→ Rag (輕量, ~200 行)
webpage_retriever.py ──→ RagBuilder Facade ─── NodePipelineBuilder (獨立)
                                             ├── VectorStoreBuilder (獨立)
                                             └── RagRetriever (可選)
```

### 既有靜態方法（已就緒，不需重寫）

| 方法 | 位置 | 重構後去向 |
|------|------|-----------|
| `_build_filters` | `Rag._build_filters` | 移至 `RagRetriever` 或保留在 `Rag` |
| `_resolve_embedding_dim` | `Rag._resolve_embedding_dim` | 移至 `VectorStoreBuilder` |
| `_default_hybrid_ranker_params` | 模組層級函式 | 移至 `VectorStoreBuilder` |
| `_load_results_json` | `Rag._load_results_json` | 保留在 `Rag`（設定管理） |
| `_set_embed_model` | `Rag._set_embed_model` | 移至 `VectorStoreBuilder` 或保留 |
| `_set_llm` | `Rag._set_llm` | 保留在 `Rag`（執行相關） |
| `_file_metadata` | `Rag._file_metadata` | 移至 `NodePipelineBuilder` |

---

## 2. 重構範圍與邊界

### In scope

- rag.py → 輕量化，移除建構邏輯，保留執行與資源管理
- rag_refactor.py（已存在但為空）→ 放置 `NodePipelineBuilder`、`VectorStoreBuilder`、`RagBuilder`
- workflow.py → 簡化兩處呼叫端
- webpage_retriever.py → 簡化一處呼叫端

### Out of scope

- rag_config.py — 保持不變（已良好設計）
- rag_helper.py — 保持不變
- config_helper.py — 保持不變
- Eval 邏輯 — 保持不變
- **Minor 問題**（#11–#15）— 暫緩

### 檔案變更總覽

| 檔案 | 操作 |
|------|------|
| rag.py | **修改**：移除建構方法，保留執行 + 資源管理 |
| rag_refactor.py | **新增**：包含 3 個新類別 |
| workflow.py | **修改**：改用 `RagBuilder` |
| webpage_retriever.py | **修改**：改用 `RagBuilder` |
| test_rag_refactor.py | **新增**：涵蓋資源管理、委派橋接、Builder 靜態方法的整合測試 |
| test | **新增**：`test_node_pipeline_builder.py`、`test_vector_store_builder.py`、`test_rag_builder.py` |

---

## 3. Phase 1：抽取 `NodePipelineBuilder`

### 3.1 新類別設計

```python
# app/modules/rag_refactor.py

class NodePipelineBuilder:
    """只負責 Document → Node 的轉換。

    封裝 SimpleDirectoryReader、IngestionPipeline 與所有 transformer。
    可獨立測試，不需 VectorStore 或 Index。
    """

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
        paragraph_separator: str = "\n\n",
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.paragraph_separator = paragraph_separator

    def build(
        self,
        md_folder_path: str,
        file_metadata_fn: Callable[[str], dict[str, Any]] | None = None,
        results_json: dict[str, Any] | None = None,
    ) -> list[BaseNode]:
        """從 Markdown 資料夾建立節點。

        Args:
            md_folder_path: 包含 .md 檔案的資料夾路徑。
            file_metadata_fn: 可選的 file_metadata callback。
            results_json: 可選的 results_json 用於預設 file_metadata。

        Returns:
            list[BaseNode]: 處理後的節點列表。
        """
        # ...
```

### 3.2 從 `Rag` 搬移的方法

| 原始方法 | 目的地 |
|----------|--------|
| `build_nodes()` 中的 `SimpleDirectoryReader` 邏輯 | `NodePipelineBuilder.build()` |
| `_file_metadata()` | `NodePipelineBuilder` 靜態方法或內部函式 |
| `MarkdownNodeParser` / `SentenceSplitter` / `MarkdownHeadingMergeParser` / `MarkdownDateExtractor` / `MarkdownImageExtractor` 的配置 | `NodePipelineBuilder.build()` 內部 |

### 3.3 `Rag.build_nodes()` 的委派橋接

```python
# rag.py — 過度期橋接方法（Phase 4 會移除）
class Rag:
    def build_nodes(self, ...) -> None:
        builder = NodePipelineBuilder(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            paragraph_separator=paragraph_separator,
        )
        self.nodes = builder.build(
            md_folder_path=self.md_docs_folder_path,
            file_metadata_fn=self._file_metadata,
        )
```

### 3.4 測試計畫

| 測試 ID | 測試案例 | 驗證方式 |
|---------|---------|----------|
| NPB.1 | 空資料夾 → 回傳空列表 | `assert nodes == []` |
| NPB.2 | 單個 .md 檔案 → 產出 >0 個 node | `assert len(nodes) > 0` |
| NPB.3 | 自訂 chunk_size → node 內容長度符合預期 | 檢查每個 node 的 text 長度 |
| NPB.4 | Heading-only 段落與下個段落合併 | `MarkdownHeadingMergeParser` 行為驗證 |
| NPB.5 | 圖片被正確提取並從內容移除 | `MarkdownImageExtractor` 行為驗證 |
| NPB.6 | 不存在的資料夾 → `FileNotFoundError` | `pytest.raises(FileNotFoundError)` |

---

## 4. Phase 2：抽取 `VectorStoreBuilder`

### 4.1 新類別設計

```python
# app/modules/rag_refactor.py

class VectorStoreBuilder:
    """只負責 VectorStore 的建立與清理。

    封裝 QdrantVectorStore / MilvusVectorStore 的建立邏輯、
    embedding 維度解析、hybrid ranker 參數管理。
    """

    @staticmethod
    def resolve_embedding_dim(embedding_name: str) -> int:
        """查詢 embedding 維度，若未知則拋錯。"""
        # 從 Rag 搬移 _resolve_embedding_dim

    @staticmethod
    def default_hybrid_ranker_params(hybrid_ranker: str) -> dict[str, Any]:
        """回傳預設 hybrid ranker 參數。"""
        # 從模組層級搬移 _default_hybrid_ranker_params

    @classmethod
    def build_qdrant(
        cls,
        collection_name: str,
        db_folder_path: str,
        hybrid_ranker: str = "WeightedRanker",
        hybrid_ranker_params: dict | None = None,
    ) -> tuple[QdrantClient, QdrantVectorStore]:
        """建立 Qdrant vector store。"""
        # 確認 hybrid_ranker_params 預設值
        # 建立 QdrantClient + QdrantVectorStore

    @classmethod
    def build_milvus(
        cls,
        collection_name: str,
        milvus_uri: str,
        embedding_name: str,
        overwrite: bool = True,
        hybrid_ranker: str = "WeightedRanker",
        hybrid_ranker_params: dict | None = None,
    ) -> MilvusVectorStore:
        """建立 Milvus vector store。"""
        # 解析 embedding dim
        # 建立 MilvusVectorStore

    @classmethod
    def build(
        cls,
        vector_store_type: str,
        collection_name: str,
        embedding_name: str,
        qdrant_db_folder_path: str | None = None,
        milvus_uri: str | None = None,
        overwrite: bool = True,
        hybrid_ranker: str = "WeightedRanker",
        hybrid_ranker_params: dict | None = None,
    ) -> tuple[QdrantClient | None, QdrantVectorStore | MilvusVectorStore]:
        """統一的 factory method，根據 type 分派到對應方法。"""

    @staticmethod
    def clean_qdrant(db_folder_path: str) -> None:
        """清理 Qdrant 資料。"""
    @staticmethod
    def clean_milvus(milvus_uri: str) -> None:
        """清理 Milvus 資料。"""
```

### 4.2 測試計畫

| 測試 ID | 測試案例 | 驗證方式 |
|---------|---------|----------|
| VSB.1 | `resolve_embedding_dim("text-embedding-3-small")` → 1536 | `assert dim == 1536` |
| VSB.2 | `resolve_embedding_dim("unknown")` → ValueError | `pytest.raises(ValueError)` |
| VSB.3 | `build_qdrant` 成功建立 client + store | `assert isinstance(qdrant_client, QdrantClient)` |
| VSB.4 | `build_milvus` 成功建立 store（需 mock） | mock `MilvusVectorStore` |
| VSB.5 | `clean_qdrant` 清理目錄 | `assert not os.path.exists(path)` |
| VSB.6 | 不支援的 vector_store_type → ValueError | `pytest.raises(ValueError)` |

---

## 5. Phase 3：建立 `RagBuilder` Facade

### 5.1 新類別設計

```python
# app/modules/rag_refactor.py

class RagBuilder:
    """Facade: 將 NodePipelineBuilder、VectorStoreBuilder 等組合為完整流程。

    呼叫端只需提供 config，不需了解內部 5 步驟的編排順序。
    支援「完整建構」與「只建到 retriever」兩種模式。
    """

    def __init__(self, config: RagConfig) -> None:
        self.config = config
        self._rag: Rag | None = None

    def build(self) -> Rag:
        """建構完整 RAG 管線：nodes → vector store → index → retriever → query engine。

        回傳的 Rag 實例已完全初始化（override_init_config 已呼叫）。
        呼叫端須使用 with 區塊確保資源釋放。
        """
        rag = self._create_rag()
        self._build_nodes(rag)
        self._build_vector_store(rag)
        self._build_index(rag)
        self._build_retriever(rag)
        self._build_query_engine(rag)
        return rag

    def build_to_retriever(self) -> Rag:
        """只建到 retriever 層級，不建 query engine。

        用於 webpage_retriever.py 的場景（只需檢索，不需問答）。
        """
        rag = self._create_rag()
        self._build_nodes(rag)
        self._build_vector_store(rag)
        self._build_index(rag)
        self._build_retriever(rag)
        return rag

    def build_to_index(
        self,
        overwrite: bool = True,
    ) -> Rag:
        """只建到 index 層級，允許控制 overwrite 行為（run_rag_query 的 rebuild 邏輯需要）。"""
        rag = self._create_rag()
        self._build_nodes(rag)
        self._build_vector_store(rag, overwrite=overwrite)
        self._build_index(rag)
        return rag

    def _create_rag(self) -> Rag:
        rag = Rag()
        rag.override_init_config(
            webpages_data_folder_path=self.config.webpages_data_folder_path,
        )
        return rag

    def _build_nodes(self, rag: Rag) -> None:
        builder = NodePipelineBuilder(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            paragraph_separator=self.config.paragraph_separator,
        )
        rag.nodes = builder.build(
            md_folder_path=rag.md_docs_folder_path,
            file_metadata_fn=rag._file_metadata,
        )

    def _build_vector_store(self, rag: Rag, overwrite: bool = True) -> None:
        qdrant_client, vector_store = VectorStoreBuilder.build(
            vector_store_type=self.config.vector_store_type,
            collection_name=self.config.collection_name,
            embedding_name=self.config.embedding_name,
            qdrant_db_folder_path=self.config.qdrant_db_folder_path,
            milvus_uri=self.config.milvus_uri,
            overwrite=overwrite,
            hybrid_ranker=self.config.hybrid_ranker,
            hybrid_ranker_params=self.config.hybrid_ranker_params,
        )
        rag.qdrant_client = qdrant_client
        rag.vector_store = vector_store

    def _build_index(self, rag: Rag) -> None:
        embed_model = rag._set_embed_model(self.config.embedding_name)
        storage_context = StorageContext.from_defaults(vector_store=rag.vector_store)
        rag.index = VectorStoreIndex(
            rag.nodes,
            storage_context=storage_context,
            embed_model=embed_model,
            show_progress=True,
        )

    def _build_retriever(self, rag: Rag) -> None:
        rag.build_retriever(
            similarity_top_k=self.config.similarity_top_k,
            query_mode=self.config.query_mode,
            hybrid_top_k=self.config.hybrid_top_k,
            alpha=self.config.alpha,
        )

    def _build_query_engine(self, rag: Rag) -> None:
        rag.build_query_engine(
            llm_name=self.config.llm_name,
            cutoff=self.config.cutoff,
            query_mode=self.config.query_mode,
        )
```

### 5.2 呼叫端簡化範例

**Before** (workflow.py `run_rag_build`):
```python
rag = Rag()
config = RagConfig.from_toml(config_name, **config_overrides)
# ... run_manager setup ...
with rag, save_logging_file(...), log_run_time(...):
    rag.override_init_config(webpages_data_folder_path=...)
    rag.build_nodes(chunk_size=config.chunk_size, ...)
    rag.build_vector_store(vector_store_type=config.vector_store_type, ...)
    rag.build_index(embedding_name=config.embedding_name)
    rag.build_retriever(similarity_top_k=config.similarity_top_k, ...)
    rag.build_query_engine(llm_name=config.llm_name, ...)
    rag.query(config.query, log_sources=True)
```

**After** (workflow.py `run_rag_build`):
```python
config = RagConfig.from_toml(config_name, **config_overrides)
# ... run_manager setup ...
rag = RagBuilder(config).build()
with rag, save_logging_file(...), log_run_time(...):
    rag.query(config.query, log_sources=True)
    save_module_config_as_toml(config, run_manager.module_config_toml_path)
```

**After** (webpage_retriever.py `create_webpage_retriever_tool`):
```python
config = RagConfig.from_toml(config_name, **config_overrides)
# ... run_manager setup ...
rag = RagBuilder(config).build_to_retriever()
tool = _webpage_RAG_to_retriever_tool(rag)
# ...
```

### 5.3 `run_rag_query` 的特殊處理

`run_rag_query` 有「首次建構」與「後續載入」兩條路徑。重構後寫法：

```python
def run_rag_query(config_name, force_rebuild=False, query_times=1, **config_overrides):
    config = RagConfig.from_toml(config_name, **config_overrides)
    rag = Rag()

    with rag, save_logging_file(...), log_run_time(...):
        rag.override_init_config(webpages_data_folder_path=config.webpages_data_folder_path)

        rebuild = force_rebuild or ...
        if rebuild or config.vector_store_type == "milvus":
            builder = RagBuilder(config)
            # 共用 _build_nodes / _build_vector_store / _build_index
            rag = builder.build_to_index(overwrite=(True if rebuild else False))
        else:
            # 直接載入現有 store + index
            rag.build_vector_store(..., overwrite=False)
            rag.load_index(embedding_name=config.embedding_name)

        rag.build_retriever(...)
        rag.build_query_engine(...)
        # ... query loop ...
```

這裡可以開放的作法：
- **方案 A**：`RagBuilder.build_to_index()` 封裝前 3 步驟，但 `run_rag_query` 的「不 rebuild 則不呼叫 builder」邏輯保留在外層。這是務實的方案。
- **方案 B**：`RagBuilder` 支援「從現有 store 載入」模式。但這會讓 builder 的職責變得不純。

**推薦方案 A** — 保留 `run_rag_query` 的特殊建構路徑作為例外（只有此處需要），其他兩處呼叫端完全簡化。

### 5.4 測試計畫

| 測試 ID | 測試案例 | 驗證方式 |
|---------|---------|----------|
| RB.1 | `RagBuilder(config).build()` 回傳完全初始化的 Rag | `assert rag.index is not None`, `assert rag.query_engine is not None` |
| RB.2 | `build_to_retriever()` 只建到 retriever | `assert rag.retriever is not None`, `assert rag.query_engine is None` |
| RB.3 | Context manager 整合：`with RagBuilder(config).build() as rag:` | 離開後 `rag._closed == True` |
| RB.4 | `build_to_index(overwrite=False)` 傳入 VectorStoreBuilder | 驗證 `overwrite` 被傳遞 |

---

## 6. Phase 4：輕量化 `Rag` 類別

### 6.1 最終 `Rag` 類別結構

```python
class Rag:
    """輕量化的 RAG 執行引擎。

    建構邏輯已移至 RagBuilder / NodePipelineBuilder / VectorStoreBuilder。
    Rag 只負責：
    - 設定管理（__init__、override_init_config）
    - 資源生命週期（context manager、close、__del__）
    - 執行（query、retrieve）
    - 評估（evaluate）
    - 方法保留相容性（build_nodes 等保留為委派橋接）
    """

    # __init__ — 不變
    # __enter__ / __exit__ / __del__ / close — 不變
    # override_init_config / _load_results_json — 不變
    # _file_metadata — 不變（仍被 NodePipelineBuilder 回呼）
    # _set_embed_model / _set_llm — 不變
    # query / retrieve / evaluate — 不變
    # _log_sources / _log_evaluation_result — 不變

    # build_nodes — 改為委派給 NodePipelineBuilder
    # build_vector_store — 改為委派給 VectorStoreBuilder
    # build_index / load_index — 不變（需要 self.vector_store）
    # build_retriever — 不變（保留 _build_filters 靜態方法）
    # build_query_engine — 不變
    # clean_vector_store — 改為委派給 VectorStoreBuilder
```

### 6.2 過渡期相容性

為避免一次性修改所有呼叫端，`Rag` 保留所有 `build_*` 方法，但內部委派給對應的 Builder：

```python
class Rag:
    def build_nodes(self, chunk_size=800, chunk_overlap=100, paragraph_separator="\n\n"):
        builder = NodePipelineBuilder(chunk_size, chunk_overlap, paragraph_separator)
        self.nodes = builder.build(
            md_folder_path=self.md_docs_folder_path,
            file_metadata_fn=self._file_metadata,
        )

    def build_vector_store(self, ..., hybrid_ranker_params=None):
        if hybrid_ranker_params is None:
            hybrid_ranker_params = VectorStoreBuilder.default_hybrid_ranker_params(hybrid_ranker)
        qdrant_client, vector_store = VectorStoreBuilder.build(...)
        self.qdrant_client = qdrant_client
        self.vector_store = vector_store

    def clean_vector_store(self, qdrant_db_folder_path=None, milvus_uri=None):
        VectorStoreBuilder.clean_qdrant(qdrant_db_folder_path)
        VectorStoreBuilder.clean_milvus(milvus_uri)
```

這樣的設計讓 `test_rag_refactor.py` 中的「Rag 資源管理」與「Rag 委派橋接」測試群組可以直接驗證此相容性層。

---

## 7. 驗證策略

### 7.1 執行順序

```
Phase 1 ──→ Phase 2 ──→ Phase 3 ──→ Phase 4
  │            │            │            │
  ▼            ▼            ▼            ▼
NPB 測試    VSB 測試    RB 測試 +     Rag 輕量化 +
                       呼叫端簡化     回歸測試不變
```

### 7.2 `test_rag_refactor.py` 測試結構

`test_rag_refactor.py` 取代原有的 `test_rag_issiue_recover.py`，將測試依**元件職責**而非 Issue 編號組織：

```python
# test_rag_refactor.py — 重構後的整合測試

# ── 群組 1：Rag 資源管理 ──
# - Context Manager 協定（__enter__ / __exit__ / __del__ / close 冪等性）
# - override_init_config Validate-Then-Swap（錯誤復原、狀態保留）
# - 對應原 T1.x、T2.x

# ── 群組 2：Rag 委派橋接 ──
# - build_nodes() 委派給 NodePipelineBuilder
# - build_vector_store() 委派給 VectorStoreBuilder
# - clean_vector_store() 委派給 VectorStoreBuilder
# - retrieve() 直接覆寫屬性（對應原 T3.x）

# ── 群組 3：VectorStoreBuilder 靜態方法 ──
# - resolve_embedding_dim（對應原 T6.x）
# - default_hybrid_ranker_params（對應原 T7.x）
# - build_qdrant / build_milvus
```

### 7.3 每 Phase 的驗證步驟

```bash
# 步驟 1：語法檢查
uv run pyright app/modules/rag_refactor.py

# 步驟 2：新模組單元測試
uv run pytest test/test_node_pipeline_builder.py -v
uv run pytest test/test_vector_store_builder.py -v
uv run pytest test/test_rag_builder.py -v

# 步驟 3：整合測試（Rag 資源管理 + 委派橋接）
uv run pytest test/test_rag_refactor.py -v

# 步驟 4：完整回歸（不含需要外部資源的整合測試）
uv run pytest test/ -v --ignore=test/test_main.py --ignore=test/test_module.py
```

### 7.4 安全網：在 Phase 3 呼叫端改寫完成前

所有拆出的 Builder 類別與 `Rag` 的委派橋接並存。在這期間：
- 新呼叫端（如新功能）使用 `RagBuilder` Facade
- 舊呼叫端繼續使用 `Rag.build_*()` 方法
- 兩條路徑的內部邏輯完全相同（Builder 類別是唯一實作）

---

## 8. 回歸測試矩陣

| 測試群組 | 檔案 | 測試數量 | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|---------|------|---------|---------|---------|---------|---------|
| Rag 資源管理 | `test_rag_refactor.py::TestResourceManagement` | 8 | ✅ 不變 | ✅ 不變 | ✅ 不變 | ✅ 不變 |
| Rag 委派橋接 | `test_rag_refactor.py::TestRagDelegation` | **新 4** | 🆕 Phase 1 起逐步新增 | 🆕 Phase 2 起逐步新增 | ✅ 完整 | ✅ 完整 |
| Rag 執行行為 | `test_rag_refactor.py::TestRagExecution` | 4 | ✅ 不變 | ✅ 不變 | ✅ 不變 | ✅ 不變 |
| VectorStoreBuilder 靜態方法 | `test_rag_refactor.py::TestVectorStoreStatics` | 6 | ✅ 不變 | ⚠️ 方法移動 + 測試改引用新類別 | ✅ 不變 | ✅ 不變 |
| NodePipelineBuilder | `test_node_pipeline_builder.py` | **新 6** | 🆕 新增 | ✅ 維持 | ✅ 維持 | ✅ 維持 |
| VectorStoreBuilder | `test_vector_store_builder.py` | **新 6** | — | 🆕 新增 | ✅ 維持 | ✅ 維持 |
| RagBuilder | `test_rag_builder.py` | **新 4** | — | — | 🆕 新增 | ✅ 維持 |
| 呼叫端整合 | test_module.py | 3 | ✅ 依賴 rag.py | ✅ 不變 | ⚠️ 需改為新路徑 | ✅ 通過 |

### 各 Phase 結束前需執行的命令

```bash
# Phase 1 完成後
uv run pytest test/test_rag_refactor.py test/test_node_pipeline_builder.py -v

# Phase 2 完成後
uv run pytest test/test_rag_refactor.py test/test_node_pipeline_builder.py test/test_vector_store_builder.py -v

# Phase 3 完成後（呼叫端已改寫）
uv run pytest test/ -v --ignore=test/test_main.py --ignore=test/test_module.py

# Phase 4 完成後（完整回歸）
uv run pytest test/ -v
uv run pyright app/modules/
```

---

## 9. 風險與緩解

| 風險 | 影響 | 緩解措施 |
|------|------|---------|
| **嵌入模型 API 呼叫**：`_set_embed_model` 在建構 index 時需要真實 API | 單元測試中無法測試完整 index 建構 | 使用 `unittest.mock.patch` 替換 `OpenAIEmbedding`；Builder 層級測試只驗證邏輯組合，不實際連線 |
| **Qdrant/Milvus 依賴**：`VectorStoreBuilder.build_qdrant` 需要檔案系統 | 檔案系統測試慢 | 使用 `tempfile.TemporaryDirectory`；`build_milvus` 使用 mock |
| **`run_rag_query` 的特殊路徑**：首次建構 vs 載入 vs 重建，邏輯較複雜 | 簡化時可能破壞重建判斷 | 保留 `run_rag_query` 的建構判斷在外層，只讓 `RagBuilder.build_to_index()` 封裝 3 步驟 |
| **匯入順序與循環依賴**：rag.py 匯入 `rag_refactor.py` 又反向 | ImportError | `rag_refactor.py` 不匯入 rag.py；Builder 回傳原始型別（`list[BaseNode]`、`QdrantVectorStore`），由 `Rag` 自行賦值 |
| **測試檔案路徑**：`mock_results_json` fixture 使用 `tmp_path` | 在不同環境需要確保 fixture 相容 | 保持 fixture 簽名不變；Builder 測試直接傳入路徑 |

---

## 10. 總結執行計畫

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 1 (Day 1)                                                         │
│ ┌──────────────────────┐ ┌─────────────────────────────────────────┐   │
│ │ 建立 NodePipeline     │ │ 撰寫 test_node_pipeline_builder.py +   │   │
│ │ Builder + Rag 委派橋接│ │ 執行回歸測試                            │   │
│ └──────────────────────┘ └─────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│ Phase 2 (Day 2)                                                         │
│ ┌──────────────────────┐ ┌─────────────────────────────────────────┐   │
│ │ 建立 VectorStore      │ │ 撰寫 test_vector_store_builder.py +    │   │
│ │ Builder + Rag 委派橋接│ │ 執行回歸測試                            │   │
│ └──────────────────────┘ └─────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│ Phase 3 (Day 2-3)                                                       │
│ ┌──────────────────────┐ ┌─────────────────────────────────────────┐   │
│ │ 建立 RagBuilder Facade│ │ 改寫 workflow.py 2 處 +                 │   │
│ │ + 撰寫 test_rag_builder│ │ webpage_retriever.py 1 處             │   │
│ └──────────────────────┘ └─────────────────────────────────────────┘   │
│ ┌──────────────────────┐ ┌─────────────────────────────────────────┐   │
│ │ 執行完整回歸測試       │ │ 特別驗證 run_rag_query 的特殊建構路徑    │   │
│ └──────────────────────┘ └─────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│ Phase 4 (Day 3)                                                         │
│ ┌──────────────────────┐ ┌─────────────────────────────────────────┐   │
│ │ Rag 輕量化：           │ │ 移除 rag.py 中的重複建構邏輯、          │   │
│ │ 保留委派橋接 + 執行邏輯 │ │ 減少 import 行數                      │   │
│ └──────────────────────┘ └─────────────────────────────────────────┘   │
│ ┌──────────────────────────────────────────────────────────────────┐   │
│ │ 最終回歸測試：uv run pytest test/ -v + uv run pyright app/modules│   │
│ └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```