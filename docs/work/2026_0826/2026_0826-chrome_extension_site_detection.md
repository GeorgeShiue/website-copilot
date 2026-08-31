# Chrome Extension 站點偵測與 Agent 路由規劃 (2026/08/26)

> 本文檔為 `2026_0819-multi_site_RAG.md` 目標 4（M4：Extension 站點偵測與路由）的實作規劃。
> 核心改造範圍：Chrome Extension 偵測使用者瀏覽的網站、後端 domain → site_id 映射、query 語境注入、M3+M4 串接。

---

## 1. 變更範圍總覽

```
extension/content.js                   ← 修改：偵測 window.location.hostname，帶入 page_url
extension/background.js               ← 修改：轉發 page_url 至 Server
src/app/server/app.py                 ← 修改：ChatRequest + DOMAIN_SITE_MAP + resolve_site_id + enrich_query
```

> M3 的改動（`rag_registry.py`、`webpage_retriever.py`、`agent.py`）已完成，本目標僅處理 Extension 前端與 Server 層的串接。

---

## 2. 模組一：Extension content.js — 偵測當前 URL

### 2-1. 動機

Chrome Extension 的 `content.js` 在每個頁面注入時，天然處於該頁面的 context 中，能直接存取 `window.location`。這是偵測使用者正在瀏覽哪個網站的最簡單、最即時的方案。

**偵測方案比較：**

| 方案 | 實作位置 | 偵測時機 | 優點 | 缺點 |
|------|---------|---------|------|------|
| **A: content.js 取 window.location** | content script | 每次送 query 時 | 最簡單、最即時 | 需後端映射 |
| B: background.js 用 chrome.tabs | service worker | message 到達時 | 不需 content script 改動 | 需 tabs 權限 |
| C: 兩者結合 | content + background | 兩階段 | 最穩健 | 較複雜 |

**採用方案 A**：`content.js` 已在頁面內，直接取 `window.location.hostname` 即可。

### 2-2. 改動

在 `content.js` 的 IIFE 內、`proxyStreamChat` 定義前，一次性偵測：

```javascript
// content.js — 在 proxyStreamChat 外部，mount 時一次性偵測
const currentHostname = window.location.hostname;
```

在 `port.postMessage` 時帶入：

```javascript
// BEFORE
port.postMessage({ type: 'chat', query: payload.query, thread_id: payload.thread_id });

// AFTER
port.postMessage({
  type: 'chat',
  query: payload.query,
  thread_id: payload.thread_id,
  page_url: currentHostname,   // 新增：當前頁面 hostname
});
```

### 2-3. 設計決策

| 決策 | 選擇 | 理由 |
|------|------|------|
| 偵測時機 | mount 時一次性偵測 | hostname 在頁面生命週期內不變；不需要每次 query 重新偵測 |
| 傳遞值 | `hostname`（非完整 URL） | 後端映射只需 hostname；完整 URL 含 path/query 不必要且可能洩露隱私 |
| 前端映射 | **不做** | 前端只負責偵測並傳遞原始 hostname，映射邏輯全部在後端，改 mapping 不需重發 Extension |

---

## 3. 模組二：Extension background.js — 轉發 page_url

### 3-1. 改動

```javascript
// BEFORE
body: JSON.stringify({ query: msg.query, thread_id: msg.thread_id }),

// AFTER
body: JSON.stringify({
  query: msg.query,
  thread_id: msg.thread_id,
  page_url: msg.page_url,      // 新增：透傳至後端
}),
```

### 3-2. 協定變更摘要

| 欄位 | Before | After |
|------|--------|-------|
| `content → background` | `{ type, query, thread_id }` | `{ type, query, thread_id, page_url }` |
| `background → server` | `{ query, thread_id }` | `{ query, thread_id, page_url }` |

**`widget.js` 不需要改動**——`page_url` 由 `content.js` 在 `proxyStreamChat` 外部處理，widget 不感知。

---

## 4. 模組三：Server app.py — 後端映射與 query 語境注入

### 4-1. ChatRequest 擴充

```python
class ChatRequest(BaseModel):
    """POST /api/chat 請求體。"""
    query: str
    thread_id: str | None = None
    page_url: str | None = None    # 新增：Chrome Extension 帶入的 hostname
```

### 4-2. Domain → site_id 後端映射

在 `app.py` 模組層級新增映射表與解析函數：

```python
DOMAIN_SITE_MAP: dict[str, str] = {
    "nculab.csie.ncu.edu.tw": "nculab",
    "csie.ncu.edu.tw": "ncucsie",
    # 新增站點時只需在此加入一行
}


def resolve_site_id(page_url: str | None) -> str | None:
    """從 hostname 解析 site_id。

    支援精確匹配與子域名 suffix 匹配：
    - "nculab.csie.ncu.edu.tw" → "nculab"（精確匹配）
    - "lab.nculab.csie.ncu.edu.tw" → "nculab"（suffix 匹配）

    Returns:
        對應的 site_id，無匹配時回傳 None。
    """
    if not page_url:
        return None
    hostname = page_url.strip().lower()
    if hostname in DOMAIN_SITE_MAP:
        return DOMAIN_SITE_MAP[hostname]
    for domain, site_id in DOMAIN_SITE_MAP.items():
        if hostname.endswith("." + domain):
            return site_id
    return None
```

**映射表為何放在 `app.py` 而非 config 檔：**
- 目前站點少（2 個），config 化增加複雜度但無實際收益
- 未來站點增多時可改為從 `configs/site_mapping.toml` 載入
- suffix matching 支援子域名（如 `lab.nculab.csie.ncu.edu.tw` → `nculab`）

### 4-3. query 前綴 site 語境

**核心問題**：LangGraph `create_agent` 的 `system_prompt` 在 agent 建立時固定，無法 per-request 注入 site_id。

**解法**：在 server 層將 site_id 前綴至 user query，讓 LLM 從 message 內容感知當前站點。

```python
def _enrich_query_with_site_context(query: str, site_id: str | None) -> str:
    """將 site_id 前綴至 query，供 LLM 感知當前站點。

    LLM 看到 "[使用者瀏覽 nculab 網站]" 前綴後，
    會自動在 webpage_retriever 工具呼叫中使用 site_id="nculab"。
    """
    if not site_id:
        return query
    return f"[使用者瀏覽 {site_id} 網站] {query}"
```

**效果範例：**

```
# Chrome Extension 在 nculab.csie.ncu.edu.tw 問「實驗室成員」
# LLM 收到的 human message：
"[使用者瀏覽 nculab 網站] 實驗室的成員有哪些？"
# LLM 自動理解 → 呼叫 webpage_retriever(site_id="nculab", query="實驗室的成員有哪些？")
```

### 4-4. endpoint 整合

```python
@app.post("/api/chat")
async def chat(
    req: ChatRequest,
    agent: RAGAgent = Depends(get_agent),
) -> StreamingResponse:
    if not req.query.strip():
        return StreamingResponse(...)
    thread_id = req.query_thread_id or f"auto-{uuid.uuid4().hex[:8]}"
    site_id = resolve_site_id(req.page_url)    # 新增
    return StreamingResponse(
        _event_stream(agent, req.query, thread_id, site_id=site_id),  # 新增 site_id
        ...
    )


async def _event_stream(
    agent: RAGAgent,
    query: str,
    thread_id: str,
    site_id: str | None = None,    # 新增
) -> AsyncIterator[str]:
    enriched_query = _enrich_query_with_site_context(query, site_id)
    # 後續用 enriched_query 替代原始 query
    ...
```

---

## 5. 三種介面的 site_id 來源

本目標完成後，三種 Agent 介面共用同一個後端 `site_id` 路由機制，差別只在 site_id 的來源：

| 介面 | site_id 來源 | 實作 |
|------|-------------|------|
| **Chrome Extension** | `window.location.hostname` → `DOMAIN_SITE_MAP` 映射 | content.js + background.js + app.py |
| **CLI** | `--site-id` 手動指定 或 query 帶 site_id 前綴 | 無需改動（已有） |
| **Server API** | 請求參數 `page_url`（可選） | ChatRequest model + mapping |

```
使用者在 nculab.csie.ncu.edu.tw 開啟頁面
  ↓
Extension: window.location.hostname → "nculab.csie.ncu.edu.tw"
  ↓
Server: resolve_site_id("nculab.csie.ncu.edu.tw") → "nculab"
  ↓
_enrich_query_with_site_context(query, "nculab")
  → "[使用者瀏覽 nculab 網站] 實驗室的成員有哪些？"
  ↓
Agent LLM: 看到 site 語境 → webpage_retriever(site_id="nculab", query="...")
  ↓
RAGRegistry.get("nculab") → 正確檢索 nculab 知識庫
```

---

## 6. 與 M3 的串接

本目標依賴 M3 的以下組件：

| M3 組件 | M4 如何使用 |
|---------|-----------|
| `RAGRegistry` | `registry.get(site_id)` 由 M3 建立，M4 透過 query 前綴觸發 |
| `webpage_retriever(site_id=...)` | M4 的 query 前綴讓 LLM 自動填入 site_id |
| `list_knowledge_bases` | 當 `resolve_site_id` 回傳 None 時，LLM 可用此工具確認站點 |
| `RAGAgent` | M4 不改動 RAGAgent，僅在 Server 層 `_event_stream` 加入 site_id 參數 |

**M3 + M4 串接流程：**

```
M4 (Server)                          M3 (Agent + RAG)
───────────                          ────────────────
resolve_site_id(page_url) → site_id
enriched_query = prefix + query
agent.graph.invoke({ messages: [("human", enriched_query)] })
        │
        └──→ LLM 看到 "[使用者瀏覽 nculab 網站]"
              → webpage_retriever(site_id="nculab", query="...")
              → RAGRegistry.get("nculab")
              → rag.retrieve(...)
              → 正確結果
```

---

## 7. 測試策略

| 測試類型 | 對象 | 驗證內容 |
|---------|------|---------|
| **單元測試** | `resolve_site_id()` | 精確匹配 / suffix 匹配 / 無匹配回傳 None / None 輸入 / 空字串 |
| **單元測試** | `_enrich_query_with_site_context()` | 有 site_id 時前綴正確 / None 時原樣回傳 |
| **Unit: Extension** | content.js mock | `window.location.hostname` 正確帶入 `page_url` |
| **Integration** | Server `/api/chat` | 傳入 `page_url` → response 正確路由 |
| **E2E: Extension** | Chrome 開啟 nculab → 問答 | 自動偵測 nculab → 正確檢索 nculab 知識庫 |
| **E2E: 換站** | 切換至 csie 頁面 → 問答 | 自動切換至 ncucsie → 正確檢索 |
| **E2E: 無映射** | localhost / 內網 IP → 問答 | `resolve_site_id` 回傳 None → LLM 自行用 `list_knowledge_bases` |

---

## 8. 實作順序

```
Step 1: Extension content.js
        → 偵測 window.location.hostname + 帶入 page_url

Step 2: Extension background.js
        → 轉發 page_url 至 Server

Step 3: Server app.py
        → ChatRequest.page_url + DOMAIN_SITE_MAP + resolve_site_id
        → _enrich_query_with_site_context
        → _event_stream / chat endpoint 整合

Step 4: 測試
        → resolve_site_id 單元測試
        → _enrich_query 單元測試
        → Server integration 測試

Step 5: 端到端驗證
        → Chrome Extension → Server → Agent → RAG 完整流程
```

---

## 9. 風險與緩解

| # | 風險 | 影響 | 緩解 |
|---|------|------|------|
| 1 | Extension hostname 無法映射 | 內網 IP / localhost / 未知站 | `resolve_site_id` 回傳 None → LLM 自行用 `list_knowledge_bases` |
| 2 | LLM 不跟隨前綴指引 | 選錯 site_id 或忽略語境 | system prompt 強化指引（M3 已完成）；tool description 說明「通常已有隱含 site_id」 |
| 3 | query 前綴 token 佔用 | `"[使用者瀏覽 nculab 網站]"` 佔 ~15 tokens | 可忽略；LLM context window 128K+ |
| 4 | 映射表維護 | 新站點需手動加 `DOMAIN_SITE_MAP` | 目前 2 站可接受；未來可改為自動掃描 `data/rag/` |
| 5 | widget.js 相容性 | widget 不感知 page_url | widget.js 不需改動——page_url 由 content.js 在外部處理 |
| 6 | Extension CSP 限制 | 部分網站 CSP 可能阻擋 content script | Extension 已使用 Manifest V3 + background proxy 繞過 CSP |

---

## 10. 檔案變更總覽

| 檔案 | 操作 | 說明 |
|------|------|------|
| `extension/content.js` | 修改 | 偵測 `window.location.hostname` + 帶入 `page_url` |
| `extension/background.js` | 修改 | 轉發 `page_url` 至 Server |
| `src/app/server/app.py` | 修改 | `ChatRequest` + `DOMAIN_SITE_MAP` + `resolve_site_id` + `_enrich_query_with_site_context` + endpoint 整合 |

**不受影響的檔案：**
- `extension/widget.js` — 不感知 page_url
- `src/app/tools/rag_registry.py` — M3 已完成，不變
- `src/app/tools/webpage_retriever.py` — M3 已完成，不變
- `src/app/agent/agent.py` — M3 已完成，不變
- `src/app/configs/agent_config.py` — M3 已完成，不變
