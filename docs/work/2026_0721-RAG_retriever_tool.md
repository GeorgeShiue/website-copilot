# RAG Retriever Tool (2026/07/21)

## 待辦事項

- [ ] Phase 1: Rag 類別新增 `retrieve()` 方法
- [ ] Phase 2: Tool Wrapper 模組
- [ ] Phase 3: Workflow 函數
- [ ] Phase 4: CLI 整合（可選）
- [ ] Phase 5: Agent 整合範例

## 概述

將當前已實作完成的 RAG 系統包裝為 Agent 可呼叫的工具，封裝範圍僅到 retriever 層級（不含 LLM 生成），使下游 Agent 可動態選擇檢索策略與 metadata 過濾條件。

### 對應升級文件

- **父文件**：[`2026_0721-RAG_Upgrade.md`](./2026_0721-RAG_Upgrade.md) §三、檢索工具封裝
- **上游文件**：[`2026_0721-RAG_Upgrade.md`](./2026_0721-RAG_Upgrade.md) §四、Agent 通訊介面（定義了本工具將遵循的 `messages` 協議）
- **下游文件**：[`2026_0721-RAG_Upgrade.md`](./2026_0721-RAG_Upgrade.md) §六、多步推理代理化（本工具為 Agentic RAG 的檢索元件）

### 修改的檔案

| 檔案 | 變更類型 | 說明 |
|------|---------|------|
| `app/modules/rag.py` | **新增方法** | 新增 `retrieve()` 方法 |
| `app/tools/rag_retriever_tool.py` | **新檔案** | Tool wrapper 模組 |
| `app/workflow/workflow.py` | **新增函數** | 新增 `run_rag_retriever_tool()` |
| `app/workflow/workflow_config.py` | **可選** | 新增 `RagRetrieverRunConfig` |
| `cli.py` | **可選** | 新增 CLI 入口 |

---

## Phase 1: Rag 類別新增 `retrieve()` 方法

### 修改檔案

`app/modules/rag.py`

### 定位

在 `build_query_engine()` 方法之後、`evaluate()` 方法之前插入新方法。

`retrieve()` 與現有 `query()` 的對比：

| 方法 | 底層呼叫 | 回傳型別 | 是否呼叫 LLM |
|------|---------|---------|-------------|
| `query()` | `RetrieverQueryEngine.query()` | `Response` | ✅ |
| `retrieve()` | `VectorIndexRetriever.retrieve()` | `list[dict]` | ❌ |

### 新增的 import

在 `rag.py` 頂部的 import 區塊無需新增——所需符號（`VectorStoreQueryMode`、`extract_sources_info`）已存在。

### 程式碼

```python
def retrieve(
    self,
    query: str,
    filter_dict: dict[str, Any] | None = None,
    similarity_top_k: int | None = None,
) -> list[dict[str, Any]]:
    """檢索相關節點，不回傳 LLM 生成結果。

    回傳結構化 dict 列表（非原始 NodeWithScore），
    讓外部工具層可以序列化，不需依賴 LlamaIndex 型別。
    支援執行期動態 filter_dict 覆寫（暫時重建 retriever）。

    Args:
        query: 搜尋查詢字串。
        filter_dict: 可選的 metadata 過濾條件 dict。
            格式與 build_retriever() 的 filter_dict 完全相同：
            - 純值 → EQ: {"page_type": "paper"}
            - tuple → 自訂 operator: {"year": (2024, FilterOperator.GTE)}
            - list tuple → IN: {"page_type": (["paper", "announcement"], FilterOperator.IN)}
            傳 None 則沿用既有 retriever 的 filter 設定（若無則不過濾）。
        similarity_top_k: 可選的 top-k 覆寫值。傳 None 則沿用既有設定。

    Returns:
        list[dict]: 每個 dict 包含 page_title、score、page_type、content、url。
    """
    if self.retriever is None:
        raise RuntimeError("Retriever has not been built, cannot retrieve")

    # 執行期參數覆寫 — 暫時重建 retriever
    if filter_dict is not None or similarity_top_k is not None:
        if similarity_top_k is None:
            similarity_top_k = self.retriever.similarity_top_k
        # 從既有 retriever 取 query_mode / hybrid_top_k / alpha
        query_mode = (
            "hybrid"
            if self.retriever._vector_store_query_mode
            == VectorStoreQueryMode.HYBRID
            else "default"
        )
        hybrid_top_k = getattr(self.retriever, "_hybrid_top_k", 10)
        alpha = getattr(self.retriever, "_alpha", 0.5)
        self.build_retriever(
            query_mode=query_mode,
            similarity_top_k=similarity_top_k,
            hybrid_top_k=hybrid_top_k,
            alpha=alpha,
            filter_dict=filter_dict,
        )

    nodes = self.retriever.retrieve(query)

    results = []
    for node in nodes:
        page_title, score, page_type = extract_sources_info(node)
        results.append({
            "page_title": page_title,
            "score": score,
            "page_type": page_type,
            "content": node.node.get_content(),
            "url": node.node.metadata.get("page_url", ""),
        })
    return results
```

### 設計決策紀錄

| 決策 | 選項 | 選擇理由 |
|------|------|---------|
| 回傳型別 | `list[dict]` vs `list[NodeWithScore]` | 避免外部工具層依賴 LlamaIndex 型別，方便序列化 |
| filter_dict 覆寫策略 | 修改 `self.retriever` vs 每次建立臨時 retriever | 簡潔且 Agent 多為序列化呼叫；未來若需純函數式可改為臨時 retriever |
| 重建時參數來源 | 從既有 retriever 讀取 vs 從 config 讀取 | 確保執行期覆寫不意外變更未指定的參數 |

### 邊界處理

| 情境 | 行為 |
|------|------|
| `self.retriever is None` | 拋出 `RuntimeError` |
| `filter_dict=None` 且 `similarity_top_k=None` | 直接呼叫既有 retriever，不重建 |
| `filter_dict=None` 但 `similarity_top_k=20` | 重建 retriever，沿用既有 filter 行為 |
| `filter_dict={} ` | 等同於 None，不重建 |
| `filter_dict={"page_type": "nonexistent"}` | 回傳空列表 `[]` |
| 節點缺少 `page_url` metadata | 該欄位回傳空字串 `""` |

---

## Phase 2: Tool Wrapper 模組

### 新檔案

`app/tools/rag_retriever_tool.py`

### 目錄結構

建立新的 `app/tools/` 目錄，未來 Phase 4 的 Graph RAG Tool 也將放置於此：

```
app/
├── modules/
├── configs/
├── workflow/
└── tools/                    ← 新增
    ├── __init__.py           ← 新增（空檔案，使目錄成為 Python 套件）
    └── rag_retriever_tool.py ← 本次新增
```

### 完整程式碼

```python
"""RAG Retriever Tool — 將 LlamaIndex retriever 包裝為 LangChain StructuredTool。

此模組提供：
- RetrieverInput: Pydantic schema，定義 Agent 呼叫工具時的輸入格式
- format_retrieval_results(): 將檢索結果格式化為純文字
- create_retriever_tool(): 工廠函數，回傳 LangChain StructuredTool
"""

import logging
from typing import Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.modules.rag import Rag

logger = logging.getLogger(__name__)


# 結果格式化常數
_MAX_CONTENT_CHARS = 800


class RetrieverInput(BaseModel):
    """Agent 呼叫 retriever 時的輸入 schema。

    LLM 在決定是否呼叫工具時會讀取 Field(description=...) 的內容，
    因此 description 應提供足夠的指引，幫助 LLM 判斷何時使用、如何填寫參數。
    """

    query: str = Field(
        description="搜尋查詢字串，用於檢索實驗室網站中的相關網頁內容"
    )
    filter_dict: dict[str, Any] | None = Field(
        default=None,
        description=(
            "可選的 metadata 過濾條件。範例：\n"
            '- {"page_type": "paper"} — 只回傳論文頁面\n'
            '- {"page_type": "paper", "year": (2024, ">=")} — 論文且年份 ≥ 2024\n'
            '- {"page_type": (["paper", "announcement"], "in")} — 論文或公告\n'
            "傳 None 則不過濾。"
        ),
    )
    similarity_top_k: int | None = Field(
        default=None,
        description=(
            "回傳的 top-k 結果數量。預設為 10。"
            "若初次檢索結果不足可調高此值以獲取更廣召回。"
        ),
    )


def format_retrieval_results(results: list[dict[str, Any]]) -> str:
    """將檢索結果格式化為 Agent 易讀的純文字。

    Args:
        results: retrieve() 回傳的 dict 列表。

    Returns:
        格式化後的純文字字串，每個結果包含標題、分數、類型、URL 與內容片段。
    """
    if not results:
        return "未檢索到相關結果。"

    lines = [f"檢索到 {len(results)} 筆相關結果：\n"]
    for i, r in enumerate(results, 1):
        lines.append(
            f"[{i}] {r['page_title']} "
            f"(score={r['score']:.3f}, type={r['page_type']})"
        )
        lines.append(f"    URL: {r['url']}")
        content = r["content"][:_MAX_CONTENT_CHARS]
        lines.append(f"    {content}\n")
    return "\n".join(lines)


def create_retriever_tool(rag: Rag) -> StructuredTool:
    """將 Rag retriever 包裝為 LangChain StructuredTool。

    Args:
        rag: 已初始化至 retriever 層級的 Rag 實例
            （需已完成 build_nodes → build_vector_store → build_index → build_retriever）。

    Returns:
        StructuredTool: 可直接傳入 create_agent()、ToolNode 或
            create_react_agent() 的工具實例。name 為 "webpage_retriever"。
    """

    def _retrieve(
        query: str,
        filter_dict: dict[str, Any] | None = None,
        similarity_top_k: int | None = None,
    ) -> str:
        logger.info(
            f"Agent tool called: query={query!r}, "
            f"filter_dict={filter_dict}, top_k={similarity_top_k}"
        )
        results = rag.retrieve(
            query=query,
            filter_dict=filter_dict,
            similarity_top_k=similarity_top_k,
        )
        return format_retrieval_results(results)

    return StructuredTool(
        name="webpage_retriever",
        description=(
            "檢索實驗室網站網頁中與查詢相關的內容。"
            "當你需要查詢實驗室的論文、研究主題、人員資訊、公告時使用此工具。"
            "可透過 filter_dict 過濾特定頁面類型"
            "（如 {\"page_type\": \"paper\"} 只查論文），"
            "或調整 similarity_top_k 控制回傳數量。"
            "回傳的內容包含原始片段與來源 URL。"
        ),
        args_schema=RetrieverInput,
        func=_retrieve,
    )
```

### 設計決策紀錄

| 決策 | 選擇 | 理由 |
|------|------|------|
| `StructuredTool` vs `@tool` | `StructuredTool` | 工具需攜帶狀態（`Rag` 實例），無法用 `@tool` 表達 |
| description 風格 | 自然語言段落 | LLM 讀取 description 決定工具選擇，應清晰描述用途與參數 |
| content 截斷長度 | 800 chars | 防止撐爆 Agent context；若使用長 context 模型可調大 |
| 回傳格式 | 純文字 | Agent 可直接讀取，不需額外解析；`ToolMessage.content` 即為字串 |

---

## Phase 3: Workflow 函數

### 修改檔案

`app/workflow/workflow.py`

### 定位

在 `run_rag_build()` 之後、`run_rag_query()` 之前插入新函數。

### 與 `run_rag_build()` 的關鍵差異

| 面向 | `run_rag_build()` | `run_rag_retriever_tool()` |
|------|-------------------|---------------------------|
| pipeline 範圍 | nodes → vector store → index → retriever → query engine | nodes → vector store → index → retriever（**不含 query engine**）|
| 回傳值 | `None` | `StructuredTool` |
| `rag.close()` | ✅ 最後呼叫 | ❌ **不呼叫**（工具需保持活著供後續多次呼叫）|
| `webpages_data_use_latest_results` | ✅ 支援 | ❌ 暫不支援（可未來加入）|

### 完整程式碼

```python
def run_rag_retriever_tool(
    run_manager: RunManager | None = None,
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    **config_overrides,
) -> StructuredTool:
    """建立 RAG 資源至 retriever 層級，並回傳包裝好的 StructuredTool。

    與 run_rag_build 的差異：
    - 只建到 retriever，不建 query engine
    - 不回傳 None，而是回傳可直接給 Agent 使用的工具
    - 不呼叫 rag.close()（工具需保持活著以回應多次呼叫）

    Args:
        run_manager: 可選的 RunManager 實例。
        config_name: RAG config 名稱（對應 configs/rag/{name}.toml）。
        run_name_use_config_name: 是否以 config 名稱為 run name。
        **config_overrides: 可覆寫 config 中的任何欄位。

    Returns:
        StructuredTool: 包裝好的 retriever 工具，可直接傳入 create_agent()。
    """
    # ----- 初始化設定和路徑 -----
    rag = Rag()
    config = RagConfig.from_toml(config_name, **config_overrides)
    if run_manager is None:
        run_manager = RunManager("rag_retriever_tool")
    if run_name_use_config_name:
        run_manager.set_run_path(config_name)
    else:
        run_manager.set_run_path(config.run_name)
    run_manager.init_module_run_paths()
    run_title = f"RAG Retriever Tool ({config_name})"

    with (
        save_logging_file(run_manager.log_path),
        log_run_time(run_title),
    ):
        # ----- 輸出開始訊息 -----
        log_session(run_title, style="purple")
        log_config("Rag Config Loaded from toml", config)

        # ----- 初始化物件 -----
        rag.override_init_config(
            webpages_data_folder_path=config.webpages_data_folder_path,
        )

        # ----- 建立 Nodes -----
        log_session("Building Nodes", style="cyan")
        rag.build_nodes(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            paragraph_separator=config.paragraph_separator,
        )

        # ----- 建立 Vector Store -----
        log_session("Building Vector Store", style="cyan")
        rag.build_vector_store(
            vector_store_type=config.vector_store_type,
            qdrant_db_folder_path=os.path.join(
                run_manager.results_folder_path, "qdrant_db"
            ),
            milvus_uri=os.path.join(run_manager.results_folder_path, "milvus.db"),
            collection_name=config.collection_name,
            embedding_name=config.embedding_name,
            hybrid_ranker=config.hybrid_ranker,
            hybrid_ranker_params=config.hybrid_ranker_params,
        )

        # ----- 建立 Index -----
        log_session("Building Index", style="cyan")
        rag.build_index(embedding_name=config.embedding_name)

        # ----- 建立 Retriever（不含 Query Engine）-----
        log_session("Building Retriever", style="cyan")
        rag.build_retriever(
            similarity_top_k=config.similarity_top_k,
            query_mode=config.query_mode,
            hybrid_top_k=config.hybrid_top_k,
            alpha=config.alpha,
            # filter_dict 不留在此處設定——留給 Agent 在呼叫工具時動態傳入
        )

        # ----- 包裝為工具並回傳 -----
        log_session("Wrapping as StructuredTool", style="cyan")
        from app.tools.rag_retriever_tool import create_retriever_tool
        tool = create_retriever_tool(rag)

        # ----- 儲存設定 -----
        save_module_config_as_toml(config, run_manager.module_config_toml_path)

        log_session("RAG Retriever Tool Created", style="green")

    return tool
```

### `rag.close()` 的生命週期

:warning: **不要在 `run_rag_retriever_tool()` 內呼叫 `rag.close()`**。

正確的生命週期：

```python
# 1. 建立工具（內部建立 Rag 實例）
tool = run_rag_retriever_tool(run_manager, config_name="hybrid")

# 2. Agent 使用工具進行多次檢索
agent = create_agent(model, tools=[tool])
agent.invoke({"messages": [...]})  # 內部呼叫 rag.retrieve()
agent.invoke({"messages": [...]})  # 再次呼叫

# 3. Agent 結束後，由呼叫者手動釋放資源
# 但 tool 內部封裝了 Rag 實例，無法直接存取
# 解決方案：在 create_retriever_tool 中註冊 close 回呼
```

若需要精確控制資源釋放，可為 `StructuredTool` 加入 `close()` 方法：

```python
# 在 create_retriever_tool() 回傳前：
tool.rag = rag  # 動態綁定 Rag 實例
# 外部可透過 tool.rag.close() 釋放資源
```

---

## Phase 4: CLI 整合（可選）

### 修改檔案

- `app/workflow/workflow_config.py` — 新增 `RagRetrieverRunConfig`
- `cli.py` — 新增 `RagRetrieverCLI` 與對應分支

### workflow_config.py

```python
@dataclass
class RagRetrieverRunConfig(BaseRunConfig):
    """RAG Retriever Tool 的執行設定。"""
    pass  # 目前無額外參數，未來可擴充 webpages_data_use_latest_results
```

### cli.py

```python
@dataclass
class RagRetrieverCLI:
    run: RagRetrieverRunConfig
    module: RagConfigCLI
```

在 `cli_args_type` 中新增：

```python
cli_args_type = (
    WebsiteCrawlerCLI
    | WebpageImageSummarizerCLI
    | RagBuildCLI
    | RagQueryCLI
    | RagRetrieverCLI  # ← 新增
)
```

分支處理：

```python
elif isinstance(cli_arg, RagRetrieverCLI):
    run_manager.set_module_path("rag_retriever_tool")
    tool = run_rag_retriever_tool(
        run_manager,
        **vars(cli_arg.run),
        **module_config_overrides,
    )
    # CLI 模式下直接列印工具資訊
    print(f"Tool created: {tool.name}")
    print(f"Tool description: {tool.description}")
    # 可選：儲存 tool 資訊供後續使用
```

---

## Phase 5: Agent 整合範例

### 版本注意

:warning: **LangGraph v1.0 已棄用 `create_react_agent`**，官方遷移路徑為：

```python
from langchain.agents import create_agent  # ✅ 新版推薦
# from langgraph.prebuilt import create_react_agent  # ❌ 已棄用
```

### 基本整合

```python
from langchain.agents import create_agent
from app.workflow.workflow import run_rag_retriever_tool
from app.workflow.workflow_manager import RunManager

# Step 1: 建立工具
run_manager = RunManager("rag_retriever_tool")
tool = run_rag_retriever_tool(run_manager, config_name="hybrid")

# Step 2: 建立 agent
agent = create_agent(
    model="google_genai:gemini-3.5-flash",
    tools=[tool],
    system_prompt=(
        "你是實驗室網站問答助理。使用 webpage_retriever 工具查詢網頁內容。\n"
        "查詢論文時請加上 filter_dict={'page_type': 'paper'}。\n"
        "查詢特定年份後的論文請加上 year filter（格式為 (2024, '>=')）。"
    ),
)

# Step 3: 執行查詢
response = agent.invoke({
    "messages": [{"role": "user", "content": "實驗室 2024 年後發表了哪些論文？"}]
})
for msg in response["messages"]:
    msg.pretty_print()
```

### 多輪對話

```python
from langgraph.checkpoint.memory import MemorySaver

agent = create_agent(
    model="google_genai:gemini-3.5-flash",
    tools=[tool],
    system_prompt="...",
    checkpointer=MemorySaver(),  # ← 啟用對話記憶
)

config = {"configurable": {"thread_id": "user-session-001"}}

# 第一輪
agent.invoke(
    {"messages": [{"role": "user", "content": "介紹一下張教授的研究領域"}]},
    config=config,
)

# 第二輪 — Agent 自動累積對話歷史
agent.invoke(
    {"messages": [{"role": "user", "content": "他最近發表的論文有哪些？"}]},
    config=config,
  )
```

### 串流輸出

```python
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "實驗室有哪些研究方向？"}]},
    stream_mode="updates",
):
    for node_name, update in chunk.items():
        if "messages" in update:
            for msg in update["messages"]:
                if hasattr(msg, "content") and msg.content:
                    print(f"[{node_name}] {msg.content[:200]}")
```

### 多工具協作（未來 Phase 5 整合 Graph RAG 後）

```python
# 兩個工具共享同一個 Agent
tool_hybrid = run_rag_retriever_tool(run_manager, config_name="hybrid")
tool_graph = create_graph_tool(rag_graph)  # Phase 4 實作

agent = create_agent(
    model="google_genai:gemini-3.5-flash",
    tools=[tool_hybrid, tool_graph],
    system_prompt=(
        "你有兩個工具：\n"
        "1. webpage_retriever — 查詢網頁細節內容、論文全文、人員資訊\n"
        "2. graph_retriever — 跨實體關係查詢、全域脈絡統整\n"
        "根據問題類型選擇合適的工具。"
    ),
)
```

---

## 驗證清單

### 單元測試建議

在 `test/` 目錄下新增 `test_rag_retriever_tool.py`，至少涵蓋以下案例：

| 測試類別 | 測試案例 | 預期結果 |
|---------|---------|---------|
| `TestRetrieveMethod` | 呼叫 `retrieve(query)` 回傳 dict 列表 | `len(results) > 0` 且 `type == list[dict]` |
| | 呼叫 `retrieve(query, filter_dict={"page_type": "paper"})` | 全部 result 的 `page_type == "paper"` |
| | 呼叫 `retrieve(query, similarity_top_k=20)` | `len(results) == 20` |
| | retriever 未建立時呼叫 | 拋出 `RuntimeError` |
| `TestFormatResults` | 空結果列表 | 回傳「未檢索到相關結果。」 |
| | 單筆結果 | 包含 page_title、score、URL、content |
| | content 超過 800 字 | 截斷至 800 字元 |
| `TestToolWrapper` | `create_retriever_tool(rag)` 回傳型別 | `StructuredTool` |
| | tool name | `"webpage_retriever"` |
| | tool 可被 invoke | `tool.func(query)` 回傳字串 |

### 整合測試建議

| 測試 | 方法 | 預期結果 |
|------|------|---------|
| `run_rag_retriever_tool()` 正常建立 | `tool = run_rag_retriever_tool(config_name="test")` | 回傳 `StructuredTool` |
| `create_agent()` 接受工具 | `agent = create_agent(model, tools=[tool])` | 不拋錯 |
| Agent invoke 正常 | `agent.invoke({"messages": [HumanMessage("...")]})` | 回傳含 `AIMessage` 的 dict |

---

## 已知限制

| 限制 | 影響 | 解決方案 / 改善方向 |
|------|------|-------------------|
| **執行緒不安全** | `Rag` 實例非執行緒安全，不支援多 Agent 平行呼叫同一個 tool | 每個 Agent 建立獨立 `Rag` 實例；或將向量儲存改用遠端服務（Milvus Cluster / Qdrant Cloud） |
| **retriever 副作用** | `retrieve()` 傳入 `filter_dict` 會覆寫 `self.retriever`，影響後續不帶 filter 的呼叫 | 改為每次建立臨時 retriever；或在呼叫前備份、呼叫後還原 |
| **content 固定截斷** | 結果 content 固定截斷 800 字元，長文件可能遺失細節 | 改為動態截斷（依 token 數），或分段回傳 |
| **LLM 無生成能力** | tool 只回傳檢索結果，不含 LLM 摘要 | 應由 Agent 的 LLM 負責摘要；若需獨立摘要能力可包裝成第二個 tool |
| **`rag.close()` 不可達** | tool 內部封裝的 `Rag` 實例無法從外部 close | 在 `create_retriever_tool()` 中將 `rag` 綁定為 tool 屬性（`tool.rag = rag`）|
