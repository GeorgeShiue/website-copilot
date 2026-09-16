# 資源生命週期重構 (2026/9/7)

> 本文檔將目前 `create_agent` 的單體式資源建構流程，重構為四階段獨立交接架構：
> **create_tool → create_agent → run_agent / run_app**。
> 核心改造範圍：`workflow.py`、`agent.py`、`server/app.py`、`cli.py`。

---

## 1. 變更範圍總覽

```
src/app/workflow/workflow.py   ← 修改：新增 create_tool()、run_app()；重構 run_agent()；刪除 run_server()
src/app/agent/agent.py         ← 修改：create_agent() 簽名變更（tools/registry/run_manager 必填）；Agent.registry 改為必填
src/app/server/app.py          ← 修改：create_app → _create_app（內部化）；刪除 start_uvicorn()
src/cli.py                     ← 修改：AgentCLI / ServerCLI 分支改用 create_tool → run_agent / run_app
```

---

## 2. 動機

### 現狀問題

目前 `create_agent()` 是一個單體式函式，在一次呼叫中完成所有資源建構：

```python
# agent.py — 現在的 create_agent
def create_agent(config=None, run_manager=None):
    if run_manager is None:
        run_manager = RunManager.for_run_no_site(...)    # ← 職責不該在此
    registry = RAGRegistry(DataManager())                # ← Stage 1
    discovery_tool = create_site_discovery_tool(registry) # ← Stage 2
    retriever_tool = create_webpage_retriever_tool(...)   # ← Stage 2
    llm = create_llm(config.llm_name)
    graph = langchain_create_agent(llm, [...])            # ← Stage 3
    return Agent(graph, tools, run_manager, config, registry)
```

**問題：**
- `RunManager` 的建立職責混在 `create_agent` 內部，CLI 和 Server 模式的路徑策略（`runs/` vs `chats/`）只能靠外部傳入 `run_manager` 參數
- RAGRegistry + 工具的建立（Stage 1+2）與 Agent 的建立（Stage 3）緊耦合，無法分離測試
- `run_agent` 同時負責問答邏輯、落盤、資源釋放，職責過重
- Server 模式的 `create_app` 可以不傳 `agent` 自動建立，隱藏了依賴關係

### 目標架構

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  create_tool │────▶│ create_agent │────▶│  run_agent   │  CLI 模式
│  Stage 1+2   │     │   Stage 3    │     │  問答+落盤    │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │
       │                    │
       │              ┌──────────────┐
       └─────────────▶│   run_app    │  Server 模式
                      │  Stage 4     │
                      └──────────────┘
```

**四階段獨立交接：**

| 階段 | 函式 | 輸入 | 輸出 | 職責 |
|------|------|------|------|------|
| 1+2 | `create_tool(config_name)` | RAG config name | `(tools, registry)` | 建立 RAGRegistry + 工具 |
| 3 | `create_agent(config, tools, registry, run_manager)` | 設定 + 資源 | `Agent` | 組裝 Agent |
| 3 | `run_agent(query, tools, registry, ...)` | tools + registry | `None` | CLI 問答 + 落盤 + close |
| 4 | `run_app(config_name)` | config name | `FastAPI` | Server 建置 + lifespan 管理 |

---

## 3. 模組一：`create_tool()` — 工具層建置

### 3-1. 職責

建立 RAGRegistry + 兩個工具（discovery + retriever），回傳給呼叫端。

### 3-2. 簽名

```python
def create_tool(
    config_name: str = "default",
) -> tuple[list[StructuredTool], RAGRegistry]:
    """建立 Agent 所需的工具層。

    流程：建立 RAGRegistry（lazy + LRU cache）
    → 建立 discovery_tool + retriever_tool
    → 回傳 (tools, registry)

    Args:
        config_name: RAG config 名稱（對應 configs/rag/{name}.toml）。

    Returns:
        (tools, registry)：工具列表與 RAG 實例管理器。
    """
    registry = RAGRegistry(DataManager())
    discovery_tool = create_site_discovery_tool(registry)
    retriever_tool = create_webpage_retriever_tool(registry)
    return [discovery_tool, retriever_tool], registry
```

### 3-3. 關鍵設計決策

| 決策 | 選擇 | 理由 |
|------|------|------|
| RAGRegistry 建立位置 | `create_tool` 內部 | Registry 的生命週期由 `create_tool` 的呼叫端管理 |
| RAG 實例建置時機 | lazy loading（`registry.get(site_id)` 時） | `create_tool` 只建立工具，不觸發 RAG 建置 |
| 與 `run_rag_build` 的關係 | 並存，職責不同 | `run_rag_build` 預建向量庫，`create_tool` 建置 Agent 工具層 |
| `config_name` 用途 | 識別用，實際 RAG config 由 `RAGRegistry.get(site_id)` 惰性載入 | `create_tool` 不需載入具體 RAG config |

### 3-4. 與 run_rag_build 的關係

```
run_rag_build(config_name, site_id)    → 預建向量庫（data/rag/{site_id}/）
create_tool(config_name)               → 建置 Agent 工具層（registry + tools）
```

兩者並存：
- `run_rag_build` 負責將爬取資料轉為向量庫（一次性或定期更新）
- `create_tool` 負責建立 Agent 問答所需的工具層（lazy 建立 RAG 實例）

---

## 4. 模組二：`create_agent()` — Agent 組裝

### 4-1. 簽名變更

```python
# BEFORE
def create_agent(
    config: AgentConfig | None = None,
    run_manager: RunManager | None = None,
) -> Agent: ...

# AFTER
def create_agent(
    config: AgentConfig,                      # 必填（移除 None 預設）
    tools: list[StructuredTool],              # 必填（新增）
    registry: RAGRegistry,                    # 必填（新增）
    run_manager: RunManager,                  # 必填（移除 None 預設）
) -> Agent: ...
```

### 4-2. 內部流程變更

```python
# BEFORE — 建立 RAGRegistry + 工具 + RunManager + LLM + Agent
def create_agent(config=None, run_manager=None):
    if run_manager is None:
        run_manager = RunManager.for_run_no_site(...)
    registry = RAGRegistry(DataManager())
    discovery_tool = create_site_discovery_tool(registry)
    retriever_tool = create_webpage_retriever_tool(...)
    llm = create_llm(config.llm_name)
    graph = langchain_create_agent(llm, [discovery_tool, retriever_tool], ...)
    return Agent(graph, tools, run_manager, config, registry)

# AFTER — 只組裝 Agent（資源由呼叫端提供）
def create_agent(config, tools, registry, run_manager):
    if not tools:
        raise ValueError("create_agent requires at least one tool")
    llm = create_llm(config.llm_name)
    checkpointer = InMemorySaver()
    graph = langchain_create_agent(llm, tools, ...)
    return Agent(graph, tools, run_manager, config, checkpointer, registry)
```

### 4-3. Agent dataclass 變更

```python
# BEFORE
@dataclass
class Agent:
    graph: CompiledStateGraph
    tools: list[StructuredTool]
    run_manager: RunManager
    config: AgentConfig
    checkpointer: InMemorySaver
    registry: RAGRegistry | None = None    # 可選

# AFTER
@dataclass
class Agent:
    graph: CompiledStateGraph
    tools: list[StructuredTool]
    run_manager: RunManager
    config: AgentConfig
    checkpointer: InMemorySaver
    registry: RAGRegistry                  # 必填（移除 Optional）
```

### 4-4. 移除的邏輯

| 移除項目 | 原因 |
|---------|------|
| `if config is None: config = AgentConfig.from_toml("default")` | config 改為必填 |
| `if run_manager is None: run_manager = RunManager.for_run_no_site(...)` | run_manager 改為必填，由呼叫端建立 |
| `registry = RAGRegistry(DataManager())` | 移至 `create_tool` |
| `discovery_tool = create_site_discovery_tool(registry)` | 移至 `create_tool` |
| `retriever_tool = create_webpage_retriever_tool(registry)` | 移至 `create_tool` |
| `save_module_config_as_toml(...)` + `log_run_paths("init")` | 移至 `run_agent`（落盤統一由 run 層處理） |

---

## 5. 模組三：`run_agent()` — CLI 問答

### 5-1. 簽名變更

```python
# BEFORE
def run_agent(
    query: str,
    config_name: str = "default",
    thread_id: str | None = None,
    stream: bool = False,
    agent_run_manager: RunManager | None = None,
    **config_overrides,
) -> RunManager: ...

# AFTER
def run_agent(
    query: str,
    tools: list[StructuredTool],              # 必填（從 create_tool 傳入）
    registry: RAGRegistry,                    # 必填（從 create_tool 傳入）
    config_name: str = "default",
    thread_id: str | None = None,
    stream: bool = False,
    data_manager: DataManager | None = None,
    run_config: AgentRunConfig | None = None,
    **config_overrides,
) -> None: ...
```

### 5-2. 內部流程

```python
def run_agent(query, tools, registry, config_name="default", ...):
    # 1. 建立 RunManager（硬編碼 base_folder="runs"）
    run_manager = RunManager.for_run_no_site(
        module="agent",
        run_name=config_name,
        base_folder="runs",
    )

    # 2. 建立 Agent
    agent = create_agent(
        config=AgentConfig.from_toml(config_name, **config_overrides),
        tools=tools,
        registry=registry,
        run_manager=run_manager,
    )

    try:
        with save_logging_file(run_manager.log_path):
            # 3. 問答
            if stream:
                result = asyncio.run(
                    agent.astream_result(query, thread_id, ...)
                )
                print()
            else:
                result = agent.ask(query, thread_id)

            # 4. 顯示結果
            log_session("Agent Response", style="green")
            print_log(result["response"])
            log_session("Sources", style="cyan")
            for i, url in enumerate(result["sources"], 1):
                print(f"{i}. {url}")

            if thread_id is None:
                thread_id = f"auto-{uuid.uuid4().hex[:8]}"

            # 5. 落盤
            agent.save_results([result], thread_id=thread_id)

            if run_config is not None:
                save_run_config_as_toml(run_config, run_manager.run_config_toml_path)
            run_manager.log_run_paths("complete")

            if data_manager is not None:
                data_manager.publish_run_metadata(
                    site_id=config_name,
                    category="agent",
                    module_config_path=run_manager.module_config_toml_path,
                    run_config_path=run_manager.run_config_toml_path,
                    log_path=run_manager.log_path,
                )
    finally:
        agent.close()
```

### 5-3. 變更摘要

| 變更項目 | BEFORE | AFTER |
|---------|--------|-------|
| `tools` / `registry` | 由 `create_agent` 內部建立 | 由呼叫端（`create_tool`）提供 |
| `RunManager` 建立位置 | `create_agent` 內部（若未傳入） | `run_agent` 內部（硬編碼 `base_folder="runs"`） |
| `agent_run_manager` 參數 | 可選 | 移除 |
| `data_manager` 參數 | 無（由 `cli.py` 外部處理） | 新增（可選，落盤 publish） |
| `run_config` 參數 | 無（由 `cli.py` 外部處理） | 新增（可選，落盤 run config） |
| `save_run_config_as_toml` | `cli.py` 外部呼叫 | `run_agent` 內部 |
| `log_run_paths("complete")` | `cli.py` 外部呼叫 | `run_agent` 內部 |
| `publish_run_metadata` | `cli.py` 外部呼叫 | `run_agent` 內部 |
| 回傳值 | `RunManager` | `None` |
| `agent.close()` | `finally` 區塊 | 保留不變 |

---

## 6. 模組四：`run_app()` — Server 模式

### 6-1. 簽名

```python
def run_app(
    config_name: str = "default",
    allowed_origins: list[str] | None = None,
) -> FastAPI:
    """建立 Server 模式的 FastAPI app。

    流程：create_tool → RunManager(base_folder="chats")
    → create_agent → _create_app(agent)

    Args:
        config_name: config 名稱（共用，分別從 configs/rag/ 和 configs/agent/ 載入）。
        allowed_origins: CORS 允許來源（None 時全開放）。

    Returns:
        FastAPI：含 /api/chat（SSE）、/api/health 與 CORS。
    """
    tools, registry = create_tool(config_name)

    run_manager = RunManager.for_run_no_site(
        module="agent",
        run_name=config_name,
        base_folder="chats",
    )

    agent = create_agent(
        config=AgentConfig.from_toml(config_name),
        tools=tools,
        registry=registry,
        run_manager=run_manager,
    )

    return _create_app(agent=agent, allowed_origins=allowed_origins)
```

### 6-2. `_create_app` — 內部實作

```python
def _create_app(
    agent: Agent,
    allowed_origins: list[str] | None = None,
) -> FastAPI:
    """建立 FastAPI app（內部實作，不對外暴露）。"""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.agent = agent
        yield
        app.state.agent.close()    # 關閉後端服務時自動釋放資源

    app = FastAPI(
        title="Website Copilot Chat",
        version="0.1.0",
        lifespan=lifespan,
    )
    # ... CORS middleware, static files, routes ...
    return app
```

### 6-3. 變更摘要

| 變更項目 | BEFORE | AFTER |
|---------|--------|-------|
| 函式名稱 | `create_app` (公開) | `_create_app` (內部) |
| `config_name` 參數 | `create_app` 接受（可選） | 移至 `run_app` |
| `agent` 參數 | `create_app` 接受（可選，可為 None） | `_create_app` 必填 |
| Agent 建立 | lifespan 內部（若 `agent is None`） | `run_app` 外部建立 |
| `base_folder` | 硬編碼 `"chats"` | 保留不變 |
| `agent.close()` | lifespan finally 區塊 | 保留不變 |
| `start_uvicorn()` | 存在 | 刪除 |

### 6-4. 刪除清單

| 函式 | 原位置 | 原因 |
|------|--------|------|
| `start_uvicorn()` | `app.py:215` | 被 `run_app` + `cli.py` 直接呼叫 `uvicorn.run()` 取代 |
| `create_app()` (公開) | `app.py:130` | 改為 `_create_app` 內部函式 |

### 6-5. 刪除 run_server 相關

| 函式 | 位置 | 原因 |
|------|------|------|
| `run_server()` | `workflow.py:503` | 被 `run_app` 取代 |
| `spawn_server()` | `server_helper.py` | 被 `run_app` 的 lifespan 取代 |
| `wait_ready()` | `server_helper.py` | 同上 |
| `validate_server()` | `server_helper.py` | 同上 |
| `shutdown_server()` | `server_helper.py` | 同上 |

---

## 7. 模組五：`cli.py` — 呼叫端改接

### 7-1. AgentCLI 分支

```python
# BEFORE
elif isinstance(cli_arg, AgentCLI):
    agent_run_manager = run_agent(
        **run_kwargs,
        **module_config_overrides,
    )
    save_run_config_as_toml(cli_arg.run, agent_run_manager.run_config_toml_path)
    agent_run_manager.log_run_paths("complete")
    if data_manager is not None:
        data_manager.publish_run_metadata(
            site_id=cli_arg.run.config_name,
            category="agent",
            module_config_path=agent_run_manager.module_config_toml_path,
            run_config_path=agent_run_manager.run_config_toml_path,
            log_path=agent_run_manager.log_path,
        )

# AFTER
elif isinstance(cli_arg, AgentCLI):
    tools, registry = create_tool(cli_arg.run.config_name)
    run_agent(
        query=cli_arg.run.query,
        tools=tools,
        registry=registry,
        config_name=cli_arg.run.config_name,
        thread_id=cli_arg.run.thread_id,
        stream=cli_arg.run.stream,
        data_manager=data_manager,
        run_config=cli_arg.run,
    )
```

### 7-2. ServerCLI 分支

```python
# BEFORE
elif isinstance(cli_arg, ServerCLI):
    run_server(**vars(cli_arg.run), mode="block")

# AFTER
elif isinstance(cli_arg, ServerCLI):
    app = run_app(
        config_name=cli_arg.run.config_name,
        allowed_origins=cli_arg.run.allowed_origins,
    )
    uvicorn.run(app, host=cli_arg.run.host, port=cli_arg.run.port)
```

### 7-3. 移除的後處理邏輯

以下後處理已移入 `run_agent` 內部，`cli.py` 不再需要：

```python
# 從 cli.py 刪除（AgentCLI 分支）
save_run_config_as_toml(cli_arg.run, agent_run_manager.run_config_toml_path)
agent_run_manager.log_run_paths("complete")
data_manager.publish_run_metadata(...)
```

---

## 8. 資源生命週期對照

### CLI 模式

```
cli.py: AgentCLI
  │
  ├─ create_tool(config_name)        → registry (lazy RAG) + tools
  │
  ├─ run_agent(query, tools, registry, data_manager=..., run_config=...)
  │   ├─ RunManager(base_folder="runs")
  │   ├─ create_agent(config, tools, registry, run_manager)
  │   ├─ agent.ask() / agent.astream_result()
  │   ├─ agent.save_results()
  │   ├─ save_run_config_as_toml()
  │   ├─ run_manager.log_run_paths("complete")
  │   ├─ data_manager.publish_run_metadata()
  │   └─ finally: agent.close()
  │       ├─ registry.close()
  │       │   └─ rag.close() for each cached RAG
  │       │       └─ MilvusClient.close()
  │       └─ gc.collect()
  │
  └─ cli.py: 無後處理（全部由 run_agent 完成）
```

### Server 模式

```
cli.py: ServerCLI
  │
  ├─ run_app(config_name)
  │   ├─ create_tool(config_name)       → registry + tools
  │   ├─ RunManager(base_folder="chats")
  │   ├─ create_agent(config, tools, registry, run_manager)
  │   └─ _create_app(agent)             → FastAPI (lifespan 綁定 agent)
  │
  ├─ uvicorn.run(app)                  → 啟動 server
  │   └─ lifespan 啟動：app.state.agent = agent
  │
  ├─ (運行中...)
  │
  └─ Ctrl+C → lifespan 關閉
      └─ agent.close()
          ├─ registry.close()
          │   └─ rag.close() for each cached RAG
          │       └─ MilvusClient.close()
          └─ gc.collect()
```

---

## 9. 設計決策總覽

| 決策 | 選擇 | 理由 |
|------|------|------|
| `create_agent` 的 `tools` / `registry` | 必填參數 | 明確建立新規範：建立 Agent 一定要給一組 tools |
| `run_agent` 的 `RunManager` | 內部建立，硬編碼 `base_folder="runs"` | CLI 模式固定使用 runs/ |
| `run_app` 的 `RunManager` | 內部建立，硬編碼 `base_folder="chats"` | Server 模式固定使用 chats/ |
| `run_agent` 回傳值 | `None` | 所有落盤工作在內部完成，不需回傳 |
| `run_agent` 後處理 | `data_manager` + `run_config` 參數 | 從 `cli.py` 移入，減少呼叫端負擔 |
| `create_app` 存在性 | 改為 `_create_app`（內部） | 不對外暴露，由 `run_app` 統一管理 |
| `agent.close()` 觸發時機 | CLI: `run_agent` finally；Server: lifespan finally | 兩種模式各自管理資源釋放 |
| `create_tool` 與 `run_rag_build` | 並存 | 職責不同：預建向量庫 vs 建置工具層 |
| config_name 對應 | 共用名稱，從不同資料夾載入 | `configs/rag/{name}.toml` vs `configs/agent/{name}.toml` |

---

## 10. 執行順序

1. **`agent.py`**：修改 `create_agent` 簽名 + `Agent` dataclass
2. **`workflow.py`**：新增 `create_tool()` + `run_app()` + 重構 `run_agent()` + 刪除 `run_server()`
3. **`app.py`**：`create_app` → `_create_app` + 刪除 `start_uvicorn()`
4. **`cli.py`**：改接 AgentCLI / ServerCLI 分支
5. **`server_helper.py`**：確認不再被引用後刪除 `spawn_server` 等函式

---

## 11. 測試驗證規劃

### 11-1. 測試策略總覽

重構的測試驗證分為三個層級：

| 層級 | 目標 | 測試位置 | 執行時機 |
|------|------|---------|---------|
| **單元測試** | 驗證每個函式的輸入/輸出/副作用 | `src/test/dev/` | 每次修改後自主執行 |
| **整合測試** | 驗證函式間的串接（create_tool → create_agent → run_agent） | `src/test/dev/` | 每個模組完成後 |
| **回歸測試** | 驗證現有行為不被破壞 | `src/test/` + `src/test/dev/` | 全部完成後 |

### 11-2. 測試原則

遵循專案現有測試模式：
- **替身**：使用 hand-rolled dataclass stubs（`_FakeAgent`、`_FakeGraph`、`_FakeRunManager`），避免觸發真實 LLM / RAG / Milvus
- **Mock**：使用 `MagicMock(spec=...)` 模擬外部依賴（`RAGRegistry`、`DataManager`）
- **斷言**：使用 plain `assert`（pytest-native）
- **暫存目錄**：使用 `tempfile.mkdtemp()` + `shutil.rmtree()` 管理測試副作用
- **無 conftest.py**：所有 fixture 在測試檔案或測試類別內部定義

### 11-3. 單元測試：`create_tool()`

**測試檔案**：`src/test/dev/test_create_tool.py`（新增）

```python
# 測試案例
test_create_tool_returns_two_tools_and_registry
    # 驗證：回傳 (tools, registry) 且 tools 長度為 2
    # Mock：RAGRegistry, create_site_discovery_tool, create_webpage_retriever_tool

test_create_tool_tools_have_correct_names
    # 驗證：tools[0].name == "list_knowledge_bases", tools[1].name == "webpage_retriever"

test_create_tool_registry_is_lazy
    # 驗證：呼叫 create_tool 後 registry.get() 未被呼叫（RAG 未建置）
    # Mock：RAGRegistry
```

**Mock 策略**：
- Mock `RAGRegistry` 類別（`@patch("app.workflow.workflow.RAGRegistry")`）
- Mock `create_site_discovery_tool` 和 `create_webpage_retriever_tool`
- 不需要真實的 `DataManager` 或 RAG 實例

### 11-4. 單元測試：`create_agent()` 簽名變更

**測試檔案**：`src/test/dev/test_agent_server.py`（修改現有）

```python
# 新增測試案例
test_create_agent_requires_tools
    # 驗證：tools 為空列表時拋出 ValueError
    # Mock：config, registry, run_manager 為 stub

test_create_agent_requires_registry
    # 驗證：registry 為 None 時拋出 TypeError（型別檢查）

test_create_agent_requires_run_manager
    # 驗證：run_manager 為 None 時拋出 TypeError（型別檢查）

test_create_agent_stores_registry_on_agent
    # 驗證：agent.registry 是傳入的 registry 實例（不再是 Optional）
```

**注意**：`create_agent` 內部仍會呼叫 `create_llm()` 和 `langchain_create_agent()`，需要 mock 這些依賴：
```python
@patch("app.agent.agent.create_llm")
@patch("app.agent.agent.langchain_create_agent")
def test_create_agent_builds_correctly(mock_langchain, mock_llm):
    ...
```

### 11-5. 單元測試：`run_agent()` 重構

**測試檔案**：`src/test/dev/test_run_agent.py`（新增）

```python
# 測試案例
test_run_agent_creates_run_manager_with_runs_base_folder
    # 驗證：RunManager.for_run_no_site 被呼叫時 base_folder="runs"
    # Mock：RunManager, create_agent

test_run_agent_calls_agent_ask
    # 驗證：agent.ask() 被正確呼叫，結果被處理
    # Mock：_FakeAgent（替身），驗證 ask() 呼叫參數

test_run_agent_saves_results
    # 驗證：agent.save_results() 被呼叫，thread_id 正確
    # Mock：_FakeAgent

test_run_agent_closes_agent_in_finally
    # 驗證：即使問答拋出例外，agent.close() 仍被呼叫
    # Mock：_FailingAgent（astream_result 拋出例外）

test_run_agent_publishes_metadata_when_data_manager_provided
    # 驗證：data_manager.publish_run_metadata() 被正確呼叫
    # Mock：DataManager, _FakeAgent

test_run_agent_skips_publish_when_no_data_manager
    # 驗證：data_manager=None 時 publish_run_metadata 未被呼叫

test_run_agent_returns_none
    # 驗證：回傳值為 None（不再是 RunManager）
```

**Mock 策略**：
- Mock `create_agent` 回傳 `_FakeAgent` 替身
- Mock `RunManager.for_run_no_site` 回傳 `_FakeRunManager` 替身
- Mock `AgentConfig.from_toml` 回傳 `_FakeConfig` 替身
- 使用 `tempfile.mkdtemp()` 驗證落盤行為

### 11-6. 單元測試：`run_app()` + `_create_app()`

**測試檔案**：`src/test/dev/test_agent_server.py`（修改現有）

```python
# 新增測試案例
test_run_app_returns_fastapi_app
    # 驗證：run_app() 回傳 FastAPI 實例
    # Mock：create_tool, create_agent, AgentConfig.from_toml

test_run_app_lifespan_sets_agent_on_state
    # 驗證：lifespan 啟動後 app.state.agent 被設定
    # 使用：TestClient + _FakeAgent

test_run_app_lifespan_calls_agent_close
    # 驗證：lifespan 關閉時 agent.close() 被呼叫
    # 使用：_FakeAgent + 驗證 close() 呼叫次數

test_create_app_removed
    # 驗證：公開的 create_app 不再存在（import 拋出 ImportError）
```

**改動現有測試**：
- 現有 `test_agent_server.py` 中的 `_make_client()` 需改為使用 `_create_app` 替代 `create_app`
- 現有的 SSE / health / CORS 測試邏輯不變，只改 app 建立方式

### 11-7. 單元測試：`cli.py` 改接

**測試檔案**：`src/test/dev/test_cli.py`（新增）

```python
# 測試案例
test_agent_cli_branch_calls_create_tool_then_run_agent
    # 驗證：AgentCLI 分支依序呼叫 create_tool → run_agent
    # Mock：create_tool, run_agent, tyro.cli

test_server_cli_branch_calls_run_app_then_uvicorn
    # 驗證：ServerCLI 分支呼叫 run_app → uvicorn.run
    # Mock：run_app, uvicorn.run

test_agent_cli_no_post_processing
    # 驗證：AgentCLI 分支不再呼叫 save_run_config_as_toml / log_run_paths / publish_run_metadata
    # Mock：所有 workflow 函式，驗證 cli.py 層不呼叫後處理
```

### 11-8. 整合測試：四階段串接

**測試檔案**：`src/test/dev/test_resource_lifecycle.py`（新增）

```python
# 測試案例（使用 mock，不觸發真實 LLM/RAG）
test_full_pipeline_create_tool_to_run_agent
    # 流程：create_tool → create_agent → run_agent（mock agent.ask）
    # 驗證：資源正確傳遞，close 被呼叫，落盤目錄正確

test_full_pipeline_create_tool_to_run_app
    # 流程：create_tool → create_agent → _create_app → TestClient
    # 驗證： lifespan 管理 close，SSE 端點可存取

test_resource_cleanup_on_agent_error
    # 流程：create_tool → create_agent → run_agent（mock agent.ask 拋出例外）
    # 驗證：agent.close() 仍被呼叫（finally 區塊）
```

### 11-9. 回歸測試：現有測試不受影響

重構完成後需確認以下現有測試仍通過：

| 測試檔案 | 測試內容 | 預期影響 |
|---------|---------|---------|
| `test_agent_server.py` | Server SSE / health / CORS | 需改 `_make_client` 使用 `_create_app` |
| `test_rag_tools.py` | RAGRegistry / retriever 工具 | **無影響**（不涉及 create_agent/run_agent） |
| `test_runmanager_datamanager.py` | RunManager / DataManager | **無影響**（不涉及 workflow 層） |
| `test_html_date_extraction.py` | HTML 日期提取 | **無影響** |
| `test_dedup_key.py` | 爬蟲去重 | **無影響** |
| `test_main.py` | 全流程 E2E（slow） | 需驗證（重構後流程不變） |
| `test_module.py` | 各 workflow 函式（slow） | 需修改（`run_agent` 簽名變更、`run_server` 刪除） |

### 11-10. 執行順序

每個模組完成後立即執行對應的 dev 測試：

```
1. agent.py 修改完成
   → uv run pytest src/test/dev/test_agent_server.py -v

2. workflow.py 新增 create_tool + run_app + 重構 run_agent
   → uv run pytest src/test/dev/test_create_tool.py -v
   → uv run pytest src/test/dev/test_run_agent.py -v

3. app.py create_app → _create_app
   → uv run pytest src/test/dev/test_agent_server.py -v

4. cli.py 改接
   → uv run pytest src/test/dev/test_cli.py -v

5. 全部完成後
   → uv run pytest src/test/dev/ -v          # 所有 dev 測試
   → uv run pytest src/test/ -m "not slow" -v # 非 slow 測試
```
