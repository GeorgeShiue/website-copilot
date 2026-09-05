# 多站 RAG 工具規劃 (2026/08/26)

> 本文檔為 `2026_0819-multi_site_RAG.md` 目標 3（M3：多站 RAG 檢索）的實作規劃。
> 核心改造範圍：`RAGRegistry` 多站管理、`webpage_retriever` 多站路由、`list_knowledge_bases` 站點發現、Agent 整合。

---

## 1. 變更範圍總覽

```
src/app/tools/rag_registry.py       ← 新增：RAGRegistry（多站 RAG 實例管理）
src/app/tools/webpage_retriever.py  ← 修改：RetrieverInputSchema + tool 改用 registry
src/app/agent/agent.py              ← 修改：create_site_discovery_tool + create_agent + Agent
src/app/configs/agent_config.py     ← 修改：DEFAULT_SYSTEM_PROMPT（多站路由版）
configs/agent/default.toml          ← 修改：system_prompt
configs/agent/test.toml             ← 修改：system_prompt
```

---

## 2. 模組一：RAGRegistry — 多站 RAG 實例管理

### 2-1. 動機

M2 完成後，資料與向量庫已按 site_id 隔離（`data/webpages/{site_id}/`、`data/rag/{site_id}/`），但 Agent 工具層仍硬綁單一 RAG 實例。需要一個 Registry 管理多站 RAG 的延遲建立、LRU 快取與生命週期。

**現狀問題：**
- `create_webpage_retriever_tool()` 硬綁一個 `config_name="default"` → 一個 RAG 實例
- 每次 tool 呼叫都需重建 RAG（~30s），無法利用 Milvus 重用機制
- 無法同時存取多個站的知識庫

### 2-2. 設計

安放位置：`src/app/tools/rag_registry.py`。

```python
class RAGRegistry:
    """管理多站 RAG 實例（lazy + LRU 快取）。

    Attributes:
        _cache: site_id → RAG 的 LRU 快取（OrderedDict）
        _configs: site_id → RAGConfig 的快取（避免重複 from_toml）
    """

    def __init__(
        self,
        data_manager: DataManager | None = None,
        default_config_name: str = "default",
        max_cached: int = 5,
    ) -> None: ...

    def list_sites(self) -> list[str]: ...
    def get(self, site_id: str) -> RAG: ...
    def close(self) -> None: ...
```

**`get(site_id)` 流程：**

1. 檢查 `_cache` 命中 → `move_to_end` 更新 LRU 順序 → 直接回傳
2. `DataManager.site_exists(site_id)` → 不存在則 `ValueError`
3. `RAGConfig.from_toml(default_config_name, site_id=site_id)` — 路徑由 site_id 動態產生
4. `RAG(webpages_data_folder_path=config.webpages_data_folder_path)`
5. `RAGBuilder(config).build_reusable(rag, force_rebuild=False)` — 利用 §14 的 Milvus 重用機制
6. 存入 `_cache` → 若超出 `max_cached` 則 `popitem(last=False)` eviction

### 2-3. 關鍵設計決策

| 決策 | 選擇 | 理由 |
|------|------|------|
| 快取資料結構 | `OrderedDict`（手動 LRU） | 比 `functools.lru_cache` 更可控，支援 eviction 時釋放 RAG |
| RAG 路徑來源 | 直接指向 `data/rag/{site_id}/` | Agent 問答不經 runs/ 中間層，直接指向正式資料 |
| Config 建立 | `RAGConfig.from_toml("default", site_id=site_id)` | 用 default 設定 + override site_id，避免每個站都要一份 config |
| Build 策略 | `build_reusable(force_rebuild=False)` | Milvus 重用：skip nodes pipeline，`load_collection()` 約 13s |
| 不需 RunManager | Registry 不建立 RunManager | Agent 問答指向正式 data/；RunManager 僅供建庫流程使用 |

### 2-4. 記憶體管理

- `max_cached=5` 限制同時載入的 RAG 實例數量
- 每個 RAG 實例佔用：Milvus 連線 + embedding model reference + index reference
- eviction 時呼叫 `rag.close()` 釋放所有資源
- 未來可改為 `max_cached` 從 AgentConfig 讀取

---

## 3. 模組二：webpage_retriever.py — 多站路由

### 3-1. RetrieverInputSchema 變更

新增 `site_id: str` 參數（必要）：

```python
class RetrieverInputSchema(BaseModel):
    site_id: str = Field(
        description=(
            "目標知識庫的 site_id（如 'nculab'、'ncucsie'）。"
            "可先呼叫 list_knowledge_bases 取得可用站點列表。"
            "若使用者問題來自特定網站，通常已有隱含的 site_id 語境。"
        ),
    )
    query: str = Field(description="搜尋查詢字串")
    filter_dict: dict[str, Any] | None = Field(default=None, ...)
    similarity_top_k: int | None = Field(default=None, ...)
```

### 3-2. `create_webpage_retriever_tool` 簽名變更

```python
# BEFORE（~90 行，含 RunManager / config / RAGBuilder / 隔離邏輯）
def create_webpage_retriever_tool(
    run_manager: RunManager | None = None,
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    **config_overrides,
) -> StructuredTool:
    config = RAGConfig.from_toml(config_name, **config_overrides)
    # ... ~50 行初始化 ...
    rag = RAGBuilder(config).build_to_retriever()
    tool = _webpage_retriever_to_tool(rag)
    return tool

# AFTER（~30 行，Registry 延遲載入）
def create_webpage_retriever_tool(
    registry: RAGRegistry,
) -> StructuredTool:
    def _retrieve(site_id, query, filter_dict=None, similarity_top_k=None):
        rag = registry.get(site_id)
        results = rag.retrieve(query=query, filter_dict=filter_dict, ...)
        return _format_retrieval_results(results)

    tool = StructuredTool(
        name="webpage_retriever",
        description="檢索指定知識庫中與查詢相關的內容。必須提供 site_id 參數。",
        args_schema=RetrieverInputSchema,
        func=_retrieve,
    )
    return tool
```

**精簡幅度**：從 ~90 行精簡至 ~30 行。RunManager、config 載入、vector store 隔離等全部移至 RAGRegistry。

### 3-3. Tool description 變更

```
# BEFORE
"檢索網站網頁中與查詢相關的內容。可透過 filter_dict 過濾特定頁面類型..."

# AFTER
"檢索指定知識庫中與查詢相關的內容。必須提供 site_id 參數指定目標知識庫。"
"可先呼叫 list_knowledge_bases 確認可用的 site_id。回傳的內容包含原始片段與來源 URL。"
```

---

## 4. 模組三：agent.py — 站點發現工具與 Agent 整合

### 4-1. `create_site_discovery_tool`（新增）

```python
def create_site_discovery_tool(registry: RAGRegistry) -> StructuredTool:
    """建立 list_knowledge_bases 工具。掃描 data/rag/ 回傳所有可用 site_id。"""
    def _list_sites() -> str:
        sites = registry.list_sites()
        if not sites:
            return "目前沒有可用的知識庫。"
        return "可用的知識庫：" + "、".join(sites)

    return StructuredTool(
        name="list_knowledge_bases",
        description="列出所有可用的知識庫站點。在呼叫 webpage_retriever 前應先確認可用的 site_id。",
        func=_list_sites,
    )
```

### 4-2. `create_agent` 流程變更

```python
# BEFORE
tool = create_webpage_retriever_tool(
    run_manager=run_manager, config_name="default", ...)
graph = create_agent(llm, [tool], system_prompt=config.system_prompt, ...)
return Agent(graph=graph, tool=tool, ...)

# AFTER
from app.tools.rag_registry import RAGRegistry

registry = RAGRegistry(DataManager())
discovery_tool = create_site_discovery_tool(registry)
retriever_tool = create_webpage_retriever_tool(registry)
graph = create_agent(
    llm, [discovery_tool, retriever_tool],
    system_prompt=config.system_prompt, ...)
return Agent(
    graph=graph, tools=[discovery_tool, retriever_tool],
    registry=registry, ...)
```

### 4-3. Agent dataclass 擴充

```python
@dataclass
class Agent:
    graph: Any
    tools: list[StructuredTool]             # 改為 list（原 tool: Any）
    run_manager: RunManager
    config: AgentConfig
    checkpointer: InMemorySaver = field(default_factory=InMemorySaver)
    registry: RAGRegistry | None = None     # 新增

    def close(self) -> None:
        if self.registry is not None:
            self.registry.close()
```

### 4-4. System Prompt 更新

```python
DEFAULT_SYSTEM_PROMPT = (
    "你是多站網站助理，可從多個學校網站知識庫中檢索資訊。\n\n"
    "## 使用工具的流程\n"
    "1. 若不確定有哪些可用的知識庫，先使用 list_knowledge_bases 查詢\n"
    "2. 使用 webpage_retriever 時必須提供 site_id 參數\n"
    "3. 若問題來自特定網站（如對話中有 site 語境），直接使用該 site 檢索\n\n"
    "## 回答規則\n"
    "- 根據檢索結果回答，必須列出參考來源的 URL\n"
    "- 若檢索結果不足以回答，請誠實說明\n"
    "- 若問題可能涉及多個站點，可分別檢索後合併回答"
)
```

`configs/agent/default.toml` 與 `configs/agent/test.toml` 同步更新。

---

## 5. 資料流變更概要

```
[改動前]
Agent query → create_webpage_retriever_tool(config_name="default")
            → RAGBuilder.build_to_retriever() → 單一 RAG 實例
            → rag.retrieve(query) → 回傳結果

[改動後]
Agent query → webpage_retriever(site_id="nculab", query="...")
            → RAGRegistry.get("nculab")
              ├─ 快取命中 → 直接回傳已有 RAG（<1ms）
              └─ 快取未命中 → RAGConfig + RAG + build_reusable（~13s）
            → rag.retrieve(query) → 回傳結果
```

---

## 6. 影響範圍

### 6-1. 向後相容性

| 呼叫點 | 影響 |
|--------|------|
| `create_agent()` | **改動**：建立 Registry + 兩個工具 |
| `run_agent()` (workflow.py) | **不受影響**：`agent.close()` 呼叫不變，內部改為 `registry.close()` |
| `app.py` (Server) | **Phase 4 改動**：此階段不受影響 |
| `run_rag_query()` (workflow.py) | **不受影響**：使用 `build_reusable()` 開獨立 RAG |
| `run_rag_build()` (workflow.py) | **不受影響**：使用 `build()` 全新建構 |

### 6-2. 不需改動的檔案

- `src/app/engines/rag/rag.py` — RAG 類別不變
- `src/app/engines/rag/rag_factory.py` — RAGBuilder / build_reusable 不變
- `src/app/configs/rag_config.py` — RAGConfig 不變
- `src/app/workflow/data_manager.py` — DataManager 不變
- `src/cli.py` — CLI 分派邏輯不變

---

## 7. 實作順序

```
Step 1: 新建 rag_registry.py
        → RAGRegistry 類別（lazy + LRU + close）

Step 2: 修改 webpage_retriever.py
        → RetrieverInputSchema 加 site_id
        → create_webpage_retriever_tool 改接收 RAGRegistry

Step 3: 修改 agent.py
        → create_site_discovery_tool()
        → create_agent 建立 Registry + 兩個工具
        → Agent 加 registry 欄位

Step 4: 更新 system prompt
        → agent_config.py DEFAULT_SYSTEM_PROMPT
        → configs/agent/default.toml
        → configs/agent/test.toml

Step 5: 測試
        → test_rag_registry.py（unit: mock DataManager）
        → test_multi_site_tool.py（integration: 真實 Milvus）
        → 端到端：Agent query 帶 site_id 前綴 → 正確路由
```

---

## 8. 測試策略

| 測試類型 | 對象 | 驗證內容 |
|---------|------|---------|
| **單元測試** | `RAGRegistry.get()` | cache hit / eviction / site not found ValueError |
| **單元測試** | `RAGRegistry.close()` | 所有 RAG 實例正確釋放 |
| **單元測試** | `resolve_site_id()` | 各種 hostname 映射（精確 + suffix） |
| **整合測試** | `webpage_retriever(site_id="nculab")` | 真實 Milvus，僅回傳 nculab 結果 |
| **整合測試** | 同一 tool 換站 | 先查 nculab 再查 ncucsie，結果不混雜 |
| **端到端** | CLI Agent | query 帶 `[使用者瀏覽 nculab 網站]` → 正確路由 |
| **效能測試** | Registry 快取 | 第二次查同站 < 3s（cache hit）；首次 ~13s |

---

## 9. 風險與緩解

| # | 風險 | 影響 | 緩解 |
|---|------|------|------|
| 1 | Milvus 首次載入慢 | 首次查詢某站 ~13s（load_collection + build retriever） | Agent 啟動時可 pre-warm 常用站（未來優化） |
| 2 | LRU eviction 後再查 | 被 eviction 的站再次查詢需重建 | max_cached=5 足夠目前 2 站規模 |
| 3 | LLM 不跟隨前綴指引 | 選錯 site_id 或忽略語境 | system prompt 強化指引；list_knowledge_bases 工具輔助 |
| 4 | RAG 實例 close 時序 | eviction 時 RAG 仍在使用 | OrderedDict 確保同 thread 安全；未來可加 reference counting |
