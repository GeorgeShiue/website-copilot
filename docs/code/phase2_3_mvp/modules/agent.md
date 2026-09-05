# AI Agent（LangGraph）

## 模組總覽
此模組以 **LangGraph `create_agent`** 將 RAG 檢索包裝為可對話的 **AI Agent**。Agent 的 LLM 推理迴圈自行決定是否呼叫 `webpage_retriever` 工具，並將檢索結果回答給使用者，回答內直接包含引用來源 URL（由 system prompt 要求）。

進階功能包含：

- **多輪對話記憶** — `InMemorySaver` + `thread_id`，相同 session 記得上下文（M2）
- **SSE 串流** — `astream_text` 共用核心，CLI 與 server 皆可逐 token 輸出
- **對話落盤** — `chats/<ts>/agent/<config>/`，每輪覆寫 `results.json` + 依 thread_id 分檔
- **資源生命週期** — `Agent.close()` 釋放 RAG 資源；server 於 lifespan 建一次、關閉釋放

- **模組實作**
	- `src/app/agent/agent.py`（**Agent 層核心**：`Agent` wrapper、`create_agent`、`ask` / `astream_text` / `astream_result` / `save_results`）
	- `src/app/tools/rag_registry.py`（**RAGRegistry**：多站 RAG 實例管理，lazy + LRU 快取）
	- `src/app/tools/site_discovery.py`（**Site Discovery 工具**：`create_site_discovery_tool`，回傳可用站點列表）
	- `src/app/tools/webpage_retriever.py`（**多站 Retriever Tool**：接受 `site_id` 參數路由至對應知識庫）
	- `src/utils/langchain_helper.py`（**LangChain 輔助**：`create_llm` / `thread_config` / `extract_sources_from_messages` / `_message_content_to_text`）
	- `src/app/configs/agent_config.py`（**設定載入**、**驗證**、**覆寫**：`from_toml` / `_validate_config` / `run_name`）
	- `src/app/workflow/workflow.py`（`run_agent`：CLI 的 agent-cli 分支執行邏輯）

- **模組設定**
	- `./configs/agent/{name}.toml`（**Agent 設定檔**：`llm_name` / `system_prompt`，預設 `default`）
	- `llm_name` 與 RAG 檢索 LLM（`RAGConfig.query_llm_name`）**解耦**，可獨立更換不影響檢索
	- API key 沿用 RAG query LLM 的環境變數：`GEMINI_RAG_QUERY_ENGINE_API_KEY`

- **模組環境**
	- `Python >= 3.13`（程式使用現代型別語法）
	- **第三方套件**：`langgraph`（**Agent 框架**，`create_agent`）、`langchain-google-genai`（**Gemini ChatModel**）、`langgraph-checkpoint`（**InMemorySaver**）、`langchain-core`（**StructuredTool**）、`python-dotenv`（**環境變數載入**）

## agent.py

### 資料結構與核心函式

- **`Agent`**（dataclass）— 包裝 LangGraph `CompiledStateGraph` 與綁定資源：
  - `graph`：create_agent 回傳的編譯圖
  - `tools`：綁定的 `StructuredTool` 列表（`list_knowledge_bases` + `webpage_retriever`）
  - `run_manager`：本次執行的 RunManager（供落盤 `chats/`）
  - `checkpointer`：`InMemorySaver` 實例（多輪記憶，thread_id 區分 session）
  - `registry`：`RAGRegistry` 實例（多站 RAG 管理，lazy + LRU 快取）
  - `close()`：釋放 RAG 資源（`registry.close()`，try/finally 保證）

- **`create_agent(config, run_manager)`** — 建立流程：
  1. 初始化 RunManager（`module="agent"`、`base_folder="chats"`）與落盤路徑
  2. 建立 `RAGRegistry`（多站 RAG 實例管理，lazy + LRU 快取，`max_cached` 限制同時載入數量）
  3. `create_site_discovery_tool(registry)` + `create_webpage_retriever_tool(registry)` 建立兩個工具
  4. `create_llm(config.llm_name)`（utils.langchain_helper）建立 Gemini ChatModel（`GEMINI_RAG_QUERY_ENGINE_API_KEY`）
  5. `create_agent(llm, [discovery_tool, retriever_tool], system_prompt, checkpointer)` 組裝並包裝為 `Agent`

- **`Agent.ask(query, thread_id)`** — 單輪/多輪問答（同步 `graph.invoke`），回傳 `{query, response, sources, timestamp}`

- **`Agent.astream_text(query, config)`** — 串流核心：以 `graph.astream(stream_mode="messages")` 逐 token 輸出，只取 `langgraph_node == "model"` 節點，Gemini 的 `list[dict]` content 統一轉純文字

- **`Agent.astream_result(query, thread_id, on_token)`** — 串流問答並收集完整結果（CLI 與 M3 server 共用）；完成後從 `graph.get_state()` 讀回 messages 擷取來源 URL

- **`Agent.save_results(results, thread_id)`** — 落盤 `results.json`（含 config 摘要）；提供 `thread_id` 時另寫 `results_<thread_id>.json` 分檔（跨 run 搜尋歷史檔由 `RunManager.find_thread_history_path()` 負責）。**注意**：CLI 模式的 `run_agent()` 不傳 `thread_id`，因此分檔僅在 server 模式（`_event_stream`）下生效。

### utils/langchain_helper.py（LangChain 輔助函式）

- **`thread_config(thread_id)`** — 建立 LangGraph 執行設定：
  - `thread_id=None` 時自動產生 `auto-{uuid}`（每次獨立，等同單輪）
  - 相同 `thread_id` 保留對話記憶（M2 多輪）

- **`extract_sources_from_messages(messages)`** — 以正則 `URL: (\S+)` 從 ToolMessage 解析來源 URL（依序去重）

- **`create_llm(llm_name)`** — 建立 LangChain ChatModel（Gemini，`GEMINI_RAG_QUERY_ENGINE_API_KEY`）；與 `utils.rag_helper.create_llm`（LlamaIndex 版）對稱

- **`_message_content_to_text(content)`** — 將 AIMessage content（`list[dict]`）轉為純文字

### 多輪記憶流程

```
使用者問題 + thread_id
  → create_agent（一次）→ graph.invoke / graph.astream（每輪）
  → LLM 決定呼叫 webpage_retriever → 檢索結果作為上下文
  → 回答（含引用 URL）→ 落盤 chats/（results.json + 分檔）
相同 thread_id → InMemorySaver 保留歷史 → 續接多輪
```

## 已知問題
- [ ] 多輪對話的 `results.json` 為每輪覆寫（歷史另存 `results_<thread_id>.json`，僅 server 模式生效；CLI 模式不建立分檔）
- [ ] Agent LLM 與 RAG 檢索 LLM 各自獨立設定，更換時需留意相容性

## 未來規劃
- [ ] **意圖識別與查詢轉換**（進階 prompt 工程）
- [ ] **答案評分與自我修正**（Agent 內建評估迴圈）
- [ ] 持久化記憶（SQLite / Redis checkpointer 取代 InMemorySaver）
