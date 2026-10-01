# 聊天伺服器（FastAPI + SSE）

## 模組總覽
此模組提供 **FastAPI + SSE 串流聊天 API**，將 Agent 的回覆逐 token 傳給前端（iframe / widget / Extension 共用同一後端）。採用 SSE 而非 WebSocket 的選型理由見 [survey/sse_vs_websocket.md](../survey/sse_vs_websocket.md)——LLM 問答是「一次問 → 一串答案」的單向突發流，SSE 以純 HTTP 達成，穿透力與實作成本皆最低。

進階功能包含：

- **SSE 事件協定** — `token`（逐字）/ `done`（response + thread_id）/ `error`（message）
- **多輪 session** — thread_id 由 server 產生（`auto-{uuid}`）並於 done 回傳，前端帶回續接
- **資源生命週期** — agent 與 run_manager 由呼叫端建立後注入 `ChatApp`（lifespan 僅綁定至 `app.state`，不重建）；`ChatApp.close()` 釋放 agent（run_manager 無需釋放），由持有它的 `ChatServer` 在 `serve()` 結束時（正常／中斷／例外）自動呼叫
- **CORS 限縮** — 預設全開放；`allowed_origins` 可限定自有網站來源（M5-3）
- **站點偵測**（M4）— `DOMAIN_SITE_MAP` + `resolve_site_id()` + `_enrich_query_with_site_context()`；`ChatRequest` 支援 `page_url` 欄位
- **嵌入表面 static** — `chat.html`（iframe）/ `widget.js`（script widget）/ `demo.html`（示範頁）

- **模組實作**
	- `src/website_copilot/server/app.py`（**FastAPI app**：`ChatApp`、`_build_fastapi_app`、`ChatRequest`、`_event_stream`、`_sse`）
	- `src/website_copilot/server/server.py`（`ChatServer`：持有 `ChatApp` 的 `uvicorn.Server` 子類，收到退出訊號時先印 log，`serve()` 結束時自動關閉 `ChatApp`）
	- `src/website_copilot/pipelines/serve.py`（`run_server_build` / `serve`：`website-copilot serve` 的執行邏輯）
	- `src/website_copilot/server/__init__.py`（匯出 `ChatApp` / `ChatRequest`）
	- `src/website_copilot/server/static/`（**嵌入表面前端檔**：chat.html / widget.js / demo.html，詳見 [interface.md](interface.md)）

- **模組設定**
	- `config_name`：AgentConfig 名稱（對應 `configs/agent/{name}.yml`，預設 `default`）
	- `allowed_origins`：CORS 允許來源列表（預設 None → `["*"]` 全開放）
	- `host` / `port`：監聽位址（預設 `127.0.0.1:8000`）

- **模組環境**
	- `Python >= 3.13`
	- **第三方套件**：`fastapi`（**Web 框架**）、`uvicorn`（**ASGI server**）、`pydantic`（**請求驗證**）、`httpx`（dev，TestClient 需要）

## app.py

### SSE 事件協定

```
POST /api/chat   {"query": "...", "thread_id": null}
→ text/event-stream, Cache-Control: no-cache

data: {"type": "token", "content": "逐"}        ← 每個 token 一個事件
data: {"type": "done", "response": "...", "thread_id": "auto-xxx"}  ← 完成（引用已寫入 response）
data: {"type": "error", "message": "..."}       ← 失敗
```

- **done 事件不含 `sources`**（M4a 後續變更）：agent 已將引用內容寫入 response（system prompt 要求）；sources 仍擷取並保留於落盤 result

### 核心函式

- **`ChatApp.create(agent, run_manager, allowed_origins=None)`** — 工廠方法：`_build_fastapi_app()` 建立 FastAPI app 並綁定 agent 與 run_manager：
  - **lifespan**：啟動時將注入的 `agent` 與 `run_manager` 綁定至 `app.state`（不在 lifespan 建立/關閉資源；資源由 `ChatServer` 結束時呼叫 `ChatApp.close()`，或由呼叫端以 context manager 管理）
  - **CORS middleware**：`allow_origins=allowed_origins`（None → `["*"]` 全開放）
  - **static mount**：`/static` → `src/website_copilot/server/static/`（M4a）
  - `GET /` → redirect `/static/demo.html`（嵌入示範入口）
  - `GET /api/health` → `{"status": "ok"}`（供健康檢查／就緒輪詢）
  - `POST /api/chat` → `StreamingResponse(_event_stream(...))`（SSE；空白 query 直接回 error 事件；`thread_id` 未提供時自動 `auto-{uuid}`）；`agent` 與 `run_manager` 由 `Depends(get_agent)` / `Depends(get_run_manager)` 自 `app.state` 取得

- **`_event_stream(agent, run_manager, query, thread_id, site_id=None)`** — SSE 事件流核心：
  1. `thread_config(thread_id)`（agent.langchain_helper）建立執行設定
  2. `astream_text` 逐 token → `yield _sse({"type": "token", "content": text})`
  3. 完成後 `graph.get_state()` 讀回 messages → `extract_sources_from_messages`（agent.langchain_helper）抽來源
  4. 組 `result` → `run_manager.save_agent_results_as_json(thread_id=..., results=[result], agent_config=agent.config)` 落盤 `results_{thread_id}.json`（讀取既有分檔 → 合併本輪 → 覆寫；檔名安全由 RunManager 負責，server 原樣傳遞 `thread_id`）
  5. `yield _sse({"type": "done", ...})`；任何例外 → `yield _sse({"type": "error", ...})`

- **`_sse(data)`** — 序列化為 SSE 格式（`data: {json}\n\n`，`ensure_ascii=False` 保留中文）
- **`resolve_site_id(page_url)`** — 從 `page_url` 解析 hostname，查 `DOMAIN_SITE_MAP` 得到 `site_id`；支援子網域匹配

- **`_enrich_query_with_site_context(query, site_id)`** — 將 `site_id` 前綴注入查詢字串，確保 Agent 在多站環境下檢索正確知識庫

- **`DOMAIN_SITE_MAP`** — hostname → site_id 對照表，定義哪些域名對應哪些知識庫
- **`run_server_build(...)`（pipelines/serve.py）** — 啟動入口（`serve()`，即 `website-copilot serve` 使用）：
  - `run_server_build(agent, run_config)`：接收由 `serve()` 經 `run_agent_build()` 建構的 agent；建立自己的 run context（`create_run_no_site_context(module="server", config_name=agent.config.config_name, base_folder="runs")`，路徑 `runs/<ts>/server/<config>/`）→ `ChatApp.create(agent, run_manager, run_config.allowed_origins)` → `uvicorn.Config(app, run_config.host, run_config.port)` → `ChatServer(config, chat_app)`（`uvicorn.Server` 子類），回傳 **`ChatServer`（非阻塞）**；由呼叫端執行 `server.run()`（或 `await server.serve()`），`ChatServer.serve()` 結束時於 `finally` 自動呼叫 `chat_app.close()`；ChatApp 可經 `server.chat_app` 取得
  - `run_config.yml` 與 `log_run_paths`（`init` → `complete`）由此函式寫出；server 目錄**不寫** `module_config.yml`（agent 設定只寫在 `run_agent_build` 的 `runs/<ts>/agent_build/<config>/`）
  - 建立 `ChatApp`／server 失敗時 re-raise，**不關閉**注入的 agent；由建立 agent 的 `serve()` 負責 `agent.close()`（不洩漏 RAG 資源）
  - **傳 app 物件而非 import string**：避免 reloader 子程序 sys.path 不含 `src/` 導致 ModuleNotFoundError

### 啟動方式

```bash
# 啟動 serve 階段（阻塞至中斷）
uv run website-copilot serve --run.port 8000

# 限縮 CORS 來源
uv run website-copilot serve --run.allowed-origins https://lab.example.edu.tw
```

## 已知問題
- [ ] SSE 併發（本機多人同時使用）— demo 階段可接受，正式版再上 Redis/queue
- [ ] 對話記憶依賴 `InMemorySaver`，不持久化（重啟即失；歷史對話留存於 `runs/` 的 `results_{thread_id}.json`）

## 未來規劃
- [ ] 正式部署（uvicorn workers / proxy 設定）
- [ ] 對話歷史查詢 API
