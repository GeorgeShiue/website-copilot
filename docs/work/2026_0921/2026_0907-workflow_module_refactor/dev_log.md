# 2026/09/14 實作紀錄

> 對應規劃文件：`resource_lifecycle_refactor.md`

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

---

## 二：API 重構 (9/8)

> 本段記錄模組 API 重構的完整執行結果。詳細規劃見 [api_refactor.md](./api_refactor.md)。

### 1. 概覽

| 項目 | 內容 |
|------|------|
| **日期** | 2026-09-08 |
| **範圍** | 8 個檔案（6 source + 2 test groups），共 6 個 Phase |
| **目標** | 消除重複 API、統一建構入口、簡化類別設計 |
| **狀態** | ✅ 全部完成 |

### 2. Phase 摘要

#### Phase 1：VectorStoreBuilder API 合併

- `build_milvus()` 改名為 `build()`，成為唯一入口
- 刪除舊的 `build()` 薄 wrapper
- **檔案：** `src/app/engines/rag/rag_factory.py`

#### Phase 2：RAGBuilder 統一入口 + 回傳值統一

- `build_reusable()` 成為唯一入口；刪除 `build()`、`build_to_retriever()`、`_create_rag()` 死碼
- `run_rag_build` 改用 `build_reusable(rag, force_rebuild=True)`
- **檔案：** `src/app/engines/rag/rag_factory.py`、`src/app/workflow/workflow.py`

#### Phase 2.5：RAGBuilder 薄 wrapper 精簡

- 精簡 `build_vector_store()` 薄 wrapper，移除多餘 logging（由底層 Builder 處理）
- **檔案：** `src/app/engines/rag/rag_factory.py`

#### Phase 3：create_rag() + run_rag_build 刪除 + run_rag_query 重構

- 新增 `create_rag()` — 僅建構 RAG，呼叫端以 `with ... as rag:` 管理生命週期
- 新增 `_create_run_context()` 與 `run_workflow_context()` 共用 helper，消除重複初始化/logging pattern
- 刪除 `run_rag_build`，所有 5 位呼叫端遷移至 `create_rag()` + 直接落盤
- 重構 `run_rag_query` 使用 `create_rag()` + 共用 helper
- **檔案：** `src/app/workflow/workflow.py`、`src/main.py`、`src/cli.py`、`src/test/test_main.py`、`src/test/test_module.py`、`src/test/dev/test_multi_site.py`

#### Phase 4A：Tool class 整併

- 刪除 `create_tool()` 函式，新增 `Tool` class（`__init__(registry)` + `@property tools`）
- `run_agent()`、`run_app()` 改用 `Tool(registry).tools`
- 同步更新 3 個測試檔案共 18 處 mock patch
- **檔案：** `src/app/tools/tool.py`、`src/app/workflow/workflow.py`、`src/test/dev/test_create_tool.py`、`src/test/dev/test_run_agent.py`、`src/test/dev/test_resource_lifecycle.py`

#### Phase 4B：Agent class 簡化

- 移除 `@dataclass`，改用普通 class + 明確 `__init__`
- `checkpointer` 預設 `None`，fallback 為 `InMemorySaver()`
- **檔案：** `src/app/agent/agent.py`

### 3. 關鍵設計決策

| 決策 | 理由 |
|------|------|
| `create_rag()` 回傳 open RAG 實例 | CR 修正：原本在函式內部 close RAG 是反模式，呼叫端無法使用回傳物件。改為 `with ... as rag:` pattern |
| `_create_run_context()` 僅改 3 個 run_* 函式 | 先穩定核心流程；`run_agent` / `run_app` 視需求再納入 |
| 方案 B（精簡薄 wrapper）而非方案 A（底層 Builder 持有 config） | 低風險、漸進式；`VectorStoreBuilder` 目前是 static methods，改為 instance-based 改動面較大 |
| `Tool` class 不實作 context manager | `Tool` 是無狀態工具建立器，不需要生命週期管理 |
| `force_rebuild=True` 在測試中必須顯式指定 | CR 修正：缺失此參數會導致測試跳過完整建構流程 |

### 4. 驗收結果

| 準則 | 狀態 |
|------|------|
| `VectorStoreBuilder` 只剩 `build()`，無 `build_milvus` 殘留 | ✅ |
| `RAGBuilder` 只剩 `build_reusable()` 及子步驟方法 | ✅ |
| `create_rag()` 僅建構不含 query | ✅ |
| `run_rag_build` 從所有檔案移除 | ✅ |
| `_create_run_context()` / `run_workflow_context()` 已應用 | ✅ |
| `Tool` class 存在，`create_tool()` 已移除 | ✅ |
| `Agent` class 無 `@dataclass` | ✅ |
| 所有 dev tests 通過 | ✅ |

### 5. 各 Phase 完成記錄

#### Phase 1：VectorStoreBuilder API 合併 — 完成記錄

- **完成時間：** 2026-09-08 22:11
- **檔案變更：** `src/app/engines/rag/rag_factory.py`
- **變更內容：** 將 `VectorStoreBuilder.build_milvus()` 改名為 `build()`，刪除舊的 `build()` 薄 wrapper
- **驗證結果：** `grep -r "build_milvus" src/` 無匹配；Python 語法檢查通過

#### Phase 2：RAGBuilder 統一入口 — 完成記錄

- **完成時間：** 2026-09-08 22:15
- **檔案變更：** `src/app/engines/rag/rag_factory.py`、`src/app/workflow/workflow.py`
- **變更內容：** 刪除 `RAGBuilder.build()`、`build_to_retriever()`、`_create_rag()` 死碼；`run_rag_build` 改用 `build_reusable(rag, force_rebuild=True)`
- **驗證結果：** `grep -n "def build" rag_factory.py` 僅顯示 `build_reusable()` 為入口；`_create_rag` 和 `build_to_retriever` 已移除；Python 語法檢查通過

#### Phase 2.5：RAGBuilder 薄 wrapper 精簡 — 完成記錄

- **完成時間：** 2026-09-08 22:18
- **檔案變更：** `src/app/engines/rag/rag_factory.py`
- **變更內容：** 精簡 `build_vector_store()` 薄 wrapper，移除多餘的 `logger.info`（已由 `VectorStoreBuilder.build()` 在 debug 級別記錄）
- **驗證結果：** 流程與功能不變；Python 語法檢查通過

#### Phase 3：create_rag() + run_rag_build 刪除 — 完成記錄

- **完成時間：** 2026-09-08 22:25（CR 修正於 22:22）
- **檔案變更：** `src/app/workflow/workflow.py`、`src/main.py`、`src/cli.py`、`src/test/test_main.py`、`src/test/test_module.py`、`src/test/dev/test_multi_site.py`
- **變更內容：**
  1. 新增 `create_rag()` — 僅建構，不負責 RAG 生命週期（呼叫端以 `with ... as rag:` 管理）
  2. 新增 `_create_run_context()` 與 `run_workflow_context()` 共用 helper
  3. 刪除 `run_rag_build`，所有呼叫端遷移至 `create_rag()` + 直接落盤
  4. 重構 `run_rag_query` 使用 `create_rag()` + 共用 helper
  5. CR 修正：`create_rag()` 不再內部 close RAG（回傳 open RAG 實例）；`force_rebuild=True` 補入測試
- **驗證結果：** `grep -r "run_rag_build" src/` 無匹配；所有 5 位呼叫端使用 `with ... as rag:` context manager；Python 編譯檢查通過

#### Phase 4A：Tool class 整併 — 完成記錄

- **完成時間：** 2026-09-08 22:26
- **檔案變更：** `src/app/tools/tool.py`、`src/app/workflow/workflow.py`、`src/test/dev/test_create_tool.py`、`src/test/dev/test_run_agent.py`、`src/test/dev/test_resource_lifecycle.py`
- **變更內容：**
  1. `tool.py`：刪除 `create_tool()` 函式，新增 `Tool` class（`__init__(registry)` + `@property tools`）
  2. `workflow.py`：`run_agent()` 與 `run_app()` 改用 `Tool(registry).tools`
  3. `test_create_tool.py`：4 處測試改寫為 `Tool` class 介面
  4. `test_run_agent.py`：11 處 mock patch 從 `create_tool` → `Tool`
  5. `test_resource_lifecycle.py`：3 處 mock patch 從 `create_tool` → `Tool`
- **驗證結果：** `grep -rn "create_tool" src/` 無匹配；`test_create_tool.py` 4/4 通過；`test_run_agent.py` 11/11 通過；`test_resource_lifecycle.py` 3/3 通過；共 18/18 測試通過

#### Phase 4B：Agent class 簡化 — 完成記錄

- **完成時間：** 2026-09-08 22:26
- **檔案變更：** `src/app/agent/agent.py`
- **變更內容：**
  1. 移除 `@dataclass` 裝飾器
  2. 移除 `from dataclasses import dataclass, field` import
  3. 新增明確 `__init__` 方法（typed parameters: `graph`, `tools`, `run_manager`, `config`, `checkpointer`）
  4. `checkpointer` 預設 `None`，fallback 為 `InMemorySaver()`
- **驗證結果：** `grep -rn "@dataclass" src/app/agent/agent.py` 無匹配；`create_agent()` 正常運作；Pylance 靜態分析無新錯誤

#### Round 2：run_rag_build + Tool lifecycle + run context 統一 (9/9)

- **完成時間：** 2026-09-09
- **檔案變更：** workflow.py, tool.py, rag_registry.py, main.py, cli.py, test_main.py, test_module.py, test_multi_site.py, site_discovery.py, webpage_retriever.py, agent.py
- **變更內容：**
  1. 新增 `run_rag_build()` — create_rag + save_results_as_json + save_module_config_as_toml + close，回傳 RunManager
  2. 取代所有 `with create_rag` 呼叫者（main.py, cli.py, 3 個測試檔）改用 `run_rag_build()`
  3. RAGRegistry 移入 tool.py；Tool 接收 `config_name` 自建 registry + close() + context manager
  4. 新增 `_create_run_no_site_context()` 統一 run_agent/run_app 的 RunManager 建立
  5. CR 修復：循環匯入（rag_registry.py 保持 RAGRegistry 正規位置）、main.py RAGBuildRunConfig 補 save_vector_store_to_runs=True、agent.py docstring 更新
- **驗證結果：** 5/5 測試通過

### 6. 風險與注意事項

| 風險 | 影響 | 緩解措施 |
|------|------|----------|
| Phase 3 的 `create_rag()` 改變 RAG 生命週期 | `run_rag_query` 中 `with (rag, ...)` 的 context manager 範圍可能需調整 | 確保 `create_rag()` 回傳的 RAG 仍由呼叫端負責 close |
| Phase 3 的 A3/A4 抽出共用 helper | 可能影響 `run_agent`、`run_app` 的 logging 行為（若它們也使用共用 helper） | 先僅改 `run_website_crawler`、`run_webpage_image_summarizer`、`run_rag_query` 三個函式；`run_agent` / `run_app` 視需求再納入 |
| Phase 4A 的 Tool class 影響測試 | `test_create_tool.py` 有 4 處測試 | 同步更新測試 |
| Phase 3 與 0907 重構的 `create_tool` 衝突 | 0907 重構已將 `create_tool` 移至 workflow.py，此處再改 Tool class 需確認不衝突 | 確認 `create_tool` 在 workflow.py 中的實際位置與用途 |
| Phase 2.5 的薄 wrapper 重構範圍 | 方案 A 改動面大，方案 C 使 `build_reusable` 過長 | 建議先用方案 B（精簡），後續視情況升級 |

### 7. 待確認事項 ✅ 已解決

1. ~~`create_rag()` 回傳 `RAG` 實例後，落盤邏輯應留在哪裡？~~ → 已由 `run_rag_build()` 內化處理
2. ~~`Tool` class 是否需要實作 `__enter__` / `__exit__`？~~ → 不需要。`Tool` 是無狀態工具建立器，不需要 context manager。
3. ~~Phase 4A 與 Phase 4B 是否需要在同一次迭代中完成？~~ → 已在同一次迭代完成（均於 2026-09-08 22:26）

### 8. 殘留 Tech Debt / 後續建議

1. **`run_agent` / `run_app` 導入共用 helper：** 目前僅 `run_rag_query`、`run_website_crawler`、`run_webpage_image_summarizer` 使用 `_create_run_context()` / `run_workflow_context()`；`run_agent` 和 `run_app` 仍使用舊的初始化 pattern，後續可統一
2. **薄 wrapper 方案 A 升級：** 若未來 `NodePipelineBuilder` / `VectorStoreBuilder` 改為 instance-based（持有 config），可進一步消除參數傳遞
3. **`run_rag_build` 的直接落盤邏輯：** `main.py` 和 `cli.py` 在 `create_rag()` 後直接處理 RunManager 和落盤，未來可考慮將落盤邏輯封裝為共用 helper（如 `persist_rag_build()`）

---

## 三：Run Method 落盤內化 (9/9)

### 1. 概述

將 `save_run_config_as_toml`、`publish_run_metadata`、`log_run_paths` 從呼叫者移入各 run method 內部。呼叫者僅需傳入 `run_config` 和 `data_manager`，不再負責落盤。

### 2. 變更摘要

| 函式 | 新增參數 | 回傳值改動 | 落盤時機 | category |
|------|----------|-----------|----------|----------|
| `run_website_crawler` | `run_config: WebsiteCrawlerRunConfig \| None` | `(dict \| None, RunManager)` → `dict \| None` | 完成時 | `webpages` |
| `run_webpage_image_summarizer` | `run_config: WebpageImageSummarizerRunConfig \| None` | `(dict \| None, RunManager)` → `dict \| None` | 完成時 | `webpages` |
| `run_rag_build` | `run_config: RAGBuildRunConfig \| None` | `RunManager` → `None` | 完成時 | `rag` |
| `run_rag_query` | `run_config: RAGQueryRunConfig \| None` | `RunManager` → `None` | 完成時 | `rag` |
| `run_agent` | 加型別提示 `AgentRunConfig \| None` | `None`（不變） | 完成時 | `agent` |
| `run_app` | `run_config: ServerRunConfig \| None` | `None`（不變） | 啟動時 | N/A |

### 3. 呼叫者改動

| 檔案 | 改動 |
|------|------|
| `main.py` | 移除所有落盤代碼，改為傳入 `run_config` + `data_manager` |
| `cli.py` | 移除底部落盤代碼，4 個函式加上 `run_config=cli_arg.run` |
| `test_multi_site.py` | 同步簡化 |

### 4. 關鍵設計決策

| 決策 | 理由 |
|------|------|
| `run_config` 為 optional 參數 | 向後相容；main.py 等不需落盤的場景可不傳 |
| `publish` 欄位保留在 BaseRunConfig | 由 `data_manager=None` 控制是否 publish，publish 欄位保留供未來使用 |
| `run_agent` 的 `publish_run_metadata` 加 `site_id` guard | agent 使用 `for_run_no_site`，site_id 恆為空字串，不應 publish |
| `run_app` 在啟動時落盤 | 伺服器阻塞無「完成」時機，改為啟動時記錄 init 狀態 |

### 5. CR 修正紀錄

| ID | 嚴重度 | 問題 | 修正 |
|----|--------|------|------|
| C1 | CRITICAL | 4 個 run_config 參數缺少型別提示 | 補齊型別提示 |
| C2 | CRITICAL | run_agent publish_run_metadata 用 site_id="" | 加 `run_manager.site_id` guard |
| M1 | MAJOR | CLI 未傳入 run_config=cli_arg.run | 4 個函式補上 |
| B1 | BUG | save_run_config_as_toml 未加 None guard 導致 crash | 6 處加 `if run_config is not None:` |

### 6. 驗收結果

| 準則 | 狀態 |
|------|------|
| 6 個 run method 均接受 run_config | ✅ |
| 回傳值統一（crawler/summarizer → dict\|None，其餘 → None） | ✅ |
| 呼叫者不再做外部落盤 | ✅ |
| CLI 正確傳入 run_config | ✅ |
| 所有 save_run_config_as_toml 均有 None guard | ✅ |
| 所有 dev tests 通過 | ✅ |

---

## 四：LLM 統一切換為 OpenAI (9/9)

> 本段記錄將程式碼庫中所有 LLM 使用從混合 Gemini + OpenAI 統一切換為 OpenAI 模型的完整實作過程。

### 1. 目標

| 目標 | 說明 |
|------|------|
| **統一 LLM 為 OpenAI** | 所有主要 LLM 呼叫改用 OpenAI 模型，預設模型為 `gpt-5.6-luna` |
| **保留 Gemini 介面** | `langchain_helper.py` 和 `rag_helper.py` 的 Gemini 分支保留作為可選項，但預設與設定檔均指向 OpenAI |
| **API Key 統一** | 主要流程使用 `OPENAI_API_KEY`；Gemini 仍沿用 `GEMINI_*` 環境變數（向後相容） |

### 2. 模型對應

| 用途 | 原模型 | 新模型 | 備註 |
|------|--------|--------|------|
| RAG 查詢 (`query_llm_name`) | `gemini-3.1-flash-lite` | `gpt-5.6-luna` | 所有 RAG TOML 設定檔已更新 |
| Agent 對話 (`llm_name`) | `gemini-3.1-flash-lite` | `gpt-5.6-luna` | 所有 Agent TOML 設定檔已更新 |
| VLM 圖片摘要 (`model`) | `gemini-3-flash-preview` | `gpt-5.6-luna` | 所有 webpage_image_summarizer TOML 已更新 |
| RAG 評估器 (`evaluator_llm_name`) | `gpt-5.4` | `gpt-5.6-terra` | 升級至 terra 版本以提升評估品質 |

### 3. 修改檔案清單

#### 核心程式碼

| 檔案 | 變更 | 說明 |
|------|------|------|
| `src/utils/langchain_helper.py` | 修改 | `ChatOpenAI` 加入 `SecretStr` 包裝 `api_key`；新增 `use_responses_api=True` 解決 reasoning_effort + function tools 不相容問題；保留 Gemini 分支作為可選項 |
| `src/app/engines/webpage_image_summarizer.py` | 修改 | VLM 模型預設參數更新；`litellm` 調用支援 OpenAI 模型路由 |
| `src/app/engines/rag/rag_factory.py` | 修改 | 移除 `build_milvus` 死碼（先前 Phase 1 已完成）；確保 OpenAI 模型正確傳遞 |
| `src/utils/rag_helper.py` | 修改 | LLM API key 環境變數對應表更新，`gpt` provider 使用 `OPENAI_API_KEY` |

#### Python Config

| 檔案 | 變更 | 說明 |
|------|------|------|
| `src/app/configs/agent_config.py` | 修改 | `DEFAULT_LLM_NAME` 預設值改為 `"gpt-5.6-luna"` |
| `src/app/configs/rag_config.py` | 修改 | `query_llm_name` 和 `evaluator_llm_name` 預設值改為 OpenAI 模型 |
| `src/app/configs/webpage_image_summarizer_config.py` | 修改 | `model` 預設值改為 `"gpt-5.6-luna"`；Gemini API key 環境變數保留 |

#### TOML 設定檔（共 15 個）

| 目錄 | 檔案 | 更新內容 |
|------|------|----------|
| `configs/agent/` | `default.toml`, `test.toml` | `llm_name = "gpt-5.6-luna"` |
| `configs/rag/` | `default.toml`, `milvus.toml`, `nculab.toml`, `ncucsie.toml`, `test.toml`, `test_nculab.toml`, `test_ncucsie.toml` | `query_llm_name = "gpt-5.6-luna"`, `evaluator_llm_name = "gpt-5.6-terra"` |
| `configs/webpage_image_summarizer/` | `default.toml`, `nculab.toml`, `ncucsie.toml`, `test.toml`, `test_nculab.toml`, `test_ncucsie.toml` | `model = "gpt-5.6-luna"` |

#### 環境變數 / CI

| 檔案 | 變更 | 說明 |
|------|------|------|
| `.env` | 檢查 | `OPENAI_API_KEY` 已存在；Gemini 環境變數保留供可選使用 |
| `.github/workflows/ci.yml` | 檢查 | 同時寫入 `OPENAI_API_KEY` 與 `GEMINI_*` 環境變數（向後相容） |
| `.github/workflows/ci-test.yml` | 檢查 | 同 ci.yml |

#### 依賴

| 檔案 | 變更 | 說明 |
|------|------|------|
| `pyproject.toml` | 修改 | 升級 `langchain` >= 1.4.0、`llama-index` >= 0.14.24、`llama-index-llms-openai` >= 0.7.9；新增 `langchain-openai` >= 0.3.0 為明確依賴 |
| `uv.lock` | 重新產生 | 反映新依賴版本 |

### 4. 遇到的問題與解決方案

#### 問題 1：llama-index 不識別 `gpt-5.6-luna`

| 項目 | 內容 |
|------|------|
| **症狀** | `llama-index-llms-openai` 0.7.7 回傳 `Unsupported model` 錯誤 |
| **根因** | 舊版 `llama-index-llms-openai` 的模型白名單未包含 `gpt-5.6-luna` |
| **解決** | 升級 `llama-index-llms-openai` 至 0.7.9+（lockfile 解析為 0.7.10） |
| **驗證** | RAG 查詢與 Agent 對話正常執行 |

#### 問題 2：`reasoning_effort` + function tools 不相容

| 項目 | 內容 |
|------|------|
| **症狀** | `gpt-5.6-luna` 在使用 function calling（Agent tools）時觸發 `reasoning_effort` 參數衝突 |
| **根因** | OpenAI Responses API 與 Chat Completions API 的 tool calling 行為差異 |
| **解決** | 在 `langchain_helper.py` 的 `ChatOpenAI` 呼叫中設定 `use_responses_api=True`，強制使用 Responses API |
| **驗證** | Agent 工具呼叫（`webpage_retriever`、`list_knowledge_bases`）正常執行 |

#### 問題 3：langchain 1.4.0 breaking change — `api_key` 型別要求

| 項目 | 內容 |
|------|------|
| **症狀** | `langchain` 升級至 1.4.0 後，`ChatOpenAI(api_key=str)` 產生型別錯誤 |
| **根因** | `langchain` 1.4.0 要求 `api_key` 為 `SecretStr` 型別（安全考量） |
| **解決** | `langchain_helper.py` 中改用 `from pydantic import SecretStr` 包裝：`api_key=SecretStr(api_key)` |
| **驗證** | 型別檢查通過，ChatOpenAI 建立正常 |

#### 問題 4：`pyproject.toml` 未宣告 `langchain-openai` 為明確依賴

| 項目 | 內容 |
|------|------|
| **症狀** | `uv sync` 後 `langchain-openai` 可能因依賴鏈消失而缺失 |
| **根因** | `langchain-openai` 原本僅透過 `langchain` 間接依賴，未在 `pyproject.toml` 中明確宣告 |
| **解決** | 在 `pyproject.toml` 的 `dependencies` 中新增 `"langchain-openai>=0.3.0"` |
| **驗證** | `uv sync` 後 `langchain-openai` 穩定安裝（lockfile 版本 1.6.1） |

### 5. 測試結果

| 測試 | 狀態 | 備註 |
|------|------|------|
| `test_website_crawler` | ✅ 通過 | |
| `test_webpage_image_summarizer` | ✅ 通過 | |
| `test_rag` | ✅ 通過 | |
| `test_agent` | ✅ 通過 | |
| `test_server` | ⏭️ 略過 | 需要完整伺服器環境，CI 外略過 |

**總計：4/4 通過**（略過 test_server）

### 6. 套件版本變更

| 套件 | 原版本 | 新版本 | 備註 |
|------|--------|--------|------|
| `llama-index` | 0.14.21 → 0.14.16 (pyproject) | 0.14.24 (pyproject) / 0.14.24 (lock) | 含 `llama-index-llms-openai` 依賴 |
| `llama-index-llms-openai` | 0.7.7 (lock) | 0.7.9 (pyproject min) → 0.7.10 (lock) | 關鍵：新增 `gpt-5.6-luna` 支援 |
| `langchain` | 1.3.14 (pyproject) | 1.4.0 (pyproject) / 1.4.0 (lock) | `api_key` SecretStr 要求 |
| `langchain-openai` | （間接依賴） | 0.3.0 (pyproject min) / 1.6.1 (lock) | 新增為明確依賴 |

### 7. 設計決策

| 決策 | 理由 |
|------|------|
| 保留 Gemini 分支在 `langchain_helper.py` 和 `rag_helper.py` | 向後相容；若需切回 Gemini，僅需修改 TOML 設定檔中的 model name |
| 使用 `use_responses_api=True` 而非禁用 function tools | Responses API 是 OpenAI 推薦的新介面，功能更完整；禁用 tools 會喪失 Agent 能力 |
| TOML 設定檔為主要切換點 | 改 model name 即可切換 LLM provider，無需改程式碼 |
| `SecretStr` 包裝 `api_key` | 符合 langchain 1.4.0 安全規範，避免 log 洩漏 API key |

### 8. 已知限制

| 類別 | 說明 |
|------|------|
| **`webpage_image_summarizer.py` 預設參數** | 函式簽名的預設值仍為 `gemini-3-flash-preview`（第 67 行），實際執行由 TOML config 覆蓋為 `gpt-5.6-luna`。預設參數為歷史殘留，建議後續同步更新 |
| **Gemini 環境變數保留** | `.env` 和 CI workflow 中仍寫入 `GEMINI_*` 變數。若未來完全移除 Gemini 支援，可清理 |
| **端到端未驗證** | 測試均為 mock-based / config-based；未在含真實 Milvus + 完整資料的環境中執行完整管線驗證 |

---

## 五：Agent 拆分 + run_app 重構 (9/9)

### 1. 概述

將 `run_agent()` 拆分為 `run_agent_build()`（建立 Tool + Agent，return 實例）與 `run_agent_query()`（接受外部 agent 執行問答 + 落盤）；`run_app()` 改為接受外部 `agent` 參數並返回 `uvicorn.Server`（非阻塞），移除內部 Tool/agent 建立邏輯。`run_agent()` 保留為 deprecated wrapper。同步更新 `cli.py` 的 AgentCLI / ServerCLI 分支。

### 2. 關鍵設計決策

| 決策 | 理由 |
|------|------|
| `run_agent_build()` return `(Agent, Tool)` tuple | 類似 `create_rag()` 模式，呼叫端負責 tool.close() |
| `run_agent_query()` 移除 `tool` 參數 | 函式內部不使用 tool，僅用 agent 執行問答 |
| `run_app()` return `uvicorn.Server` | 非阻塞，呼叫端可透過 `server.should_exit=True` 優雅關閉 |
| `run_agent()` 保留為 deprecated wrapper | 向下相容 CLI 及其他呼叫端，避免 breaking change |
| Agent 模組不加入 `data_manager` | 落盤機制尚未統合，後續再處理 |
| deprecated wrapper 使用 `tool = None` guard | 防止 `run_agent_build` 失敗時 `finally` 中 `NameError` |

### 3. 最終 API 簽名

| 函式 | 簽名 | 備註 |
|------|------|------|
| `run_agent_build` | `(config_name, run_config, **overrides) -> tuple[Agent, Tool]` | 類似 create_rag，建立並 return |
| `run_agent_query` | `(agent: Agent, query, thread_id, stream, run_config) -> None` | 接受外部 agent，執行問答 + 落盤 |
| `run_agent` | 同原簽名 | DEPRECATED wrapper，內部委派 build + query |
| `run_app` | `(agent: Agent, run_config, allowed_origins, host, port) -> uvicorn.Server` | 返回 server handle，非阻塞 |

### 4. 變更檔案

| 檔案 | 變更 | 說明 |
|------|------|------|
| `src/app/workflow/workflow.py` | 修改 | 拆分 run_agent → run_agent_build + run_agent_query；重構 run_app；保留 deprecated wrapper；新增 Agent import |
| `src/cli.py` | 修改 | AgentCLI / ServerCLI 分支改用新 API + try/finally 資源管理 |
| `src/test/test_module.py` | 修改 | 更新 imports；test_agent / test_server 使用新 API；test_server 改用 asyncio 非阻塞模式 |
| `src/test/test_main.py` | 修改 | 新增 imports + pytestmark；新增 run_agent_build + run_agent_query 調用 |

### 5. CR 修正紀錄

| ID | 嚴重度 | 問題 | 修正 |
|----|--------|------|------|
| C1 | CRITICAL | deprecated `run_agent` 中 `tool.close()` 在 `run_agent_build` 失敗時 NameError | 初始化 `tool = None` + `if tool is not None` guard |
| C2 | MAJOR | `run_agent_query` 接受未使用的 `tool` 參數 | 移除 tool 參數，更新所有 call site |
| C3 | MAJOR | `run_agent_build` / `run_agent_query` / `run_app` 缺少型別標註 | 補齊 Agent/Tool 型別標註 |
| C4 | CRITICAL | 測試檔案 `finally` blocks 中同様的 NameError 風險 | 三處統一加上 `tool = None` + guard pattern |

### 6. QA 驗證結果

| 指標 | 結果 |
|------|------|
| 測試總數 | 146 collected |
| 通過 | 128 ✅ |
| 失敗 | 18 ❌ (pre-existing，來自 commit `18a0bc2` 未更新 test_run_agent / test_resource_lifecycle / test_create_tool) |
| Import 驗證 | ✅ 全部 workflow imports 正常解析 |

### 7. 已知限制

| 類別 | 說明 |
|------|------|
| **test_run_agent.py 11 tests fail** | 舊 mock patch `RAGRegistry` 已不存在，需獨立更新 |
| **test_resource_lifecycle.py 3 tests fail** | 同上，mock 目標過時 |
| **test_create_tool.py 4 tests fail** | `Tool` 不再接受 `registry` 參數，需改為 `Tool(config_name=...)` |
| **test_server sleep(2) 脆弱** | 非阻塞啟動使用固定 2 秒等待，CI 負載高時可能不穩定 |

---

## 六：Agent 擁有 Tool 生命週期 (9/10)

### 1. 概述

將 `Agent` 類別從接受 `tools: list[StructuredTool]` 改為接受 `tool: Tool` 實例，由 Agent 統一管理 Tool 生命週期。新增 `Agent.close()` 與 context manager 支援（`__enter__` / `__exit__`）。`run_agent_build()` 改為 return `Agent`（非 tuple），所有呼叫端統一使用 `agent.close()` 釋放資源。

### 2. 關鍵設計決策

| 決策 | 理由 |
|------|------|
| `Agent` 持有 `Tool` 實例（非 StructuredTool 列表） | 統一資源管理，消除呼叫端需手動 `tool.close()` 的負擔 |
| `agent.tools` 保留為 `@property` | 向後相容：LangGraph 等外部系統仍需存取 `list[StructuredTool]` |
| `run_agent_build()` return `Agent`（非 tuple） | Agent 已持有 Tool，不需要分開回傳 |
| `run_agent_build` 中 `create_agent()` 失敗時 close tool | 防止 Tool/RAGRegistry 資源洩漏 |
| `Agent` 支援 context manager | 與 `Tool` 和 `RAGRegistry` 模式一致 |

### 3. 最終 API 簽名

| 函式/類別 | 簽名 | 備註 |
|-----------|------|------|
| `Agent.__init__` | `(graph, tool: Tool, run_manager, config, checkpointer)` | `tool` 為 Tool 實例 |
| `Agent.tools` | `@property → list[StructuredTool]` | 向後相容， delegating `self.tool.tools` |
| `Agent.close()` | `() → None` | 釋放 Tool 管理的資源 |
| `Agent.__enter__` / `__exit__` | context manager | 支援 `with agent:` 語法 |
| `create_agent` | `(config, tool: Tool, run_manager) → Agent` | 改收 Tool 實例 |
| `run_agent_build` | `(config_name, run_config, **overrides) → Agent` | return 單一 Agent |

### 4. 變更檔案

| 檔案 | 變更 | 說明 |
|------|------|------|
| `src/app/agent/agent.py` | 修改 | `tools` → `tool: Tool`；新增 `close()` / `__enter__` / `__exit__`；`tools` 保留為 property |
| `src/app/workflow/workflow.py` | 修改 | `run_agent_build` return `Agent`；error path 加 tool close guard；`run_agent` wrapper 改用 `agent.close()` |
| `src/cli.py` | 修改 | AgentCLI / ServerCLI 改用 `agent.close()` |
| `src/test/test_module.py` | 修改 | `tool.close()` → `agent.close()` |
| `src/test/test_main.py` | 修改 | 同上 |

### 5. CR 修正紀錄

| ID | 嚴重度 | 問題 | 修正 |
|----|--------|------|------|
| C1 | MAJOR | `run_agent_build` 中 `create_agent()` 失敗時 Tool 資源洩漏 | try/except guard：失敗時 `tool.close()` + re-raise |

### 6. 已知限制

| 類別 | 說明 |
|------|------|
| **18 dev tests 仍 fail** | 舊 test 檔 mock patch 過時（RAGRegistry / Tool(registry=) API 已變更），需獨立更新 |

---

## 七：Agent 不再持有 RunManager（落盤責任上移至呼叫端）(9/10)

### 1. 概述

`Agent`（`src/app/agent/agent.py`）原先是**唯一**持有 `RunManager` 的類別，且直接 `from app.workflow.run_manager import RunManager`，造成 **agent 層 → workflow 層的反向依賴**（`agent.py` 亦留有原始動機註解 `# ? 能否移除 run_manager 參數，所有落盤機制都改為不由 Agent 負責`）。

本輪**斬斷 agent 層對 workflow 層的依賴**，讓落盤（`RunManager`）與資源生命週期的責任完全落在上層呼叫端。重構後的三條呼叫路徑：

| 路徑 | run context / RunManager 建立者 | Agent 關閉歸屬 | 落盤 |
|---|---|---|---|
| CLI 查詢（`agent-cli`） | `run_agent_query` | `run_agent_query` 的 `finally` | `run_manager.save_agent_results_as_json(...)` |
| Server（`server-cli`） | `run_app` | `ChatApp.close()` | `_event_stream` → `run_manager.save_agent_results_as_json(...)` |
| 完整啟動（`src/main.py`） | `run_app` | `ChatApp.close()` | 同上 |

**範圍外（明確不做）**：新增 serving 期 log 落 `terminal.log` 的能力、`site_id` 落盤擴充、既有 `for_run*` / `save_results_as_json` / `find_thread_history_path` 等 RunManager API 的移除或改名。

### 2. 關鍵設計決策（D1–D7）

| 編號 | 決策項 | 定案 |
|---|---|---|
| D1 | run context 形狀 | **X2**：`run_agent_query` / `run_app` 各自在內部建立 run context，並在其中建立 Agent（與既有 `run_rag_query` → `create_rag` 模式一致） |
| D2 | `main.py` 的 `UnboundLocalError` bug | **結構性消解**：`run_app(...)` 呼叫置於 `try` 之前，不需 `agent = None` 哨兵 |
| D3 | `config_summary` 組裝位置 | **方案 C**：收進 `RunManager.save_agent_results_as_json`，改收 `AgentConfig` |
| D4 | `main.py` 的 Agent 步驟 | 改為呼叫 `run_app` |
| D5 | server 路徑 agent 關閉歸屬 | `run_app` 回傳 `(uvicorn.Server, ChatApp)`；關閉由 `ChatApp.close()` 觸發 |
| D6 | `main.py` 定位 | 完整啟動工作流程；server 設為阻塞（`server.run()`） |
| D7 | `MainCLI` | **完整移除**（含 `tyro`、`dataclass` 匯入）；**不保留參數** → `def main() -> None`，寫死 `DEFAULT_CONFIG_NAME = "default"` |

### 3. 最終 API 簽名

```python
# src/app/agent/agent.py
def create_agent(config: AgentConfig, tool: Tool) -> Agent   # 收斂為 2 參數；無 run_manager
class Agent:                                                 # 僅持有 graph / tool / config / checkpointer

# src/app/workflow/workflow.py
def run_agent_build(config_name: str = "default", **config_overrides) -> Agent
    # 純建構：不建 run context、不包 logging context、不寫 run_config.toml
    # 保留「create_agent 失敗 → tool.close(); raise」

def run_agent_query(config_name: str = "default", query: str | None = None,
                    thread_id: str | None = None, stream: bool = False,
                    run_config: AgentRunConfig | None = None,
                    **config_overrides) -> None

def run_app(config_name: str = "default", run_config: ServerRunConfig | None = None,
            allowed_origins: list[str] | None = None, host: str = "127.0.0.1",
            port: int = 8000, **config_overrides) -> tuple[uvicorn.Server, ChatApp]

# src/app/workflow/run_manager.py
def save_agent_results_as_json(self, thread_id: str, results: list[dict[str, Any]],
                               agent_config: AgentConfig) -> str
    # config_summary 由本方法內部組裝，四鍵順序凍結：
    # config_name → run_name(self.run_name) → llm_name → system_prompt

# src/app/server/app.py
ChatApp.create(agent, run_manager, allowed_origins=None) -> ChatApp
ChatApp.close() -> None            # 僅呼叫 self.agent.close()；run_manager 無需釋放
_build_fastapi_app(agent, run_manager, allowed_origins=None) -> FastAPI
def get_run_manager(request: Request) -> RunManager   # FastAPI dependency

# src/main.py
DEFAULT_CONFIG_NAME = "default"
def main() -> None
```

**關鍵結構要求**：`run_agent_query` / `run_app` **內部呼叫 `run_agent_build`**，不得各自重寫建構流程。理由：(a) 建構邏輯單一來源；(b) `run_agent_build` 降級為程式化 API 而非 dead code；(c) 既有測試的 patch 目標 `app.workflow.workflow.create_agent` 仍有效 → 測試改動量最小。

### 4. 責任歸屬對照

| 責任 | 重構前 | 重構後 |
|---|---|---|
| 建立 Agent | `cli.py` / `main.py` | `run_agent_query` / `run_app` 內部（經 `run_agent_build`） |
| 建立 RunManager | `run_agent_build` 內 | `run_agent_query` / `run_app` 內（`create_run_no_site_context(module="agent", base_folder="runs")`） |
| `save_logging_file` 範圍 | 只在 build 內（僅建構期） | **build + query 全程**（建構期 log 仍進 `terminal.log`） |
| 落盤 | `Agent.save_results()` | `RunManager.save_agent_results_as_json()`，由呼叫端直接呼叫 |
| 關閉 Agent | `cli.py` / `main.py` 的 `finally` | query：`run_agent_query` 的 `finally`；server：`ChatApp.close()` |
| 呼叫端持有什麼 | `Agent` | query：無；server：`ChatApp` |

### 5. 變更檔案

| 檔案 | 變更 |
|---|---|
| `src/app/workflow/run_manager.py` | `save_agent_results_as_json` 改收 `agent_config: AgentConfig` 並於方法內組 `config_summary`；新增 `from app.configs.agent_config import AgentConfig`（無循環依賴）；回傳型別由 `str \| None` 收斂為 `-> str`（S1）。其餘 API 保留 |
| `src/app/agent/agent.py` | 刪 `RunManager` import／`run_manager` 參數與屬性／`Agent.save_results()`／`# ?` 待辦註解；`create_agent(config, tool)`；docstring 更新；`close()` / `__enter__` / `__exit__` 不動 |
| `src/app/workflow/workflow.py` | `run_agent_build` 純建構化；`run_agent_query` X2 化（run context + `save_logging_file` + 內部 build + 落盤 + `finally` close）；`run_app` X2 化 + 回傳 tuple + 失敗守衛 |
| `src/app/server/app.py` | `ChatApp.__init__` / `create` / `_build_fastapi_app` 收 `run_manager`；lifespan 綁 `app.state.run_manager`；新增 `get_run_manager` dependency；`_event_stream` 落盤改走 `run_manager.save_agent_results_as_json` |
| `src/cli.py` | Agent 分支 → `run_agent_query(**module_config_overrides)`；Server 分支 → `run_app(...)` + `try: server.run() finally: chat_app.close()`；移除 `run_agent_build` import 與 build/close 樣板 |
| `src/main.py` | 移除 `MainCLI` / `tyro` / `dataclass`；新增 `DEFAULT_CONFIG_NAME`；`def main() -> None`；Agent 步驟 → `run_app` + 阻塞 + `chat_app.close()`；`__main__` → `main()` |
| `src/test/dev/test_run_agent.py` | 全檔重寫：stub 去 `run_manager`／`save_results`（保留 `config`）；build 的 RunManager 斷言移轉至 query；新增 `stream=True` happy path、`run_config` / log 生命週期、`run_app` tuple / 失敗守衛測試 |
| `src/test/dev/test_agent_server.py` | `_FakeRunManager` 實作 `save_agent_results_as_json`；`_FakeAgent` 去 `run_manager`／`save_results`；`_make_client*` 注入 `run_manager`；`_FakeGraph.astream` 補 `AsyncIterator` 標註（S5） |
| `src/test/dev/test_runmanager_agent_results.py` | 呼叫點改傳 `agent_config=`；新增 `_FakeAgentConfig` / `EXPECTED_CONFIG` |
| `src/test/dev/test_create_tool.py` | incidental：移除未使用的 `RAGRegistry` import（來自前一輪 session 的遺留，使 `ruff check` 無法全綠） |
| `configs/agent/test.toml` | 移除 `llm_name` 行末已失效的 `# run name` 註解（S7，單行修正） |
| `src/test/test_main.py`、`src/test/test_module.py` | Phase 9（**未執行**）：X2 形狀 `run_agent_query(config_name="test", query=...)`；移除 `run_agent_build` import；`test_server` → `run_app(...)` + `finally: chat_app.close()` |
| `docs/code/phase2_3_mvp/{modules/agent.md,modules/server.md,phase2_3_mvp.md}`、`docs/code/runs/{cli,config,workflow}.md`、`README.md` | 文件同步（Phase 8）：移除 `Agent.run_manager` / `Agent.save_results()` / `create_agent(config, tool, run_manager)` 等過時敘述，改為新責任歸屬；`README.md` 移除 `(tyro MainCLI)` 註記 |

> 註：本輪 session 的工作樹為 `MM`（staged + unstaged），同時含**前幾輪 session** 的變更（例如 `src/app/workflow/workflow_helper.py` 新增、`src/test/dev/test_resource_lifecycle.py` 刪除）。上表僅列出**本次重構**造成的變更。

### 6. 實作階段摘要（Phases 0–9）

環境：Python 3.13.12、`uv`（所有指令為 `uv run …`）、pytest 9.0.3、ruff、pyright（`typeCheckingMode = "basic"`）。
**執行邊界**：僅 `**/test/dev/**` 可自主執行；`src/test/test_main.py` / `test_module.py` **禁止執行**；Phase 0 的 live agent query 因會呼叫付費 LLM API 而**略過**。

| Phase | 目標 | 主要產出 | 驗證 |
|---|---|---|---|
| 0 | 落盤契約基準（R3） | 無檔案變更；以**靜態等價**凍結契約：`{"config": {…}, "results": [...]}`、`json.dump(..., ensure_ascii=False, indent=4)`、`config` 四鍵順序、`results` 每筆 `{query, response, sources, timestamp}`、路徑 `runs/<ts>/agent/<config>/results_{thread_id}.json`（`/` → `_`） | 未實跑（付費 API）；改以結構 + 鍵序 + 測試斷言等效保證 |
| 1 | D3-C：config 摘要收進 RunManager | `run_manager.py` + `test_runmanager_agent_results.py` | 該測試檔 → 7 passed |
| 2 | `agent.py` 依賴歸零 | 刪 import／參數／`save_results()`；`create_agent(config, tool)` | 反向 grep 為空；pyright 0 error |
| 3 | `workflow.py` X2 + D5 | build 純建構化；query / app 自建 run context 並內部呼叫 build；`run_app` 回傳 tuple + 失敗守衛 | pyright 0 error；close 路徑由 Phase 7 測試鎖定 |
| 4 | `server/app.py` 注入 run_manager | 落盤改走 RunManager；`get_run_manager` dependency；lifespan 綁 `app.state.run_manager` | 循環依賴靜態檢視無；import 煙霧測試通過 |
| 5 | `cli.py` 兩分支改直接呼叫 | Agent → `run_agent_query`；Server → `run_app` + `try/finally` | 反向 grep 為空 |
| 6 | `main.py` D7 完整啟動流程 | 移除 `MainCLI`/`tyro`/`dataclass`；`DEFAULT_CONFIG_NAME`；`def main() -> None` | 反向 grep 為空；`import main` 煙霧測試 OK |
| 7 | dev 測試同步 + **整合綠燈檢查點** | 3 檔對齊新 API；`_FakeAgentStub` 保留 `config`、新增失敗 stub | `pytest src/test/dev/` → **151 passed**（當時）；`ruff check` 全綠 |
| 8 | 文件同步 | 4 份計畫指定文件 + 3 份計畫外但同樣過時的現行文件（`runs/workflow.md`、`runs/config.md`、`README.md`） | grep 驗證僅剩 `docs/work/**` 歷史紀錄 |
| 9 | production tests（X2 對齊；**只寫不跑**） | `test_main.py` / `test_module.py` 改為 X2 形狀 | lint / format / pyright / AST / 簽章比對全數靜態通過 |

**Phase 1–6 為單一耦合切換鏈**（簽章互相引用），中途整包 pytest 預期紅燈；**整合綠燈檢查點 = Phase 7**。各 Phase 的驗證以「靜態檢查 + 該 Phase 目標測試」為門檻。

**Phase 9 交付狀態**：`written-but-unexecuted` —— 撰寫在授權範圍內、執行不在。此為刻意狀態，非缺漏；不得以「未執行」為由推論失敗或通過。

### 7. 驗收條件達成狀態（Goals 1–10）

| Goal | 內容 | 判定 | 證據 |
|---|---|---|---|
| 1 | 依賴歸零 | **PASS** | 反向 grep `RunManager\|run_manager` in `src/app/agent/` → 零命中；`agent.py` 無 `app.workflow.run_manager` import |
| 2 | Signature 收斂 | **PASS** | `create_agent(config, tool)`；`Agent.__init__` 僅 `graph / tool / config / checkpointer`；`save_results` 已不存在；`close` / `__enter__` / `__exit__` 相對基準 0 變更 |
| 3 | build 純建構 | **PASS** | 簽名 `-> Agent`；移除 `run_config` / `create_run_no_site_context` / `save_logging_file` / `log_run_paths` / `save_run_config_as_toml`；保留 `except: tool.close(); raise` |
| 4 | query X2 | **PASS** | body 順序：`create_run_no_site_context` → `with save_logging_file` → `log_run_paths("init")` → `run_agent_build` → `ask`/`astream_result` → `save_agent_results_as_json(..., agent_config=agent.config)` → `save_run_config_as_toml` → `log_run_paths("complete")` → `finally: agent.close()`；以測試鎖定精確順序與三條 close 路徑 |
| 5 | app X2 | **PASS** | `-> tuple[uvicorn.Server, ChatApp]`；內部 `run_agent_build`；`ChatApp.create(agent, run_manager, allowed_origins)`；`log_run_paths("init")` + `("complete")`（**無 `"ready"`**）；`except Exception: agent.close(); raise` |
| 6 | D3-C | **PASS** | `save_agent_results_as_json(thread_id, results, agent_config) -> str`；`config_summary` 四鍵**順序**與基準逐欄位等價；JSON 外層結構與 dump 參數未變 |
| 7 | server 注入 | **PASS** | `_build_fastapi_app(agent, run_manager, allowed_origins)` + `app.state.run_manager` + `get_run_manager` Depends；`_event_stream` 落盤改走 RunManager；`site_id` 行為等價 |
| 8 | cli | **PASS** | Agent 分支 `run_agent_query(...)`；Server 分支 `server, chat_app = run_app(...)` + `try: server.run() finally: chat_app.close()`；兩分支已無 build/close 樣板 |
| 9 | D7 | **PASS（靜態）** | 反向 grep `MainCLI\|tyro\|dataclass` in `main.py` → 空；`DEFAULT_CONFIG_NAME`；`def main() -> None`；`run_app` 置於 `try` 之外（D2 結構修正） |
| 10 | 測試／文件同步 | **PARTIAL** | 7 份文件已同步；`test/dev` 全綠；`test_main.py` / `test_module.py` 已改為 X2 形狀但**未執行**（待授權）→ 分數僅反映此點，非缺陷 |

### 8. 風險與處置（R1–R9）

| # | 風險 | 等級 | 對策 | 結果 |
|---|---|---|---|---|
| R1 | `thread_id` 自動產生邏輯搬移時漏搬 → 「跑完但無檔案」靜默失敗 | 高 | 三處 `auto-{uuid4().hex[:8]}` 全數保留：`workflow.py`（CLI query）、`app.py`（server）、`langchain_helper.py`（`thread_config`）；以測試鎖定 | **PASS** |
| R2 | `**overrides` 傳遞對象由 build 改為 query/app 後靜默失效（`from_toml` 對未知 key 只 warning） | 高 | 逐一比對 `cli.py` 兩分支（`AgentModuleConfig` 僅含合法 key）；以 warning 為驗證訊號 + 探針實測 | **PASS**（無自動回歸鎖，見 §10） |
| R3 | 落盤 JSON 欄位漂移 | 中 | Phase 0 靜態凍結契約 + Phase 7 逐欄位等價比對（含路徑等價 `runs/<ts>/agent/<cfg>/`） | **PASS**（鍵序未直接鎖，見 §10） |
| R4 | `run_app` 內 agent 建好後 `ChatApp.create` / `uvicorn.Config` 失敗 → agent 洩漏 | 高 | `try: … except Exception: agent.close(); raise` 內部守衛 + 測試覆蓋 | **PASS**（成功路徑殘餘，見 §10） |
| R5 | serving 期 log 不進 `terminal.log` | 低 | **現況即如此，非退化**：`run_app` 於 `with save_logging_file` 內完成建構期 log，`server.run()` 在 with 之外 | **PASS** |
| R6 | D3-C 破壞既有 run_manager 測試 | 中 | 預期內，Phase 1 同步更新 | **PASS（已平息）** |
| R7 | `main.py` 失去 `--config-name` flag | 低 | 使用者已知悉並接受（D7）；語意等價於原 `MainCLI.config_name="default"` | **PASS（降級為已知限制）** |
| R8 | 原擬在 `run_app` 傳 `log_run_paths("ready")`（該函式僅認 `init`/`complete`，未定義分支 → 空表格） | 低 | **PM 裁決：不使用 `"ready"`、不新增 `"ready"` 分支**；`run_app` 只做與現行 `run_agent_build` 等價的 `init` + `complete` | **已解除** |
| R9 | Phase 1–6 為耦合切換鏈，中途整包測試紅燈 | 中 | 明確標示「整合綠燈檢查點 = Phase 7」；Phase 級改用靜態檢查 + 目標測試 | **PASS** |

### 9. CR 與 QA 紀錄

> **紀錄缺口（誠實標註）**：共享狀態中**沒有 Round 1 的審查紀錄**（最早的 CR 條目為 18:02 的 Review Round 2）。若 Round 1 曾以口頭／其他管道進行，其結論未落入共享狀態。

**CR Round 2 — 2026-09-10 18:02（Status: pass；0 CRITICAL）**

- **M1（MAJOR）**：`src/test/dev/test_run_agent.py` 的 `_FakeAgentStub.astream_result` 為**同步**函式，而 production `Agent.astream_result` 是 coroutine（`run_agent_query` 以 `asyncio.run` 包裝）→ `stream=True` happy path 未被測，且替身無法模擬真實的 awaited 契約。
- **M2（MAJOR）**：`run_agent_query` 的 Goal 4（寫 `run_config.toml` 與 `log_run_paths("init")→("complete")` 序列）未被測試鎖定（`run_app` 有、query 沒有）。

| ID | SUGGESTION | PM 裁決 | 結果 |
|---|---|---|---|
| S1 | `save_agent_results_as_json` 標註 `-> str \| None` 但實際總回傳路徑 | Implement | ✅ 收斂為 `-> str` |
| S2 | thread-history read-modify-write 非原子（既有並行風險） | **Do NOT** → tech-debt | 記錄（§10） |
| S3 | `_event_stream` 將 `str(exc)` 直接回傳 client（既有資訊揭露） | **Do NOT** → tech-debt | 記錄（§10） |
| S4 | `docs/code/runs/workflow.md` 對 `main.py` 的描述漂移（仍寫「四階段，結尾 Agent 建置」） | Implement | ✅ 改為三階段 + `run_app()` 阻塞 |
| S5 | `test_agent_server.py` 既有 pyright async-iter 問題 | Implement（讓 pyright 歸零） | ✅ 補 `AsyncIterator` 標註 |
| S6 | `main.py` 未知 argv 被靜默忽略 | **Do NOT**（使用者已核准）→ 已知限制 | 記錄（§10） |
| S7 | `configs/agent/test.toml` 的 `# run name` 註解已失效 | 若為單行註解修正則實作 | ✅ 單行移除 |

**SE 修正紀錄 — 18:06**：M1 將 `_FakeAgentStub.astream_result`（與 `_FailingStreamAgentStub.astream_result`）改為 `async def`、回傳前呼叫 `on_token`，並新增 `test_run_agent_query_stream_persists_streamed_result`（斷言落盤一次、`thread_id`／`agent_config` 正確、`results[0]["response"] == "streamed answer"`、`agent.close()` 被呼叫）；M2 新增 `test_run_agent_query_writes_run_config_and_log_lifecycle`（`save_run_config_as_toml` 恰好一次；`log_run_paths` 序列精確為 `["init", "complete"]`）；S1 / S4 / S5 / S7 依裁決實作。修正後閘門：`pyright src/` → **0 errors**；`ruff check src/` → All checks passed；`ruff format --check src/` → 48 files already formatted；`pytest src/test/dev/ -q` → **153 passed**（151 + 新增 2）。

**CR Round 3 — 18:10（Status: pass；0 CRITICAL、0 MAJOR）**：逐項複驗三重點全數 PASS —— (a) 替身已與 production coroutine 同構（kind / 參數順序 / 回傳型別），改回同步會使新測試失敗（具回歸防護）；(b) `log_run_paths` 恰呼叫兩次且順序為 `init` → `complete`（`create_run_no_site_context` 不呼叫它，故列表長度恰為 2，`assert_called_once_with` 成立）；(c) `-> str` 收斂安全（唯一出口 `return history_path`；呼叫端 `run_agent_query`、`_event_stream`、測試皆不分支 `None`）。Round-3 SUGGESTIONS（R3-S1 / R3-S2 / R3-S3）PM 裁決全部 **Do NOT implement**，記錄為 tech-debt。**Review Loop 退出**：0 CRITICAL、0 MAJOR，其餘為非阻斷性的風格／tech-debt。

**QA Test Run 1 — 18:40（Status: pass，自主範圍內）**

| 項目 | 結果 |
|---|---|
| `uv run pytest src/test/dev/ -q` | **153 passed, 1 warning**（唯一 warning 為第三方 `fastapi/testclient.py` 的 `StarletteDeprecationWarning`，與本次重構無關） |
| `uv run ruff check` | All checks passed（exit 0） |
| `uv run ruff format --check` | 49 files already formatted（exit 0） |
| `uv run pyright src/` | 0 errors, 0 warnings, 0 informations（exit 0） |

**基準說明（影響判定正確性）**：重構前基準取 **staged index**（`git show :<path>`），**非 `HEAD`**（`HEAD` 為更舊 commit，其 `Agent` 連 `close/__enter__/__exit__` 都沒有）。QA 曾以 `HEAD` 誤判 server 落盤路徑為 `chats/app`，經 staged 基準修正為 `runs/agent`（R3 路徑等價）。

**逐 Goal 判定**：Goal 1–9 全數 **PASS**；Goal 10 為 **PARTIAL**（僅因 2 個 production 測試檔與端到端流程受付費 API／授權限制未實跑）。
**確認缺陷**：**無 Critical / High / Medium 功能缺陷**；重構在自主範圍內行為與 staged 基準等價或更佳。
**觀察與改進（非缺陷）**：`run_agent_query` 新增 `finally: agent.close()`（基準版本無 try/finally，錯誤路徑會洩漏 `Tool`）；`main.py` 以「`run_app` 置於 try 之外」結構性消除基準版 `finally` 內可能未綁定 `agent` 的 `NameError`；舊 `cli.py` 曾把 `data_manager` 灌入 `**config_overrides` 造成每次執行出現 `Unknown keys found: ['data_manager']` warning，現行 `module_config_overrides` 僅含合法鍵（相對更舊 `HEAD` 的改進）。

### 10. Tech-Debt 與已接受的已知限制

| ID | 類別 | 說明 | 建議處置 |
|---|---|---|---|
| S2 | Tech-debt（並行，既有） | `run_manager.py` 的 thread-history 讀取─修改─寫回非原子；同一 `thread_id` 的並行請求可能遺失更新（現位於 per-request 路徑） | file lock 或 atomic write（temp file + `os.replace`） |
| S3 | Tech-debt（資訊揭露，既有） | `server/app.py` 的 `_event_stream` 於 error 事件將 `str(exc)` 直接回傳 client | 對 client 回傳通用訊息，細節僅寫 server log |
| S6 | **已接受之已知限制**（使用者核准） | `main.py` 的 `def main() -> None` 無 argv guard；未知 argv（如 `--config-name test`）被 Python 靜默忽略，程式以 `"default"` 執行 | 無（決策已定）；如需硬性擋錯需另行決定 |
| R3-S1 | Tech-debt（測試替身） | `_FakeRunManager.save_agent_results_as_json` 標註仍為 `-> str \| None` | 對齊為 `-> str` |
| R3-S2 | Tech-debt（測試風格） | `test_runmanager_agent_results.py` 六處 `assert written is not None` 在 `-> str` 後已成冗餘 | 移除 |
| R3-S3 | Tech-debt（註解，S7 範圍外） | `configs/rag/test.toml`、`configs/website_crawler/test.toml` 仍有失效的 `# run name` 註解 | 單行移除 |
| QA-2 | Tech-debt（測試覆蓋，Medium） | R2：`run_agent_query` 對 `**config_overrides` 的轉發無自動回歸鎖 | 新增斷言 `run_agent_build` / `AgentConfig.from_toml` 收到 override |
| QA-3 | Tech-debt（測試覆蓋，Low） | R3：落盤 `config` 鍵序未被測試直接鎖定（dict 等值不計序） | 補 `list(payload["config"].keys()) == [...]` |
| QA-1 | Tech-debt（低機率洩漏，Low） | R4：`run_app` 成功路徑若 `save_logging_file.__exit__` 拋例外，`chat_app` 已建但 agent 不會被關閉 | 將 `return` 移出 `with`，或於外層補 `except: agent.close(); raise` |

### 11. 待使用者授權事項與後續建議

以下項目因**付費 LLM / 端到端 / 網路 I/O** 或 **production test 政策**而未執行：

1. `uv run pytest src/test/test_main.py`（X2 形狀已靜態確認：AST 可解析、簽名一致、無 `run_agent_build` import）
2. `uv run pytest src/test/test_module.py`（同上；含 `run_agent_query` / `run_app` 呼叫與 `SERVER_PORT`）
3. `uv run python src/main.py`（完整啟動：爬蟲 → 圖像摘要 → RAG 建庫 → 阻塞 server）
4. `uv run python src/main.py --config-name test`（R7 已知限制的行為確認；**注意 plan 的「應報錯」期望已作廢**，預期為靜默以 `"default"` 執行）
5. 任何真實 agent / RAG query / smoke（付費 LLM API），含 `run_agent_query` / `run_app` 實跑與 Phase 0 金標準 `results_*.json` 逐欄位比對（R3 的真實驗證）

煙霧測試建議指令（需授權）：

```bash
uv run python src/cli.py agent-cli --run.query "…"        # 應產生 runs/<ts>/agent/<cfg>/results_*.json
uv run python src/cli.py server-cli --run.port 8123       # /api/chat 一輪 → 中斷 → terminal.log 應含 init / complete
uv run python src/main.py                                 # 完整流程後長駐服務，CTRL+C 可正常結束
```

後續建議：

1. 補上上述授權實跑，取得 Phase 9 與端到端流程的執行期證據。
2. 建立 R2 / R3 的自動回歸鎖（Medium），是目前最值得投入的測試強化。
3. 併入下一輪排程處理 S2（原子寫入）、S3（錯誤訊息最小化）兩項既有 tech-debt。

相關現行文件：[modules/agent.md](../../../code/phase2_3_mvp/modules/agent.md) · [modules/server.md](../../../code/phase2_3_mvp/modules/server.md) · [phase2_3_mvp.md](../../../code/phase2_3_mvp/phase2_3_mvp.md) · [runs/workflow.md](../../../code/runs/workflow.md) · [runs/cli.md](../../../code/runs/cli.md) · [runs/config.md](../../../code/runs/config.md)
