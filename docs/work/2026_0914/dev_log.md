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

---

## 二：API 重構 (9/8)

> 本段記錄模組 API 重構的完整執行結果。詳細規劃見 [2026_0908-api_refactor.md](./2026_0908-api_refactor.md)。

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
