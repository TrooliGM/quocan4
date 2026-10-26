// Tab-local drafts, never authentication proof. The backend still verifies ownership.
const TTL = 2 * 60 * 60 * 1000;
const read = key => { try { const v = JSON.parse(sessionStorage.getItem(key)); if (v && Number.isFinite(v.at) && Date.now()>=v.at && Date.now()-v.at<TTL) return v; sessionStorage.removeItem(key); return null; } catch { return null; } };
const write = (key, value) => { try { sessionStorage.setItem(key, JSON.stringify({...value, at:Date.now()})); } catch { /* Private browsing may disable storage. */ } };
const JOURNEY='laban.active-journey.v1';
const uuid=value=>typeof value==='string'&&/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i.test(value);
export function currentJourney() {
  const v=read(JOURNEY);
  return v&&typeof v.uid==='string'&&uuid(v.id)?v:null;
}
// A tab-local return pointer, never proof of ownership. Chat GET still verifies UID.
export function rememberJourney(uid,session) {
  if(uid&&uuid(session?.id)){write(JOURNEY,{uid,id:session.id});window.dispatchEvent(new Event('laban:journey-change'));}
}
export function forgetJourney(uid) {
  try {if(!uid||currentJourney()?.uid===uid){sessionStorage.removeItem(JOURNEY);window.dispatchEvent(new Event('laban:journey-change'));}}catch{}
}
export function journeyPath(value) {
  let url;try{url=new URL(value,location.href);}catch{return value;}
  if(url.origin!==location.origin||!['/','/ai-career-advisor','/chat','/mot-ngay-lam-viec'].includes(url.pathname))return value;
  if(url.searchParams.has('login')||url.searchParams.has('return_to'))return value;
  const journey=currentJourney();
  if(journey)url.searchParams.set('conversation',journey.id);
  return url.pathname+url.search+url.hash;
}
// Native anchors preserve modifier clicks and Back/Forward. No fetch, popup or AI.
export function installJourneyNavigation() {
  if(window.__labanJourneyNavigation)return;
  window.__labanJourneyNavigation=true;
  const originals=new WeakMap();
  const prepare=link=>{
    const actual=link.getAttribute('href');if(!actual||link.hasAttribute('download'))return;
    const previous=originals.get(link),raw=previous?.rendered===actual?previous.raw:actual;
    let url;try{url=new URL(raw,location.href);}catch{return;}
    if(url.origin!==location.origin)return;
    if(link.target&&link.target!=='_self')link.removeAttribute('target');
    // Keep document-local hash navigation local (modal/menu/skip links).
    if(raw.startsWith('#'))return;
    const path=journeyPath(raw);originals.set(link,{raw,rendered:path});if(path!==actual)link.setAttribute('href',path);
  };
  const scan=node=>{if(node.nodeType!==1&&node!==document)return;if(node.matches?.('a[href]'))prepare(node);node.querySelectorAll?.('a[href]').forEach(prepare);};
  scan(document);
  window.addEventListener('laban:journey-change',()=>scan(document));
  new MutationObserver(records=>{for(const r of records)if(r.type==='childList')r.addedNodes.forEach(scan);else prepare(r.target);}).observe(document.documentElement,{subtree:true,childList:true,attributes:true,attributeFilter:['href','target']});
  document.addEventListener('click',event=>{const link=event.target.closest?.('a[href]');if(link){window.dispatchEvent(new Event('laban:before-navigate'));prepare(link);}},true);
}
export function safeReturnPath(value) {
  if (typeof value !== 'string' || !value.startsWith('/') || value.startsWith('//') || /[\\\u0000-\u0020]/.test(value)) return '/';
  const url = new URL(value, location.origin);
  if (url.origin !== location.origin || !['/','/ai-career-advisor','/chat','/mot-ngay-lam-viec'].includes(url.pathname)) return '/';
  const allowed = new URLSearchParams();
  for (const key of ['mode','career_id','career','nghe','scene']) {
    const v = url.searchParams.get(key);
    if (v && /^[a-z0-9_-]{1,80}$/.test(v)) allowed.set(key,v);
  }
  const conversation=url.searchParams.get('conversation');
  if (conversation && /^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i.test(conversation)) allowed.set('conversation',conversation);
  return url.pathname + (allowed.size ? '?'+allowed : '') + (/^#[a-zA-Z0-9_-]{1,80}$/.test(url.hash) ? url.hash : '');
}
export function beginLogin(path=location.pathname+location.search+location.hash) { write('laban.login-return', {path:safeReturnPath(path)}); }
export function loginDestination() { return safeReturnPath(new URLSearchParams(location.search).get('return_to') || read('laban.login-return')?.path || '/'); }
export function finishLogin(target=loginDestination()) { const path=safeReturnPath(target); try { sessionStorage.removeItem('laban.login-return'); } catch {} return path; }
export function chatLoginURL(id) {
  const path=safeReturnPath('/ai-career-advisor'+(id?'?conversation='+encodeURIComponent(id):''));
  beginLogin(path);
  return '/?login=1&return_to='+encodeURIComponent(path);
}
export function saveDraft(uid, id, value) { if (uid && id) write(`laban.draft.${uid}.${id}`,value); }
export function loadDraft(uid, id) {
  const draft=read(`laban.draft.${uid}.${id}`);
  if (!draft) return null;
  const survey=draft.survey;
  if (survey && (!Number.isInteger(survey.step) || survey.step<0 || survey.step>4 || !Array.isArray(survey.answers) || survey.answers.length!==5 || survey.answers.some(a=>typeof a!=='string'||a.length>400) || !['anh','chị'].includes(survey.address))) return null;
  const p=draft.pending;
  const pending=p&&p.session_id===id&&uuid(p.request_id)&&typeof p.message==='string'&&p.message.length<=2000 ? p : null;
  return {survey,pending, message:typeof draft.message==='string' ? draft.message.slice(0,2000) : '',...(draft.explorationPrepared ? {explorationPrepared:true} : {})};
}
export function transferDrafts(source, target) {
  if (!source || source===target) return;
  try {
    const journey=currentJourney();
    if(journey?.uid===source)rememberJourney(target,{id:journey.id});
    const id=sessionStorage.getItem(`laban.advisor.${source}`);
    if (id) {
      const draft=loadDraft(source,id);
      if (draft) saveDraft(target,id,draft);
      sessionStorage.setItem(`laban.advisor.${target}`,id);
      sessionStorage.removeItem(`laban.draft.${source}.${id}`);
      sessionStorage.removeItem(`laban.advisor.${source}`);
    }
  } catch { /* Transfer on server has already succeeded. */ }
}
export function forgetDraft(uid,id) { try { sessionStorage.removeItem(`laban.draft.${uid}.${id}`); } catch {} }
