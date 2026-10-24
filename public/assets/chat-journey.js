// Tab-local drafts, never authentication proof. The backend still verifies ownership.
const TTL = 2 * 60 * 60 * 1000;
const read = key => { try { const v = JSON.parse(sessionStorage.getItem(key)); if (v && Number.isFinite(v.at) && Date.now()>=v.at && Date.now()-v.at<TTL) return v; sessionStorage.removeItem(key); return null; } catch { return null; } };
const write = (key, value) => { try { sessionStorage.setItem(key, JSON.stringify({...value, at:Date.now()})); } catch { /* Private browsing may disable storage. */ } };
export function safeReturnPath(value) {
  if (typeof value !== 'string' || !value.startsWith('/') || value.startsWith('//') || /[\\\u0000-\u0020]/.test(value)) return '/';
  const url = new URL(value, location.origin);
  if (url.origin !== location.origin || !['/','/ai-career-advisor','/chat','/mot-ngay-lam-viec'].includes(url.pathname)) return '/';
  const allowed = new URLSearchParams();
  for (const key of ['mode','career_id','nghe','scene']) {
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
  return {survey, message:typeof draft.message==='string' ? draft.message.slice(0,2000) : '',...(draft.explorationPrepared ? {explorationPrepared:true} : {})};
}
export function transferDrafts(source, target) {
  if (!source || source===target) return;
  try {
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
