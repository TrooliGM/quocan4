const select = (s) => document.querySelector(s);
const dialog = select('#auth-dialog');
let sdk, auth, mode = 'login', busy = false, ready = false, configTask, profileEpoch = 0;

const messages = {
  'auth/invalid-email': 'Bạn kiểm tra lại địa chỉ email nhé.',
  'auth/invalid-credential': 'Email hoặc mật khẩu chưa đúng. Bạn thử lại nhé.',
  'auth/user-not-found': 'Email hoặc mật khẩu chưa đúng. Bạn thử lại nhé.',
  'auth/wrong-password': 'Email hoặc mật khẩu chưa đúng. Bạn thử lại nhé.',
  'auth/email-already-in-use': 'Email này đã có tài khoản. Bạn chọn Đăng nhập hoặc Quên mật khẩu nhé.',
  'auth/weak-password': 'Mật khẩu chưa đủ mạnh. Hãy dùng ít nhất 6 ký tự và thêm chữ, số hoặc ký hiệu.',
  'auth/password-does-not-meet-requirements': 'Mật khẩu chưa đáp ứng yêu cầu. Hãy dùng thêm chữ hoa, chữ thường, số và ký hiệu.',
  'auth/popup-closed-by-user': 'Bạn đã đóng cửa sổ Google. Có thể thử lại khi sẵn sàng.',
  'auth/cancelled-popup-request': 'Một cửa sổ đăng nhập khác đang mở.',
  'auth/popup-blocked': 'Trình duyệt đang chặn cửa sổ Google. Hãy cho phép cửa sổ bật lên rồi thử lại.',
  'auth/unauthorized-domain': 'Địa chỉ website này chưa được bật cho đăng nhập. Hãy báo cho nhóm dự án.',
  'auth/operation-not-allowed': 'Cách đăng nhập này chưa được bật. Hãy báo cho nhóm dự án.',
  'auth/network-request-failed': 'Chưa kết nối được Firebase. Bạn kiểm tra mạng rồi thử lại nhé.',
  'auth/too-many-requests': 'Bạn thử quá nhiều lần. Hãy chờ một chút rồi thử lại.',
  'auth/user-disabled': 'Tài khoản đang bị tạm khóa. Bạn liên hệ nhóm dự án nhé.',
  'auth/account-exists-with-different-credential': 'Email đã dùng một cách đăng nhập khác. Hãy đăng nhập bằng cách bạn đã dùng trước đó.',
  'auth/web-storage-unsupported': 'Trình duyệt chưa cho phép lưu phiên đăng nhập. Hãy kiểm tra cài đặt lưu trữ của trang.',
};
function status(message = '', error = false) {
  select('#auth-status').textContent = message;
  select('#auth-status').classList.toggle('error', error);
}
function errorMessage(error) { return messages[error.code] || error.userMessage || 'Chưa thực hiện được. Bạn thử lại sau nhé.'; }
function setBusy(value) {
  busy = value;
  ['#auth-submit', '#google-signin', '#forgot-password', '#signout-button', '#verify-email', '#refresh-profile'].forEach((id) => { select(id).disabled = value || !ready; });
  ['#mode-login', '#mode-register'].forEach((id) => { select(id).disabled = value; });
  select('#auth-form').setAttribute('aria-busy', String(value));
  select('#auth-submit').textContent = value ? 'Đang xử lý…' : mode === 'register' ? 'Tạo tài khoản ↗' : 'Đăng nhập ↗';
}
function setMode(value) {
  if (busy) return;
  mode = value; const register = value === 'register';
  select('#name-field').hidden = !register;
  select('#auth-name').required = register;
  select('#confirm-password-field').hidden = !register;
  select('#auth-confirm-password').required = register;
  select('#auth-confirm-password').value = '';
  select('#auth-title').textContent = register ? 'Bắt đầu hành trình của bạn.' : 'Mừng bạn trở lại!';
  select('#auth-subtitle').textContent = register ? 'Tạo tài khoản để cùng La Bàn khám phá tương lai.' : 'Đăng nhập để có một góc khám phá của riêng mình.';
  select('#auth-password').autocomplete = register ? 'new-password' : 'current-password';
  select('#password-hint').hidden = !register;
  select('#forgot-password').hidden = register;
  select('#auth-password').value = '';
  for (const [id, selected] of [['#mode-login', !register], ['#mode-register', register]]) {
    select(id).classList.toggle('selected', selected); select(id).setAttribute('aria-pressed', String(selected));
  }
  status(); setBusy(false);
}
function displayUser(user) {
  const name = user?.displayName?.trim() || user?.email?.split('@')[0] || 'Bạn';
  const initial = [...name][0]?.toLocaleUpperCase('vi') || 'B';
  select('#auth-guest').hidden = Boolean(user);
  select('#auth-member').hidden = !user;
  select('#account-avatar').hidden = !user;
  select('#account-avatar').textContent = user ? initial : '';
  select('#account-label').textContent = user ? 'Tài khoản' : 'Đăng nhập';
  select('#auth-title').textContent = user ? 'Góc nhỏ của bạn.' : mode === 'register' ? 'Bắt đầu hành trình của bạn.' : 'Mừng bạn trở lại!';
  if (user) {
    select('#profile-initial').textContent = initial;
    select('#profile-name').textContent = name;
    select('#profile-email').textContent = user.email || '';
    select('#profile-verified').textContent = user.emailVerified ? '✓ Email đã được xác minh' : 'Email chưa được xác minh';
    select('#verify-email').hidden = user.emailVerified;
    select('#refresh-profile').hidden = user.emailVerified;
    select('#profile-verified').classList.toggle('verified', user.emailVerified);
  } else {
    ['#profile-initial', '#profile-name', '#profile-email', '#profile-verified'].forEach((id) => { select(id).textContent = ''; });
  }
}
async function backendProfile(user, force = false) {
  const token = await user.getIdToken(force);
  const response = await fetch('/api/auth/me', {headers: {Authorization: `Bearer ${token}`}, cache: 'no-store', signal: AbortSignal.timeout(15000)});
  if (!response.ok) {
    const error = new Error('backend_auth');
    error.userMessage = response.status === 401 ? 'Phiên đăng nhập chưa được xác thực. Bạn đăng xuất rồi thử lại nhé.' : 'Bạn đã đăng nhập Firebase, nhưng chưa kết nối được hồ sơ trên máy chủ. Hãy thử lại sau.';
    throw error;
  }
  return (await response.json()).user;
}
async function ensureAuth() {
  if (configTask) return configTask;
  configTask = (async () => {
    try {
      const response = await fetch('/api/auth/config', {cache:'no-store', signal:AbortSignal.timeout(10000)});
      if (!response.ok) throw new Error('config_failed');
      const data = await response.json();
      if (!data.configured) { select('#auth-setup-message').hidden = false; return false; }
      const [appSDK, authSDK] = await Promise.all([
        import('https://www.gstatic.com/firebasejs/12.19.0/firebase-app.js'),
        import('https://www.gstatic.com/firebasejs/12.19.0/firebase-auth.js')
      ]);
      sdk = authSDK; auth = sdk.getAuth(appSDK.initializeApp(data.config)); auth.languageCode = 'vi';
      ready = true; select('#auth-setup-message').hidden = true; setBusy(false);
      sdk.onAuthStateChanged(auth, (user) => {
        const epoch = ++profileEpoch;
        displayUser(user);
        if (user) backendProfile(user).catch((error) => { if (epoch === profileEpoch) status(errorMessage(error), true); });
      });
      return true;
    } catch {
      status('Chưa tải được đăng nhập. Kiểm tra mạng rồi đóng và mở lại hộp đăng nhập để thử lại.', true);
      return false;
    }
  })();
  const result = await configTask;
  if (!result) configTask = null;
  return result;
}
document.querySelectorAll('[data-open-auth]').forEach((button) => button.addEventListener('click', () => { if (!dialog.open) dialog.showModal(); ensureAuth(); }));
select('#mode-login').addEventListener('click', () => setMode('login'));
select('#mode-register').addEventListener('click', () => setMode('register'));
select('#toggle-password').addEventListener('click', () => {
  const visible = select('#auth-password').type === 'password';
  select('#auth-password').type = visible ? 'text' : 'password';
  select('#toggle-password').textContent = visible ? 'Ẩn' : 'Hiện';
  select('#toggle-password').setAttribute('aria-label', visible ? 'Ẩn mật khẩu' : 'Hiện mật khẩu');
  select('#toggle-password').setAttribute('aria-pressed', String(visible));
});
async function persistence() { await sdk.setPersistence(auth, select('#remember-login').checked ? sdk.browserLocalPersistence : sdk.browserSessionPersistence); }
select('#auth-form').addEventListener('submit', async (event) => {
  event.preventDefault(); if (busy || !ready) return;
  const email = select('#auth-email').value.trim(), password = select('#auth-password').value, name = select('#auth-name').value.trim();
  if (mode === 'register' && !name) { status('Bạn nhập tên hiển thị nhé.', true); select('#auth-name').focus(); return; }
  if (mode === 'register' && password !== select('#auth-confirm-password').value) { status('Hai mật khẩu chưa giống nhau. Bạn nhập lại nhé.', true); select('#auth-confirm-password').focus(); return; }
  setBusy(true); status();
  try {
    await persistence();
    const credential = mode === 'register' ? await sdk.createUserWithEmailAndPassword(auth, email, password) : await sdk.signInWithEmailAndPassword(auth, email, password);
    if (mode === 'register') {
      try { await sdk.updateProfile(credential.user, {displayName: name}); }
      catch { displayUser(credential.user); status('Tài khoản đã tạo, nhưng chưa lưu được tên hiển thị. Bạn vẫn có thể đăng nhập.', true); return; }
      displayUser(credential.user);
      try { await sdk.sendEmailVerification(credential.user); status('Tài khoản đã tạo! Kiểm tra hộp thư để xác minh email.'); }
      catch { status('Tài khoản đã tạo. Bạn có thể bấm “Gửi email xác minh” để thử lại.'); }
    } else { status('Đăng nhập thành công. Chào mừng bạn trở lại!'); }
    await backendProfile(credential.user, true);
  } catch (error) { status(errorMessage(error), true); }
  finally { select('#auth-password').value = ''; select('#auth-confirm-password').value = ''; setBusy(false); }
});
select('#google-signin').addEventListener('click', () => {
  if (busy || !ready) return;
  setBusy(true); status();
  const provider = new sdk.GoogleAuthProvider(); provider.setCustomParameters({prompt: 'select_account'});
  // Mở popup ngay trong click để giữ quyền mở cửa sổ của trình duyệt.
  const popup = sdk.signInWithPopup(auth, provider);
  (async () => {
    try {
      const credential = await popup;
      await persistence();
      await backendProfile(credential.user);
      status('Đăng nhập Google thành công. Chào bạn!');
    } catch (error) { status(errorMessage(error), true); }
    finally { setBusy(false); }
  })();
});
select('#forgot-password').addEventListener('click', async () => {
  if (busy || !ready) return;
  const email = select('#auth-email');
  if (!email.value.trim() || !email.reportValidity()) { status('Nhập email ở ô phía trên để nhận đường dẫn đặt lại mật khẩu.', true); email.focus(); return; }
  setBusy(true); status();
  try {
    await sdk.sendPasswordResetEmail(auth, email.value.trim());
    status('Nếu email có tài khoản, bạn sẽ nhận được hướng dẫn đặt lại mật khẩu. Kiểm tra cả thư rác nhé.');
  } catch (error) { status(error.code === 'auth/user-not-found' ? 'Nếu email có tài khoản, bạn sẽ nhận được hướng dẫn đặt lại mật khẩu.' : errorMessage(error), error.code !== 'auth/user-not-found'); }
  finally { setBusy(false); }
});
select('#signout-button').addEventListener('click', async () => {
  if (busy || !ready) return;
  setBusy(true);
  try { await sdk.signOut(auth); select('#auth-form').reset(); busy = false; setMode('login'); status('Bạn đã đăng xuất. Hẹn gặp lại!'); }
  catch (error) { status(errorMessage(error), true); }
  finally { setBusy(false); }
});
select('#verify-email').addEventListener('click', async () => {
  if (busy || !auth?.currentUser) return;
  setBusy(true);
  try { await sdk.sendEmailVerification(auth.currentUser); status('Đã gửi email xác minh. Kiểm tra hộp thư và thư rác nhé.'); }
  catch (error) { status(errorMessage(error), true); }
  finally { setBusy(false); }
});
select('#refresh-profile').addEventListener('click', async () => {
  if (busy || !auth?.currentUser) return;
  setBusy(true);
  try { await sdk.reload(auth.currentUser); displayUser(auth.currentUser); await backendProfile(auth.currentUser, true); status(auth.currentUser.emailVerified ? 'Email đã được xác minh. Cảm ơn bạn!' : 'Chưa thấy email được xác minh. Bạn mở đường dẫn trong email rồi thử lại nhé.'); }
  catch (error) { status(errorMessage(error), true); }
  finally { setBusy(false); }
});
dialog.addEventListener('close', () => { select('#auth-password').value = ''; select('#auth-confirm-password').value = ''; select('#auth-password').type = 'password'; select('#toggle-password').textContent = 'Hiện'; select('#toggle-password').setAttribute('aria-pressed','false'); select('#toggle-password').setAttribute('aria-label','Hiện mật khẩu'); });
setBusy(false);
ensureAuth();
