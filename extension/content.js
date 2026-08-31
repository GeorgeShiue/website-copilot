/* Website Copilot - content script（M4b）
 *
 * 角色：在「任何網站」注入浮動 widget，並以 chrome.runtime.Port
 * 代理聊天請求（繞過網頁 CSP / CORS）。
 *
 * 執行順序（manifest content_scripts）：widget.js 先載入（提供
 * WebsiteCopilotWidget.mount），本檔再呼叫 mount 並傳入 streamChat。
 *
 * streamChat 與 widget.js 預設 transport（fetch）同介面：
 *   傳入 payload → 回傳 { ok, status, body: { getReader() } }
 */
'use strict';

(function () {
  if (!window.WebsiteCopilotWidget) {
    console.warn('[wc] WebsiteCopilotWidget 未載入，跳過掛載');
    return;
  }
  if (window.__wcMounted) return; // 防止重複掛載
  window.__wcMounted = true;

  const ENDPOINT = 'http://127.0.0.1:8000';
  const currentHostname = window.location.hostname;

  function proxyStreamChat(payload) {
    // 回傳 Promise<{ ok, status, body: ReadableStream-like }>
    return new Promise((resolve, reject) => {
      const port = chrome.runtime.connect({ name: 'wc-chat' });
      const stream = new ReadableStream({
        start(controller) {
          let buffer = '';
          const pump = () => {
            // 依 \n\n 切出「含結尾 \n\n」的完整 SSE 區塊送往 widget：
            // 若不含結尾 \n\n，widget 端 parse 後 slice 會吃掉首字元造成事件遺失/污染
            const idx = buffer.lastIndexOf('\n\n');
            if (idx !== -1) {
              const chunk = buffer.slice(0, idx + 2);
              buffer = buffer.slice(idx + 2);
              controller.enqueue(new TextEncoder().encode(chunk));
            }
          };
          port.onMessage.addListener((msg) => {
            if (msg.type === 'chunk') {
              buffer += msg.data;
              pump();
            } else if (msg.type === 'done') {
              pump();
              controller.close();
            } else if (msg.type === 'error') {
              controller.error(new Error(msg.message));
            }
          });
          port.onDisconnect.addListener(() => {
            controller.error(new Error('與背景程序連線中斷'));
          });
        },
        pull() { /* ReadableStream 由 getReader 驅動，enqueue 於 start 內處理 */ },
        cancel() { port.disconnect(); },
      });

      port.postMessage({ type: 'chat', query: payload.query, thread_id: payload.thread_id, page_url: currentHostname });
      resolve({ ok: true, status: 200, body: stream });
    });
  }

  window.WebsiteCopilotWidget.mount({
    endpoint: ENDPOINT,
    streamChat: proxyStreamChat,
  });
})();
