/* Website Copilot - background service worker（M4b）
 *
 * 角色：代理 content script 的聊天請求到後端（localhost:8000），
 * 繞過網頁 CSP / CORS 限制（extension origin 不受網頁限制）。
 * 同時管理 thread_id 的共享狀態（chrome.storage.session），
 * 使跨 tab、跨頁面的對話共享同一份記憶。
 *
 * 協定（content.js ↔ background.js，經 chrome.runtime.Port）：
 *   content → background: { type: 'chat', query, thread_id, page_url }
 *   background → content（串流中）: { type: 'chunk', data: <bytes-as-text> }
 *   background → content（完成）: { type: 'done' }
 *   background → content（失敗）: { type: 'error', message }
 *
 * thread_id 生命週期：
 *   1. 收到 chat 請求時，從 storage 讀取 thread_id 覆寫 msg
 *   2. 串流完成後，從 done 事件解析 thread_id 寫回 storage
 *   3. Chrome 關閉時 storage.session 自動清除
 */
'use strict';

const ENDPOINT = 'http://127.0.0.1:8000';

// Alarm 事件處理：SW 被 alarm 喚醒時，不做任何事（僅保持活躍）
if (chrome.alarms && chrome.alarms.onAlarm) {
  chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === 'wc-keepalive') return;
  });
}

chrome.runtime.onConnect.addListener((port) => {
  if (port.name !== 'wc-chat') return;

  // 使用 chrome.alarms 保持 Service Worker 活躍（Chrome ~30s 無活動會終止 SW）
  // 每 25 秒觸發 alarm，SW 收到 alarm 事件後重新計時，避免被終止
  const ALARM_NAME = 'wc-keepalive';
  if (chrome.alarms) {
    chrome.alarms.create(ALARM_NAME, { periodInMinutes: 25 / 60 });
  }

  port.onDisconnect.addListener(() => {
    if (chrome.alarms) chrome.alarms.clear(ALARM_NAME);
  });

  port.onMessage.addListener(async (msg) => {
    if (!msg || msg.type !== 'chat') return;

    // 從共享 storage 讀取 thread_id，覆寫 content 傳來的 null
    const { thread_id: storedThreadId } = await chrome.storage.session.get('thread_id');
    msg.thread_id = storedThreadId || null;

    const controller = new AbortController();
    // content 斷線（頁面關閉/重整）時中止 fetch + 清除 alarm
    port.onDisconnect.addListener(() => {
      controller.abort();
      if (chrome.alarms) chrome.alarms.clear(ALARM_NAME);
    });

    try {
      const resp = await fetch(ENDPOINT + '/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: msg.query, thread_id: msg.thread_id, page_url: msg.page_url }),
        signal: controller.signal,
      });
      if (!resp.ok || !resp.body) {
        port.postMessage({ type: 'error', message: '伺服器回應異常（HTTP ' + resp.status + '）' });
        return;
      }
      let doneThreadId = null;
      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      // fetch 進行中 SW 不會休眠；逐塊轉送即為 keepalive
      while (true) {
        const r = await reader.read();
        if (r.done) break;
        const text = decoder.decode(r.value, { stream: true });
        // 從 SSE data 行解析 thread_id（僅 done 事件中出現）
        const match = text.match(/"thread_id"\s*:\s*"([^"]+)"/);
        if (match) doneThreadId = match[1];
        port.postMessage({ type: 'chunk', data: text });
      }
      port.postMessage({ type: 'done' });
      // 寫回 storage，供所有 tab 共用
      if (doneThreadId) {
        await chrome.storage.session.set({ thread_id: doneThreadId });
      }
    } catch (err) {
      if (err.name === 'AbortError') return; // 使用者關閉頁面，不需通知
      port.postMessage({ type: 'error', message: String(err.message || err) });
    }
  });
});
