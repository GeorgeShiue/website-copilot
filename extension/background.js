/* Website Copilot - background service worker（M4b）
 *
 * 角色：代理 content script 的聊天請求到後端（localhost:8000），
 * 繞過網頁 CSP / CORS 限制（extension origin 不受網頁限制）。
 *
 * 協定（content.js ↔ background.js，經 chrome.runtime.Port）：
 *   content → background: { type: 'chat', query, thread_id }
 *   background → content（串流中）: { type: 'chunk', data: <bytes-as-text> }
 *   background → content（完成）: { type: 'done' }
 *   background → content（失敗）: { type: 'error', message }
 */
'use strict';

const ENDPOINT = 'http://127.0.0.1:8000';

chrome.runtime.onConnect.addListener((port) => {
  if (port.name !== 'wc-chat') return;

  port.onMessage.addListener(async (msg) => {
    if (!msg || msg.type !== 'chat') return;
    const controller = new AbortController();
    // content 斷線（頁面關閉/重整）時中止 fetch
    port.onDisconnect.addListener(() => controller.abort());

    try {
      const resp = await fetch(ENDPOINT + '/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: msg.query, thread_id: msg.thread_id }),
        signal: controller.signal,
      });
      if (!resp.ok || !resp.body) {
        port.postMessage({ type: 'error', message: '伺服器回應異常（HTTP ' + resp.status + '）' });
        return;
      }
      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      // fetch 進行中 SW 不會休眠；逐塊轉送即為 keepalive
      while (true) {
        const r = await reader.read();
        if (r.done) break;
        port.postMessage({ type: 'chunk', data: decoder.decode(r.value, { stream: true }) });
      }
      port.postMessage({ type: 'done' });
    } catch (err) {
      if (err.name === 'AbortError') return; // 使用者關閉頁面，不需通知
      port.postMessage({ type: 'error', message: String(err.message || err) });
    }
  });
});
