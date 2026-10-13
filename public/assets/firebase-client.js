// Một cấu hình Firebase chung cho trang chủ và khu vực tư vấn.
let task;
export function getFirebase() {
  if (!task) task = initialize().catch((error) => { task = null; throw error; });
  return task;
}
async function initialize() {
  const response = await fetch('/api/auth/config', {cache: 'no-store', signal: AbortSignal.timeout(10000)});
  if (!response.ok) throw new Error('Không tải được cấu hình đăng nhập.');
  const data = await response.json();
  if (!data.configured) throw new Error('Đăng nhập Firebase chưa được cấu hình.');
  const [appSDK, sdk] = await Promise.all([
    import('https://www.gstatic.com/firebasejs/12.19.0/firebase-app.js'),
    import('https://www.gstatic.com/firebasejs/12.19.0/firebase-auth.js')
  ]);
  const application = appSDK.getApps().length ? appSDK.getApp() : appSDK.initializeApp(data.config);
  const auth = sdk.getAuth(application);
  auth.languageCode = 'vi';
  return {auth, sdk};
}
export async function restoredUser(auth, sdk) {
  return new Promise((resolve, reject) => {
    const unsubscribe = sdk.onAuthStateChanged(auth, (user) => { unsubscribe(); resolve(user); }, reject);
  });
}
