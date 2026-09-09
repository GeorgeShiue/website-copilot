# 2026/09/14 實作紀錄

> 對應規劃文件：`2026_0907-resource_lifecycle_refactor.md`

---

## 一：資源生命週期重構 (9/7)

### 1. 概述

將原先 `create_agent()` 的單體式資源建構流程，重構為四階段獨立交接架構：**create_tool → create_agent → run_agent / run_app**。核心改造包括：`create_agent` 不再負責建立 Registry 或工具；`run_agent` / `run_app` 內化 registry 與 tool 建立，registry 生命週期由 Python context manager 管理；`RAGRegistry` 移除 `DataManager` 依賴改為自管 site 掃描；`create_app` 僅接收 `agent` 不再管理 registry；`uvicorn.run()` 移入 `run_app` 使其成為 Server 模式的完整入口。

### 2. 最終架構

**資源交接管線：**

```
run_agent / run_app
  └→ with RAGRegistry(...) as registry:    # context manager 管理生命週期
       └→ create_tool(registry)            # 建立工具層
            └→ create_agent(config, tools, run_manager)  # 建立 Agent
                 └→ agent.ask() / uvicorn.run(app)       # 執行
```

**最終 API 簽名：**

| 函式/類別 | 簽名 | 備註 |
|-----------|------|------|
| `create_app` | `(agent: Agent, allowed_origins: list[str] \| None = None) -> FastAPI` | 不含 registry；registry 由呼叫端 `with` 管理 |
| `create_tool` | `(registry: RAGRegistry) -> list[StructuredTool]` | 純工具工廠，不管理資源 |
| `create_agent` | `(config: AgentConfig, tools: list[StructuredTool], run_manager: RunManager) -> Agent` | Agent 為純 dataclass，無 registry 欄位 |
| `run_agent` | `(query, config_name, thread_id, stream, data_manager, run_config, **overrides) -> None` | 內部 `with (registry, ...):` |
| `run_app` | `(config_name, allowed_origins, host, port) -> None` | 內部 `with RAGRegistry(...) as registry:` + `uvicorn.run()` |
| `RAGRegistry` | `(config_name="default", base_folder="data", max_cached=5)` | 支援 context manager；無 DataManager 依賴 |

**關鍵設計決策：**

- Registry 生命週期由呼叫端 `with` 區塊統一管理，`close()` 在 `__exit__` 中自動呼叫
- `create_app` 的 lifespan 不負責 registry 清理（避免 double-close）
- `RAGRegistry` 自行實作 `_list_sites()` / `_site_exists()`，不依賴 `DataManager`
- `Agent` 為純 dataclass（`graph`, `tools`, `run_manager`, `config`, `checkpointer`），無 `close()` 方法

### 3. 變更檔案

| 檔案 | 變更 | 說明 |
|------|------|------|
| `src/app/agent/agent.py` | 修改 | 移除 `registry` 欄位、`close()` 方法；`create_agent` 改為必填 config/tools/run_manager |
| `src/app/workflow/workflow.py` | 修改 | `run_agent`/`run_app` 內化 registry+tool 建立；`uvicorn.run()` 移入 `run_app`；移除 `run_server()` |
| `src/app/server/app.py` | 修改 | `create_app` 移除 `registry` 參數；lifespan 不再負責 registry 清理 |
| `src/app/server/__init__.py` | 修改 | 匯出 `create_app` |
| `src/app/tools/rag_registry.py` | 修改 | 移除 `DataManager` 依賴；新增 `__enter__`/`__exit__`；內建 `_list_sites()`/`_site_exists()` |
| `src/app/tools/tool.py` | 修改 | `create_tool(registry)` 改為接收 registry 參數，回傳 `list[StructuredTool]` |
| `src/cli.py` | 修改 | AgentCLI 直接呼叫 `run_agent`；ServerCLI 直接呼叫 `run_app`；移除 `import uvicorn` |
| `src/utils/server_helper.py` | **已刪除** | 9 個函式已無引用 |
| `src/test/dev/test_create_tool.py` | 新增 | `create_tool` 單元測試 |
| `src/test/dev/test_run_agent.py` | 新增 | `run_agent` 單元測試（含 context manager 路徑） |
| `src/test/dev/test_resource_lifecycle.py` | 新增 | 整合管線測試 |
| `src/test/dev/test_rag_tools.py` | 新增 | `RAGRegistry` 單元測試（含 context manager、缺失目錄分支） |
| `src/test/dev/test_agent_server.py` | 修改 | 適配 `create_app` 新簽名 |
| `src/test/dev/_helpers.py` | 新增 | 共用測試輔助函式（`mock_exit_delegates_to_real`） |
| `src/test/test_module.py` | 修改 | 適配新 API |

### 4. 測試覆蓋

| 測試檔案 | 數量 | 覆蓋內容 |
|---------|------|---------|
| `test_create_tool.py` | 4 | 工具建立、registry 傳遞 |
| `test_run_agent.py` | 10 | RunManager 建立、ask/save_results、context manager close（成功/失敗/registry 建立失敗）、publish_run_metadata |
| `test_resource_lifecycle.py` | 3 | 整合管線：資源流動、成功路徑 close、錯誤路徑 close |
| `test_rag_tools.py` | 8 | Registry CRUD、cache hit/miss、LRU 淘汰、context manager、缺失目錄分支 |
| `test_agent_server.py` | — | SSE / health / CORS 端點、`create_app` 新簽名 |
| `test_module.py` | — | 整合 smoke test |

### 5. CR 修正紀錄

共 11 件問題，經兩輪 CR 修正完成：

| ID | 嚴重度 | 問題 | 修正 |
|----|--------|------|------|
| C1 | MAJOR | `uvicorn.run()` 在 context manager 外部 | 移入 `with` 區塊 |
| M1 | MAJOR | `create_app` lifespan 與 context manager 雙重 close | 移除 `create_app` 的 `registry` 參數 |
| M2 | MAJOR | 測試 assertion 為 vacuous | 補上 `create_tool` mock 驗證 |
| A1 | SUGGESTION | `dev.md` API 簽名過時 | 更新 |
| A2 | SUGGESTION | registry 建立失敗路徑無測試 | 新增 |
| B1 | SUGGESTION | 測試方法名過時 | 重新命名 |
| B2 | SUGGESTION | 缺少 webpages 目錄不存在分支測試 | 新增 |
| S1 | SUGGESTION | `with (` 格式不一致 | 統一 |
| C2 | MINOR | 測試 docstring 沿用「finally 區塊」 | 改為「context manager」 |
| C3 | MINOR | 測試輔助函式重複 | 抽至 `_helpers.py` |
| C4 | MINOR | `__exit__` 無型別標註 | 補齊 |

### 6. 已知限制

| 類別 | 說明 |
|------|------|
| **test_cli.py 未實作** | AgentCLI / ServerCLI 分支測試尚未建立 |
| **未驗證整合** | 測試均為 mock-based / temp-dir-based，未在含真實 LLM / RAG / Milvus 的環境中執行端到端驗證 |
| **app.py module docstring 過時** | 頂層 docstring 仍提及舊 API 名稱，待後續修正 |
