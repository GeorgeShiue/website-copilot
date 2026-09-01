## SSE 前端完整深入解說

> 本文是 `sse.md` 的姊妹篇。`sse.md` 專注於 SSE 協定規範與後端實作；本文則深入前端如何**消費** SSE 串流，涵蓋 Fetch API、ReadableStream、Shadow DOM、Chrome Extension 架構、Service Worker 生命週期等核心概念。所有程式碼範例均來自本專案的 `extension/` 目錄。

---

### 一、Fetch API 與 ReadableStream

#### 1.1 傳統 fetch vs 串流 fetch

大多數人對 `fetch` 的認知停留在「等整個 response 完整回來」：

```javascript
// 傳統用法：等到完整 JSON 回來才執行 .then()
const resp = await fetch('/api/chat', { method: 'POST', body: ... });
const data = await resp.json();  // ← 阻塞，直到整個 response body 下載完畢
console.log(data.response);       // 此時才拿到完整回答
```

SSE 場景下，LLM 逐 token 產生回答，可能持續 10~60 秒。若等到完整回答才開始渲染，使用者會看到長時間空白——失去了串流的意義。

#### 1.2 `resp.body`：原始串流入口

`fetch()` 回傳的 `Response` 物件有一個 `.body` 屬性，它的型別是 `ReadableStream`：

```javascript
const resp = await fetch(endpoint + '/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, thread_id }),
});
// resp.body 就是 ReadableStream<Uint8Array>
// 它不是 Promise，不是陣列——它是一個「可讀取的位元組流」
```

`ReadableStream` 本質上是一個**拉式（pull-based）**的資料管道。你必須主動去「拉」資料，它不會推給你。

#### 1.3 `getReader()` 與 `reader.read()`

要從 `ReadableStream` 讀取資料，必須先取得一個 reader：

```javascript
var reader = resp.body.getReader();  // 取得 ReadableStreamDefaultReader
var decoder = new TextDecoder();     // 後面會詳解：把 Uint8Array 轉成字串

while (true) {
    var r = await reader.read();     // 阻塞，直到有新資料可讀
    if (r.done) break;               // true = 伺服器已關閉連線，串流結束

    // r.value 是 Uint8Array（原始位元組）
    var text = decoder.decode(r.value, { stream: true });
    // ... 處理 text
}
```

`reader.read()` 回傳一個 Promise，resolve 為 `{ value: Uint8Array, done: boolean }`：

| 欄位 | 型別 | 意義 |
|------|------|------|
| `value` | `Uint8Array` | 本次 chunk 的原始位元組資料 |
| `done` | `boolean` | `false` = 伺服器還有資料；`true` = 串流結束 |

**這就是串流消費的核心模式：`while(true)` + `await reader.read()`。** 每次迴圈只拿一個 chunk，處理完立刻去拿下一個，不必等待整個回應完成。

#### 1.4 為什麼不用 EventSource？

[EventSource](https://developer.mozilla.org/en-US/docs/Web/API/EventSource) 是瀏覽器內建的 SSE 客戶端，但有致命限制：

| 特性 | EventSource | fetch + ReadableStream |
|------|-------------|----------------------|
| HTTP 方法 | 只支援 GET | GET / POST / PUT ... |
| 帶 body | ❌ 不可能 | ✅ `body: JSON.stringify(...)` |
| 自訂 header | ❌ 受限 | ✅ 任意 header |
| 二進位控制 | ❌ | ✅ 完全掌控 |

本專案的 API 需要 POST `query` + `thread_id`，所以**必須**用 `fetch + ReadableStream`。

---

### 二、TextDecoder 與 TextEncoder

#### 2.1 為什麼需要轉換？

HTTP response body 在網路傳輸時是**二進位位元組**（`Uint8Array`），不是字串。`fetch` 的 `.body` 回傳的是原始位元組流，人類可讀的文字必須經過編碼轉換。

```
伺服器送出的 JSON（UTF-8 編碼）：
  byte[]: [123, 34, 116, 121, 112, 101, ...]
                    ↓ TextDecoder
              '{"type":"token",...'
```

#### 2.2 TextDecoder：位元組 → 字串

```javascript
var decoder = new TextDecoder();          // 預設 UTF-8
var r = await reader.read();              // r.value 是 Uint8Array
var text = decoder.decode(r.value);       // 轉成 JavaScript 字串
```

**`{ stream: true }` 的關鍵意義：**

```javascript
buffer += decoder.decode(r.value, { stream: true });
```

`{ stream: true }` 告訴 decoder：「這不是最後一個 chunk。如果 UTF-8 多位元組字元被 chunk 邊界切斷，請暫存未完成的位元組，等下一次 `decode()` 時再合併。」

為什麼這很重要？中文是多位元組字元：

```
UTF-8 編碼：
  "你" → 3 bytes: [0xE4, 0xBD, 0xA0]
  "好" → 3 bytes: [0xE5, 0xA5, 0xBD]

如果 TCP chunk 邊界切在 "你" 的中間：
  chunk 1: [..., 0xE4, 0xBD]     ← 只收到 2/3 bytes
  chunk 2: [0xA0, 0xE5, ...]     ← 剩下的 1 byte + 下一個字

不加 stream: true：
  chunk 1 decode → "�"            ← 亂碼！decoder 認為位元組序列不完整

加了 stream: true：
  chunk 1 decode → ""             ← decoder 暫存 2 bytes，回傳空字串
  chunk 2 decode → "你好"          ← 合併後正確解碼
```

**本專案的使用場景**：後端回傳的 SSE data 中包含中文（如 `{"content":"你"}`），chunk 邊界完全可能切在中文字的中間位元組。不加 `stream: true` 就會產生亂碼。

#### 2.3 TextEncoder：字串 → 位元組

`TextEncoder` 是 `TextDecoder` 的逆操作，將 JavaScript 字串轉為 `Uint8Array`：

```javascript
// content.js 中使用 TextEncoder 的場景
const chunk = buffer.slice(0, idx + 2);
controller.enqueue(new TextEncoder().encode(chunk));
```

這裡的用途：`content.js` 建立了一個**假的 ReadableStream**（fake stream），把 background.js 傳來的文字資料重新包裝成 `Uint8Array` 送給 widget.js 的 reader。因為 `ReadableStream` 的 `enqueue()` 只接受 `Uint8Array`，不接受字串。

#### 2.4 編碼對照表

| 工具 | 方向 | 輸入 | 輸出 | 使用場景 |
|------|------|------|------|----------|
| `TextDecoder` | 位元組 → 字串 | `Uint8Array` | `string` | 解析 SSE chunk |
| `TextEncoder` | 字串 → 位元組 | `string` | `Uint8Array` | fake ReadableStream enqueue |

---

### 三、SSE 事件解析：chunk 邊界問題

#### 3.1 TCP chunk ≠ SSE event

SSE 規範以 `\n\n`（空行）作為事件分隔符。但 TCP 層的 chunk 邊界由網路狀況決定，**不保證對齊 SSE 事件邊界**。

一次 `reader.read()` 拿到的 chunk 可能是以下任一種：

```
情況 A：一個完整事件 ✅
  chunk: data: {"type":"token","content":"你"}\n\n

情況 B：半個事件 ❌
  chunk: data: {"type":"token","cont
  （下一個 chunk 才來 "ent":"你"}\n\n）

情況 C：多個事件合在一起 ✅
  chunk: data: {"type":"token","content":"你"}\n\ndata: {"type":"token","content":"好"}\n\n

情況 D：一個事件 + 下一個事件的開頭 ✅
  chunk: data: {"type":"token","content":"你"}\n\ndata: {"type":"t
  （下一個 chunk 才來 "oken","content":"好"}\n\n）
```

情況 B 和 D 都會導致問題：B 缺少結尾的 `\n\n`，D 的第二個事件不完整。

#### 3.2 緩衝累積與 `\n\n` 切分

解決方案：在前端維護一個 `buffer` 字串，每收到新 chunk 就累積進去，然後按 `\n\n` 切出**有結尾的完整事件**：

```javascript
// widget.js 中的完整串流迴圈
var buffer = '';
while (true) {
    var r = await reader.read();
    if (r.done) break;

    buffer += decoder.decode(r.value, { stream: true });

    var events = parseSseEvents(buffer);           // 切出完整事件
    buffer = buffer.slice(buffer.lastIndexOf('\n\n') + 2);  // 保留未解析殘留

    events.forEach(function (ev) { /* 消費事件 */ });
}
```

**`buffer.slice(buffer.lastIndexOf('\n\n') + 2)` 的作用**：找出最後一個 `\n\n` 的位置，將其之前（含）的資料交給 `parseSseEvents` 解析，之後的資料留到下一次 chunk 合併。

#### 3.3 `parseSseEvents` 逐行拆解

```javascript
function parseSseEvents(chunk) {
    var events = [];
    chunk.split('\n\n').forEach(function (block) {
        // block 可能是：
        //   "data: {完整 JSON}"
        //   "data: {不完整"           ← 缺少 }\n\n，在 JSON.parse 時會失敗
        //   ""                        ← 空字串（chunk 以 \n\n 結尾時）

        var dataLines = block.split('\n')
            .filter(function (line) {
                return line.indexOf('data:') === 0;   // 只取 data: 開頭的行
            })
            .map(function (line) { return line.slice(5); });  // 去掉 "data:" 前綴（含空格）

        if (dataLines.length > 0) {
            try {
                events.push(JSON.parse(dataLines.join('')));   // 合併多行 data 並解析 JSON
            } catch (e) {
                /* 忽略不完整的 JSON → 等下一次 chunk 合併後再試 */
            }
        }
    });
    return events;
}
```

#### 3.4 具體執行範例

假設後端連續送出兩個 token 事件，但 TCP 切成三個 chunk：

```
後端原始資料：
  data: {"type":"token","content":"你"}\n\ndata: {"type":"token","content":"好"}\n\n

TCP chunk 1:  data: {"type":"token","content":"你"}\n\ndata: {"type":"t
TCP chunk 2:  oken","content":"好"}\n\n
```

**第 1 次迴圈（收到 chunk 1）：**

```
buffer = 'data: {"type":"token","content":"你"}\\n\\ndata: {"type":"t'
split('\\n\\n') → ['data: {"type":"token","content":"你"}', 'data: {"type":"t']
  block 1: data: → '{"type":"token","content":"你"}' → JSON.parse ✅ → events[0]
  block 2: data: → '{"type":"t' → JSON.parse ❌ → catch 忽略
events = [{ type: "token", content: "你" }]
buffer = buffer.slice(lastIndexOf('\\n\\n') + 2) → 'data: {"type":"t'
```

**第 2 次迴圈（收到 chunk 2）：**

```
buffer = 'data: {"type":"t' + 'oken","content":"好"}\\n\\n'
       = 'data: {"type":"token","content":"好"}\\n\\n'
split('\\n\\n') → ['data: {"type":"token","content":"好"}', '']
  block 1: data: → '{"type":"token","content":"好"}' → JSON.parse ✅ → events[0]
  block 2: (空) → length === 0 → 跳過
events = [{ type: "token", content: "好" }]
buffer = '' (全部解析完畢)
```

#### 3.5 try/catch 的必要性

`parseSseEvents` 中的 `try/catch` **不是多餘的錯誤處理，而是正常流程的一部分**。chunk 邊界切在 JSON 中間是完全合法的（見上面情況 B），此時 `JSON.parse` 一定會 throw。catch 忽略它，等 buffer 累積完整後自然能解析。

---

### 四、Shadow DOM 樣式隔離

#### 4.1 為什麼需要隔離？

widget.js 被注入到**任意網站**，這些網站有自己的 CSS：

```css
/* 目標網站可能有這類全域樣式 */
button { background: red !important; }
input  { width: 100%; border: 2px solid black; }
div    { margin: 0; padding: 0; }
```

如果 widget 的 DOM 直接掛在 `document.body` 下，這些樣式會**污染** widget 的按鈕、輸入框、訊息氣泡。反之，widget 的樣式也可能影響目標網站。

#### 4.2 Shadow DOM 是什麼？

Shadow DOM 是瀏覽器的**樣式隔離機制**。每個 Shadow Root 自成一個封裝的 DOM 子樹，外部 CSS 無法穿透進來，內部 CSS 也不會洩漏出去。

```
document.body
  ├── (目標網站的 DOM)
  └── div#wc-widget-root          ← 宿主元素（host）
        └── #shadow-root (open)   ← Shadow Root（封裝邊界）
              ├── <style>          ← widget 的 CSS，只在這裡生效
              ├── <button class="wc-toggle">
              └── <div class="wc-panel">
                    └── ...
```

#### 4.3 `attachShadow({ mode: 'open' })` 實作

```javascript
// widget.js 中的 DOM 建立
var host = document.createElement('div');
host.id = 'wc-widget-root';
host.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:2147483647;...';
var shadow = host.attachShadow({ mode: 'open' });  // 建立 Shadow Root
```

| mode | 外部可否透過 `host.shadowRoot` 存取 |
|------|--------------------------------------|
| `'open'` | ✅ 可以（`host.shadowRoot` 回傳 Shadow Root） |
| `'closed'` | ❌ 不可以（`host.shadowRoot` 回傳 `null`） |

本專案用 `open` 模式，方便除錯和維護。

#### 4.4 樣式封裝的實證

```javascript
var style = document.createElement('style');
style.textContent = [
    '.wc-toggle{width:56px;height:56px;border-radius:50%;...}',
    '.wc-panel{...}',
    '.wc-messages{...}',
    // ... 全部 widget CSS
].join('');
shadow.appendChild(style);
```

這些 CSS 規則**只在 Shadow Root 內部生效**。目標網站的 `.wc-toggle` 規則不會影響 widget，widget 的 `button` 規則也不會影響目標網站。

#### 4.5 z-index: 2147483647

```javascript
host.style.cssText = '...;z-index:2147483647;...';
```

`2147483647` 是 32-bit 有號整數的最大值，確保 widget 永遠在所有頁面元素之上。宿主元素的 `style` 是設定在 `document` 樹上的（Shadow DOM 外部），因此用 `host.style` 而非 Shadow Root 內的元素。

---

### 五、Markdown 渲染管線

#### 5.1 三階段管線概覽

widget.js 的 markdown 渲染是一個**三階段管線**：

```
原始 LLM 輸出
    │
    ▼
Stage 1: escapeHtml()     ← HTML 實體轉義（防 XSS）
    │
    ▼
Stage 2: renderInline()   ← 行內語法（粗體、斜體、連結、行內代碼）
    │
    ▼
Stage 3: renderMarkdown() ← 區塊語法（標題、列表、引用、段落）
    │
    ▼
HTML 字串 → innerHTML 設入 DOM
```

#### 5.2 Stage 1：`escapeHtml` — XSS 防線

```javascript
function escapeHtml(text) {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}
```

LLM 回答中可能包含 HTML（有意或無意）：`<script>alert('xss')</script>`。如果直接塞進 `innerHTML`，瀏覽器會執行 `<script>` 標籤。`escapeHtml` 把 `<` 轉成 `&lt;`，讓瀏覽器將其視為純文字而非 HTML 標籤。

**先 escape 再渲染**的順序至關重要——這確保後續步驟產生的 HTML 標籤（`<strong>`、`<a>` 等）不會被二次 escape。

#### 5.3 Stage 2：`renderInline` — 行內語法與 placeholder token 機制

```javascript
function renderInline(text) {
    // ① 保護 inline code（後續 regex 不影響 code 內容）
    var blocks = [];
    text = text.replace(/`([^`]+)`/g, function (m, c) {
        blocks.push(c);
        return '\u0000' + (blocks.length - 1) + '\u0000';  // 用 null 字元佔位
    });

    // ② 連結（只允許 http/https）
    text = text.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, function (m, label, url) {
        var safe = /^https?:\/\//i.test(url) ? url : '#';
        return '<a href="' + safe + '" target="_blank" rel="noopener">' + label + '</a>';
    });

    // ③ 粗體 → 斜體（順序：粗體先，避免 **x** 被斜體吃掉）
    text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // ④ 還原 inline code
    text = text.replace(/\u0000(\d+)\u0000/g, function (m, i) {
        return '<code>' + blocks[parseInt(i, 10)] + '</code>';
    });
    return text;
}
```

**Placeholder token 機制的核心問題**：inline code 內的內容不應被其他 regex 處理。例如 `` `**不是粗體**` `` 中的 `**` 不應被轉成 `<strong>`。

解法是「先佔位、再處理、最後還原」：

```
原始文字:  這是 `**not bold**` 的例子

Step ①:   這是 \u00000\u0000 的例子          ← code 被抽到 blocks[0]
Step ②:   這是 \u00000\u0000 的例子          ← 連結 regex 不影響
Step ③:   這是 \u00000\u0000 的例子          ← 粗體 regex 不影響（沒有 **）
Step ④:   這是 <code>**not bold**</code> 的例子  ← 還原，code 內的 ** 被保護
```

#### 5.4 Stage 3：`renderMarkdown` — 區塊級狀態機

`renderMarkdown` 逐行解析 HTML 轉義後的文字，使用**狀態機**追蹤當前區塊類型：

```javascript
function renderMarkdown(text) {
    var escaped = escapeHtml(text);    // Stage 1
    var lines = escaped.split('\n');
    var html = [];
    var listType = null;   // 'ul' | 'ol' | null  ← 當前列表狀態
    var paragraph = null;  // currently accumulating paragraph content

    function closeList() {
        if (listType) { html.push('</' + listType + '>'); listType = null; }
    }
    function closeParagraph() {
        if (paragraph) { html.push('<p>' + paragraph + '</p>'); paragraph = null; }
    }

    for (var i = 0; i < lines.length; i++) {
        var trimmed = lines[i].trim();
        if (!trimmed) { closeList(); closeParagraph(); continue; }  // 空行：關閉所有區塊

        // 標題：# ~ ######
        var h = /^(#{1,6})\s+(.*)$/.exec(trimmed);
        if (h) { closeList(); closeParagraph(); /* ... render heading ... */ continue; }

        // 引用：>（escape 後 &gt;）
        var q = /^&gt;\s?(.*)$/.exec(trimmed);
        if (q) { closeList(); closeParagraph(); /* ... render blockquote ... */ continue; }

        // 無序列表：- 或 *
        var ul = /^[*\-]\s+(.*)$/.exec(trimmed);
        if (ul) {
            closeParagraph();
            if (listType !== 'ul') { closeList(); html.push('<ul>'); listType = 'ul'; }
            html.push('<li>' + renderInline(ul[1]) + '</li>');
            continue;
        }

        // 有序列表：1. 2. 3.
        var ol = /^\d+\.\s+(.*)$/.exec(trimmed);
        if (ol) { /* 類似 ul，listType = 'ol' */ continue; }

        // 一般文字：累積到 paragraph，空行時輸出 <p>
        closeList();
        if (paragraph) { paragraph += '<br>' + renderInline(trimmed); }
        else { paragraph = renderInline(trimmed); }
    }
    closeList(); closeParagraph();
    return html.join('');
}
```

**狀態轉換圖**：

```
                ┌──── 空行 ────┐
                ▼              │
  (none) ──→ [paragraph] ──→ </p>
    │           │
    │  - item  │  文字行（同段落接續）
    ▼           ▼
  [ul]      paragraph += '<br>' + text
    │
    │  空行
    ▼
  </ul> → (none)
```

#### 5.5 token 事件 vs done 事件的渲染策略差異

```javascript
events.forEach(function (ev) {
    if (ev.type === 'token') {
        // 逐字追加 plain text，不做 markdown 渲染
        respEl.appendChild(document.createTextNode(ev.content));
    } else if (ev.type === 'done') {
        // 一次性用完整 response 重新渲染 markdown
        respEl.innerHTML = renderMarkdown(ev.response);
    }
});
```

**為什麼 token 階段不做 markdown 渲染？** 因為 markdown 語法可能跨多個 token：

```
token 1: "**"
token 2: "bol"
token 3: "d**"

中途渲染 token 1: <strong>          ← 殘缺 HTML
中途渲染 token 2: <strong>bol       ← 更殘缺
中途渲染 token 3: <strong>bold</strong>  ← 才完整
```

所以先用 `createTextNode` 追加純文字（安全、無 HTML 解析），等 `done` 事件帶來完整回答後，再一次性執行 `innerHTML = renderMarkdown(ev.response)` 產生正確的 HTML。

---

### 六、Chrome Extension 架構（MV3）

#### 6.1 Manifest V3 的三大角色

```
┌─────────────────────────────────────────────────┐
│  manifest.json                                   │
│                                                   │
│  content_scripts: ["widget.js", "content.js"]     │
│      ↓ 注入到每個網頁                             │
│                                                   │
│  background: { service_worker: "background.js" }  │
│      ↓ 獨立執行緒，不受網頁限制                    │
│                                                   │
│  host_permissions: ["http://localhost:8000/*"]    │
│      ↓ 允許 background 發起 fetch 到後端          │
└─────────────────────────────────────────────────┘
```

| 角色 | 檔案 | 執行環境 | 能做的事 | 不能做的事 |
|------|------|----------|----------|------------|
| Content Script | `widget.js` + `content.js` | 網頁的 DOM 環境 | 操作 DOM、讀取頁面內容 | 發起跨域 fetch（受 CSP 限制） |
| Service Worker | `background.js` | 獨立背景環境 | 發起 fetch、存取 Chrome API | 操作 DOM |
| Host Permissions | `manifest.json` | — | 授權 background 存取特定 URL | — |

#### 6.2 Content Script 的執行上下文

Content script 在**網頁的 DOM 環境**中執行，但有獨立的 JavaScript 環境（隔離的世界）。它可以：
- ✅ 讀寫 `document`（操作 DOM）
- ✅ 存取 `chrome.runtime` API
- ❌ 存取網頁的 JavaScript 變數（如 `window.jQuery`）
- ❌ 發起跨越 CSP 限制的 fetch（受目標網站 CSP 策略限制）

#### 6.3 `matches: ["<all_urls>"]` 的意義

```json
"content_scripts": [{
    "matches": ["<all_urls>"],
    "js": ["widget.js", "content.js"],
    "run_at": "document_idle"
}]
```

`<all_urls>` 是一個特殊模式，表示 match **所有 HTTP/HTTPS URL**。這讓 widget 能注入到任何網站。

`run_at: "document_idle"` 表示 content script 在 DOM 樹建構完成後、`DOMContentLoaded` 事件觸發後載入——確保 `document.body` 已經存在。

#### 6.4 為什麼需要 Service Worker 做 fetch 代理？

Content script 不能直接 fetch 後端的原因是 **CSP（Content Security Policy）**：

```
目標網站的 CSP header：
  Content-Security-Policy: default-src 'self'; connect-src https://api.example.com

→ content script 的 fetch() 會被瀏覽器阻擋（localhost:8000 不在白名單中）
```

Service Worker 不受網頁 CSP 限制，加上 `host_permissions` 授權，就能自由 fetch 後端：

```json
"host_permissions": [
    "http://localhost:8000/*",
    "http://127.0.0.1:8000/*"
]
```

---

### 七、Content Script ↔ Background 通訊

#### 7.1 Port API 與雙向通訊

Content script 和 background 透過 `chrome.runtime.connect` 建立一個**持久的雙向通道（Port）**：

```
content.js                          background.js
    │                                     │
    ├── port = chrome.runtime.connect()   │
    │     name: 'wc-chat'                 │
    │                                     │
    ├── port.postMessage({type:'chat'}) ──►│  ← 發送聊天請求
    │                                     │
    │                                     ├── fetch('/api/chat')
    │                                     ├── reader.read() ← 逐 chunk
    │                                     │
    │◄── port.postMessage({type:'chunk'})─┤  ← 逐 chunk 轉送
    │◄── port.postMessage({type:'chunk'})─┤
    │     ...                             │
    │◄── port.postMessage({type:'done'})──┤  ← 串流結束
```

#### 7.2 訊息協定

本專案定義了四種訊息類型：

```javascript
// content.js → background.js
{ type: 'chat', query: '...', thread_id: '...', page_url: '...' }

// background.js → content.js（串流中）
{ type: 'chunk', data: 'data: {"type":"token","content":"你"}\n\n' }

// background.js → content.js（完成）
{ type: 'done' }

// background.js → content.js（失敗）
{ type: 'error', message: '伺服器回應異常（HTTP 500）' }
```

#### 7.3 `proxyStreamChat`：把 Port 訊息流包裝成 ReadableStream

content.js 的核心魔法是把 Port 的訊息流（`onMessage`）轉換為 `ReadableStream`，讓 widget.js **完全不知道 transport 差異**：

```javascript
function proxyStreamChat(payload) {
    return new Promise((resolve, reject) => {
        const port = chrome.runtime.connect({ name: 'wc-chat' });
        const stream = new ReadableStream({
            start(controller) {
                let buffer = '';
                const pump = () => {
                    const idx = buffer.lastIndexOf('\n\n');
                    if (idx !== -1) {
                        const chunk = buffer.slice(0, idx + 2);  // 取完整 SSE 區塊
                        buffer = buffer.slice(idx + 2);           // 保留殘留
                        controller.enqueue(new TextEncoder().encode(chunk));  // 字串 → Uint8Array
                    }
                };
                port.onMessage.addListener((msg) => {
                    if (msg.type === 'chunk') { buffer += msg.data; pump(); }
                    else if (msg.type === 'done') { pump(); controller.close(); }
                    else if (msg.type === 'error') { controller.error(new Error(msg.message)); }
                });
                port.onDisconnect.addListener(() => {
                    controller.error(new Error('與背景程序連線中斷'));
                });
            },
            cancel() { port.disconnect(); },
        });
        port.postMessage({ type: 'chat', query: payload.query, thread_id: payload.thread_id, page_url: currentHostname });
        resolve({ ok: true, status: 200, body: stream });
    });
}
```

**為何 `pump()` 要等 `\n\n` 才送出？** 因為 widget.js 的 `parseSseEvents` 依賴 `\n\n` 切分事件。如果送出不含結尾 `\n\n` 的 chunk，widget 端會把不完整的資料推入 buffer，`lastIndexOf('\n\n')` 找不到分隔符，導致事件積壓在 buffer 中延遲解析。

---

### 八、Service Worker 生命週期與 Keep-Alive

#### 8.1 MV3 Service Worker ≠ 舊版 Background Page

Manifest V2 的 `background.scripts` 會建立一個長期存在的 background page，幾乎不會被關閉。Manifest V3 改用 **Service Worker**，它與 PWA 的 Service Worker 共享相同的生命週期規則：

| 特性 | MV2 Background Page | MV3 Service Worker |
|------|--------------------|--------------------|
| 存在時間 | 瀏覽器開啟期間 | ~30 秒無活動後終止 |
| 記憶體 | 持久化 | 終止後丟失 |
| 喚醒方式 | 一直存在 | 事件驅動（message、alarm 等） |

#### 8.2 30 秒終止問題

Chrome 會在 Service Worker 無活動（沒有收到事件）約 **30 秒**後自動終止它。SSE 串流可能持續數分鐘（LLM 長回答），如果 SW 在串流中途被終止，fetch 連線斷裂，使用者看到錯誤。

```
時間軸：
  t=0     SW 收到 chat 請求，開始 fetch + 串流
  t=30    SW 無收到新事件 → Chrome 終止 SW
  t=31    fetch 連線被切斷 → content.js 收到 disconnect
  t=31    使用者看到「與背景程序連線中斷」
```

#### 8.3 `chrome.alarms` Keep-Alive 模式

解法：使用 `chrome.alarms` 定期喚醒 SW，重置 30 秒計時器：

```javascript
// background.js
const ALARM_NAME = 'wc-keepalive';

chrome.runtime.onConnect.addListener((port) => {
    if (port.name !== 'wc-chat') return;

    // 建立 keep-alive alarm（每 25 秒觸發一次）
    if (chrome.alarms) {
        chrome.alarms.create(ALARM_NAME, { periodInMinutes: 25 / 60 });
    }

    // port 斷線時清除 alarm
    port.onDisconnect.addListener(() => {
        if (chrome.alarms) chrome.alarms.clear(ALARM_NAME);
    });

    // alarm 事件處理：只需收到事件即可重置 SW 計時器
    chrome.alarms.onAlarm.addListener((alarm) => {
        if (alarm.name === 'wc-keepalive') return;  // 做任何事，只要收到就好
    });
});
```

**為什麼選 25 秒？** SW 的終止寬限期約 30 秒，25 秒的間隔確保 SW 在被終止前一定會收到 alarm 事件重置計時器。

**為什麼 alarm 清理在 `port.onDisconnect` 中？** 當使用者關閉頁面或 content script 斷線時，串流已無意義，應立即清除 alarm，避免 SW 繼續被無意義地喚醒。

#### 8.4 Keep-Alive 時間軸

```
t=0      SW 收到 chat 請求 → alarm.create({periodInMinutes: 25/60})
t=0~25   fetch + 串流進行中
t=25     alarm 觸發 → SW 收到事件 → 30 秒計時器重置
t=25~50  串流繼續
t=50     alarm 再次觸發 → 計時器再次重置
...
t=done   port 斷線 → alarm.clear() → SW 正常進入終止倒數
```

---

### 九、跨 Tab 共享狀態：`chrome.storage.session`

#### 9.1 為什麼需要跨 Tab 共享？

使用者可能在多個分頁中使用 widget。所有分頁應共享同一份對話記憶（`thread_id`），使 LLM 能記住之前在其他 Tab 問過的問題。

#### 9.2 `chrome.storage.session` 的特性

| 特性 | `chrome.storage.session` | `chrome.storage.local` |
|------|--------------------------|----------------------|
| 清除時機 | Chrome 關閉時自動清除 | 永久保留 |
| 容量 | 10 MB（預設） | 5 MB（MV3） |
| 用途 | 短暫的 session 狀態 | 長期設定 |

本專案選擇 `session` 而非 `local`，因為 `thread_id` 是與當前瀏覽器 session 綁定的——關閉 Chrome 後對話記憶應重新開始。

#### 9.3 讀寫流程

```javascript
// background.js

// ① 收到 chat 請求時：從 storage 讀取 thread_id
port.onMessage.addListener(async (msg) => {
    const { thread_id: storedThreadId } = await chrome.storage.session.get('thread_id');
    msg.thread_id = storedThreadId || null;  // 覆寫 content 傳來的 null
    // ... 用 msg.thread_id 呼叫後端 API
});

// ② 串流完成後：把 done 事件中的 thread_id 寫回 storage
if (doneThreadId) {
    await chrome.storage.session.set({ thread_id: doneThreadId });
}
```

**生命週期**：

```
Tab A 第一次問答
  → background 讀 storage → thread_id = null
  → 呼叫後端 → done 事件帶回 thread_id = "auto-abc123"
  → background 寫入 storage

Tab B 第二次問答
  → background 讀 storage → thread_id = "auto-abc123"  ← 跨 Tab 共享
  → 呼叫後端 → 後端延續對話記憶
```

---

### 十、取消與錯誤處理

#### 10.1 AbortController：取消 fetch

當使用者關閉頁面或 content script 斷線時，應主動取消進行中的 fetch，避免無意義的網路傳輸和後端運算。

```javascript
// background.js
const controller = new AbortController();

// content 斷線（頁面關閉/重整）時中止 fetch
port.onDisconnect.addListener(() => {
    controller.abort();              // 取消 fetch
    if (chrome.alarms) chrome.alarms.clear(ALARM_NAME);  // 清除 keep-alive
});

try {
    const resp = await fetch(ENDPOINT + '/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: msg.query, thread_id: msg.thread_id }),
        signal: controller.signal,   // 綁定 AbortController
    });
    // ... 串流處理
} catch (err) {
    if (err.name === 'AbortError') return;  // 使用者主動取消，不需通知
    port.postMessage({ type: 'error', message: String(err.message || err) });
}
```

#### 10.2 AbortError vs 真實錯誤

| 錯誤型別 | `err.name` | 處理方式 |
|----------|-----------|----------|
| 使用者取消（頁面關閉/重整） | `'AbortError'` | 靜默返回 `return`，不通知 |
| 網路錯誤 / 後端當機 | `'TypeError'` / `'FetchError'` | `port.postMessage({ type: 'error' })` |
| 後端回傳 4xx/5xx | （在 fetch 外處理） | 檢查 `resp.ok`，發送 error |

`AbortError` 是「正常行為」不是「錯誤」——使用者關閉頁面，fetch 自然應該中止，不需要報錯。

#### 10.3 錯誤傳播路徑

```
後端錯誤（HTTP 500）
  → background.js: port.postMessage({ type: 'error', message: '伺服器回應異常...' })
    → content.js: proxyStreamChat 的 ReadableStream 觸發 controller.error()
      → widget.js: catch 區塊捕獲 → respEl.className = 'wc-msg wc-error'
        → 使用者看到紅色錯誤氣泡
```

#### 10.4 `wc-error` 錯誤展示

```javascript
// widget.js — 處理 error 事件和 catch 區塊
} else if (ev.type === 'error') {
    respEl.textContent = '';
    respEl.className = 'wc-msg wc-error';   // 紅色背景、紅色文字
    respEl.textContent = '錯誤：' + ev.message;
}

// catch 區塊（fetch 失敗、連線中斷等）
} catch (err) {
    respEl.textContent = '';
    respEl.className = 'wc-msg wc-error';
    respEl.textContent = '錯誤：' + err.message;
}
```

CSS 樣式（在 Shadow DOM 的 `<style>` 中）：

```css
.wc-error {
    align-self: flex-start;
    background: #fee2e2;    /* 淺紅色背景 */
    color: #991b1b;         /* 深紅色文字 */
    border: 1px solid #fecaca;
}
```

---

### 十一、完整生命週期圖

```
┌─────────────────────────────────────────────────────────────────┐
│                        使用者在對話框輸入問題                      │
│                        按下 Enter 或點擊送出                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  widget.js: sendQuery(query)                                    │
│  ① 建立使用者訊息 DOM (wc-msg wc-user)                          │
│  ② 建立助手回應 DOM (wc-msg wc-assistant) + typing indicator    │
│  ③ 調用 streamChat({ query, thread_id })                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
┌──────────────────────┐    ┌───────────────────────────────────┐
│ 網頁版               │    │ Extension 版                      │
│                      │    │                                   │
│ streamChat =         │    │ streamChat = proxyStreamChat      │
│   defaultStreamChat  │    │   ① chrome.runtime.connect()     │
│   → fetch POST       │    │   ② port.postMessage({chat})     │
│     /api/chat        │    │   ③ 建立 fake ReadableStream      │
│   → resp.body        │    │   ④ 回傳 { ok, body: stream }    │
└──────────┬───────────┘    └──────────────┬────────────────────┘
           │                               │
           │                               ▼
           │                    ┌────────────────────────────────┐
           │                    │  background.js (Service Worker)│
           │                    │  ① 從 storage.session 讀 thread_id │
           │                    │  ② 建立 AbortController        │
           │                    │  ③ fetch POST /api/chat        │
           │                    │  ④ reader.read() 逐 chunk      │
           │                    │  ⑤ port.postMessage({chunk})   │
           │                    │     ↓ 重複直到 done             │
           │                    │  ⑥ port.postMessage({done})    │
           │                    │  ⑦ 寫回 thread_id 到 storage    │
           │                    │  ⑧ alarm.clear()               │
           │                    └──────────────┬────────────────┘
           │                                   │
           │                    ┌──────────────┘
           │                    │  (Extension 版：Port 訊息)
           │                    ▼
           │           ┌────────────────────────────────────────┐
           │           │  content.js: proxyStreamChat            │
           │           │  port.onMessage → buffer → pump()      │
           │           │  → controller.enqueue(Uint8Array)      │
           │           │  → ReadableStream 送給 widget.js        │
           │           └──────────────┬─────────────────────────┘
           │                          │
           ▼                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  widget.js: while(true) { reader.read() }                      │
│                                                                 │
│  chunk 來了：                                                    │
│    buffer += decoder.decode(value, { stream: true })            │
│    events = parseSseEvents(buffer)   ← 按 \n\n 切分             │
│    buffer = buffer.slice(lastIndexOf('\n\n') + 2)               │
│                                                                 │
│  對每個 event：                                                   │
│    ┌───────────────────────────────────────────────────────┐    │
│    │ type=token:                                          │    │
│    │   respEl.appendChild(createTextNode(content))        │    │
│    │   第一個 token 時隱藏 typing indicator                │    │
│    │   messagesEl.scrollTop = scrollHeight  ← 自動捲底     │    │
│    ├───────────────────────────────────────────────────────┤    │
│    │ type=done:                                           │    │
│    │   respEl.innerHTML = renderMarkdown(response)        │    │
│    │     → escapeHtml → renderInline → renderMarkdown     │    │
│    │   threadId = ev.thread_id  ← 保存供下一輪使用         │    │
│    ├───────────────────────────────────────────────────────┤    │
│    │ type=error:                                          │    │
│    │   respEl.className = 'wc-msg wc-error'               │    │
│    │   respEl.textContent = '錯誤：' + ev.message          │    │
│    └───────────────────────────────────────────────────────┘    │
│                                                                 │
│  reader.read() 返回 done=true → 連線關閉                        │
│  sendBtn.disabled = false → 恢復輸入                             │
└─────────────────────────────────────────────────────────────────┘
```

---

### 附錄 A：關鍵 API 速查表

| API | MDN 連結 | 用途 | 本專案使用位置 |
|-----|---------|------|--------------|
| `fetch()` | [MDN](https://developer.mozilla.org/en-US/docs/Web/API/fetch) | 發起 HTTP 請求 | widget.js、background.js |
| `ReadableStream` | [MDN](https://developer.mozilla.org/en-US/docs/Web/API/ReadableStream) | 串流資料管道 | widget.js、content.js |
| `ReadableStreamDefaultReader` | [MDN](https://developer.mozilla.org/en-US/docs/Web/API/ReadableStreamDefaultReader) | 從 ReadableStream 逐 chunk 讀取 | widget.js |
| `TextDecoder` | [MDN](https://developer.mozilla.org/en-US/docs/Web/API/TextDecoder) | Uint8Array → string | widget.js、background.js |
| `TextEncoder` | [MDN](https://developer.mozilla.org/en-US/docs/Web/API/TextEncoder) | string → Uint8Array | content.js |
| `AbortController` | [MDN](https://developer.mozilla.org/en-US/docs/Web/API/AbortController) | 取消 fetch | background.js |
| `attachShadow()` | [MDN](https://developer.mozilla.org/en-US/docs/Web/API/Element/attachShadow) | 建立 Shadow DOM | widget.js |
| `chrome.runtime.connect()` | [Chrome API](https://developer.chrome.com/docs/extensions/reference/runtime/#method-connect) | 建立 Port 通訊通道 | content.js |
| `chrome.alarms` | [Chrome API](https://developer.chrome.com/docs/extensions/reference/api/alarms) | 定時喚醒 Service Worker | background.js |
| `chrome.storage.session` | [Chrome API](https://developer.chrome.com/docs/extensions/reference/api/storage#property-session) | 短暫跨 Tab 共享狀態 | background.js |
| `document.createTextNode()` | [MDN](https://developer.mozilla.org/en-US/docs/Web/API/Document/createTextNode) | 安全建立純文字節點（無 HTML 解析） | widget.js |
| `innerHTML` | [MDN](https://developer.mozilla.org/en-US/docs/Web/API/Element/innerHTML) | 設入 HTML（僅用於 markdown 渲染結果） | widget.js |

---

### 附錄 B：與 sse.md 的交叉引用

| sse.md 主題 | 本文對應章節 |
|-------------|-------------|
| SSE 協定規範（§一） | 本文 §三：chunk 邊界問題 |
| 後端 `_sse()` 序列化（§2.1） | 本文 §三：`parseSseEvents` 解析 |
| 後端 `_event_stream()` 串流（§2.2） | 本文 §一：ReadableStream 消費 |
| 前端解析（§三，淺層） | 本文 §一~§三（完整深入） |
| Extension 模式 SSE 變體（§四） | 本文 §七：Port 通訊 + fake ReadableStream |
| 心跳 Keep-Alive（§5.1） | 本文 §八：Service Worker Keep-Alive（不同層級的 keep-alive） |
| `stream: true`（§5.3） | 本文 §二：完整 UTF-8 編碼解說 |
| 完整生命週期圖（§六） | 本文 §十一：擴展為網頁版 + Extension 版雙路徑 |
