# AI Agent（LangGraph）

## 模組總覽
此模組以 **LangGraph `create_agent`** 將 RAG 檢索包裝為可對話的 **AI Agent**。Agent 的 LLM 推理迴圈自行決定是否呼叫 `webpage_retriever` 工具，並將檢索結果回答給使用者，回答內直接包含引用來源 URL（由 system prompt 要求）。

進階功能包含：

- **多輪對話記憶** — `InMemorySaver` + `thread_id`，相同 session 記得上下文（M2）
- **SSE 串流** — `astream_text` 共用核心，CLI 與 server 皆可逐 token 輸出
- **對話落盤** — `runs/<ts>/agent/<config>/results_{thread_id}.json`（讀取既有分檔 → 合併本輪 → 覆寫；`thread_id` 未提供時自動 `auto-{uuid}`）
- **資源生命週期** — `Agent.close()`（委派 `Tool.close()`）釋放 RAG 資源；agent 由 `run_agent_query()` / `run_app()` 在各自的 run context 內以 `create_agent()` 建立並持有：前者於 `finally` 關閉、後者由 `ChatApp.close()` 關閉
- **落盤責任在呼叫端** — `Agent` 不再持有 `RunManager`（agent 層不依賴 workflow 層）；落盤由 `run_agent_query()` 與 `_event_stream()` 呼叫 `RunManager.save_agent_results_as_json()`

- **模組實作**
	- `src/app/agent/agent.py`（**Agent 層核心**：`Agent` wrapper、`create_agent`、`ask` / `astream_text` / `astream_result`）
	- `src/app/tools/rag_registry.py`（**RAGRegistry**：多站 RAG 實例管理，lazy + LRU 快取）
	- `src/app/tools/site_discovery.py`（**Site Discovery 工具**：`create_site_discovery_tool`，回傳可用站點列表）
	- `src/app/tools/webpage_retriever.py`（**多站 Retriever Tool**：接受 `site_id` 參數路由至對應知識庫）
	- `src/utils/langchain_helper.py`（**LangChain 輔助**：`create_llm` / `thread_config` / `extract_sources_from_messages` / `_message_content_to_text`）
	- `src/app/configs/agent_config.py`（**設定載入**、**驗證**、**覆寫**：`from_toml` / `_validate_config` / `run_name`）
	- `src/app/workflow/workflow.py`（`run_agent_query`：CLI agent-cli 分支執行邏輯；`run_app`：server 分支；`run_agent_build`：agent 建構 + 落盤的程式化 API）

- **模組設定**
	- `./configs/agent/{name}.toml`（**Agent 設定檔**：`llm_name` / `system_prompt`，預設 `default`）
	- `llm_name` 與 RAG 檢索 LLM（`RAGConfig.query_llm_name`）**解耦**，可獨立更換不影響檢索
	- API key 依 model name 自動路由：含 `gemini` → `GEMINI_RAG_QUERY_ENGINE_API_KEY`；其他（`gpt*` 等，預設）→ `OPENAI_API_KEY`

- **模組環境**
	- `Python >= 3.13`（程式使用現代型別語法）
	- **第三方套件**：`langgraph`（**Agent 框架**，`create_agent`）、`langchain-google-genai`（**Gemini ChatModel**）、`langchain-openai`（**OpenAI ChatModel**）、`langgraph-checkpoint`（**InMemorySaver**）、`langchain-core`（**StructuredTool**）、`python-dotenv`（**環境變數載入**）

## agent.py

### 資料結構與核心函式

- **`Agent`**（一般 class）— 包裝 LangGraph `CompiledStateGraph` 與綁定資源：
  - `graph`：create_agent 回傳的編譯圖
  - `tool`：綁定的 `Tool` 實例；`tools` property 回傳 `tool.tools`（`list_knowledge_bases` + `webpage_retriever`）
  - `config`：本次使用的 `AgentConfig`（供呼叫端落盤時組 config 摘要）
  - `checkpointer`：`InMemorySaver` 實例（多輪記憶，thread_id 區分 session）
  - `close()`：委派 `Tool.close()` 釋放資源（try/finally 保證）
  - **不持有 `RunManager`**：agent 層與 workflow 層無依賴（落盤責任已上移至呼叫端）

- **`create_agent(config_name="default", **config_overrides)`** — 內部自行建立 `AgentConfig.from_toml(config_name, **config_overrides)` 與 `Tool(config_name)`，再組裝 LLM + 編譯圖並包裝為 `Agent`：
  1. `AgentConfig.from_toml()` 建立設定、`Tool(config_name)` 建立工具（含 `RAGRegistry` 工具）；無工具時拋 `ValueError`
  2. `create_llm(config.llm_name)`（utils.langchain_helper）建立 ChatModel（依 model name 自動路由 Gemini / OpenAI）
  3. 建立 `InMemorySaver` checkpointer
  4. 以 LangGraph `create_agent` 組裝 `tool.tools`、`system_prompt` 與 checkpointer，並包裝為 `Agent`；任一步驟失敗時 `tool.close()` 後 re-raise
- **`run_agent_build(config_name="default", run_config=None, **config_overrides) -> None`（workflow.py）** — agent 建構 + 落盤的程式化 API：建立 run context（`create_run_no_site_context(module="agent_build")`，路徑 `runs/<ts>/agent_build/<config>/`）並以 `with run_workflow_context(...)` 包住 logging 生命週期，內部呼叫 `create_agent(config_name, **config_overrides)`，寫出 `module_config.toml` 與（`run_config` 非 None 時）`run_config.toml`，最後 `agent.close()`。**`run_agent_query()` / `run_app()` 不經此函式**，而是在各自的 run context 內直接呼叫 `create_agent()`

- **`Agent.ask(query, thread_id)`** — 單輪/多輪問答（同步 `graph.invoke`），回傳 `{query, response, sources, timestamp}`

- **`Agent.astream_text(query, config)`** — 串流核心：以 `graph.astream(stream_mode="messages")` 逐 token 輸出，只取 `langgraph_node == "model"` 節點，Gemini 的 `list[dict]` content 統一轉純文字

- **`Agent.astream_result(query, thread_id, on_token)`** — 串流問答並收集完整結果（CLI 與 M3 server 共用）；完成後從 `graph.get_state()` 讀回 messages 擷取來源 URL

- **`RunManager.save_agent_results_as_json(thread_id, results, agent_config)`**（run_manager.py）— 落盤對話結果（含 config 摘要）：以 `agent_config` 組出 `{config_name, run_name, llm_name, system_prompt}` 摘要，寫入 `results_{thread_id}.json`（讀取既有分檔 → 合併本輪 → 覆寫）。摘要組裝由 RunManager 負責（`agent_config` 由呼叫端傳入），因此 `Agent` 不需持有 `RunManager`；`run_agent_query()` 與 server 的 `_event_stream()` 皆以此落盤。

### utils/langchain_helper.py（LangChain 輔助函式）

- **`thread_config(thread_id)`** — 建立 LangGraph 執行設定：
  - `thread_id=None` 時自動產生 `auto-{uuid}`（每次獨立，等同單輪）
  - 相同 `thread_id` 保留對話記憶（M2 多輪）

- **`extract_sources_from_messages(messages)`** — 以正則 `URL: (\S+)` 從 ToolMessage 解析來源 URL（依序去重）

- **`create_llm(llm_name)`** — 建立 LangChain ChatModel，依 model name 自動路由：含 `gemini` → `ChatGoogleGenerativeAI`（`GEMINI_RAG_QUERY_ENGINE_API_KEY`）；其他（`gpt*` 等）→ `ChatOpenAI`（`OPENAI_API_KEY`，`use_responses_api=True`、`api_key` 以 `SecretStr` 包裝）；與 `utils.rag_helper.create_llm`（LlamaIndex 版）對稱

- **`_message_content_to_text(content)`** — 將 AIMessage content（`list[dict]`）轉為純文字

### 多輪記憶流程

```
使用者問題 + thread_id
  → run_agent_query / run_app 建立 run context 與 create_agent（一次）→ graph.invoke / graph.astream（每輪）
  → LLM 決定呼叫 webpage_retriever → 檢索結果作為上下文
  → 回答（含引用 URL）→ 落盤 runs/（results_{thread_id}.json 讀取 → 合併 → 覆寫）
相同 thread_id → InMemorySaver 保留歷史 → 續接多輪
```

## 已知問題
- [ ] 對話記憶依賴 `InMemorySaver`，不持久化（重啟即失；歷史對話仍留存於 `runs/` 的 `results_{thread_id}.json`）
- [ ] Agent LLM 與 RAG 檢索 LLM 各自獨立設定，更換時需留意相容性

## 未來規劃
- [ ] **意圖識別與查詢轉換**（進階 prompt 工程）
- [ ] **答案評分與自我修正**（Agent 內建評估迴圈）
- [ ] 持久化記憶（SQLite / Redis checkpointer 取代 InMemorySaver）
