// Same-origin server guest cookie; Firebase is only needed for an existing account.
import {getFirebase, restoredUser} from './firebase-client.js';

let opening;
export async function guestSession() {
  if (!opening) opening = fetch('/api/ai/guest/session', {method:'POST',credentials:'same-origin',cache:'no-store'})
    .then(async response => {
      const body = await response.json();
      if (!response.ok) throw new Error(typeof body.detail==='string' ? body.detail : body.detail?.message || 'Chưa mở được phiên khách. Bạn thử lại sau nhé.');
      return body.user;
    }).finally(() => { opening = null; });
  return opening;
}

export async function aiHeaders() {
  let current;
  try { const {auth,sdk} = await getFirebase(); current = await restoredUser(auth,sdk); }
  catch { /* Guest does not require Firebase service. */ }
  if (current) return {'Content-Type':'application/json', Authorization:`Bearer ${await current.getIdToken()}`};
  await guestSession();
  return {'Content-Type':'application/json'};
}
