// Bằng chứng khách chỉ ở RAM trong lượt nâng cấp, không ghi token vào storage.
import {transferDrafts} from './chat-journey.js';
let pendingClaim = null;
function savedClaim() { try { const v=JSON.parse(sessionStorage.getItem('laban.claim-target')); return v && Date.now()-v.at<7200000 ? v : null; } catch { return null; } }
export const hasPendingGuestClaim = () => Boolean(pendingClaim || savedClaim());

async function transferHistory(auth, target, guest, guestToken) {
  if (savedClaim() && savedClaim().uid!==target.uid) throw new Error('Lần chuyển lịch sử đang gắn với tài khoản khác. Chưa chuyển dữ liệu.');
  if (hasPendingGuestClaim()) return retryGuestClaim(auth);
  pendingClaim = {target, guest, guestToken};
  try { sessionStorage.setItem('laban.claim-target',JSON.stringify({uid:target.uid,at:Date.now(),anonymousProof:!!guestToken})); } catch {}
  await retryGuestClaim(auth);
}

export async function retryGuestClaim(auth) {
  if (!pendingClaim) {
    const saved=savedClaim();
    if (!saved) return;
    if (saved.uid!==auth.currentUser?.uid || saved.anonymousProof) throw new Error('Không thể khôi phục bằng chứng khách cho tài khoản này. Giữ phiên cũ để thử lại.');
    pendingClaim={target:auth.currentUser,guest:null,guestToken:null};
  }
  let {target, guest, guestToken} = pendingClaim;
  if (auth.currentUser?.uid !== target.uid) throw new Error('Tài khoản đã thay đổi; chưa chuyển lịch sử khách.');
  if (!guest) {
    const response = await fetch('/api/ai/guest/session',{cache:'no-store',signal:AbortSignal.timeout(15000)});
    if (!response.ok) throw new Error('Chưa kiểm tra được lịch sử khách. Bạn thử lại nhé.');
    guest = (await response.json()).user;
  }
  // Recover a response lost after COMMIT, without repeating a claim using an invalidated cookie.
  const previous=savedClaim();
  if (!guest && previous?.source) {
    const sid=previous.session;
    if (!sid || !/^[a-f0-9-]{36}$/i.test(sid)) throw new Error('Chưa xác minh được cuộc trò chuyện đã chuyển.');
    const response=await fetch('/api/ai/sessions/'+encodeURIComponent(sid),{headers:{Authorization:`Bearer ${await target.getIdToken(true)}`},cache:'no-store',signal:AbortSignal.timeout(15000)});
    if (!response.ok || auth.currentUser?.uid!==target.uid) throw new Error('Chưa xác minh được chủ sở hữu cuộc trò chuyện.');
    transferDrafts(previous.source,target.uid); clearClaim(); return;
  }
  if (!guest || guest.uid === target.uid) { if (guest) transferDrafts(guest.uid,target.uid); clearClaim(); return; }
  if (!guestToken && !guest.server_guest) throw new Error('Không lấy được bằng chứng phiên khách. Bạn thử đăng nhập lại từ phiên khách nhé.');
  pendingClaim = {target, guest, guestToken};
  try { sessionStorage.setItem('laban.claim-target',JSON.stringify({uid:target.uid,at:Date.now(),anonymousProof:!!guestToken,source:guest.uid,session:sessionStorage.getItem(`laban.advisor.${guest.uid}`)})); } catch {}
  const token = await target.getIdToken(true);
  const response = await fetch('/api/ai/guest/claim', {method:'POST',headers:{Authorization:`Bearer ${token}`,'Content-Type':'application/json'},
    body:JSON.stringify({guest_id_token:guestToken}),cache:'no-store',signal:AbortSignal.timeout(15000)});
  if (!response.ok) {
    const error = new Error('guest_claim_failed');
    error.userMessage = 'Bạn đã đăng nhập, nhưng lịch sử khách chưa chuyển xong. Giữ trang này mở và bấm “Thử giữ lịch sử” để thử lại.';
    throw error;
  }
  // Session UUID giữ nguyên; chỉ chuyển con trỏ tab sau khi server xác nhận.
  if (auth.currentUser?.uid !== target.uid) throw new Error('Tài khoản đã thay đổi; chưa khôi phục bản nháp.');
  transferDrafts(guest.uid,target.uid);
  clearClaim();
}
function clearClaim() { pendingClaim=null; try { sessionStorage.removeItem('laban.claim-target'); } catch {} }

export async function resumeGuestTransfer(auth) {
  if (hasPendingGuestClaim()) return retryGuestClaim(auth);
  if (auth.currentUser && !auth.currentUser.isAnonymous) return transferHistory(auth,auth.currentUser,null,null);
}

export async function signInEmailPreservingGuest(auth,sdk,email,password,create=false) {
  const guest = auth.currentUser?.isAnonymous ? auth.currentUser : null;
  const guestToken = guest ? await guest.getIdToken() : null;
  let result;
  if (create && guest) {
    result = await sdk.linkWithCredential(guest,sdk.EmailAuthProvider.credential(email,password));
  } else {
    result = create ? await sdk.createUserWithEmailAndPassword(auth,email,password) : await sdk.signInWithEmailAndPassword(auth,email,password);
  }
  await transferHistory(auth,result.user,guest,guestToken);
  await result.user.getIdToken(true); // Cập nhật provider sau link cùng UID.
  return result;
}

export function signInGooglePreservingGuest(auth,sdk,provider) {
  const guest = auth.currentUser?.isAnonymous ? auth.currentUser : null;
  const proof = guest ? guest.getIdToken() : Promise.resolve(null);
  // Popup mở ngay trong click; không await network trước khi mở.
  const popup = guest ? sdk.linkWithPopup(guest,provider) : sdk.signInWithPopup(auth,provider);
  return (async()=>{
    // Gắn handler cho cả hai promise ngay để popup/proof lỗi không bị unhandled.
    const [proofResult,popupResult] = await Promise.allSettled([proof,popup]);
    if (proofResult.status === 'rejected') throw proofResult.reason;
    const guestToken = proofResult.value;
    let result;
    try {
      if (popupResult.status === 'rejected') throw popupResult.reason;
      result = popupResult.value;
    }
    catch(error) {
      if (!guest || error.code !== 'auth/credential-already-in-use') throw error;
      const credential = sdk.GoogleAuthProvider.credentialFromError(error);
      if (!credential || !guestToken) throw error;
      result = await sdk.signInWithCredential(auth,credential);
    }
    await transferHistory(auth,result.user,guest,guestToken);
    await result.user.getIdToken(true);
    return result;
  })();
}
