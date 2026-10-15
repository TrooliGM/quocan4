// Bằng chứng khách chỉ ở RAM trong lượt nâng cấp, không ghi token vào storage.
let pendingClaim = null;
export const hasPendingGuestClaim = () => Boolean(pendingClaim);

async function transferHistory(auth, target, guest, guestToken) {
  if (!guest || guest.uid === target.uid) return;
  if (!guestToken) throw new Error('Không lấy được bằng chứng phiên khách. Bạn thử đăng nhập lại từ phiên khách nhé.');
  pendingClaim = {target, guest, guestToken};
  await retryGuestClaim(auth);
}

export async function retryGuestClaim(auth) {
  if (!pendingClaim) return;
  const {target, guest, guestToken} = pendingClaim;
  if (auth.currentUser?.uid !== target.uid) throw new Error('Tài khoản đã thay đổi; chưa chuyển lịch sử khách.');
  const token = await target.getIdToken(true);
  const response = await fetch('/api/ai/guest/claim', {method:'POST',headers:{Authorization:`Bearer ${token}`,'Content-Type':'application/json'},
    body:JSON.stringify({guest_id_token:guestToken}),cache:'no-store',signal:AbortSignal.timeout(15000)});
  if (!response.ok) {
    const error = new Error('guest_claim_failed');
    error.userMessage = 'Bạn đã đăng nhập, nhưng lịch sử khách chưa chuyển xong. Giữ trang này mở và bấm “Thử giữ lịch sử” để thử lại.';
    throw error;
  }
  // Session UUID giữ nguyên; chỉ chuyển con trỏ tab sau khi server xác nhận.
  try {
    const current = sessionStorage.getItem(`laban.advisor.${guest.uid}`);
    if (current) sessionStorage.setItem(`laban.advisor.${target.uid}`,current);
  } catch { /* Không bắt buộc storage để xác thực tài khoản. */ }
  pendingClaim = null;
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
