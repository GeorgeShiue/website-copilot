# 模組 API 重構規劃 (2026/09/08)

> 本文檔基於專案中 7 項 TODO 的整理與分析，規劃一系列模組 API 重構任務。
> 核心目標：消除重複 API、統一建構入口、簡化類別設計，讓每個模組只有一個清晰的進入點。

## 1. 變更範圍總覽

```
src/app/engines/rag/rag_factory.py   ← 修改：VectorStoreBuilder 合併 API；RAGBuilder 統一入口 + 薄 wrapper 重構
src/app/workflow/workflow.py          ← 修改：run_rag_build → create_rag()；run_rag_query 改用 create_rag()；初始化 / logging 模式去重
src/app/tools/tool.py                 ← 修改：create_tool() → Tool class
src/app/tools/rag_registry.py        ← 讀取：確認 Tool class 整併後的介面
src/app/agent/agent.py                ← 修改：Agent 移除 @dataclass，改用普通 class
```

---

## 2. 動機

### 現狀問題

| 問題 | 描述 | 影響端 |
|------|------|--------|
| **API 表面積過大** | `VectorStoreBuilder` 有 `build()` + `build_milvus()` 兩個重複入口；`RAGBuilder` 有 `build()` + `build_to_retriever()` + `build_reusable()` 三個入口 | 所有呼叫端 |
| **RAGBuilder 回傳值不一致** | `build()` / `build_to_retriever()` 回傳 `RAG`，`build_reusable()` 回傳 `None`；且所有呼叫端都 discard 回傳值（因 `rag` 已是同一物件） | rag_factory.py |
| **RAGBuilder 子步驟薄 wrapper** | `build_nodes`、`build_vector_store`、`clean_vector_store` 各僅 2-4 行，只是把 `self.config` 解包傳給底層 Builder | rag_factory.py |
| **Workflow 初始化模式重複** | 4 個 `run_*` 函式重複相同的 `XConfig.from_toml()` → `RunManager.for_run()` 初始化 pattern | workflow.py |
| **Workflow logging preamble 重複** | 4 個 `run_*` 函式重複相同的 `save_logging_file` + `log_session` + `log_config` + `log_run_paths("init")` logging pattern | workflow.py |
| **Workflow 職責混雜** | `run_rag_build` 內含 query 步驟（build 應只負責建構）；`run_rag_query` 自行建構 RAG（應從外部取得） | workflow.py |
| **工具層散佈** | `create_tool()` 函式與 `RAGRegistry` 分離，工具建立邏輯分散 | tool.py, rag_registry.py |
| **類別設計過時** | `Agent` 使用 `@dataclass` 但已有較多狀態與 method，dataclass 的便利性已成負擔 | agent.py |

### 目標架構（重構後）

```
workflow.py (流程編排)
┌──────────────────────────────────────────┐
│ _create_run_context()     ← 共用初始化    │
│ run_workflow_context()    ← 共用 logging  │
│ create_rag(config_name) → RAG            │  ← 僅負責建構
│ run_rag_query(config_name) → RunManager   │  ← 查詢 + 評估 + 落盤
│ run_agent(query, ...)                     │  ← 不變（已在 0907 重構）
│ run_app(config_name)                      │  ← 不變（已在 0907 重構）
└──────────────────────────────────────────┘
                    │
                    ▼
rag_factory.py (建構引擎)
┌──────────────────────────────────────────┐
│ class VectorStoreBuilder:                 │
│   build() → MilvusVectorStore  ← 唯一入口 │
│   clean_milvus()                          │
│ class RAGBuilder:                         │
│   build_reusable(rag, force) → None       │  ← 唯一入口（取代 build）
│   build_evaluators(rag)                   │
│   (子步驟方法精簡，移除薄 wrapper)           │
└──────────────────────────────────────────┘
                    │
                    ▼
tool.py (工具層)
┌──────────────────────────────────────────┐
│ class Tool:                               │
│   __init__(registry: RAGRegistry)         │  ← 持有 registry
│   create_tools() → list[StructuredTool]   │  ← 產生工具
└──────────────────────────────────────────┘
                    │
                    ▼
agent.py (Agent 類別)
┌──────────────────────────────────────────┐
│ class Agent:  (普通 class)                │
│   __init__(graph, tools, ...)             │
│   ask() / astream_result() / save_results │
└──────────────────────────────────────────┘
```

---

## 3. 執行順序與依賴

```
Phase 1: VectorStoreBuilder 合併
  ↓  (RAGBuilder.build_vector_store 呼叫 VectorStoreBuilder.build)
Phase 2: RAGBuilder 統一入口 + 回傳值統一
  ↓  (build_reusable 為唯一入口後，再精簡子步驟薄 wrapper)
Phase 2.5: RAGBuilder 薄 wrapper 重構
  ↓  (Builder 穩定後，workflow 層級重構)
Phase 3: create_rag() + run_rag_query 重構 + 初始化/logging 去重
  ↓  (Tool class 依賴 create_rag API 穩定)
Phase 4: Tool class 整併  +  Agent class 簡化 (可並行)
```

---

## 4. Phase 1：VectorStoreBuilder API 合併

### 4-1. 現狀

```python
class VectorStoreBuilder:
    @staticmethod
    def build_milvus(
        collection_name, milvus_uri, embedding_name,
        overwrite=True, hybrid_ranker="WeightedRanker",
        hybrid_ranker_params=None,
    ) -> MilvusVectorStore:
        # 完整的 Milvus 建置邏輯（~40 行）
        ...

    @staticmethod
    def build(
        collection_name, embedding_name, milvus_uri,
        overwrite=True, hybrid_ranker="WeightedRanker",
        hybrid_ranker_params=None,
    ) -> MilvusVectorStore:
        return VectorStoreBuilder.build_milvus(...)  # ← 薄 wrapper
```

**呼叫端：**
- `RAGBuilder.build_vector_store()` 呼叫 `VectorStoreBuilder.build()`（[rag_factory.py:296](/Users/george/Desktop/Program/website-copilot/src/app/engines/rag/rag_factory.py:296)）
- `VectorStoreBuilder.build()` 內部呼叫 `build_milvus()`（[rag_factory.py:217](/Users/george/Desktop/Program/website-copilot/src/app/engines/rag/rag_factory.py:217)）

### 4-2. 目標

移除 `build()` 薄 wrapper，將 `build_milvus` 改名為 `build`，作為唯一入口。

### 4-3. 變更

| 操作 | 方法 | 說明 |
|------|------|------|
| 改名 | `build_milvus()` → `build()` | 成為唯一入口，參數不變 |
| 刪除 | `build()` | 移除薄 wrapper |
| 更新 | `RAGBuilder.build_vector_store()` | 呼叫 `VectorStoreBuilder.build()`（參數名不變，無需改動） |

### 4-4. 驗收標準

- `VectorStoreBuilder` 只剩 `build()`（原 `build_milvus` 的完整邏輯），無 `build_milvus` 殘留
- `RAGBuilder.build_vector_store()` 正常呼叫新 `build()`，無語法錯誤
- 所有既有測試通過（如有）

---

## 5. Phase 2：RAGBuilder 統一入口 + 回傳值統一

        self.build_to_retriever(rag)
        self.build_query_engine(rag)
        return rag

    def build_to_retriever(self, rag: RAG | None = None) -> RAG:  # ← 回傳 RAG
        rag = rag or self._create_rag()
        self.build_nodes(rag)
        self.build_vector_store(rag)
        self.build_index(rag)
        self.build_retriever(rag)
        return rag

    def build_reusable(self, rag: RAG, force_rebuild: bool = False) -> None:  # ← 回傳 None
        # 有條件重建 / 載入既有 index
        ...
        self.build_retriever(rag)
        self.build_query_engine(rag)
```

**呼叫端：**
- `build()` → `workflow.py:275`（`run_rag_build`）— 回傳值已 discard
- `build_reusable()` → `workflow.py:363`（`run_rag_query`）、`rag_registry.py:90`（`RAGRegistry`）— 回傳值已 discard
- `build_to_retriever()` → 僅被 `build()` 內部呼叫，無外部呼叫端

**回傳值問題：** `build()` 和 `build_to_retriever()` 回傳 `RAG`，但所有呼叫端都 discard 回傳值（因 `rag` 物件已由呼叫端持有，建構是 in-place 注入）。回傳值的存在誤導讀者以為可能回傳不同物件。

### 5-2. 目標

1. `build_reusable()` 為唯一入口。`build()` 及 `build_to_retriever()` 刪除。
2. 所有公開 build 方法統一回傳 `None`（`rag` 的狀態變更為 in-place 注入）。

### 5-3. 變更

| 操作 | 方法 | 說明 |
|------|------|------|
| 保留 | `build_reusable(rag, force_rebuild)` | 唯一入口，參數不變，回傳 `None` |
| 刪除 | `build(rag)` | 呼叫端改用 `build_reusable(rag, force_rebuild=True)` |
| 刪除 | `build_to_retriever(rag)` | 僅被 `build()` 使用，隨之刪除 |

### 5-4. 呼叫端影響

| 呼叫端 | 檔案:行 | 變更 |
|--------|---------|------|
| `run_rag_build` | workflow.py:275 | `builder.build(rag)` → `builder.build_reusable(rag, force_rebuild=True)` |
| `run_rag_query` | workflow.py:363 | 不變（已使用 `build_reusable`） |
| `RAGRegistry` | rag_registry.py:90 | 不變（已使用 `build_reusable`） |

### 5-5. 驗收標準

- `RAGBuilder` 只剩 `build_reusable()` 及其子步驟方法（`build_nodes`、`build_vector_store` 等）
- `build()` 和 `build_to_retriever()` 已刪除
- `run_rag_build` 改用 `build_reusable(rag, force_rebuild=True)` 後功能不變
- `RAGBuilder` 所有公開 build 方法回傳值一致（全部為 `None`）
- 所有既有測試通過

---

## 6. Phase 2.5：RAGBuilder 薄 wrapper 重構

> 此 Phase 在 Phase 2 完成後執行。此時 `RAGBuilder` 只剩 `build_reusable()` + 子步驟方法，
> 是審視並精簡薄 wrapper 的最佳時機。

### 6-1. 現狀

Phase 2 完成後，`RAGBuilder` 的子步驟方法狀態：

| `load_index(rag)` | ~9 行 | 從 vector store 載入 index，賦值 `rag.index` |
| `build_retriever(rag)` | ~26 行 | 建 `VectorIndexRetriever`，賦值 `rag.retriever` |
| `build_query_engine(rag)` | ~22 行 | 建 LLM + response_synthesizer + query engine，賦值 `rag.query_engine` |
| `build_evaluators(rag)` | ~18 行 | 建 faithfulness + relevancy evaluator，賦值 `rag.evaluators` |

**問題：** `build_nodes`、`build_vector_store`、`clean_vector_store` 都是 2-15 行的薄 wrapper，只是把 `self.config` 解包傳給底層 Builder，再把結果賦值給 `rag`。三層間接呼叫鏈：`RAGBuilder.build_vector_store` → `VectorStoreBuilder.build` → `VectorStoreBuilder.build_milvus`。

### 6-2. 目標

精簡薄 wrapper，讓 `RAGBuilder` 的子步驟方法各自承擔完整邏輯，或讓底層 Builder 直接持有 config。

### 6-3. 候選方案

| 方案 | 做法 | 優點 | 缺點 |
|------|------|------|------|
| **A：底層 Builder 持有 config** | `NodePipelineBuilder(config)` / `VectorStoreBuilder(config)` 在 constructor 接收 config，`build(rag)` 不需再傳 config 欄位 | 減少參數傳遞；底層 Builder 可自行驗證 config | 改動面較大；`VectorStoreBuilder` 目前是 static methods |
| **B：保留 wrapper 但精簡** | 保留 `build_nodes` 等方法，但將 logging / 錯誤處理下沉到底層 Builder | 改動面小；保持 `RAGBuilder` 作為 facade 的角色 | 薄 wrapper 仍然存在 |
| **C：合併進 `build_reusable`** | 將 `build_nodes`、`build_vector_store` 等的邏輯直接寫入 `build_reusable` 的重建分支中 | 消除 wrapper；流程一目了然 | `build_reusable` 會變長（~80 行）；失去子步驟的可單獨測試性 |

**建議：方案 B**（低風險、漸進式），在 Phase 2.5 先精簡，後續視情況升級為方案 A。

### 6-4. 具體變更（方案 B）

| 方法 | 變更 |
|------|------|
| `build_nodes(rag)` | 將 logging 下沉，移除多餘的 config 解包（若方案 A 則由 `NodePipelineBuilder` 自行持有 config） |
| `build_vector_store(rag)` | 同上 |
| `clean_vector_store(rag)` | 不變（已足夠精簡） |
| `build_index` / `load_index` / `build_retriever` / `build_query_engine` | 這些方法已有足夠邏輯，維持不變 |

### 6-5. 驗收標準

- `RAGBuilder` 的薄 wrapper 方法（`build_nodes`、`build_vector_store`）已精簡或消除
- `build_reusable()` 的流程不變，功能不變
- 所有既有測試通過

---

## 7. Phase 3：create_rag() 與 run_rag_query 重構

### 7-1. 現狀

```python
# workflow.py — run_rag_build（目前）
def run_rag_build(config_name, ..., **config_overrides) -> RunManager:
    config = RAGConfig.from_toml(config_name, **config_overrides)
    run_manager = RunManager.for_run(module="rag_build", ...)
    rag = RAG(webpages_data_folder_path=config.webpages_data_folder_path or "")
    with (rag, ...):
        builder = RAGBuilder(config)
        builder.build(rag)              # ← 建構
        rag.query(config.query, ...)     # ← 不該在此
        run_manager.save_results_as_json(...)
        ...
    rag = RAG(webpages_data_folder_path=config.webpages_data_folder_path or "")  # ← 自行建構
    with (rag, ...):
        builder = RAGBuilder(config)
        builder.build_reusable(rag, force_rebuild=force_rebuild)  # ← 重複建構邏輯
        builder.build_evaluators(rag)
        for i in range(query_times):
            response = rag.query(config.query, ...)
            faithfulness, relevancy = rag.evaluate(...)
            ...
    return run_manager
```

**額外問題：**

- **初始化模式重複（A3）**：4 個 `run_*` 函式（`run_website_crawler`、`run_webpage_image_summarizer`、`run_rag_build`、`run_rag_query`）重複相同的初始化 pattern：
  ```python
  config = XConfig.from_toml(config_name, **config_overrides)
  run_name = config.config_name if run_name_use_config_name else config.run_name
  run_manager = RunManager.for_run(module="...", site_id=config.site_id, run_name=run_name)
  ```
- **Logging preamble 重複（A4）**：4 個 `run_*` 函式重複相同的 logging pattern：
  ```python
  with (
      save_logging_file(run_manager.log_path),
      log_run_time(run_title),
  ):
      log_session(f"...({config_name})", style="purple")
      log_config("... Config Loaded from toml", config)
      log_session("Run Paths", style="cyan")
      run_manager.log_run_paths("init")
  ```

### 7-2. 目標

1. 將 `run_rag_build` 的建構邏輯抽出為 `create_rag()` 函式，僅負責建構
2. 移除 `run_rag_build` 中的 query 環節（build 函式不應查詢）
3. `run_rag_query` 改用 `create_rag()` 取得 RAG 實例，不再自行建構
4. **抽出共用的初始化 helper（A3）**：統一 `config + RunManager` 的建立模式
5. **抽出共用的 logging context manager（A4）**：統一 workflow 層的 logging pattern

### 7-3. 目標 API

#### 7-3-1. `create_rag()`

```python
def create_rag(
    config_name: str = "default",
    force_rebuild: bool = False,
    webpages_data_use_latest_results: bool = False,
    save_vector_store_to_runs: bool = False,
    data_manager: DataManager | None = None,
    **config_overrides,
) -> RAG:
    """建立並建構 RAG 實例（含 nodes、vector store、index、retriever、query engine）。

    流程：RAGConfig → RAG → RAGBuilder.build_reusable → build_evaluators
    不包含 query 步驟（由呼叫端負責）。

    Args:
        config_name: RAGConfig 名稱（對應 configs/rag/{name}.toml）。
        force_rebuild: 是否強制重建向量庫。
        webpages_data_use_latest_results: 是否使用最新的 webpage 資料。
        save_vector_store_to_runs: 是否將向量庫儲存到 runs/ 目錄。
        data_manager: DataManager 實例（可選，用於取得最新資料路徑）。
        **config_overrides: RAGConfig 覆寫值（含 site_id）。

    Returns:
        已建構完成的 RAG 實例（呼叫端需負責 close）。
    """
    config = RAGConfig.from_toml(config_name, **config_overrides)

    # 解決 webpages 資料路徑
    if webpages_data_use_latest_results:
        if data_manager is None:
            raise ValueError(
                "data_manager is required when webpages_data_use_latest_results=True"
            )
        config.webpages_data_folder_path = data_manager.get_webpages_path(config.site_id)

    # 解決向量庫存放位置
    if save_vector_store_to_runs:
        run_manager = RunManager.for_run(
            module="rag_build", site_id=config.site_id, run_name=config.config_name,
        )
        config.milvus_uri = os.path.join(run_manager.results_folder_path, "milvus.db")

    rag = RAG(webpages_data_folder_path=config.webpages_data_folder_path or "")
    builder = RAGBuilder(config)
    builder.build_reusable(rag, force_rebuild=force_rebuild)
    builder.build_evaluators(rag)
    return rag
```

#### 7-3-2. `_create_run_context()`（A3）

```python
def _create_run_context(
    config_class: type[BaseConfig],
    config_name: str,
    module: str,
    run_name_use_config_name: bool = False,
    **config_overrides,
) -> tuple[BaseConfig, RunManager]:
    """共用的 workflow 初始化：建立 config + RunManager。

    取代 4 個 run_* 函式中重複的初始化 pattern。
    """
    config = config_class.from_toml(config_name, **config_overrides)
    run_name = config.config_name if run_name_use_config_name else config.run_name
    run_manager = RunManager.for_run(
        module=module, site_id=config.site_id, run_name=run_name,
    )
    return config, run_manager
```

#### 7-3-3. `run_workflow_context()`（A4）

```python
@contextmanager
def run_workflow_context(
    run_manager: RunManager,
    config: BaseConfig,
    config_name: str,
    run_title: str,
):
    """共用的 workflow logging context manager。

    取代 4 個 run_* 函式中重複的 logging preamble。
    """
    with (
        save_logging_file(run_manager.log_path),
        log_run_time(run_title),
    ):
        log_session(run_title, style="purple")
        log_config(f"{config.__class__.__name__} Loaded from toml", config)
        log_session("Run Paths", style="cyan")
        run_manager.log_run_paths("init")
        yield
```

### 7-4. run_rag_query 變更

```python
# BEFORE
def run_rag_query(config_name, ..., **config_overrides) -> RunManager:
    ...
    rag = RAG(webpages_data_folder_path=config.webpages_data_folder_path or "")
    with (rag, ...):
        builder = RAGBuilder(config)
        builder.build_reusable(rag, force_rebuild=force_rebuild)
        builder.build_evaluators(rag)
        ...

# AFTER
def run_rag_query(config_name, ..., **config_overrides) -> RunManager:
    config, run_manager = _create_run_context(
        RAGConfig, config_name, module="rag_query",
        run_name_use_config_name=run_name_use_config_name,
        **config_overrides,
    )

    rag = create_rag(config_name, force_rebuild=force_rebuild, **config_overrides)
    with (
        rag,
        run_workflow_context(run_manager, config, config_name, f"RAG Query ({config_name})"),
    ):
        for i in range(query_times):
            response = rag.query(config.query, ...)
            faithfulness, relevancy = rag.evaluate(...)
            ...
    return run_manager
```

### 7-5. run_rag_build 處置

`run_rag_build` 將完全刪除，不保留 wrapper。原本的建構與落盤流程改由各呼叫端直接處理：
- **建構**：呼叫 `create_rag()`
- **落盤**：由呼叫端在 `create_rag()` 後直接執行

#### 呼叫端遷移

| 檔案與行號 | 變更 |
|------------|------|
| `src/main.py:84` | 將 `run_rag_build(...)` 改為 `create_rag(...)` + 直接落盤 |
| `src/cli.py:108` | 將 `run_rag_build(...)` 改為 `create_rag(...)` + 直接落盤 |
| `src/test/test_main.py:25` | 更新 import，並將呼叫改為 `create_rag` |
| `src/test/test_module.py:29` | 更新 import，並將呼叫改為 `create_rag` |
| `src/test/dev/test_multi_site.py:137` | 更新 import，並將呼叫改為 `create_rag` |

### 7-6. 驗收標準

- `create_rag()` 存在，僅執行建構流程（nodes → vector store → index → retriever → query engine → evaluators），不包含 `rag.query()`
- `run_rag_query` 內部透過 `create_rag()` 取得 RAG 實例，不直接呼叫 `RAGBuilder`
- `run_rag_build` 已從所有檔案（workflow.py、main.py、cli.py、tests）移除
- `_create_run_context()` 存在，4 個 `run_*` 函式的初始化 pattern 已統一
- `run_workflow_context()` 存在，4 個 `run_*` 函式的 logging pattern 已統一
- `RAGRegistry` 的 `build_reusable` 呼叫不受影響（Phase 2 已穩定）

---

## 8. Phase 4A：Tool class 整併

### 8-1. 現狀

```python
# tool.py
def create_tool(registry: RAGRegistry) -> list[StructuredTool]:
    discovery_tool = create_site_discovery_tool(registry)
    retriever_tool = create_webpage_retriever_tool(registry)
    return [discovery_tool, retriever_tool]

# rag_registry.py
class RAGRegistry:
    def get(self, site_id: str) -> RAG: ...
    def list_sites(self) -> list[str]: ...
    def close(self) -> None: ...
```

**呼叫端：**
- `workflow.py:480`（`run_agent`）：`tools = create_tool(registry)`
- `workflow.py:554`（`run_app`）：`tools = create_tool(registry)`
- `test/dev/test_create_tool.py`：4 處測試呼叫

    def __init__(self, registry: RAGRegistry) -> None:
        self.registry = registry
        self._tools: list[StructuredTool] | None = None

    def create_tools(self) -> list[StructuredTool]:
        """建立 discovery + retriever 工具（lazy，僅建立一次）。"""
        if self._tools is None:
            self._tools = [
                create_site_discovery_tool(self.registry),
                create_webpage_retriever_tool(self.registry),
            ]
        return self._tools

    @property
    def tools(self) -> list[StructuredTool]:
        """取得工具列表（自動建立）。"""
        return self.create_tools()
```

### 8-4. 呼叫端影響

| 呼叫端 | 檔案:行 | BEFORE | AFTER |
|--------|---------|--------|-------|
| `run_agent` | workflow.py:480 | `tools = create_tool(registry)` | `tool = Tool(registry)` → `tool.tools` |
| `run_app` | workflow.py:554 | `tools = create_tool(registry)` | `tool = Tool(registry)` → `tool.tools` |
| 測試 | test_create_tool.py | `create_tool(registry=mock_registry)` | `Tool(mock_registry).tools` |

### 8-5. 驗收標準

- `Tool` class 存在於 `tool.py`，`__init__` 接收 `RAGRegistry`
- `Tool` 持有 registry 並提供 `create_tools()` / `tools` 屬性
- `create_tool()` 函式已移除
- `run_agent`、`run_app` 改用 `Tool(registry).tools`
- 所有既有測試通過

---

## 9. Phase 4B：Agent class 簡化（可與 4A 並行）

### 9-1. 現狀

```python
@dataclass
class Agent:
    graph: Any
    tools: list[StructuredTool]
    run_manager: RunManager
    config: AgentConfig
    checkpointer: InMemorySaver = field(default_factory=InMemorySaver)

    def ask(self, query, thread_id=None) -> dict: ...
    async def astream_text(self, query, config) -> AsyncIterator[str]: ...
    async def astream_result(self, query, thread_id, ...) -> dict: ...
    def save_results(self, results, thread_id=None) -> None: ...
    def close(self) -> None: ...
```

### 9-2. 目標

移除 `@dataclass`，改為普通 class。原因：Agent 已有 5 個屬性 + 5 個 method，dataclass 的自動 `__init__` / `__repr__` 等便利性已不足以下衡其帶來的隱晦性（屬性無預設值驗證、無自訂初始化邏輯）。

### 9-3. 變更

```python
# BEFORE
@dataclass
class Agent:
    graph: Any
    tools: list[StructuredTool]
    run_manager: RunManager
    config: AgentConfig
    checkpointer: InMemorySaver = field(default_factory=InMemorySaver)
        checkpointer: InMemorySaver | None = None,
    ) -> None:
        self.graph = graph
        self.tools = tools
        self.run_manager = run_manager
        self.config = config
        self.checkpointer = checkpointer or InMemorySaver()
```

### 9-4. 呼叫端影響

| 呼叫端 | 變更 |
|--------|------|
| `create_agent()` (agent.py) | 不變（已使用 `Agent(graph, tools, ...)` 位置參數） |
| 所有測試 | 不變（dataclass 和普通 class 的位置參數建構方式相同） |

### 9-5. 驗收標準

- `Agent` class 無 `@dataclass` 裝飾器
- 使用明確定義的 `__init__`，含型別提示
- `checkpointer` 預設為 `None`，`__init__` 內 fallback 為 `InMemorySaver()`
- `from dataclasses import dataclass, field` 可從 import 列表移除
- 所有既有測試通過

