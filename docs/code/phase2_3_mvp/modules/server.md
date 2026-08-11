# 聊天伺服器（FastAPI + SSE）

## 模組總覽
此模組提供 **FastAPI + SSE 串流聊天 API**，將 Agent 的回覆逐 token 傳給前端（iframe / widget / Extension 共用同一後端）。採用 SSE 而非 WebSocket 的選型理由見 [survey/sse_vs_websocket.md](../survey/sse_vs_websocket.md)——LLM 問答是「一次問 → 一串答案」的單向突發流，SSE 以純 HTTP 達成，穿透力與實作成本皆最低。

進階功能包含：

- **SSE 事件協定** — `token`（逐字）/ `done`（response + thread_id）/ `error`（message）
- **多輪 session** — thread_id 由 server 產生（`auto-{uuid}`）並於 done 回傳，前端帶回續接
- **資源生命週期** — agent 於 lifespan 啟動建一次、關閉釋放（`create_rag_agent` 每次重建向量庫隔離副本，不可 per-request）
- **CORS 限縮** — 預設全開放；`allowed_origins` 可限定自有網站來源（M5-3）
- **嵌入表面 static** — `chat.html`（iframe）/ `widget.js`（script widget）/ `demo.html`（示範頁）

- **模組實作**
	- `src/app/server/app.py`（**FastAPI app**：`create_app`、`run_server`、`ChatRequest`、`_event_stream`、`_sse`）
	- `src/app/server/__init__.py`（匯出 `create_app` / `run_server` / `ChatRequest`）
	- `src/app/server/static/`（**嵌入表面前端檔**：chat.html / widget.js / demo.html，詳見 [interface.md](interface.md)）
	- `scripts/server_up.py`（**啟動腳本**：一條指令啟動 + 等待就緒 + 保持運行；rich 輸出 / tyro 參數 / SIGTERM 乾淨關閉）

- **模組設定**
	- `config_name`：AgentConfig 名稱（對應 `configs/agent/{name}.toml`，預設 `default`）
	- `allowed_origins`：CORS 允許來源列表（預設 None → `["*"]` 全開放）
	- `host` / `port`：監聽位址（預設 `127.0.0.1:8000`）

- **模組環境**
	- `Python >= 3.10`
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

- **`create_app(config_name, agent, allowed_origins)`** — 建立 FastAPI app：
  - **lifespan**：`agent=None` 時以 `create_rag_agent(config=AgentConfig.from_toml(config_name), run_manager=RunManager("agent", base_folder="chats"))` 建立，關閉時 `agent.close()`
  - **CORS middleware**：`allow_origins=allowed_origins or ["*"]`
  - **static mount**：`/static` → `src/app/server/static/`（M4a）
  - `GET /` → redirect `/static/demo.html`（嵌入示範入口）
  - `GET /api/health` → `{"status": "ok"}`（供 `server_up.py` / smoke 腳本輪詢）
  - `POST /api/chat` → `StreamingResponse(_event_stream(...))`（SSE；空白 query 直接回 error 事件）

- **`_event_stream(agent, query, thread_id)`** — SSE 事件流核心：
  1. `thread_config(thread_id)` 建立執行設定
  2. `astream_text` 逐 token → `yield _sse({"type": "token", "content": text})`
  3. 完成後 `graph.get_state()` 讀回 messages → `extract_sources_from_messages` 抽來源
  4. 組 `result` → `save_conversation_results(agent, [result], thread_id=thread_id)` 落盤（含分檔）
  5. `yield _sse({"type": "done", ...})`；任何例外 → `yield _sse({"type": "error", ...})`

- **`_sse(data)`** — 序列化為 SSE 格式（`data: {json}\n\n`，`ensure_ascii=False` 保留中文）

- **`run_server(config_name, host, port, allowed_origins)`** — 啟動入口（`cli.py server-cli` 分派）：
  - `setup_logging` → `create_app` → `uvicorn.run(app, ...)`
  - **傳 app 物件而非 import string**：避免 reloader 子程序 sys.path 不含 `src/` 導致 ModuleNotFoundError

### 啟動方式

```bash
# 一條指令（scripts/server_up.py：rich 輸出、tyro 參數、Ctrl+C 乾淨關閉）
uv run python scripts/server_up.py --port 8000

# 直接 CLI（背景執行）
uv run python src/cli.py server-cli --run.port 8000

# 限縮 CORS 來源
uv run python src/cli.py server-cli --run.allowed-origins https://lab.example.edu.tw
```

## 已知問題
- [ ] SSE 併發（本機多人同時使用）— demo 階段可接受，正式版再上 Redis/queue
- [ ] `results.json` 多輪覆寫（歷史依 thread_id 分檔）

## 未來規劃
- [ ] 正式部署（uvicorn workers / proxy 設定）
- [ ] 對話歷史查詢 API
