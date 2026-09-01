## SSE 完整深入解說

### 一、SSE 協定的原始規範（HTTP 層）

SSE 定義在 [HTML Living Standard § Server-sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html)，本質上只是一個**嚴格格式化的 HTTP response body**：

```
HTTP/1.1 200 OK
Content-Type: text/event-stream    ← 必須是這個 MIME type
Cache-Control: no-cache            ← 禁止快取（每次都要最新）
Connection: keep-alive             ← 保持連線不關

data: 第一行\n\n                   ← 一個完整事件（data 行 + 空行結尾）
data: 第二行\n\n                   ← 下一個事件
```

#### 事件格式的完整語法

每個事件由**多個欄位**組成，用 `\n` 分隔，**以空行 `\n\n` 結尾**表示一個事件完整：

```
event: token              ← 事件類型（可選，預設 "message"）
id: 42                    ← 事件 ID（可選，用於斷線重連）
retry: 3000               ← 重連間隔 ms（可選，僅 EventSource 用）
data: {"type":"token"}    ← 資料（必填，可多行）
                           ← 空行 = 事件結束
```

**你專案的簡化**：只用 `data:` 欄位，把所有資訊塞進 JSON——這是最常見的實踐，因為 `event:` 和 `id:` 在 `fetch + ReadableStream` 模式下沒有額外價值。

---

### 二、後端實作逐行拆解

#### 2.1 `_sse()` — 序列化函式

```python
def _sse(data: dict[str, Any]) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
```

做三件事：
1. `json.dumps(data, ensure_ascii=False)` — 把 dict 轉成 JSON，保留中文原文
2. 前綴 `data: ` — SSE 規範要求
3. 結尾 `\n\n` — **這是事件的分隔符**，前端靠它判斷「一個事件結束了」

#### 2.2 `_event_stream()` — 逐 token 串流的核心

```python
async def _event_stream(agent, query, thread_id, site_id=None):
    chunks: list[str] = []                                    # ① 累積所有 token
    config = thread_config(thread_id)

    async for text in astream_text(agent, enriched_query, config):  # ② 逐 token 迭代
        chunks.append(text)
        yield _sse({"type": "token", "content": text})       # ③ 每個 token 立即 yield

    # ④ 全部 token 串完後，送 done 事件（含完整回答）
    yield _sse({"type": "done", "response": "".join(chunks), "thread_id": thread_id})
```

**關鍵概念：`yield` 是什麼？**

`_event_stream` 是一個 **async generator**。`yield` 不是一次把所有資料吐完，而是**每次遇到 yield 就暫停，把一個事件送出去，等前端讀走後再繼續**。這就是 SSE 「邊算邊送」的機制：

```
時間軸：
  t=0   yield token "你"     → 前端收到
  t=0.1 yield token "好"     → 前端收到
  t=0.2 yield token "！"    → 前端收到
  t=0.5 yield done           → 前端收到，串流結束
```

#### 2.3 FastAPI 端如何掛上 response

```python
@app.post("/api/chat")
async def chat(req: ChatRequest, agent=Depends(get_agent)):
    thread_id = req.thread_id or f"auto-{uuid.uuid4().hex[:12]}"
    # StreamingResponse 把 async generator 包裝成 HTTP response body
    return StreamingResponse(
        _event_stream(agent, req.query, thread_id, site_id),
        media_type="text/event-stream",        # SSE 必要的 MIME type
        headers={
            "Cache-Control": "no-cache",       # 禁止 proxy/CDN 快取
            "X-Accel-Buffering": "no",         # 告訴 Nginx 不要 buffer
        },
    )
```

`StreamingResponse` 的作用：**不等 generator 跑完，立刻開始把 yield 出來的字串寫入 HTTP response body**。HTTP 連線保持開啟，直到 generator 跑完或客戶端斷線。

---

### 三、前端解析逐行拆解

#### 3.1 發起請求

```javascript
var resp = await fetch(endpoint + '/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, thread_id }),
});
var reader = resp.body.getReader();   // ReadableStream 的 reader
var decoder = new TextDecoder();       // binary → string
```

**為什麼不用 `EventSource`？**
`EventSource` 只支援 GET 請求，不能帶 POST body。你的 API 需要送 `query` + `thread_id`，所以必須用 `fetch` + `ReadableStream`。

#### 3.2 逐 chunk 讀取

```javascript
while (true) {
    var r = await reader.read();       // 阻塞等待下一個 chunk
    if (r.done) break;                // 伺服器關閉連線

    buffer += decoder.decode(r.value, { stream: true });
    var events = parseSseEvents(buffer);    // 切分出完整事件
    buffer = buffer.slice(buffer.lastIndexOf('\n\n') + 2);  // 保留未解析殘留
}
```

**這裡有一個核心問題：chunk 邊界不保證對齊事件邊界。**

一次 `reader.read()` 拿到的 `r.value` 可能是：
- 一個完整事件 ✅
- 半個事件 ❌（`data: {"type":"token","cont` — 被 TCP 切斷）
- 多個事件合在一起 ✅
- 一個事件 + 下一個事件的開頭 ✅

所以必須用 `buffer` 累積，按 `\n\n` 切分：

```javascript
function parseSseEvents(chunk) {
    var events = [];
    chunk.split('\n\n').forEach(function (block) {
        var dataLines = block.split('\n')
            .filter(line => line.indexOf('data:') === 0)
            .map(line => line.slice(5));        // 去掉 "data: " 前綴
        if (dataLines.length > 0) {
            try { events.push(JSON.parse(dataLines.join(''))); }
            catch (e) { /* 不完整的 JSON → 忽略，等下一次 chunk */ }
        }
    });
    return events;
}
```

#### 3.3 事件消費邏輯

```javascript
events.forEach(function (ev) {
    if (ev.type === 'token') {
        // 逐字追加到 DOM（plain text，不做 markdown 渲染）
        respEl.appendChild(document.createTextNode(ev.content));
    } else if (ev.type === 'done') {
        // 一次性用完整 response 重新渲染 markdown
        respEl.innerHTML = renderMarkdown(ev.response);
        threadId = ev.thread_id;   // 保存 thread_id 供下一輪使用
    } else if (ev.type === 'error') {
        respEl.className = 'wc-msg wc-error';
        respEl.textContent = '錯誤：' + ev.message;
    }
});
```

**為什麼 `token` 階段不做 markdown 渲染？** 因為 `**bold` 可能跨多個 token（第一個 token 傳 `**`，第二個傳 `bol`，第三個傳 `d**`），中途渲染會出現殘缺的 HTML。所以先 plain text 追加，`done` 時才用完整文字做一次 markdown → HTML 轉換。

---

### 四、Extension 模式的 SSE 變體

Content script 不能直接 fetch（受 CSP 限制），所以改用 `Port` + `ReadableStream` 模擬：

```
content.js                          background.js
    │                                     │
    ├── port.postMessage({type:'chat'}) ──►│
    │                                     │── fetch('/api/chat')
    │                                     │── reader.read() ← 逐 chunk
    │◄── port.postMessage({type:'chunk'})─┤
    │                                     │── ...
    │◄── port.postMessage({type:'done'})──┤
```

`content.js` 把 Port 訊息流包裝成一個 **fake ReadableStream**，讓 `widget.js` 的 `sendQuery` 函式**完全不知道 transport 差異**：

```javascript
const stream = new ReadableStream({
    start(controller) {
        let buffer = '';
        const pump = () => {
            const idx = buffer.lastIndexOf('\n\n');
            if (idx !== -1) {
                // ⚠️ 保留 \n\n 結尾，確保 widget 端 parseSseEvents 能正確切分
                const chunk = buffer.slice(0, idx + 2);
                buffer = buffer.slice(idx + 2);
                controller.enqueue(new TextEncoder().encode(chunk));
            }
        };
        port.onMessage.addListener((msg) => {
            if (msg.type === 'chunk') { buffer += msg.data; pump(); }
            else if (msg.type === 'done') { pump(); controller.close(); }
            else if (msg.type === 'error') { controller.error(new Error(msg.message)); }
        });
    },
    cancel() { port.disconnect(); },
});
resolve({ ok: true, status: 200, body: stream });
```

---

### 五、SSE 的隱藏陷阱與最佳實踐

#### 5.1 心跳（Keep-Alive）

HTTP 長連線會被 proxy/負載平衡器在空閒時中斷（通常 30~60 秒）。如果你的 LLM 回應慢（如 RAG 檢索 + 長 prompt），連線可能在第一個 token 送出前就被斷掉。

**解法**：定期送空的 heartbeat 事件：

```python
# 後端定期送 ": heartbeat\n\n"（以冒號開頭的行是 SSE 註解，前端會忽略）
async def _event_stream(...):
    async for text in astream_text(...):
        yield _sse({"type": "token", "content": text})
    yield _sse({"type": "done", ...})
```

你的專案目前**沒有送 heartbeat**，如果未來 LLM 延遲增加，需要在 `_event_stream` 中加一個 timeout wrapper 定期送 `: keepalive\n\n`。

#### 5.2 資料完整性：不完整的 JSON

`parseSseEvents` 中的 `try/catch` 忽略 JSON parse 錯誤是正確的——因為 chunk 邊界可能切在 JSON 中間：

```
收到的 chunk:  data: {"type":"token","cont
下一個 chunk:  ent":"你好"}\n\n
```

第一個 chunk 的 `data:` 行是不完整的 JSON，`JSON.parse` 會 throw，被 catch 忽略。第二個 chunk 到來後，buffer 合併，`\n\n` 分隔後能正確 parse。

#### 5.3 `stream: true` 的 `TextDecoder`

```javascript
decoder.decode(r.value, { stream: true })
```

`{ stream: true }` 告訴 decoder「這不是最後一個 chunk，如果 UTF-8 多位元字元被切斷，先暫存」。中文是多位元字元（UTF-8 每字 3 bytes），如果 chunk 邊界切在一個中文字的中間，不加 `stream: true` 會產生乱码。

#### 5.4 `Cache-Control: no-cache` + `X-Accel-Buffering: no`

這兩個 header 是為了**穿透中間代理**：

| Header | 目標 | 原因 |
|---|---|---|
| `Cache-Control: no-cache` | 瀏覽器、CDN | 禁止快取 SSE 流 |
| `X-Accel-Buffering: no` | Nginx 反向代理 | Nginx 預設會 buffer 後端輸出，SSE 就失去了「即時」效果 |

#### 5.5 連線數限制

HTTP/1.1 下，瀏覽器對**同一域名最多 6 條併發連線**。你的 widget 每次問答佔一條。如果用戶在多個 iframe 同時問答，可能觸及上限。HTTP/2 的多工（multiplexing）不受此限制。

---

### 六、完整生命週期圖

```
用戶按下送出
    │
    ▼
widget.js: streamChat({ query, thread_id })
    │
    ├─ 網頁版：fetch POST /api/chat
    │   └─ resp.body.getReader() → 逐 chunk 讀取
    │
    └─ Extension 版：Port.postMessage → background.js
        └─ fetch POST /api/chat → reader.read()
        └─ port.postMessage({type:'chunk'}) → content.js
            └─ ReadableStream.enqueue → widget.js reader
    │
    ▼
widget.js: parseSseEvents(buffer)  ← 按 \n\n 切分
    │
    ├─ type=token  → appendChild(textNode)     ← plain text 追加
    ├─ type=done   → innerHTML=renderMarkdown() ← markdown → HTML
    └─ type=error  → 顯示錯誤訊息
    │
    ▼
連線關閉，reader.read() 返回 done=true
```