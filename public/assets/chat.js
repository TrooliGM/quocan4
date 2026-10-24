import {getFirebase, restoredUser} from './firebase-client.js';
import {GoogleMic, BrowserMic} from './mic-recorder.js';
import {guestSession} from './ai-access.js';
import {chatLoginURL, saveDraft, loadDraft} from './chat-journey.js';
import {explorationQuestion} from './career-question.js';
import {storyQuestion} from './story-journey.js';

const $ = (selector) => document.querySelector(selector);
let auth, sdk, user, config, active = null, sessions = [], pending = null;
let busy = false, phase = 'idle', identityEpoch = 0;
let actionResolve = null;
let guestQuota = null;
let micMode = null, recorder = null, micTurn = 0, transcriptAbort = null;
const loginURL = () => chatLoginURL(selectedSession || active?.id);
let selectedSession=null, navigation=0, navigationAbort=null, loadingSession=null, creation=null, historyRevision=0;
const sessionCache=new Map(), CACHE_TTL=30000;
function cacheSession(row) {
  sessionCache.delete(row.id);sessionCache.set(row.id,{row:structuredClone(row),at:Date.now()});
  while(sessionCache.size>20)sessionCache.delete(sessionCache.keys().next().value);
}
function upsertSession(row) {
  const header={id:row.id,title:row.title,created_at:row.created_at,updated_at:row.updated_at,remember:row.remember};
  sessions=[header,...sessions.filter(s=>s.id!==row.id)].sort((a,b)=>b.updated_at.localeCompare(a.updated_at));
  historyRevision++;cacheSession(row);renderHistory();
}
function cachedSession(id) {
  const entry=sessionCache.get(id),header=sessions.find(s=>s.id===id);
  return entry && Date.now()-entry.at<CACHE_TTL && (!header || header.title===entry.row.title && header.updated_at===entry.row.updated_at) ? structuredClone(entry.row) : null;
}
let entryContext = null;
const analysisMessage = 'Hãy phân tích khảo sát của em, gợi ý khoảng 3 nhóm nghề cùng lý do, môn học, kỹ năng và trải nghiệm để thử.';
const surveyQuestions = [
  ['Em yêu thích lĩnh vực nào?', ['Em tò mò về máy tính và cách các ứng dụng hoạt động.', 'Em thích sáng tạo, thiết kế và thể hiện ý tưởng qua hình ảnh.', 'Em quan tâm đến việc giúp đỡ và chăm sóc người khác.', 'Em muốn hiểu cách kinh doanh và tổ chức công việc.', 'Em thích tìm hiểu thiên nhiên, môi trường và khoa học.', 'Em chưa rõ sở thích và muốn khám phá nhiều lĩnh vực.']],
  ['Em thích làm những hoạt động gì?', ['Em thích vẽ, làm đồ thủ công hoặc thử thiết kế một sản phẩm.', 'Em thích tìm hiểu một ứng dụng hoặc giải một câu đố.', 'Em thích lắng nghe, giải thích bài và giúp đỡ bạn bè.', 'Em thích chăm cây, quan sát động vật hoặc hoạt động ngoài trời.', 'Em thích tổ chức việc nhóm và trình bày ý tưởng.', 'Em chưa có hoạt động yêu thích rõ ràng, nhưng sẵn sàng thử.']],
  ['Em nhận thấy điểm mạnh của mình là gì?', ['Em thường kiên nhẫn thử lại khi chưa làm được một việc.', 'Em thích đặt câu hỏi và tìm cách giải thích vấn đề.', 'Em biết lắng nghe và cố gắng hiểu cảm xúc của người khác.', 'Em hay nghĩ ra cách làm hoặc ý tưởng khác nhau.', 'Em cố gắng giữ lời hẹn và hoàn thành phần việc của mình.', 'Em chưa nhận ra điểm mạnh và muốn tìm hiểu qua trải nghiệm.']],
  ['Em mong muốn công việc tương lai như thế nào?', ['Em mong công việc tạo ra điều có ích cho mọi người.', 'Em muốn có không gian sáng tạo và thử những ý tưởng mới.', 'Em mong một nhịp làm việc ổn định, cân bằng với cuộc sống.', 'Em muốn được học hỏi và khám phá những vấn đề mới.', 'Em thích làm việc cùng người khác và thấy kết quả cụ thể.', 'Em chưa có hình dung rõ và muốn hiểu nhiều môi trường làm việc.']],
  ['Em muốn AI tư vấn điều gì?', ['Em muốn biết những nhóm nghề nào đáng để mình khám phá.', 'Em muốn hiểu công việc thực tế, không chỉ tên của một nghề.', 'Em muốn biết môn học và kỹ năng có thể bắt đầu rèn luyện.', 'Em muốn tìm một hoạt động nhỏ, an toàn để thử sức.', 'Em muốn hiểu cả khó khăn và trách nhiệm của nghề.', 'Em chưa biết nên hỏi gì, hãy giúp em bắt đầu từng bước.']]
];
const surveyDrafts = new Map();
const preparedQuestions = new Set();
const needsSurvey = () => Boolean(active?.messages?.[0]?.survey_required && !active.messages[0].survey);
function renderSurvey() {
  const form = $('#career-survey'); form.hidden = !needsSurvey();
  $('#message-form').hidden = needsSurvey();
  if (!needsSurvey()) return;
  let draft = surveyDrafts.get(active.id);
  if (!draft) { draft = loadDraft(user.uid,active.id)?.survey || {step:0, answers:['','','','',''], address:'chị'}; surveyDrafts.set(active.id, draft); }
  const [question, suggestions] = surveyQuestions[draft.step];
  $('#survey-step').textContent = `Câu ${draft.step + 1} / 5`;
  $('#survey-progress').value = draft.step + 1;
  $('#survey-question').textContent = question;
  $('#survey-answer').value = draft.answers[draft.step];
  $('#survey-address').value = draft.address;
  $('#survey-back').disabled = draft.step === 0 || busy;
  $('#survey-next').textContent = draft.step === 4 ? 'Nhận gợi ý từ AI ↗' : 'Tiếp tục →';
  $('#survey-next').disabled = busy;
  const chips = $('#survey-suggestions'); chips.replaceChildren();
  for (const text of suggestions) {
    const chip = document.createElement('button'); chip.type = 'button'; chip.textContent = text;
    chip.addEventListener('click', () => {
      const input = $('#survey-answer');
      input.value = [input.value.trim(), text].filter(Boolean).join(', ').slice(0,400);
      draft.answers[draft.step] = input.value; persistJourney(); input.focus();
    }); chips.append(chip);
  }
}
$('#survey-answer').addEventListener('input', () => { if (active) { surveyDrafts.get(active.id).answers[surveyDrafts.get(active.id).step] = $('#survey-answer').value; persistJourney(); } });
$('#survey-address').addEventListener('change', () => { if (active) { surveyDrafts.get(active.id).address = $('#survey-address').value; persistJourney(); } });
$('#survey-back').addEventListener('click', () => { const draft = surveyDrafts.get(active.id); if (!busy && draft.step > 0) { draft.step--; persistJourney(); renderSurvey(); $('#survey-question').focus(); } });
$('#career-survey').addEventListener('submit', async event => {
  event.preventDefault(); if (busy || !active) return;
  const draft = surveyDrafts.get(active.id);
  draft.answers[draft.step] = $('#survey-answer').value.trim();
  if (!draft.answers[draft.step]) return $('#survey-answer').focus();
  if (draft.step < 4) { draft.step++; persistJourney(); renderSurvey(); $('#survey-question').focus(); return; }
  const id = active.id, epoch = identityEpoch;
  busy = true; updateControls(); renderSurvey(); notice();
  try {
    const data = await jsonAPI(`/api/ai/sessions/${id}/survey`, {method:'PUT', body:JSON.stringify({answers:draft.answers,address:draft.address})});
    if (epoch !== identityEpoch || active?.id !== id) return;
    active = data.session; surveyDrafts.delete(id); upsertSession(active);persistJourney();renderMessages();
    const context = active.messages[0].career_context;
    if (context?.mode === 'career_exploration') {
      await prepareExplorationDraft();
      notice('Em có thể sửa câu hỏi trước khi gửi.');
    } else $('#message-input').value = analysisMessage;
  } catch (error) { notice(failure(error)); }
  finally { if (epoch === identityEpoch) { busy = false; updateControls(); renderSurvey(); } }
  if (epoch === identityEpoch && active?.id === id && !needsSurvey() && active.messages[0].career_context?.mode !== 'career_exploration') await send();
});

function notice(text = '', retry = false) {
  $('#chat-notice-text').textContent = text;
  $('#chat-notice').hidden = !text;
  $('#retry-send').hidden = !retry;
}
function scrollBottom() { $('#chat-scroll').scrollTop = $('#chat-scroll').scrollHeight; }
function renderGuestQuota() {
  const label = $('#guest-quota-text');
  if (!config?.is_guest) return;
  const {limit, remaining} = guestQuota || {};
  if (!Number.isInteger(limit) || limit <= 0 || !Number.isInteger(remaining)) {
    label.textContent = 'Bạn đang dùng thử · Đang tải số lượt còn lại…';
    return;
  }
  if (remaining === 0) {
    label.textContent = `Bạn đã dùng hết ${limit} câu hỏi miễn phí. Đăng nhập để tiếp tục cuộc trò chuyện.`;
    return;
  }
  const count = document.createElement('strong');
  count.textContent = `${remaining}/${limit}`;
  label.replaceChildren(document.createTextNode('Bạn đang dùng thử · còn '), count, document.createTextNode(' câu hỏi miễn phí.'));
}
function updateControls() {
  $('#survey-next').disabled = busy;
  $('#survey-back').disabled = busy || !active || !surveyDrafts.get(active.id)?.step;
  $('#survey-answer').disabled = busy;
  $('#survey-address').disabled = busy;
  document.querySelectorAll('#survey-suggestions button').forEach(button => { button.disabled = busy; });
  const listening = ['starting-mic', 'listening', 'transcribing'].includes(phase);
  const surveying = needsSurvey();
  const exhausted = config?.is_guest && guestQuota?.remaining === 0;
  $('#send-message').disabled = surveying || exhausted || busy || listening || !config?.configured || !$('#message-input').value.trim();
  $('#message-input').disabled = surveying || busy || listening;
  $('#start-chat').disabled = busy;
  $('#microphone').disabled = surveying || busy || !micMode || phase === 'starting-mic' || phase === 'transcribing';
  $('#microphone').classList.toggle('recording', phase === 'listening');
  $('#microphone').setAttribute('aria-label', phase === 'listening' ? 'Dừng mic và nhận diện' : 'Nói bằng micro');
  $('#mic-status').hidden = !listening;
  $('#thinking').hidden = !busy || phase !== 'thinking';
  $('#guest-banner').hidden = !config?.is_guest;
  $('#guest-banner').classList.toggle('limit-reached',Boolean(exhausted));
  $('#guest-login').setAttribute('aria-disabled',String(busy || listening));
  renderGuestQuota();
  $('#connection-status').textContent = phase === 'thinking' ? 'Đang suy nghĩ' : phase === 'starting-mic' ? 'Đang mở mic' : phase === 'listening' ? 'Đang nghe' : phase === 'transcribing' ? 'Đang nhận diện' : config?.mode === 'demo' ? 'Bản demo' : config?.configured ? 'Sẵn sàng' : 'Chưa cấu hình';
}
async function api(path, options = {}, retried = false) {
  if (!user || (!user.server_guest && auth?.currentUser?.uid !== user.uid)) throw new Error('Phiên đăng nhập đã thay đổi. Vui lòng đăng nhập lại.');
  const owner = user.uid;
  const token = user.server_guest ? null : await user.getIdToken(retried);
  if (!user.server_guest && auth?.currentUser?.uid !== owner) throw new Error('Phiên đăng nhập đã thay đổi.');
  const headers = {...options.headers, ...(token ? {Authorization: `Bearer ${token}`} : {})};
  if (typeof options.body === 'string') headers['Content-Type'] = 'application/json';
  const response = await fetch(path, {...options, headers, cache: 'no-store', signal: options.signal || AbortSignal.timeout(100000)});
  if (!user.server_guest && auth?.currentUser?.uid !== owner) throw new Error('Phiên đăng nhập đã thay đổi.');
  if (response.status === 401 && !retried && !user.server_guest) return api(path, options, true);
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const error = new Error(typeof data.detail === 'string' ? data.detail : data.detail?.message || 'Chưa thực hiện được. Bạn kiểm tra kết nối rồi thử lại nhé.');
    error.code = data.detail?.code;
    if(error.code==='GUEST_LIMIT_REACHED') {
      const {limit, used_questions, remaining} = data.detail;
      guestQuota = {limit, used_questions, remaining};
    }
    error.status = response.status;
    if (response.status === 401) {
      persistJourney(); const target=loginURL();
      clearPrivateUI();
      location.replace(target);
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
function persistJourney() {
  if (active && user) saveDraft(user.uid, active.id, {survey:needsSurvey() ? surveyDrafts.get(active.id) : null, message:$('#message-input').value,explorationPrepared:preparedQuestions.has(active.id)});
}
async function prepareExplorationDraft() {
  const id=active?.id, epoch=identityEpoch, context=active?.messages?.[0]?.career_context;
  if (context?.mode!=='career_exploration' || needsSurvey() || active.messages.length!==1 || $('#message-input').value || preparedQuestions.has(id)) return;
  const career=await jsonAPI('/api/career-library/'+encodeURIComponent(context.career_id));
  if (epoch!==identityEpoch || active?.id!==id || $('#message-input').value) return;
  const fromStory=storyQuestion(context.career_id,id);
  $('#message-input').value=fromStory?.text || explorationQuestion(career,active.messages[0].survey);
  preparedQuestions.add(id);
  persistJourney(); resizeInput();
}
function rememberActive() {
  try { if (active) { sessionStorage.setItem(storageKey(), active.id); persistJourney(); } else sessionStorage.removeItem(storageKey()); } catch { /* Tab riêng tư có thể chặn storage. */ }
  const url=new URL(location.href);
  if(url.searchParams.has('conversation')){if(active)url.searchParams.set('conversation',active.id);else url.searchParams.delete('conversation');history.replaceState(null,'',url);}
}
function setSidebar(open) {
  const mobile = window.innerWidth <= 760;
  $('#chat-sidebar').classList.toggle('open', mobile && open);
  $('#drawer-backdrop').hidden = !mobile || !open;
  $('#open-sidebar').setAttribute('aria-expanded', String(mobile && open));
  $('#chat-main').inert = mobile && open;
  $('#chat-sidebar').inert = mobile && !open;
  if (mobile) { if (open) $('#close-sidebar').focus(); else $('#open-sidebar').focus(); }
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
    const row = document.createElement('div'); row.className = 'history-item'; row.classList.toggle('active', item.id === (selectedSession || active?.id));
    const open = document.createElement('button'); open.className = 'history-open';
    open.title = item.title;
    open.setAttribute('aria-current', item.id === (selectedSession || active?.id) ? 'true' : 'false');
    open.dataset.sessionId=item.id;
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
  const epoch = identityEpoch,revision=historyRevision;
  const data = await jsonAPI('/api/ai/sessions');
  if (epoch !== identityEpoch) return;
  sessions = revision===historyRevision ? data.items : [...new Map([...data.items,...sessions].map(s=>[s.id,s])).values()].sort((a,b)=>b.updated_at.localeCompare(a.updated_at)); renderHistory();
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
  const body = document.createElement('div'); body.className = 'message-body';
  const label = document.createElement('span'); label.className = 'message-label'; label.textContent = message.role === 'assistant' ? `La Bàn AI${message.mode === 'demo' ? ' · Trả lời mẫu' : ''}` : 'Bạn';
  const bubble = document.createElement('div'); bubble.className = 'message-bubble';
  if (message.role === 'assistant') markdown(bubble, message.content);
  else bubble.textContent = message.request_id === active?.messages?.[0]?.survey?.analysis_request_id
    ? 'Em đã hoàn thành khảo sát và muốn khám phá những hướng nghề đáng tìm hiểu.' : message.content;
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
  if(message.role==='user')body.append(label);
  body.append(bubble);
  if(message.mode==='demo'){const note=document.createElement('p');note.className='quiet-note';note.textContent='Trả lời mẫu · chưa gọi DeepSeek';body.append(note);}
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
  const context = active?.messages?.[0]?.career_context;
  if (context?.mode === 'career_exploration') $('#session-note').textContent += ` · Tìm hiểu: ${context.career_name || context.career_id}`;
  const storyReturn=context?.mode==='career_exploration' ? storyQuestion(context.career_id,active.id) : null;
  if (storyReturn) {
    const back=document.createElement('a');back.href=storyReturn.path;back.textContent=' · '+(storyReturn.label || 'Quay lại tình huống trong truyện')+' ↗';
    $('#session-note').append(back);
  }
  if (context?.mode === 'career_exploration' && active.messages[0].survey && active.messages.length === 1 && !$('#message-input').value) {
    prepareExplorationDraft().catch(error=>notice(failure(error)));
  }
  renderSurvey();
  list.hidden = !active || needsSurvey();
  renderHistory();
  if (active && !needsSurvey()) scrollBottom(); else $('#chat-scroll').scrollTop = 0;
}
async function createSession() {
  if (active) return active;
  if (creation) return creation;
  const epoch = identityEpoch;
  const task=(async()=>{
    const data = await jsonAPI('/api/ai/sessions', {method:'POST', body:JSON.stringify({remember:$('#remember-chat').checked, ...(entryContext || {})})});
    if (epoch !== identityEpoch) throw new Error('Phiên đăng nhập đã thay đổi.');
    active = data.session; selectedSession=active.id; entryContext = null; pending = null;
    upsertSession(active);rememberActive(); renderMessages();return active;
  })();
  creation=task;
  try{return await task;}finally{if(creation===task)creation=null;}
}
async function startChat(prompt = '') {
  if (busy) return;
  cancelMic();
  busy = true; phase='creating'; updateControls(); notice('Đang tạo cuộc trò chuyện…');
  try {
    await createSession();
    notice();
    if (prompt) {
      if (needsSurvey()) surveyDrafts.get(active.id).answers[4] = prompt;
      else { $('#message-input').value = prompt; resizeInput(); }
    }
  } catch (error) { notice(failure(error)); }
  finally { busy = false;phase='idle'; updateControls(); if (active) $('#message-input').focus(); }
}
async function loadSession(id) {
  if (!user || (!user.server_guest && auth?.currentUser?.uid!==user.uid)) {
    const target=loginURL();persistJourney();clearPrivateUI();location.replace(target);return;
  }
  if (busy && phase!=='loading') return notice('Đợi La Bàn trả lời xong rồi mở cuộc trò chuyện khác nhé.');
  if(loadingSession===id)return;
  cancelMic(); persistJourney();
  navigationAbort?.abort();const ticket=++navigation;
  const controller=new AbortController();navigationAbort=controller;loadingSession=id;selectedSession=id;
  notice('Đang mở cuộc trò chuyện…'); pending = null; busy = true; phase='loading';
  const savedCache=cachedSession(id);active=null;$('#message-input').value='';renderMessages();updateControls();
  if(window.innerWidth<=760)setSidebar(false);
  const epoch = identityEpoch;
  try {
    const data = savedCache ? {session:savedCache} : await jsonAPI(`/api/ai/sessions/${id}`,{signal:controller.signal});
    if (epoch !== identityEpoch || ticket!==navigation) return;
    $('#message-input').value = '';
    active = data.session;
    if(!savedCache)cacheSession(active);
    const saved=loadDraft(user.uid,active.id);
    if (saved?.explorationPrepared) preparedQuestions.add(active.id);
    if (needsSurvey() && saved?.survey) surveyDrafts.set(active.id,saved.survey);
    $('#message-input').value = saved?.message || '';
    rememberActive(); renderMessages(); resizeInput();
    notice();
    if (window.innerWidth <= 760) setSidebar(false);
  } catch (error) { if(ticket===navigation && epoch===identityEpoch && error.name!=='AbortError'){sessionCache.delete(id);notice(failure(error));} }
  finally { if(ticket===navigation && epoch===identityEpoch){busy = false;phase='idle';loadingSession=null;navigationAbort=null;updateControls();} }
}
function freshChat() {
  if (busy && phase!=='loading') return notice('Đợi La Bàn trả lời xong rồi bắt đầu cuộc trò chuyện mới nhé.');
  persistJourney();navigation++;navigationAbort?.abort();navigationAbort=null;loadingSession=null;selectedSession=null;busy=false;phase='idle';
  cancelMic();
  active = null; entryContext = null; pending = null; rememberActive();
  $('#message-input').value = ''; $('#remember-chat').checked = false; notice(); renderMessages(); resizeInput(); updateControls();
  if (window.innerWidth <= 760) setSidebar(false);
}
async function send(retry = false) {
  if (busy || ['listening','transcribing','starting-mic'].includes(phase)) return;
  const text = retry && pending ? pending.message : $('#message-input').value.trim();
  if (!text || !config.configured) return;
  if(config.is_guest && guestQuota?.remaining===0 && !retry){notice(`Bạn đã dùng hết ${guestQuota.limit} câu hỏi. Đăng nhập Google hoặc email để tiếp tục nhé.`);updateControls();return;}
  if (text.length > 2000) return notice('Mỗi tin nhắn tối đa 2.000 ký tự nhé.');
  notice(); busy = true; phase = 'thinking'; updateControls();
  const epoch = identityEpoch;
  try {
    await createSession();
    if (needsSurvey()) { surveyDrafts.get(active.id).answers[4] = text; return; }
    if (!retry || !pending) pending = {session_id:active.id, request_id:text === analysisMessage && active.messages[0]?.survey ? active.messages[0].survey.analysis_request_id : crypto.randomUUID(), message:text};
    const request = {...pending}; renderMessages();
    $('#message-input').value = ''; resizeInput();
    const data = await jsonAPI('/api/ai/chat', {method:'POST', body:JSON.stringify(request)});
    if (epoch !== identityEpoch || active?.id !== request.session_id) return;
    active = data.session; pending = null; upsertSession(active);persistJourney(); renderMessages();
    if(data.guest_quota) guestQuota=data.guest_quota;
    busy = false; phase = 'idle'; updateControls();
  } catch (error) {
    if (epoch !== identityEpoch) return;
    notice(failure(error), Boolean(pending));
    // Giữ mã request khi thử lại để backend không tạo tin nhắn trùng.
  } finally {
    if (epoch === identityEpoch) { busy = false; phase = 'idle'; updateControls(); $('#message-input').focus(); }
  }
}
function resizeInput() {
  const input = $('#message-input');
  const ceiling = Math.min(130, Math.max(64, (window.visualViewport?.height || window.innerHeight) * .24));
  input.style.height = 'auto';
  input.style.height = `${Math.min(input.scrollHeight, ceiling)}px`;
  updateControls();
}

// Điều chỉnh bố cục theo vùng nhìn thấy khi bàn phím điện thoại mở.
// Không can thiệp luồng gửi tin, mic hoặc trạng thái hội thoại.
function syncChatViewport() {
  const viewport = window.visualViewport;
  if (window.innerWidth <= 760 && viewport && viewport.scale === 1) {
    document.body.style.setProperty('--chat-viewport-height', `${Math.round(viewport.height)}px`);
    document.body.style.setProperty('--chat-viewport-top', `${Math.round(viewport.offsetTop)}px`);
  } else {
    document.body.style.removeProperty('--chat-viewport-height');
    document.body.style.removeProperty('--chat-viewport-top');
  }
  resizeInput();
}
let viewportFrame;
function scheduleViewportLayout() {
  cancelAnimationFrame(viewportFrame);
  viewportFrame = requestAnimationFrame(syncChatViewport);
}
window.addEventListener('resize', scheduleViewportLayout);
window.visualViewport?.addEventListener('resize', scheduleViewportLayout);
window.visualViewport?.addEventListener('scroll', scheduleViewportLayout);
syncChatViewport();

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
    upsertSession(data.session);
  } catch (error) { notice(failure(error)); }
}
async function deleteSession(item) {
  if (busy) return;
  const confirmed = await askAction({title:'Xóa cuộc trò chuyện này?', description:'Tin nhắn và phần ghi nhớ của cuộc trò chuyện sẽ bị xóa. Bạn không thể khôi phục thao tác này.', confirm:'Xóa cuộc trò chuyện'});
  if (!confirmed) return;
  try {
    await api(`/api/ai/sessions/${item.id}`, {method:'DELETE'});
    if (active?.id === item.id) freshChat();
    sessionCache.delete(item.id);sessions=sessions.filter(s=>s.id!==item.id);historyRevision++;renderHistory();
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
  navigation++;navigationAbort?.abort();navigationAbort=null;loadingSession=null;selectedSession=null;sessionCache.clear();creation=null;
  identityEpoch++; entryContext = null; cancelMic(); surveyDrafts.clear(); preparedQuestions.clear(); $('#career-survey').hidden = true;
  $('#survey-answer').value = '';
  $('#survey-suggestions').replaceChildren();
  $('#survey-question').textContent = '';
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
$('#message-input').addEventListener('input', () => { if (active?.messages?.[0]?.career_context?.mode==='career_exploration') preparedQuestions.add(active.id); resizeInput(); persistJourney(); });
$('#guest-login').addEventListener('click', event => {
  if (busy || ['starting-mic','listening','transcribing'].includes(phase)) { event.preventDefault(); return; }
  event.preventDefault();persistJourney();location.assign(loginURL());
});
window.addEventListener('pagehide', persistJourney);
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
  try { if (!user?.server_guest) await sdk.signOut(auth); clearPrivateUI(); location.replace('/'); }
  catch (error) { notice(failure(error)); }
});

async function initialize() {
  try {
    try { ({auth, sdk} = await getFirebase()); user = await restoredUser(auth, sdk); }
    catch { /* Server guest works without Firebase configuration/network. */ }
    if (!user) user = await guestSession();
    const owner = user.uid;
    if(auth && sdk) sdk.onAuthStateChanged(auth, (current) => {
      if (user?.server_guest ? current && !current.isAnonymous : !current || current.uid !== owner) {
        persistJourney();const target=loginURL();clearPrivateUI();location.replace(target);
      }
    });
    const historyTask=refreshHistory().catch(error=>{if(user?.uid===owner)notice(failure(error));});
    config = await jsonAPI('/api/ai/config');
    guestQuota = config.guest_quota;
    micMode = config.microphone?.google && window.isSecureContext && navigator.mediaDevices?.getUserMedia && window.AudioContext ? 'google'
      : window.isSecureContext && (window.SpeechRecognition || window.webkitSpeechRecognition) ? 'browser' : null;
    $('#microphone').title = micMode === 'google' ? 'Nói tiếng Việt bằng Google Speech-to-Text; tự dừng sau 3 giây im lặng'
      : micMode === 'browser' ? 'Nói tiếng Việt bằng nhận diện của trình duyệt; tự dừng sau 3 giây im lặng' : 'Mic cần Chrome trên localhost hoặc HTTPS.';
    $('#user-name').textContent = config.is_guest ? 'Khách dùng thử' : user.displayName || 'Bạn';
    $('#account-caption').textContent = config.is_guest ? 'Khám phá cùng La Bàn' : 'Tài khoản của bạn';
    $('#user-initial').textContent = config.is_guest ? 'K' : [...(user.displayName || 'Bạn')][0].toLocaleUpperCase('vi');
    const banner = [];
    if (config.mode === 'demo') banner.push('BẢN DEMO · Câu trả lời mẫu để thử giao diện. Chưa kết nối DeepSeek và chưa phân tích năng lực.');
    else if (!config.configured) banner.push('Tư vấn AI đang chờ cấu hình khóa DeepSeek.');
    if (micMode === 'browser') banner.push('Mic đang dùng nhận diện của trình duyệt. Google Speech-to-Text cần cấu hình Cloud trên máy chủ.');
    $('#mode-banner').hidden = !banner.length; $('#mode-banner').textContent = banner.join(' ');
    $('#auth-loading').hidden = true; $('#chat-app').hidden = false;
    setSidebar(false);
    const entryURL = new URL(location.href);
    const requested=entryURL.searchParams.get('conversation');
    if(requested && /^[a-f0-9-]{36}$/i.test(requested)) await loadSession(requested);
    else if (entryURL.searchParams.has('mode')) {
      const mode = entryURL.searchParams.get('mode');
      const career_id = entryURL.searchParams.get('career_id');
      entryContext = {mode, ...(career_id ? {career_id} : {})};
      active = null; pending = null;
      await startChat();
      if (active) { entryURL.searchParams.delete('mode'); entryURL.searchParams.delete('career_id'); history.replaceState(null,'',entryURL); }
    }
    let previous; try { previous = sessionStorage.getItem(storageKey()); } catch { /* Không bắt buộc storage. */ }
    if (!active && !requested && previous) await loadSession(previous);
    else renderMessages();
    const url = new URL(location.href);
    if (url.searchParams.get('start') === '1' || config.is_guest) {
      // Đăng nhập mở ngay phiên tạm; chỉ lưu lâu dài khi có lựa chọn đồng ý.
      if (!active && !requested) await startChat();
      if (active) {
        url.searchParams.delete('start');
        history.replaceState(null, '', url);
        $('#message-input').focus();
      }
    }
    updateControls();
    await historyTask;
  } catch (error) {
    $('#auth-loading p').textContent = failure(error);
    if (!$('#chat-app').hidden) notice(failure(error));
  }
}
initialize();
