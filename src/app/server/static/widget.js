/* 實驗室網站問答助理 - 浮動 widget（M4a）
 *
 * 用法（自有網站任何頁面加一行即可）：
 *   <script src="http://localhost:8000/static/widget.js"
 *           data-endpoint="http://localhost:8000"></script>
 *
 * 行為：右下角浮動按鈕 → 點開對話框 → 串流問答（多輪記憶自動處理）。
 * 純 vanilla JS，零依賴。
 */
(function () {
  'use strict';

  var scriptEl = document.currentScript;
  var ENDPOINT = (scriptEl && scriptEl.dataset.endpoint) || 'http://localhost:8000';
  var threadId = null;

  /* ---------- DOM 建立（shadow DOM 隔離樣式） ---------- */
  var host = document.createElement('div');
  host.id = 'wc-widget-root';
  host.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:2147483647;font-family:-apple-system,"Segoe UI","Noto Sans TC",sans-serif;';
  var shadow = host.attachShadow({ mode: 'open' });

  var style = document.createElement('style');
  style.textContent = [
    '.wc-toggle{width:56px;height:56px;border-radius:50%;border:none;cursor:pointer;',
    '  background:#2563eb;color:#fff;font-size:24px;box-shadow:0 4px 12px rgba(0,0,0,.25);}',
    '.wc-toggle:hover{background:#1d4ed8;}',
    '.wc-panel{position:fixed;bottom:88px;right:20px;width:360px;max-width:calc(100vw - 40px);',
    '  height:480px;max-height:calc(100vh - 120px);background:#fff;border-radius:12px;',
    '  box-shadow:0 8px 32px rgba(0,0,0,.25);display:none;flex-direction:column;overflow:hidden;}',
    '.wc-panel.open{display:flex;}',
    '.wc-header{background:#2563eb;color:#fff;padding:12px 16px;font-size:14px;font-weight:600;}',
    '.wc-messages{flex:1;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:10px;',
    '  background:#f8fafc;}',
    '.wc-msg{max-width:85%;padding:8px 12px;border-radius:10px;font-size:13px;line-height:1.5;',
    '  white-space:pre-wrap;word-break:break-word;}',
    '.wc-user{align-self:flex-end;background:#2563eb;color:#fff;border-bottom-right-radius:3px;}',
    '.wc-assistant{align-self:flex-start;background:#fff;border:1px solid #e2e8f0;',
    '  border-bottom-left-radius:3px;}',
    '.wc-error{align-self:flex-start;background:#fee2e2;color:#991b1b;border:1px solid #fecaca;}',
    '.wc-sources{margin-top:6px;padding-top:6px;border-top:1px dashed #cbd5e1;font-size:11px;',
    '  color:#64748b;display:flex;flex-direction:column;gap:3px;}',
    '.wc-sources a{color:#2563eb;text-decoration:none;word-break:break-all;}',
    '.wc-inputbar{display:flex;gap:8px;padding:10px;background:#fff;border-top:1px solid #e2e8f0;}',
    '.wc-inputbar input{flex:1;padding:8px 10px;border:1px solid #cbd5e1;border-radius:8px;',
    '  font-size:13px;outline:none;}',
    '.wc-inputbar input:focus{border-color:#2563eb;}',
    '.wc-inputbar button{padding:8px 14px;background:#2563eb;color:#fff;border:none;',
    '  border-radius:8px;font-size:13px;cursor:pointer;}',
    '.wc-inputbar button:disabled{opacity:.6;cursor:not-allowed;}'
  ].join('');
  shadow.appendChild(style);

  var toggleBtn = document.createElement('button');
  toggleBtn.className = 'wc-toggle';
  toggleBtn.textContent = '💬';
  toggleBtn.title = '問實驗室網站助理';
  shadow.appendChild(toggleBtn);

  var panel = document.createElement('div');
  panel.className = 'wc-panel';
  panel.innerHTML = [
    '<div class="wc-header">實驗室網站問答助理</div>',
    '<div class="wc-messages">',
    '  <div class="wc-msg wc-assistant">你好！請輸入問題，例如「實驗室的成員有哪些人？」</div>',
    '</div>',
    '<div class="wc-inputbar">',
    '  <input type="text" placeholder="輸入你的問題…" autocomplete="off">',
    '  <button type="button">送出</button>',
    '</div>'
  ].join('');
  shadow.appendChild(panel);
  document.body.appendChild(host);

  var messagesEl = panel.querySelector('.wc-messages');
  var inputEl = panel.querySelector('input');
  var sendBtn = panel.querySelector('button');

  /* ---------- 行為 ---------- */
  toggleBtn.addEventListener('click', function () {
    panel.classList.toggle('open');
    if (panel.classList.contains('open')) inputEl.focus();
  });

  function appendSources(msgEl, sources) {
    var box = document.createElement('div');
    box.className = 'wc-sources';
    sources.forEach(function (url, i) {
      var a = document.createElement('a');
      a.href = url;
      a.target = '_blank';
      a.rel = 'noopener';
      a.textContent = (i + 1) + '. ' + url;
      box.appendChild(a);
    });
    msgEl.appendChild(box);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function parseSseEvents(chunk) {
    var events = [];
    chunk.split('\n\n').forEach(function (block) {
      var dataLines = block.split('\n').filter(function (line) {
        return line.indexOf('data:') === 0;
      }).map(function (line) { return line.slice(5); });
      if (dataLines.length > 0) {
        try { events.push(JSON.parse(dataLines.join(''))); } catch (e) { /* 忽略不完整 JSON */ }
      }
    });
    return events;
  }

  async function sendQuery(query) {
    var userEl = document.createElement('div');
    userEl.className = 'wc-msg wc-user';
    userEl.textContent = query;
    messagesEl.appendChild(userEl);

    var respEl = document.createElement('div');
    respEl.className = 'wc-msg wc-assistant';
    messagesEl.appendChild(respEl);
    messagesEl.scrollTop = messagesEl.scrollHeight;

    sendBtn.disabled = true;
    inputEl.disabled = true;
    var buffer = '';
    try {
      var resp = await fetch(ENDPOINT + '/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query, thread_id: threadId }),
      });
      if (!resp.ok || !resp.body) {
        throw new Error('伺服器回應異常（HTTP ' + resp.status + '）');
      }
      var reader = resp.body.getReader();
      var decoder = new TextDecoder();
      while (true) {
        var r = await reader.read();
        if (r.done) break;
        buffer += decoder.decode(r.value, { stream: true });
        var events = parseSseEvents(buffer);
        buffer = buffer.slice(buffer.lastIndexOf('\n\n') + 2);
        events.forEach(function (ev) {
          if (ev.type === 'token') {
            respEl.textContent += ev.content;
            messagesEl.scrollTop = messagesEl.scrollHeight;
          } else if (ev.type === 'done') {
            respEl.textContent = ev.response;
            threadId = ev.thread_id;   // 記住，續問記得上下文
            if (ev.sources && ev.sources.length > 0) appendSources(respEl, ev.sources);
          } else if (ev.type === 'error') {
            respEl.className = 'wc-msg wc-error';
            respEl.textContent = '錯誤：' + ev.message;
          }
        });
      }
    } catch (err) {
      respEl.className = 'wc-msg wc-error';
      respEl.textContent = '錯誤：' + err.message;
    } finally {
      sendBtn.disabled = false;
      inputEl.disabled = false;
      inputEl.focus();
    }
  }

  function submit() {
    var query = inputEl.value.trim();
    if (!query) return;
    inputEl.value = '';
    sendQuery(query);
  }

  sendBtn.addEventListener('click', submit);
  inputEl.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') submit();
  });
})();
