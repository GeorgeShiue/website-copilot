/* 網站助理 - 浮動 widget（M4a / M4b）
 *
 * 網頁版用法（自有網站任何頁面加一行即可）：
 *   <script src="http://localhost:8000/static/widget.js"
 *           data-endpoint="http://localhost:8000"></script>
 *
 * Chrome Extension 用法（M4b，content.js 呼叫）：
 *   WebsiteCopilotWidget.mount({
 *     endpoint: 'http://localhost:8000',
 *     streamChat: proxyStreamChat,   // 可選：自訂 transport（預設 fetch）
 *   });
 *
 * 行為：右下角浮動按鈕 → 點開對話框 → 串流問答（多輪記憶自動處理）。
 * 純 vanilla JS，零依賴。
 */
(function () {
  'use strict';

  /* ---------- 預設 transport：直接 fetch 後端（網頁版用） ---------- */
  function defaultStreamChat(endpoint) {
    return function (payload) {
      return fetch(endpoint + '/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
    };
  }

  /* ---------- mount factory：建立 widget 實例（DOM/串流/markdown 全在閉包內） ---------- */
  function mount(options) {
    var endpoint = options.endpoint || 'http://localhost:8000';
    var streamChat = options.streamChat || defaultStreamChat(endpoint);
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
    /* markdown 渲染樣式（assistant 訊息內） */
    '.wc-msg ul,.wc-msg ol{margin:4px 0 4px 1.4em;padding-left:.4em;}',
    '.wc-msg li{margin:2px 0;}',
    '.wc-msg strong{font-weight:700;}',
    '.wc-msg code{background:rgba(0,0,0,.06);padding:1px 4px;border-radius:4px;font-size:.9em;font-family:monospace;}',
    '.wc-msg a{color:#2563eb;text-decoration:underline;word-break:break-all;}',
    '.wc-msg blockquote{border-left:3px solid #e2e8f0;padding-left:10px;color:#64748b;margin:4px 0;}',
    '.wc-msg h1,.wc-msg h2,.wc-msg h3,.wc-msg h4{margin:8px 0 4px;font-size:1.05em;}',
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
  toggleBtn.title = '問網站助理';
  shadow.appendChild(toggleBtn);

  var panel = document.createElement('div');
  panel.className = 'wc-panel';
  panel.innerHTML = [
    '<div class="wc-header">網站助理</div>',
    '<div class="wc-messages">',
    '  <div class="wc-msg wc-assistant">你好！我是你的網站助手，請輸入你的問題。</div>',
    '</div>',
    '<div class="wc-inputbar">',
    '  <input type="text" name="wc-query" placeholder="輸入你的問題…" autocomplete="off">',
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

  /* ---------- 輕量 markdown 渲染（先 escape HTML 防 XSS，再轉語法） ---------- */
  function escapeHtml(text) {
    return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function renderInline(text) {
    // 先保護 inline code（後續 regex 不影響 code 內容）
    var blocks = [];
    text = text.replace(/`([^`]+)`/g, function (m, c) {
      blocks.push(c);
      return '\u0000' + (blocks.length - 1) + '\u0000';
    });
    // 連結：只允許 http/https
    text = text.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, function (m, label, url) {
      var safe = /^https?:\/\//i.test(url) ? url : '#';
      return '<a href="' + safe + '" target="_blank" rel="noopener">' + label + '</a>';
    });
    // 粗體 → 斜體（順序：粗體先，避免 **x** 被斜體吃掉）
    text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    // 還原 inline code
    text = text.replace(/\u0000(\d+)\u0000/g, function (m, i) {
      return '<code>' + blocks[parseInt(i, 10)] + '</code>';
    });
    return text;
  }

  function renderMarkdown(text) {
    var escaped = escapeHtml(text);
    var lines = escaped.split('\n');
    var html = [];
    var listType = null;   // 'ul' | 'ol' | null
    var paragraph = null;

    function closeList() {
      if (listType) { html.push('</' + listType + '>'); listType = null; }
    }
    function closeParagraph() {
      if (paragraph) { html.push('<p>' + paragraph + '</p>'); paragraph = null; }
    }

    for (var i = 0; i < lines.length; i++) {
      var trimmed = lines[i].trim();
      if (!trimmed) { closeList(); closeParagraph(); continue; }
      // 標題 # ~ ######
      var h = /^(#{1,6})\s+(.*)$/.exec(trimmed);
      if (h) {
        closeList(); closeParagraph();
        var level = h[1].length;
        html.push('<h' + level + '>' + renderInline(h[2]) + '</h' + level + '>');
        continue;
      }
      // 引用（escape 後 &gt;）
      var q = /^&gt;\s?(.*)$/.exec(trimmed);
      if (q) {
        closeList(); closeParagraph();
        html.push('<blockquote>' + renderInline(q[1]) + '</blockquote>');
        continue;
      }
      // 無序列表
      var ul = /^[*\-]\s+(.*)$/.exec(trimmed);
      if (ul) {
        closeParagraph();
        if (listType !== 'ul') { closeList(); html.push('<ul>'); listType = 'ul'; }
        html.push('<li>' + renderInline(ul[1]) + '</li>');
        continue;
      }
      // 有序列表
      var ol = /^\d+\.\s+(.*)$/.exec(trimmed);
      if (ol) {
        closeParagraph();
        if (listType !== 'ol') { closeList(); html.push('<ol>'); listType = 'ol'; }
        html.push('<li>' + renderInline(ol[1]) + '</li>');
        continue;
      }
      // 一般文字：空行隔段落，同段落內以 <br> 接續
      closeList();
      if (paragraph) { paragraph += '<br>' + renderInline(trimmed); }
      else { paragraph = renderInline(trimmed); }
    }
    closeList(); closeParagraph();
    return html.join('');
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
      var resp = await streamChat({ query: query, thread_id: threadId });
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
            respEl.innerHTML = renderMarkdown(ev.response);   // markdown 渲染（串流期間維持純文字）
            threadId = ev.thread_id;   // 記住，續問記得上下文
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
  }

  /* ---------- 公開 API（供 Chrome Extension content.js 呼叫） ---------- */
  window.WebsiteCopilotWidget = { mount: mount };

  /* ---------- 網頁版自動掛載（<script> 載入時） ----------
   * content script 環境（M4b）的 document.currentScript 為 null，不會自動掛載，
   * 由 content.js 顯式呼叫 WebsiteCopilotWidget.mount({ streamChat: proxy })。
   */
  if (document.currentScript) {
    var autoEndpoint = document.currentScript.dataset.endpoint || 'http://localhost:8000';
    mount({ endpoint: autoEndpoint });
  }
})();
