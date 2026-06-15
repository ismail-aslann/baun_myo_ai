let sessions = JSON.parse(localStorage.getItem('baun_v7') || '[]');
let cid = null, cmsgs = [], busy = false;

const U_AV = `<i class="fa-solid fa-user"></i>`;
const A_AV = `<i class="fa-solid fa-robot"></i>`;

function save() { localStorage.setItem('baun_v7', JSON.stringify(sessions)) }
function getSess(id) { return sessions.find(s => s.id === id) }
function mkSess(txt) {
    const id = Date.now().toString();
    sessions.push({ id, title: (txt || 'Sohbet').slice(0, 30), messages: [] });
    save(); return id;
}

function scrollEnd() { 
    const w = document.querySelector('.msgs-wrapper'); 
    if(w) w.scrollTop = w.scrollHeight; 
}
function showWelcome(v) { 
    document.getElementById('welcome-screen').style.display = v ? 'flex' : 'none'; 
}

function renderHistory() {
    const el = document.getElementById('chat-history-list');
    if (!sessions.length) { 
        el.innerHTML = '<div class="h-empty"><i class="fa-regular fa-comment-dots"></i><span>Henüz sohbet yok</span></div>'; 
        return; 
    }
    el.innerHTML = [...sessions].reverse().map(s => `
        <button class="h-item ${s.id === cid ? 'active' : ''}" onclick="loadSess('${s.id}')">
            <i class="fa-regular fa-message"></i>
            <span style="overflow:hidden;text-overflow:ellipsis">${s.title}</span>
        </button>`).join('');
}

function buildBubble(m) {
    const u = m.role === 'user';
    const txt = (m.content || '').replace(/\n/g, '<br>');
    return `<div class="msg ${u ? 'user' : 'assistant'}"><div class="av">${u ? U_AV : A_AV}</div><div class="bubble">${txt}</div></div>`;
}

function addBubble(m) {
    const w = document.getElementById('chat-messages');
    const d = document.createElement('div');
    d.innerHTML = buildBubble(m);
    w.appendChild(d.firstElementChild);
    scrollEnd();
}

function renderMsgs(arr) {
    const w = document.getElementById('chat-messages');
    w.innerHTML = '';
    arr.forEach(m => addBubble(m));
    scrollEnd();
}

function showTyping() {
    const w = document.getElementById('chat-messages');
    const d = document.createElement('div');
    d.className = 'msg assistant'; d.id = 'typing';
    d.innerHTML = `<div class="av">${A_AV}</div><div class="bubble typing-bub"><div class="dots"><span></span><span></span><span></span></div></div>`;
    w.appendChild(d); scrollEnd();
}

function hideTyping() { const e = document.getElementById('typing'); if (e) e.remove() }

function loadSess(id) {
    cid = id; const s = getSess(id);
    cmsgs = s ? [...s.messages] : [];
    renderMsgs(cmsgs); showWelcome(cmsgs.length === 0); renderHistory();
}

async function send(txt) {
    if (busy) return;
    txt = txt.trim(); if (!txt) return;
    if (!cid) cid = mkSess(txt);

    const um = { role: 'user', content: txt };
    cmsgs.push(um); showWelcome(false); addBubble(um);

    const inp = document.getElementById('chat-input');
    inp.value = '';
    busy = true; showTyping();

    try {
        const hist = cmsgs.slice(0, -1).map(m => ({ role: m.role, content: m.content || '' }));
        const body = { message: txt, history: hist };

        // CANLI URL BURADA
        const res = await fetch('https://baun-myo-ai.onrender.com/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        hideTyping(); busy = false;
        const am = { role: 'assistant', content: data.response || '(Boş yanıt)' };
        cmsgs.push(am); addBubble(am);
    } catch (e) {
        hideTyping(); busy = false;
        const em = { role: 'assistant', content: `Bağlantı hatası: ${e.message}` };
        cmsgs.push(em); addBubble(em);
    }
    const s = getSess(cid);
    if (s) { s.messages = [...cmsgs]; save() }
    renderHistory();
}

let sbOpen = window.innerWidth >= 768;
document.getElementById('sidebar-toggle').onclick = () => {
    sbOpen = !sbOpen; 
    const sb = document.getElementById('sidebar');
    if(sbOpen) {
        sb.style.transform = 'translateX(0)';
        sb.style.width = 'var(--sidebar-width)';
    } else {
        sb.style.transform = 'translateX(-100%)';
        sb.style.width = '0';
    }
};

document.getElementById('new-chat-btn').onclick = () => {
    cid = null; cmsgs = []; renderMsgs([]); showWelcome(true); renderHistory();
};

document.getElementById('clear-history-btn').onclick = () => {
    sessions = []; save(); cid = null; cmsgs = []; renderMsgs([]); showWelcome(true); renderHistory();
};

document.addEventListener('click', e => {
    const chip = e.target.closest('.chip');
    if (chip) send(chip.innerText);
});

document.getElementById('send-btn').onclick = () => send(document.getElementById('chat-input').value);

document.getElementById('chat-input').addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { 
        e.preventDefault(); 
        send(document.getElementById('chat-input').value);
    }
});

renderHistory(); showWelcome(true);
if (window.innerWidth < 768) {
    document.getElementById('sidebar').style.transform = 'translateX(-100%)';
}