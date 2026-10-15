import {getFirebase, restoredUser} from './firebase-client.js';
import {GoogleMic, BrowserMic} from './mic-recorder.js';

const $ = (selector) => document.querySelector(selector);
let auth, sdk, user, config, active = null, sessions = [], pending = null;
let busy = false, phase = 'idle', identityEpoch = 0;
let actionResolve = null;
let guestQuota = null;
let micMode = null, recorder = null, micTurn = 0, transcriptAbort = null;
const loginURL = '/?login=1';

function notice(text = '', retry = false) {
  $('#chat-notice-text').textContent = text;
  $('#chat-notice').hidden = !text;
  $('#retry-send').hidden = !retry;
}
function scrollBottom() { $('#chat-scroll').scrollTop = $('#chat-scroll').scrollHeight; }
function updateControls() {
  const listening = ['starting-mic', 'listening', 'transcribing'].includes(phase);
  const exhausted = config?.is_guest && guestQuota?.remaining === 0;
  $('#send-message').disabled = exhausted || busy || listening || !config?.configured || !$('#message-input').value.trim();
  $('#message-input').disabled = busy || listening;
  $('#start-chat').disabled = busy;
  $('#microphone').disabled = busy || !micMode || phase === 'starting-mic' || phase === 'transcribing';
  $('#microphone').classList.toggle('recording', phase === 'listening');
  $('#microphone').setAttribute('aria-label', phase === 'listening' ? 'Dừng mic và nhận diện' : 'Nói bằng micro');
  $('#mic-status').hidden = !listening;
  $('#thinking').hidden = !busy || phase !== 'thinking';
  $('#guest-banner').hidden = !config?.is_guest;
  $('#guest-banner').classList.toggle('limit-reached',Boolean(exhausted));
  $('#guest-login').setAttribute('aria-disabled',String(busy || listening));
  if(config?.is_guest) $('#guest-quota-text').textContent = exhausted ? 'Bạn đã dùng hết 8 câu hỏi miễn phí. Đăng nhập để tiếp tục cuộc trò chuyện.' : `Bạn đang dùng thử · còn ${guestQuota?.remaining ?? 8}/8 câu hỏi miễn phí.`;
  $('#connection-status').textContent = phase === 'thinking' ? 'Đang suy nghĩ' : phase === 'starting-mic' ? 'Đang mở mic' : phase === 'listening' ? 'Đang nghe' : phase === 'transcribing' ? 'Đang nhận diện' : config?.mode === 'demo' ? 'Bản demo' : config?.configured ? 'Sẵn sàng' : 'Chưa cấu hình';
}
async function api(path, options = {}, retried = false) {
  if (!user || auth.currentUser?.uid !== user.uid) throw new Error('Phiên đăng nhập đã thay đổi. Vui lòng đăng nhập lại.');
  const owner = user.uid;
  const token = await user.getIdToken(retried);
  if (auth.currentUser?.uid !== owner) throw new Error('Phiên đăng nhập đã thay đổi.');
  const headers = {...options.headers, Authorization: `Bearer ${token}`};
  if (typeof options.body === 'string') headers['Content-Type'] = 'application/json';
  const response = await fetch(path, {...options, headers, cache: 'no-store', signal: options.signal || AbortSignal.timeout(100000)});
  if (auth.currentUser?.uid !== owner) throw new Error('Phiên đăng nhập đã thay đổi.');
  if (response.status === 401 && !retried) return api(path, options, true);
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const error = new Error(typeof data.detail === 'string' ? data.detail : data.detail?.message || 'Chưa thực hiện được. Bạn kiểm tra kết nối rồi thử lại nhé.');
    error.code = data.detail?.code;
    if(error.code==='GUEST_LIMIT_REACHED') guestQuota={limit:8,used_questions:8,remaining:0};
    error.status = response.status;
    if (response.status === 401) {
      clearPrivateUI();
      location.replace(loginURL);
    }
    throw error;
  }
  return response;
}
async function jsonAPI(path, options = {}) {
  const epoch = identityEpoch;
  const data = await (await api(path, options)).json();
  if (epoch !== identityEpoch) throw new Error('Phiên đăng nhập đã thay đổi.');
  return data;
}
function failure(error) {
  return ['TimeoutError', 'AbortError'].includes(error.name) ? 'Phản hồi hơi lâu. Bạn có thể thử lại nhé.' : error.message || 'Chưa kết nối được. Bạn thử lại nhé.';
}
function storageKey() { return `laban.advisor.${user.uid}`; }
function rememberActive() {
  try { if (active) sessionStorage.setItem(storageKey(), active.id); else sessionStorage.removeItem(storageKey()); } catch { /* Tab riêng tư có thể chặn storage. */ }
}
function setSidebar(open) {
  const mobile = window.innerWidth <= 760;
  $('#chat-sidebar').classList.toggle('open', open);
  $('#drawer-backdrop').hidden = !open;
  $('#open-sidebar').setAttribute('aria-expanded', String(open));
  $('#chat-main').inert = mobile && open;
  $('#chat-sidebar').inert = mobile && !open;
  if (open) $('#close-sidebar').focus(); else $('#open-sidebar').focus();
}
function renderHistory() {
  const list = $('#history-list'); list.replaceChildren();
  const query = $('#history-search').value.trim().toLocaleLowerCase('vi');
  const rows = sessions.filter((item) => item.title.toLocaleLowerCase('vi').includes(query));
  if (!rows.length) {
    const empty = document.createElement('p'); empty.className = 'history-empty';
    empty.textContent = query ? 'Chưa tìm thấy cuộc trò chuyện.' : 'Hành trình của bạn bắt đầu từ một câu hỏi nhỏ. Những cuộc trò chuyện sẽ xuất hiện ở đây.';
    list.append(empty);
  }
  for (const item of rows) {
    const row = document.createElement('div'); row.className = 'history-item'; row.classList.toggle('active', item.id === active?.id);
    const open = document.createElement('button'); open.className = 'history-open';
    const title = document.createElement('strong'); title.textContent = item.title;
    const caption = document.createElement('small'); caption.textContent = item.remember ? new Date(item.updated_at).toLocaleDateString('vi-VN', {day:'numeric', month:'short'}) : 'Phiên tạm · không lưu lâu dài';
    open.append(title, caption); open.addEventListener('click', () => loadSession(item.id));
    const rename = document.createElement('button'); rename.className = 'icon-button'; rename.textContent = '✎'; rename.setAttribute('aria-label', `Đổi tên: ${item.title}`);
    rename.addEventListener('click', () => renameSession(item));
    const remove = document.createElement('button'); remove.className = 'icon-button'; remove.textContent = '×'; remove.setAttribute('aria-label', `Xóa: ${item.title}`);
    remove.addEventListener('click', () => deleteSession(item));
    row.append(open, rename, remove); list.append(row);
  }
}
async function refreshHistory() {
  const epoch = identityEpoch;
  const data = await jsonAPI('/api/ai/sessions');
  if (epoch !== identityEpoch) return;
  sessions = data.items; renderHistory();
}
function markdown(element, content) {
  if (window.marked && window.DOMPurify) {
    element.innerHTML = window.DOMPurify.sanitize(window.marked.parse(content, {breaks:true}), {
      ALLOWED_TAGS: ['p','br','strong','em','ul','ol','li','blockquote','h2','h3','h4','pre','code','hr','del','a'],
      ALLOWED_ATTR: ['href','title'], ALLOW_DATA_ATTR: false
    });
    element.querySelectorAll('a').forEach((link) => { link.target = '_blank'; link.rel = 'noopener noreferrer'; });
  } else { element.textContent = content; element.style.whiteSpace = 'pre-wrap'; }
}
function plainMessage(message) {
  return message.content + (message.recommendations || []).map((career, i) =>
    `\n\n${i+1}. ${career.name}\n${career.reason}\nKỹ năng: ${career.skills}\nThách thức: ${career.challenge}\nBước thử nhỏ: ${career.next_step}`).join('');
}
function messageRow(message) {
  const row = document.createElement('article'); row.className = `message-row ${message.role}`;
  if (message.role === 'assistant') {
    const image = document.createElement('img'); image.src = '/assets/compass.svg'; image.alt = ''; image.className = 'assistant-avatar'; row.append(image);
  }
  const body = document.createElement('div'); body.className = 'message-body';
  const label = document.createElement('span'); label.className = 'message-label'; label.textContent = message.role === 'assistant' ? `La Bàn AI${message.mode === 'demo' ? ' · Trả lời mẫu' : ''}` : 'Bạn';
  const bubble = document.createElement('div'); bubble.className = 'message-bubble';
  if (message.role === 'assistant') markdown(bubble, message.content); else bubble.textContent = message.content;
  if (message.recommendations?.length) {
    const cards = document.createElement('div'); cards.className = 'recommendations';
    for (const [index, career] of message.recommendations.entries()) {
      const card = document.createElement('section'); card.className = 'career-recommendation';
      const name = document.createElement('h3'); name.textContent = `${String(index+1).padStart(2,'0')} · ${career.name}`; card.append(name);
      for (const [key, title] of [['reason','Vì sao đáng khám phá'], ['skills','Kỹ năng'], ['challenge','Thách thức'], ['next_step','Bước thử nhỏ']]) {
        if (!career[key]) continue;
        const paragraph = document.createElement('p'); if (key === 'challenge') paragraph.className = 'challenge';
        const strong = document.createElement('strong'); strong.textContent = title + ': '; paragraph.append(strong, document.createTextNode(career[key])); card.append(paragraph);
      }
      cards.append(card);
    }
    bubble.append(cards);
  }
  body.append(label, bubble);
  if (message.role === 'assistant') {
    const actions = document.createElement('div'); actions.className = 'message-actions';
    const copy = document.createElement('button'); copy.textContent = '▣ Sao chép';
    copy.addEventListener('click', async () => {
      try { await navigator.clipboard.writeText(plainMessage(message)); copy.textContent = '✓ Đã sao chép'; setTimeout(() => { copy.textContent = '▣ Sao chép'; }, 1800); }
      catch { notice('Trình duyệt chưa cho phép sao chép. Bạn có thể chọn đoạn văn bản để sao chép.'); }
    });
    actions.append(copy);
    body.append(actions);
  }
  row.append(body); return row;
}
function renderMessages() {
  const list = $('#messages'); list.replaceChildren();
  $('#welcome').hidden = Boolean(active); list.hidden = !active;
  if (active) {
    for (const message of active.messages) list.append(messageRow(message));
    if (pending && pending.session_id === active.id && !active.messages.some((item) => item.request_id === pending.request_id)) list.append(messageRow({role:'user', content:pending.message}));
  }
  $('#session-note').textContent = active ? active.remember ? 'Lịch sử đã bật · Bạn có thể xóa bất cứ lúc nào.' : 'Phiên tạm · Không ghi nhớ cho lần đăng nhập sau.' : 'Một góc trò chuyện riêng, theo nhịp của bạn.';
  renderHistory();
  if (active) scrollBottom(); else $('#chat-scroll').scrollTop = 0;
}
async function createSession() {
  if (active) return active;
  const epoch = identityEpoch;
  const data = await jsonAPI('/api/ai/sessions', {method:'POST', body:JSON.stringify({remember:$('#remember-chat').checked})});
  if (epoch !== identityEpoch) throw new Error('Phiên đăng nhập đã thay đổi.');
  active = data.session; pending = null; rememberActive(); renderMessages();
  await refreshHistory();
  return active;
}
async function startChat(prompt = '') {
  if (busy) return;
  cancelMic();
  busy = true; updateControls(); notice();
  try {
    await createSession();
    if (prompt) { $('#message-input').value = prompt; resizeInput(); }
  } catch (error) { notice(failure(error)); }
  finally { busy = false; updateControls(); if (active) $('#message-input').focus(); }
}
async function loadSession(id) {
  if (busy) return notice('Đợi La Bàn trả lời xong rồi mở cuộc trò chuyện khác nhé.');
  cancelMic();
  notice(); pending = null; busy = true; updateControls();
  const epoch = identityEpoch;
  try {
    const data = await jsonAPI(`/api/ai/sessions/${id}`);
    if (epoch !== identityEpoch) return;
    active = data.session; rememberActive(); renderMessages();
    $('#message-input').value = ''; resizeInput();
    if (window.innerWidth <= 760) setSidebar(false);
  } catch (error) { notice(failure(error)); if (error.status === 404) await refreshHistory(); }
  finally { busy = false; updateControls(); }
}
function freshChat() {
  if (busy) return notice('Đợi La Bàn trả lời xong rồi bắt đầu cuộc trò chuyện mới nhé.');
  cancelMic();
  active = null; pending = null; rememberActive();
  $('#message-input').value = ''; $('#remember-chat').checked = false; notice(); renderMessages(); resizeInput(); updateControls();
  if (window.innerWidth <= 760) setSidebar(false);
}
async function send(retry = false) {
  if (busy || ['listening','transcribing','starting-mic'].includes(phase)) return;
  const text = retry && pending ? pending.message : $('#message-input').value.trim();
  if (!text || !config.configured) return;
  if(config.is_guest && guestQuota?.remaining===0 && !retry){notice('Bạn đã dùng hết 8 câu hỏi. Đăng nhập Google hoặc email để tiếp tục nhé.');updateControls();return;}
  if (text.length > 2000) return notice('Mỗi tin nhắn tối đa 2.000 ký tự nhé.');
  notice(); busy = true; phase = 'thinking'; updateControls();
  const epoch = identityEpoch;
  try {
    await createSession();
    if (!retry || !pending) pending = {session_id:active.id, request_id:crypto.randomUUID(), message:text};
    const request = {...pending}; renderMessages();
    $('#message-input').value = ''; resizeInput();
    const data = await jsonAPI('/api/ai/chat', {method:'POST', body:JSON.stringify(request)});
    if (epoch !== identityEpoch || active?.id !== request.session_id) return;
    active = data.session; pending = null; renderMessages();
    if(data.guest_quota) guestQuota=data.guest_quota;
    await refreshHistory().catch(() => notice('Câu trả lời đã có, nhưng danh sách lịch sử chưa tải lại được.'));
    busy = false; phase = 'idle'; updateControls();
  } catch (error) {
    if (epoch !== identityEpoch) return;
    notice(failure(error), Boolean(pending));
    // Giữ mã request khi thử lại để backend không tạo tin nhắn trùng.
  } finally {
    if (epoch === identityEpoch) { busy = false; phase = 'idle'; updateControls(); $('#message-input').focus(); }
  }
}
function resizeInput() { const input = $('#message-input'); input.style.height = 'auto'; input.style.height = `${Math.min(input.scrollHeight,130)}px`; updateControls(); }

function cancelMic() {
  micTurn++; transcriptAbort?.abort(); transcriptAbort = null;
  recorder?.stop(true); recorder = null;
  if (['starting-mic', 'listening', 'transcribing'].includes(phase)) phase = 'idle';
  updateControls();
}

async function beginMic() {
  if (busy || !micMode || phase === 'starting-mic' || phase === 'transcribing') return;
  if (phase === 'listening') { recorder?.stop(false); return; }
  const turn = ++micTurn, epoch = identityEpoch, before = $('#message-input').value.trim();
  const current = () => recorder === instance && turn === micTurn && epoch === identityEpoch;
  const finish = () => { recorder = null; phase = 'idle'; transcriptAbort = null; updateControls(); $('#message-input').focus(); };
  const putText = text => {
    const joined = [before, text].filter(Boolean).join(' ');
    $('#message-input').value = joined.slice(0, 2000); finish(); resizeInput();
    notice(joined.length > 2000 ? 'Văn bản đã đạt giới hạn 2.000 ký tự. Bạn kiểm tra và sửa trước khi gửi.' : 'Đã nhận diện tiếng Việt. Bạn kiểm tra và sửa lời nói trước khi bấm Gửi.');
  };
  const callbacks = {
    onStart() { if (current()) { phase = 'listening'; updateControls(); } },
    onStatus(text) { if (current()) $('#mic-status-text').textContent = text; },
    async onComplete(result) {
      if (!current()) return;
      if (typeof result === 'string') { putText(result); return; }
      phase = 'transcribing'; $('#mic-status-text').textContent = 'Đang chuyển lời nói thành chữ bằng Google…'; updateControls();
      const controller = new AbortController(); transcriptAbort = controller;
      try {
        const data = await jsonAPI('/api/voice/transcribe', {method:'POST', body:result, headers:{'Content-Type':'audio/wav'},
          signal:AbortSignal.any([controller.signal, AbortSignal.timeout(45000)])});
        if (current()) putText(data.transcript);
      } catch (error) {
        if (current()) {
          finish(); notice(failure(error));
          if ([502, 503].includes(error.status) && window.isSecureContext && (window.SpeechRecognition || window.webkitSpeechRecognition)) micMode = 'browser';
        }
      }
    },
    onEmpty() { if (current()) { finish(); notice('Mic chưa nghe thấy lời nói. Bạn thử lại hoặc gõ câu hỏi nhé.'); } },
    onError(error) { if (current()) { finish(); notice(error.name === 'NotAllowedError' ? 'Bạn chưa cho phép micro. Có thể bật quyền rồi thử lại.' : failure(error)); } }
  };
  const instance = micMode === 'google' ? new GoogleMic(callbacks) : new BrowserMic(callbacks);
  recorder = instance; phase = 'starting-mic'; $('#mic-status-text').textContent = 'Đang xin quyền micro…'; notice(); updateControls();
  try { await instance.start(); }
  catch (error) { if (current()) { finish(); notice(error.name === 'NotAllowedError' ? 'Bạn chưa cho phép micro. Có thể bật quyền rồi thử lại.' : failure(error)); } }
}

function askAction({title, description, value = null, confirm = 'Xác nhận'}) {
  $('#action-title').textContent = title; $('#action-description').textContent = description;
  $('#rename-label').hidden = value === null; $('#rename-input').hidden = value === null;
  $('#rename-input').required = value !== null; $('#rename-input').value = value || '';
  $('#confirm-action').textContent = confirm; $('#action-error').textContent = '';
  $('#action-dialog').showModal();
  if (value !== null) { $('#rename-input').focus(); $('#rename-input').select(); }
  return new Promise((resolve) => { actionResolve = resolve; });
}
async function renameSession(item) {
  if (busy) return;
  const title = await askAction({title:'Đặt tên cho cuộc trò chuyện', description:'Một cái tên giúp bạn dễ tìm lại hành trình của mình.', value:item.title, confirm:'Lưu tên'});
  if (!title) return;
  try {
    const data = await jsonAPI(`/api/ai/sessions/${item.id}`, {method:'PATCH', body:JSON.stringify({title})});
    if (active?.id === item.id) active.title = data.session.title;
    await refreshHistory();
  } catch (error) { notice(failure(error)); }
}
async function deleteSession(item) {
  if (busy) return;
  const confirmed = await askAction({title:'Xóa cuộc trò chuyện này?', description:'Tin nhắn và phần ghi nhớ của cuộc trò chuyện sẽ bị xóa. Bạn không thể khôi phục thao tác này.', confirm:'Xóa cuộc trò chuyện'});
  if (!confirmed) return;
  try {
    await api(`/api/ai/sessions/${item.id}`, {method:'DELETE'});
    if (active?.id === item.id) freshChat();
    await refreshHistory();
  } catch (error) { notice(failure(error)); }
}
async function openProfile() {
  try {
    const data = await jsonAPI('/api/ai/career-profile'); const content = $('#profile-content'); content.replaceChildren();
    for (const [key, label] of [['interests','Sở thích'], ['strengths','Điểm mạnh tự chia sẻ'], ['growth_skills','Kỹ năng muốn phát triển'], ['careers','Nghề bạn quan tâm']]) {
      const heading = document.createElement('h3'); heading.textContent = label; content.append(heading);
      const values = data.profile[key];
      if (!values.length) { const empty = document.createElement('p'); empty.className = 'profile-empty'; empty.textContent = 'Chưa có điều bạn chọn ghi nhớ.'; content.append(empty); }
      else { const tags = document.createElement('div'); tags.className = 'profile-tags'; for (const value of values) { const tag = document.createElement('span'); tag.textContent = value; tags.append(tag); } content.append(tags); }
    }
    $('#profile-dialog').showModal();
  } catch (error) { notice(failure(error)); }
}

function clearPrivateUI() {
  identityEpoch++; cancelMic();
  active = null; pending = null; sessions = []; busy = false;
  $('#messages').replaceChildren(); $('#history-list').replaceChildren(); $('#profile-content').replaceChildren();
  $('#message-input').value = ''; $('#user-name').textContent = ''; $('#user-initial').textContent = '';
  document.querySelectorAll('dialog[open]').forEach((dialog) => dialog.close());
  $('#chat-app').hidden = true; $('#auth-loading').hidden = false;
}

$('#new-chat').addEventListener('click', freshChat);
$('#end-session').addEventListener('click', freshChat);
$('#history-search').addEventListener('input', renderHistory);
$('#open-sidebar').addEventListener('click', () => setSidebar(true));
$('#close-sidebar').addEventListener('click', () => setSidebar(false));
$('#drawer-backdrop').addEventListener('click', () => setSidebar(false));
document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && $('#chat-sidebar').classList.contains('open')) setSidebar(false); });
$('#chat-sidebar').addEventListener('keydown', (event) => {
  if (event.key !== 'Tab' || window.innerWidth > 760 || !$('#chat-sidebar').classList.contains('open')) return;
  const buttons = [...$('#chat-sidebar').querySelectorAll('button:not(:disabled), a, input')].filter((element) => element.getClientRects().length);
  const first = buttons[0], last = buttons.at(-1);
  if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
  if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
});
matchMedia('(max-width:760px)').addEventListener('change', () => setSidebar(false));
$('#start-chat').addEventListener('click', () => startChat());
document.querySelectorAll('[data-prompt]').forEach((button) => button.addEventListener('click', () => startChat(button.dataset.prompt)));
$('#message-input').addEventListener('input', resizeInput);
$('#message-input').addEventListener('keydown', (event) => { if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) { event.preventDefault(); send(); } });
$('#message-form').addEventListener('submit', (event) => { event.preventDefault(); send(); });
$('#retry-send').addEventListener('click', () => send(true));
$('#microphone').addEventListener('click', beginMic);
$('#cancel-mic').addEventListener('click', cancelMic);
$('#open-profile').addEventListener('click', openProfile);
document.querySelectorAll('[data-close-dialog]').forEach((button) => button.addEventListener('click', () => button.closest('dialog').close()));
$('#action-dialog').addEventListener('close', () => { if (actionResolve) { actionResolve(false); actionResolve = null; } });
$('#action-form').addEventListener('submit', (event) => {
  event.preventDefault(); const value = $('#rename-input').hidden ? true : $('#rename-input').value.trim();
  if (!value) { $('#action-error').textContent = 'Bạn nhập tên cuộc trò chuyện nhé.'; return; }
  const resolve = actionResolve; actionResolve = null; $('#action-dialog').close(); resolve?.(value);
});
$('#delete-all-data').addEventListener('click', async () => {
  if (busy) return;
  $('#profile-dialog').close();
  const confirmed = await askAction({title:'Xóa lịch sử và ghi nhớ?', description:'Toàn bộ cuộc trò chuyện và hồ sơ hướng nghiệp của tài khoản này sẽ bị xóa khỏi máy chủ hiện tại.', confirm:'Xóa toàn bộ'});
  if (!confirmed) return;
  try { await api('/api/ai/data', {method:'DELETE'}); freshChat(); await refreshHistory(); notice('Đã xóa lịch sử và dữ liệu ghi nhớ của bạn.'); }
  catch (error) { notice(failure(error)); }
});
$('#logout').addEventListener('click', async () => {
  try { await sdk.signOut(auth); clearPrivateUI(); location.replace('/'); }
  catch (error) { notice(failure(error)); }
});

async function initialize() {
  try {
    ({auth, sdk} = await getFirebase());
    user = await restoredUser(auth, sdk);
    if (!user) {
      try {user=(await sdk.signInAnonymously(auth)).user;}
      catch {throw new Error('Chưa mở được phiên khách. Bạn có thể đăng nhập Google/email; nhóm dự án cần bật Anonymous trong Firebase.');}
    }
    const owner = user.uid;
    sdk.onAuthStateChanged(auth, (current) => { if (!current || current.uid !== owner) { clearPrivateUI(); location.replace(loginURL); } });
    await jsonAPI('/api/auth/me');
    config = await jsonAPI('/api/ai/config');
    guestQuota = config.guest_quota;
    micMode = config.microphone?.google && window.isSecureContext && navigator.mediaDevices?.getUserMedia && window.AudioContext ? 'google'
      : window.isSecureContext && (window.SpeechRecognition || window.webkitSpeechRecognition) ? 'browser' : null;
    $('#microphone').title = micMode === 'google' ? 'Nói tiếng Việt bằng Google Speech-to-Text; tự dừng sau 3 giây im lặng'
      : micMode === 'browser' ? 'Nói tiếng Việt bằng nhận diện của trình duyệt; tự dừng sau 3 giây im lặng' : 'Mic cần Chrome trên localhost hoặc HTTPS.';
    $('#user-name').textContent = config.is_guest ? 'Khách dùng thử' : user.displayName || 'Bạn';
    $('#user-initial').textContent = config.is_guest ? 'K' : [...(user.displayName || 'Bạn')][0].toLocaleUpperCase('vi');
    const banner = [];
    if (config.mode === 'demo') banner.push('BẢN DEMO · Câu trả lời mẫu để thử giao diện. Chưa kết nối DeepSeek và chưa phân tích năng lực.');
    else if (!config.configured) banner.push('Tư vấn AI đang chờ cấu hình khóa DeepSeek.');
    if (micMode === 'browser') banner.push('Mic đang dùng nhận diện của trình duyệt. Google Speech-to-Text cần cấu hình Cloud trên máy chủ.');
    $('#mode-banner').hidden = !banner.length; $('#mode-banner').textContent = banner.join(' ');
    await refreshHistory();
    $('#auth-loading').hidden = true; $('#chat-app').hidden = false;
    setSidebar(false);
    let previous; try { previous = sessionStorage.getItem(storageKey()); } catch { /* Không bắt buộc storage. */ }
    if (previous && sessions.some((item) => item.id === previous)) await loadSession(previous);
    else renderMessages();
    const url = new URL(location.href);
    if (url.searchParams.get('start') === '1' || config.is_guest) {
      // Đăng nhập mở ngay phiên tạm; chỉ lưu lâu dài khi có lựa chọn đồng ý.
      if (!active) await startChat();
      if (active) {
        url.searchParams.delete('start');
        history.replaceState(null, '', url);
        $('#message-input').focus();
      }
    }
    updateControls();
  } catch (error) {
    $('#auth-loading p').textContent = failure(error);
    if (!$('#chat-app').hidden) notice(failure(error));
  }
}
initialize();
