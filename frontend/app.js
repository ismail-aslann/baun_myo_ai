'use strict';

(() => {
  const STORE_KEY = 'baun_chats_v2';
  const MAX_SESSIONS = 50;
  const MAX_LEN = 2000;
  const $ = (id) => document.getElementById(id);
  const mobileMq = window.matchMedia('(max-width: 860px)');

  const els = {
    root: document.documentElement, main: $('main'),
    sidebar: $('sidebar'), backdrop: $('backdrop'), history: $('history'), search: $('search'),
    msgs: $('msgs'), scroller: $('scroller'), toBottom: $('to-bottom'),
    input: $('input'), form: $('composer'), send: $('send-btn'), counter: $('counter'),
    title: $('chat-title'), status: $('status'), statusText: $('status-text'),
    clear: $('clear-btn'), theme: $('theme-btn'), announcer: $('announcer'),
  };

  // ---------- storage (localStorage kapalı olabilir) ----------
  function load() {
    try {
      const data = JSON.parse(localStorage.getItem(STORE_KEY) || '[]');
      if (!Array.isArray(data)) return [];
      return data
        .filter((s) => s && typeof s.id === 'string' && Array.isArray(s.messages))
        .map((s) => ({ ...s, title: String(s.title || 'Sohbet'), updated: Number(s.updated) || 0 }));
    } catch (e) { return []; }
  }
  function persist() {
    try {
      const keep = [...sessions].sort((a, b) => b.updated - a.updated).slice(0, MAX_SESSIONS);
      localStorage.setItem(STORE_KEY, JSON.stringify(keep));
    } catch (e) { /* kota dolu veya kapalı: yoksay */ }
  }

  let sessions = load();
  let current = null;      // aktif oturum
  let controller = null;   // aktif isteğin AbortController'ı

  // ---------- helpers ----------
  const icon = (name) => `<svg aria-hidden="true"><use href="#i-${name}"/></svg>`;
  const escapeHtml = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  function renderMarkdown(text) {
    if (!(window.marked && window.DOMPurify)) return escapeHtml(text).replace(/\n/g, '<br>');
    const html = window.marked.parse(text, { breaks: true, gfm: true });
    const clean = window.DOMPurify.sanitize(html, {
      FORBID_TAGS: ['img', 'style', 'form', 'input', 'button', 'iframe', 'video', 'audio', 'svg'],
      FORBID_ATTR: ['style'],
    });
    const tpl = document.createElement('template');
    tpl.innerHTML = clean;
    tpl.content.querySelectorAll('a').forEach((a) => { a.target = '_blank'; a.rel = 'noopener noreferrer'; });
    tpl.content.querySelectorAll('table').forEach((t) => {
      const wrap = document.createElement('div');
      wrap.className = 'table-wrap';
      t.replaceWith(wrap); wrap.appendChild(t);
    });
    return tpl.innerHTML;
  }

  const isMobile = () => mobileMq.matches;
  const distanceFromBottom = () => els.scroller.scrollHeight - els.scroller.scrollTop - els.scroller.clientHeight;
  function scrollEnd(force) {
    if (force || distanceFromBottom() < 140) els.scroller.scrollTop = els.scroller.scrollHeight;
  }
  els.scroller.addEventListener('scroll', () => {
    els.toBottom.hidden = els.main.classList.contains('empty') || distanceFromBottom() < 200;
  }, { passive: true });
  els.toBottom.addEventListener('click', () => {
    els.scroller.scrollTo({ top: els.scroller.scrollHeight, behavior: 'smooth' });
  });

  function setEmpty(empty) {
    els.main.classList.toggle('empty', empty);
    if (empty) els.toBottom.hidden = true;
  }

  // ---------- sidebar ----------
  function setDrawer(open) {
    els.sidebar.classList.toggle('open', open);
    els.backdrop.hidden = !open;
  }
  function setCollapsed(collapsed) {
    els.root.classList.toggle('sb-collapsed', collapsed);
    try { localStorage.setItem('baun_sb', collapsed ? 'collapsed' : 'open'); } catch (e) { /* yoksay */ }
  }
  $('open-sidebar').addEventListener('click', () => (isMobile() ? setDrawer(true) : setCollapsed(false)));
  $('collapse-btn').addEventListener('click', () => (isMobile() ? setDrawer(false) : setCollapsed(true)));
  els.backdrop.addEventListener('click', () => setDrawer(false));
  mobileMq.addEventListener('change', () => setDrawer(false));

  function groupLabel(ts) {
    if (!ts) return 'Daha eski';
    const day = 864e5;
    const startToday = new Date(); startToday.setHours(0, 0, 0, 0);
    const t = startToday.getTime();
    if (ts >= t) return 'Bugün';
    if (ts >= t - day) return 'Dün';
    if (ts >= t - 7 * day) return 'Son 7 gün';
    if (ts >= t - 30 * day) return 'Son 30 gün';
    return 'Daha eski';
  }

  function renderHistory() {
    const q = els.search.value.trim().toLocaleLowerCase('tr');
    const list = [...sessions]
      .sort((a, b) => b.updated - a.updated)
      .filter((s) => !q || s.title.toLocaleLowerCase('tr').includes(q)
        || s.messages.some((m) => String(m.content).toLocaleLowerCase('tr').includes(q)));

    if (!list.length) {
      els.history.innerHTML = q
        ? `<div class="h-empty">${icon('search')}<span>“${escapeHtml(els.search.value.trim())}” için sonuç yok</span></div>`
        : `<div class="h-empty">${icon('chat')}<span>Henüz sohbet yok.<br>İlk sorunu sor!</span></div>`;
      return;
    }
    let html = '';
    let lastGroup = '';
    for (const s of list) {
      const g = groupLabel(s.updated);
      if (g !== lastGroup) { html += `<div class="h-group">${g}</div>`; lastGroup = g; }
      html += `
        <div class="h-item ${current && s.id === current.id ? 'active' : ''}" data-id="${escapeHtml(s.id)}">
          <button class="h-open" title="${escapeHtml(s.title)}">${escapeHtml(s.title)}</button>
          <button class="h-del" aria-label="Sohbeti sil" title="Sohbeti sil">${icon('trash')}</button>
        </div>`;
    }
    els.history.innerHTML = html;
  }
  els.search.addEventListener('input', renderHistory);

  els.history.addEventListener('click', (e) => {
    const item = e.target.closest('.h-item');
    if (!item) return;
    const id = item.dataset.id;
    if (e.target.closest('.h-del')) {
      if (current && current.id === id) newChat({ focus: false });
      sessions = sessions.filter((s) => s.id !== id);
      persist(); renderHistory();
      return;
    }
    openSession(id);
    setDrawer(false);
  });

  let clearArmed = null;
  function resetClear() {
    clearTimeout(clearArmed); clearArmed = null;
    els.clear.classList.remove('confirm');
    els.clear.querySelector('span').textContent = 'Tüm geçmişi sil';
  }
  els.clear.addEventListener('click', () => {
    if (!clearArmed) {
      els.clear.classList.add('confirm');
      els.clear.querySelector('span').textContent = 'Emin misin? Tekrar bas';
      clearArmed = setTimeout(resetClear, 3000);
      return;
    }
    resetClear();
    stopStreaming();
    sessions = []; persist(); newChat({ focus: false });
  });

  // ---------- messages ----------
  function messageEl(m) {
    const div = document.createElement('div');
    div.className = `msg ${m.role}${m.error ? ' error' : ''}`;
    if (m.role === 'user') {
      div.innerHTML = '<div class="bubble"></div>';
      div.querySelector('.bubble').textContent = m.content;
    } else {
      div.innerHTML = `<div class="av">${icon('cap')}</div><div class="body"><div class="bubble"></div><div class="tools"></div></div>`;
      setAssistantContent(div, m.content, !m.error);
    }
    return div;
  }

  function setAssistantContent(div, text, withTools) {
    div.querySelector('.bubble').innerHTML = renderMarkdown(text);
    const tools = div.querySelector('.tools');
    tools.innerHTML = withTools && text ? `<button class="tool copy">${icon('copy')}<span>Kopyala</span></button>` : '';
    const btn = tools.querySelector('.copy');
    if (!btn) return;
    btn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(text);
        btn.innerHTML = `${icon('check')}<span>Kopyalandı</span>`;
        setTimeout(() => { btn.innerHTML = `${icon('copy')}<span>Kopyala</span>`; }, 1500);
      } catch (e) { /* pano izni yok */ }
    });
  }

  function renderMessages() {
    els.msgs.innerHTML = '';
    const list = current ? current.messages : [];
    list.forEach((m) => els.msgs.appendChild(messageEl(m)));
    setEmpty(list.length === 0);
    els.title.textContent = current ? current.title : 'BAÜN MYO Asistan';
    document.title = current ? `${current.title} · BAÜN MYO Asistan` : 'BAÜN MYO Asistan';
    if (list.length) scrollEnd(true); else els.scroller.scrollTop = 0;
  }

  function openSession(id) {
    if (controller) stopStreaming();
    current = sessions.find((s) => s.id === id) || null;
    renderMessages(); renderHistory();
  }

  function newChat({ focus = true } = {}) {
    if (controller) stopStreaming();
    current = null;
    renderMessages(); renderHistory();
    if (focus && !isMobile()) els.input.focus();
  }
  $('new-chat-btn').addEventListener('click', () => { newChat(); setDrawer(false); });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') setDrawer(false);
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); newChat(); }
  });

  // ---------- composer ----------
  function autosize() {
    els.input.style.height = 'auto';
    els.input.style.height = Math.min(els.input.scrollHeight, 200) + 'px';
  }
  function updateComposer() {
    const len = els.input.value.length;
    els.counter.hidden = len < MAX_LEN * 0.75;
    els.counter.textContent = `${len} / ${MAX_LEN}`;
    els.counter.classList.toggle('warn', len >= MAX_LEN);
    if (!controller) els.send.disabled = !els.input.value.trim();
  }
  els.input.addEventListener('input', () => { autosize(); updateComposer(); });
  els.input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
      e.preventDefault();
      // Yanıt akarken Enter yanıtı kesmesin; durdurmak için yalnızca Durdur butonu.
      if (!controller) els.form.requestSubmit();
    }
  });
  els.form.addEventListener('submit', (e) => {
    e.preventDefault();
    if (controller) { stopStreaming(); return; }
    send(els.input.value);
  });
  $('chips').addEventListener('click', (e) => {
    const chip = e.target.closest('.chip');
    if (chip && !controller) send(chip.dataset.q);
  });

  function setBusy(busy) {
    els.send.classList.toggle('stop', busy);
    els.send.innerHTML = icon(busy ? 'stop' : 'up');
    els.send.setAttribute('aria-label', busy ? 'Durdur' : 'Gönder');
    els.send.title = busy ? 'Durdur' : 'Gönder';
    els.send.disabled = busy ? false : !els.input.value.trim();
  }
  function stopStreaming() { if (controller) controller.abort(); }

  function cleanHistory(messages) {
    // Hatalı yanıtları ve onlara ait soruları çıkar (art arda iki "user" olmasın).
    const out = [];
    messages.forEach((m, i) => {
      const next = messages[i + 1];
      if (m.error) return;
      if (m.role === 'user' && (!next || next.error)) return;
      out.push({ role: m.role, content: m.content });
    });
    return out;
  }

  async function send(raw) {
    const text = (raw || '').trim().slice(0, MAX_LEN);
    if (!text || controller) return;

    if (!current) {
      current = {
        id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
        title: text.length > 48 ? text.slice(0, 47) + '…' : text,
        updated: Date.now(),
        messages: [],
      };
      sessions.push(current);
    }
    const session = current;
    const history = cleanHistory(session.messages);

    const userMsg = { role: 'user', content: text };
    session.messages.push(userMsg);
    session.updated = Date.now();
    setEmpty(false);
    els.title.textContent = session.title;
    document.title = `${session.title} · BAÜN MYO Asistan`;
    els.msgs.appendChild(messageEl(userMsg));
    els.input.value = ''; autosize(); updateComposer();
    persist(); renderHistory();
    scrollEnd(true);

    const aDiv = document.createElement('div');
    aDiv.className = 'msg assistant streaming';
    aDiv.innerHTML = `<div class="av">${icon('cap')}</div><div class="body"><div class="bubble"><span class="thinking"><span class="shimmer">Düşünüyor…</span></span></div><div class="tools"></div></div>`;
    els.msgs.appendChild(aDiv);
    scrollEnd(true);

    controller = new AbortController();
    setBusy(true);
    let answer = '';
    let error = null;
    let aborted = false;
    let sawDone = false;
    let frame = 0;
    const paint = () => {
      frame = 0;
      if (current === session) { setAssistantContent(aDiv, answer, false); scrollEnd(); }
    };

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, history }),
        signal: controller.signal,
      });
      if (res.status === 429) throw new Error('Çok hızlı soru gönderdin, lütfen biraz bekle.');
      if (!res.ok || !res.body) throw new Error('Sunucuya şu an ulaşılamıyor, biraz sonra tekrar dene.');

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buf = '';
      let done = false;
      while (!done) {
        const { value, done: end } = await reader.read();
        if (end) break;
        buf += decoder.decode(value, { stream: true });
        let idx;
        while ((idx = buf.indexOf('\n\n')) !== -1) {
          const evt = buf.slice(0, idx); buf = buf.slice(idx + 2);
          const line = evt.split('\n').find((l) => l.startsWith('data: '));
          if (!line) continue;
          const payload = line.slice(6);
          if (payload === '[DONE]') { done = true; sawDone = true; break; }
          let obj;
          try { obj = JSON.parse(payload); } catch (e) { continue; }
          if (obj.error) { error = obj.error; continue; }
          if (obj.t) { answer += obj.t; if (!frame) frame = requestAnimationFrame(paint); }
        }
      }
    } catch (e) {
      if (e.name === 'AbortError') aborted = true;
      else error = navigator.onLine ? (e.message || 'Bağlantı hatası') : 'İnternet bağlantısı yok.';
    } finally {
      if (!sawDone && !aborted && !error) error = 'Bağlantı kesildi.';
      if (frame) cancelAnimationFrame(frame);
      controller = null;
      setBusy(false);
    }

    let final;
    if (answer) {
      final = { role: 'assistant', content: answer };
      if (error) final.content += `\n\n_(Yanıt yarıda kesildi: ${error})_`;
      else if (aborted) final.content += '\n\n_(Yanıt durduruldu.)_';
    } else if (error) {
      final = { role: 'assistant', content: `⚠️ ${error}`, error: true };
    } else {
      final = { role: 'assistant', content: '_(Yanıt durduruldu.)_', error: true };
    }
    session.messages.push(final);
    session.updated = Date.now();
    persist();
    els.announcer.textContent = final.error ? final.content : 'Yanıt hazır: ' + final.content.slice(0, 300);
    if (current === session) {
      aDiv.replaceWith(messageEl(final));
      scrollEnd();
      if (!isMobile()) els.input.focus();
    }
  }

  // ---------- theme ----------
  function currentTheme() {
    return els.root.dataset.theme || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  }
  function paintThemeIcon() { els.theme.innerHTML = icon(currentTheme() === 'dark' ? 'sun' : 'moon'); }
  els.theme.addEventListener('click', () => {
    const next = currentTheme() === 'dark' ? 'light' : 'dark';
    els.root.dataset.theme = next;
    try { localStorage.setItem('baun_theme', next); } catch (e) { /* yoksay */ }
    paintThemeIcon();
  });

  // ---------- health ----------
  async function checkHealth() {
    try {
      const h = await (await fetch('/api/health')).json();
      els.status.className = 'pill ' + (h.key_configured ? 'ok' : 'err');
      els.statusText.textContent = h.key_configured ? 'Çevrimiçi' : 'API anahtarı eksik';
    } catch (e) {
      els.status.className = 'pill err';
      els.statusText.textContent = 'Sunucuya ulaşılamıyor';
    }
  }

  paintThemeIcon();
  renderHistory();
  renderMessages();
  checkHealth();
  if (!isMobile()) els.input.focus();
})();
