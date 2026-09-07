# 嵌入介面（iframe / widget / Extension）

## 模組總覽
此模組提供**三種嵌入方式**，共用同一後端（`server.md` 的 `/api/chat` SSE）與同一 widget 核心。iframe 與 script widget 由網站管理員在 HTML 注入；Chrome Extension 由造訪者端注入（任何網站自動浮出）。

三種方式比較：

| 方式 | 顯示範圍 | 安裝成本 | 實作成本 | 用途 |
| --- | --- | --- | --- | --- |
| iframe embed | 自有網頁區塊 | 零 | ⭐ 最低 | 自有網站 demo、正式嵌入 |
| `<script>` widget | 自有網站任何頁面 | 零 | 低 | 一行 `<script>` 即用 |
| Chrome Extension | 任何網站（即時浮出） | 需安裝（load unpacked） | 中 | 加分展示（本機開發模式） |

進階功能包含：

- **shadow DOM 隔離** — widget 樣式不污染嵌入網站
- **mount factory** — `WebsiteCopilotWidget.mount({endpoint, streamChat})`，網頁/Extension 共用同一份 widget.js
- **transport 抽象** — 網頁版預設 fetch；Extension 傳 chrome.runtime 代理（繞過 CSP/CORS）
- **markdown 渲染** — 粗體 / 列表 / 連結 / 程式碼；先 escape HTML 防 XSS

- **模組實作**
	- `src/app/server/static/chat.html`（**iframe 版聊天頁**：同 origin 呼叫 `/api/chat`，多輪自動帶 thread_id）
	- `src/app/server/static/widget.js`（**浮動 widget 核心**：shadow DOM、mount factory、SSE 解析、markdown 渲染、typing indicator）
	- `src/app/server/static/demo.html`（**嵌入示範頁**：`GET /` redirect 至此，展示 iframe + script 兩種方式）
	- `extension/manifest.json`（**MV3**：content_scripts + background + `alarms` / `storage` 權限）
	- `extension/background.js`（**代理串流**：`chrome.runtime.onConnect` → fetch SSE → 逐塊 postMessage；keepalive via `chrome.alarms`；`chrome.storage.session` 保存 thread_id）
	- `extension/content.js`（**注入掛載 + 站點偵測**：`window.location.hostname` 偵測 + `page_url` 帶入 + proxyStreamChat 建立 port + ReadableStream 轉接）
	- `extension/widget.js`（**複本**：與 `static/widget.js` 同步，含 typing indicator；⚠️ Chrome 不載入 symlink 的 content script）
	- `scripts/m4b_extension_test.py`（**自動化驗證**：xvfb + Playwright 端到端）

## widget.js

### mount factory（M4b-1 重構）

```javascript
// 網頁版自動掛載（<script data-endpoint> 載入時，document.currentScript 存在）
window.WebsiteCopilotWidget = { mount: mount };
if (document.currentScript) {
  mount({ endpoint: document.currentScript.dataset.endpoint });
}

// Extension 版（content.js 顯式呼叫；content script 環境 currentScript 為 null 不自動掛載）
WebsiteCopilotWidget.mount({
  endpoint: 'http://127.0.0.1:8000',
  streamChat: proxyStreamChat,   // 自訂 transport（預設 fetch）
});
```

- **`defaultStreamChat(endpoint)`** — 預設 transport：`fetch(endpoint + '/api/chat')`
- **`streamChat(payload)`** — transport 抽象介面：傳入 `{query, thread_id}`，回傳 `{ok, status, body: {getReader()}}`
- **`parseSseEvents(chunk)`** — 以空行分隔解析 `data:` JSON 事件
- **`renderMarkdown(text)`** — 輕量 markdown 渲染（escape → 段落/列表/標題/引用/粗體/斜體/連結/inline code）；`token` 期間維持純文字累加，`done` 才一次渲染
- **Typing Indicator** — 等待後端回應時在回覆區顯示三個跳動圓點（CSS animation），收到第一個 token 徎淡出移除

## extension/

### 資料流（background 代理）

```
content.js（頁面 isolated world）
  → 偵測 window.location.hostname → currentHostname
  → WebsiteCopilotWidget.mount({streamChat: proxyStreamChat})
  → proxyStreamChat：chrome.runtime.connect({name: 'wc-chat'}) + ReadableStream
  → background.js（service worker）
  → fetch('http://127.0.0.1:8000/api/chat', {page_url: hostname})（不受頁面 CSP/CORS 限制）
  → 逐塊 port.postMessage({type: 'chunk'}) → content.js 依 \n\n 切 SSE 區塊 → widget 解析

chrome.storage.session 共享 thread_id → 換頁面保留對話記憶
chrome.alarms 定期喚醒 SW → 避免 Chrome ~30s 終止 Service Worker
```

- **`background.js`** — `chrome.runtime.onConnect` 監聽 `wc-chat` port；`AbortController` 於 content 斷線時中止 fetch（fetch 進行中 SW 不休眠，chunk 兼 keepalive）；`chrome.alarms` 以 25 秒週期保持 SW 活躍；`chrome.storage.session` 保存/讀取 `thread_id` 實現跨頁面 session 共享
- **`content.js`** — `proxyStreamChat(payload)`：建立 port + `ReadableStream`，依 `\n\n` 切出「含結尾」的 SSE 區塊（⚠️ 若不含結尾，widget 端 parse 後 slice 會吃字元致串流中斷）；`window.location.hostname` 偵測 → `page_url` 帶入 fetch body；`__wcMounted` 防重複掛載
- **`manifest.json`** — MV3：`content_scripts: ["widget.js", "content.js"]`（`<all_urls>`、`document_idle`）+ `background.service_worker` + `host_permissions`（localhost:8000）+ `permissions: ["alarms", "storage"]`

### 同步規則

⚠️ `extension/widget.js` 為 `src/app/server/static/widget.js` 的**實體複本**（Chrome 不載入 symlink 的 content script）。修改源頭後需同步：

```bash
cp src/app/server/static/widget.js extension/widget.js
```

### 使用方式

```html
<!-- ① iframe：網頁任意位置 -->
<iframe src="http://localhost:8000/static/chat.html" width="360" height="520"></iframe>

<!-- ② script widget：</body> 前加一行（右下角浮動 💬） -->
<script src="http://localhost:8000/static/widget.js" data-endpoint="http://localhost:8000"></script>

<!-- ③ Chrome Extension：chrome://extensions → 載入未封裝項目 → 選 extension/ 資料夾 -->
```

## 已知問題
- [ ] `extension/widget.js` 為複本需手動同步（見上）
- [ ] Extension 為本機開發模式（load unpacked），未上架
- [ ] bookmarklet（`javascript:` 書籤）受網站 CSP 限制，僅供 demo

## 未來規劃
- [ ] **Extension 上架**
- [ ] **網站導航**（AI 直接控制網站介面跳轉、篩選）
- [ ] **專責代理**（多 Agent 分工）
