# Survey
> [docs/code/phase2_3_mvp/survey/sse_vs_websocket.md](survey/sse_vs_websocket.md)

# 1. AI Agent（LangGraph）
> [docs/code/phase2_3_mvp/modules/agent.md](modules/agent.md)

## 實作進度
- [x] **Agent 框架**（LangGraph `create_agent`）
    - [x] **RAG 工具包裝**（`webpage_retriever` StructuredTool，零轉接）
    - [x] **自動檢索**（LLM 推理迴圈自行決定呼叫工具）
    - [x] **引用來源**（回答內含檢索來源 URL，由 system prompt 要求）
- [x] **多輪對話記憶**（`InMemorySaver` + `thread_id`）
- [x] **SSE 串流**（`astream_text` 共用核心，CLI 與 server 皆可用）
- [x] **對話落盤**（`chats/<ts>/agent/<config>/`，每輪覆寫 `results.json`；server 模式依 thread_id 分檔 `results_<thread_id>.json`）
- [x] **資源生命週期**（`Agent.close()` 釋放；server lifespan 建一次、關閉釋放）
- [x] **多站 RAG 路由**（M3：`RAGRegistry` + `webpage_retriever(site_id)` + `list_knowledge_bases`）
    - [x] `RAGRegistry` — lazy + LRU 快取管理多站 RAG 實例
    - [x] `webpage_retriever` — 接受 `site_id` 參數路由至對應知識庫
    - [x] `list_knowledge_bases` — 供 LLM 確認可用站點列表
    - [x] `Agent.close()` — 透過 `registry.close()` 釋放所有 RAG 資源

## 已知問題
- [ ] 多輪對話的 `results.json` 為每輪覆寫（歷史另存 `results_<thread_id>.json`，僅 server 模式生效；CLI 模式不建立分檔）
- [ ] Agent LLM 與 RAG 檢索 LLM 各自獨立設定（`AgentConfig.llm_name` / `RAGConfig.query_llm_name`），需留意更換時的相容性

## 未來規劃
- [ ] **意圖識別與查詢轉換**（進階 prompt 工程）
- [ ] **答案評分與自我修正**（Agent 內建評估迴圈）
- [ ] 持久化記憶（SQLite / Redis checkpointer 取代 InMemorySaver）

# 2. 聊天伺服器（FastAPI + SSE）
> [docs/code/phase2_3_mvp/modules/server.md](modules/server.md)

## 實作進度
- [x] **FastAPI + SSE**（`POST /api/chat`，事件協定 token / done / error）
    - [x] **逐 token 串流**（`StreamingResponse` + async generator）
    - [x] **多輪 session**（thread_id 由 server 產生並於 done 回傳）
    - [x] **錯誤處理**（error 事件；空白 query 拒絕）
- [x] **健康檢查**（`GET /api/health`）
- [x] **CORS**（預設全開放；`allowed_origins` 可限縮）
- [x] **啟動腳本**（`scripts/server_up.py`：一條指令啟動 + 等待就緒 + 保持運行；rich 輸出 / tyro 參數）
- [x] **站點偵測**（M4：`DOMAIN_SITE_MAP` + `resolve_site_id()` + `_enrich_query_with_site_context()`）
    - [x] `ChatRequest` 新增 `page_url` 欄位
    - [x] 從 `page_url` 解析 hostname → 查 `DOMAIN_SITE_MAP` → 得到 `site_id`
    - [x] 自動將 `site_id` 前綴注入查詢，確保 Agent 檢索正確知識庫

## 已知問題
- [ ] SSE 併發（本機多人同時使用）— demo 階段可接受，正式版再上 Redis/queue
- [ ] `results.json` 多輪覆寫（歷史依 thread_id 分檔）

## 未來規劃
- [ ] 正式部署（uvicorn workers / proxy 設定）
- [ ] 對話歷史查詢 API

# 3. 嵌入介面（iframe / widget / Extension）
> [docs/code/phase2_3_mvp/modules/interface.md](modules/interface.md)

## 實作進度
- [x] **iframe 嵌入**（`/static/chat.html`，同 origin 呼叫 API）
- [x] **script widget**（`/static/widget.js`）
    - [x] **shadow DOM 隔離樣式**（不污染嵌入網站）
    - [x] **mount factory**（`WebsiteCopilotWidget.mount({endpoint, streamChat})`，網頁/Extension 共用）
    - [x] **transport 抽象**（預設 fetch；Extension 傳 chrome.runtime 代理）
    - [x] **markdown 渲染**（粗體 / 列表 / 連結 / 程式碼；先 escape 防 XSS）
    - [x] **Typing Indicator**（等待後端回應時顯示三個跳動圓點）
- [x] **Chrome Extension**（`extension/`）
    - [x] **任何網站注入**（content script `<all_urls>`）
    - [x] **background 代理**（`chrome.runtime.Port` → fetch SSE，繞過 CSP/CORS）
    - [x] **站點偵測**（`content.js` 偵測 `window.location.hostname`，自動帶入 `page_url`）
    - [x] **Service Worker Keepalive**（`chrome.alarms` 定期喚醒，避免 Chrome ~30s 終止 SW）
    - [x] **跨頁面 session 共享**（`chrome.storage.session` 保存 `thread_id`，換頁面保留對話記憶）
    - [x] **自動化測試**（`scripts/m4b_extension_test.py`，xvfb + Playwright）

## 已知問題
- [ ] `extension/widget.js` 為 `static/widget.js` 的複本（Chrome 不載入 symlink），需手動同步
- [ ] Extension 的 widget 輸入框無 id/name（可及性 warning，已補 name 消除）

## 未來規劃
- [ ] **Extension 上架**（目前僅本機開發模式 load unpacked）
- [ ] **網站導航**（AI 直接控制網站介面跳轉、篩選）
- [ ] **專責代理**（多 Agent 分工）
