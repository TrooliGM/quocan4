# Bật đăng nhập Firebase cho La Bàn

Phần mã đã có: đăng ký/đăng nhập email và mật khẩu, đăng nhập Google, quên mật khẩu, xác minh email, xem tài khoản và đăng xuất. Cần tạo Firebase project và điền cấu hình trước khi đăng nhập thật.

## 1. Tạo project

1. Mở [Firebase Console](https://console.firebase.google.com/) và đăng nhập tài khoản Google của bạn.
2. Chọn **Create a project / Tạo dự án**, đặt tên `La Ban KHKT 2027`.
3. Google Analytics không bắt buộc cho chức năng đăng nhập; có thể bỏ qua.
4. Chờ project tạo xong và mở project đó.

## 2. Đăng ký website

1. Vào biểu tượng bánh răng cạnh **Project Overview → Project settings**.
2. Ở mục **Your apps**, chọn biểu tượng **Web `</>`**.
3. Đặt nickname `La Ban Web`, rồi chọn **Register app**. Không cần bật Firebase Hosting vì website dùng Vercel.
4. Chọn cấu hình SDK; sao chép đoạn `firebaseConfig`. Nếu giao diện hỏi npm/script tag, chỉ cần tìm đoạn cấu hình.

Ví dụ minh họa, cần thay bằng giá trị của chính project bạn:

```javascript
const firebaseConfig = {
  apiKey: "GIA_TRI_API_KEY",
  authDomain: "PROJECT_ID.firebaseapp.com",
  projectId: "PROJECT_ID",
  storageBucket: "...",
  messagingSenderId: "...",
  appId: "..."
};
```

Cấu hình Web này được dùng ở trình duyệt để nhận diện project. Tính năng đăng nhập hiện tại không cần `storageBucket` hoặc `measurementId`. Không gửi hay đưa service account/private key lên GitHub. [Tài liệu cấu hình Firebase Web](https://firebase.google.com/docs/web/learn-more#config-object).

## 3. Bật các cách đăng nhập

1. Vào **Build → Authentication → Get started**.
2. Chọn **Sign-in method / Sign-in providers**.
3. Chọn **Email/Password**, bật **Email/Password** và lưu. Không cần bật email link.
4. Chọn **Google**, bật, chọn email hỗ trợ của project rồi lưu.
5. Vào **Authentication → Settings → Authorized domains**. Thêm `localhost` và `127.0.0.1` nếu chưa có để chạy thử trên máy. Khi lên Vercel, thêm đúng hostname của website, ví dụ `ten-du-an.vercel.app`, không thêm `https://`, cổng hoặc đường dẫn.

[Đăng nhập email/mật khẩu](https://firebase.google.com/docs/auth/web/password-auth), [đăng nhập Google](https://firebase.google.com/docs/auth/web/google-signin).

## 4. Điền cấu hình trên máy

Mở thư mục `D:\khkt`. Nếu chưa có `.env`, sao chép `.env.example` và đổi tên bản sao thành `.env`. Nếu đã có `.env`, giữ các giá trị hiện tại rồi bổ sung các dòng dưới đây:

```env
FIREBASE_API_KEY=gia_tri_apiKey
FIREBASE_AUTH_DOMAIN=gia_tri_authDomain
FIREBASE_PROJECT_ID=gia_tri_projectId
FIREBASE_APP_ID=gia_tri_appId
FIREBASE_MESSAGING_SENDER_ID=gia_tri_messagingSenderId
```

Không chép dấu phẩy, dấu ngoặc hoặc toàn bộ đoạn JavaScript vào `.env`. Không thay đổi các dòng DeepSeek đang dùng.

Trong PowerShell:

```powershell
cd D:\khkt
python -m pip install -r requirements.txt
python -m uvicorn app:app --reload
```

Nếu server đã chạy, nhấn **Ctrl + C** rồi chạy lại sau khi sửa `.env`. Mở **http://127.0.0.1:8000**, bấm **Đăng nhập** ở góc trên bên phải.

## 5. Kiểm tra thật

- Chọn **Tạo tài khoản**, nhập tên hiển thị, email bạn có thể nhận thư và mật khẩu.
- Kiểm tra tài khoản xuất hiện trong **Firebase Console → Authentication → Users**.
- Mở thư xác minh, bấm đường dẫn rồi quay lại website và chọn **Tôi đã xác minh**.
- Đăng xuất, thử đăng nhập lại bằng email/mật khẩu.
- Thử **Quên mật khẩu**, kiểm tra thư đặt lại mật khẩu.
- Thử **Tiếp tục với Google**. Nếu popup bị chặn, cho phép popup của trang rồi thử lại.
- Tải lại trang để xem trạng thái đăng nhập được giữ. Mặc định là phiên của tab; chỉ chọn **Giữ đăng nhập trên thiết bị này** trên máy cá nhân.

## Vercel

Trong project Vercel, thêm năm biến `FIREBASE_*` trên ở **Settings → Environment Variables**, rồi redeploy. Thêm hostname triển khai vào **Authorized domains** của Firebase. Các tên miền preview mới cũng cần được cho phép nếu dùng để thử Google login.

## Cách xác thực và giới hạn

- Browser gửi mật khẩu trực tiếp tới Firebase SDK, không gửi mật khẩu qua backend Python.
- Browser dùng Firebase ID token làm Bearer token cho `/api/auth/me`. Backend dùng `google-auth` để xác minh chữ ký, thời hạn và audience, đồng thời kiểm tra issuer, subject, auth_time và RS256/kid. Khóa công khai được cache theo `max-age`.
- Không cần service account cho bước xác minh token này. [Google Auth](https://google-auth.readthedocs.io/en/latest/reference/google.oauth2.id_token.html), [yêu cầu kiểm tra ID token của Firebase](https://firebase.google.com/docs/auth/admin/verify-id-tokens).
- Chưa kiểm tra thu hồi token hoặc trạng thái disabled theo thời gian thực trên backend. ID token đã phát có thể còn hiệu lực đến khi hết hạn; cần bổ sung Firebase Admin và kiểm tra revocation trước khi xây chức năng quản trị nhạy cảm.
- Không ghi hồ sơ hay lịch sử vào Firestore ở bước này; tài khoản được Firebase Authentication quản lý. AI/trang chủ vẫn dùng được như trước, không yêu cầu đăng nhập.
- Chưa tích hợp Zalo.

## Lỗi thường gặp

| Hiện tượng | Cách xử lý |
| --- | --- |
| “Đăng nhập đang được thiết lập” | Kiểm tra đủ 4 biến bắt buộc: API_KEY, AUTH_DOMAIN, PROJECT_ID, APP_ID; khởi động lại server. |
| Cách đăng nhập chưa được bật | Bật provider tương ứng ở Firebase Authentication. |
| Địa chỉ website chưa được bật | Thêm hostname vào Authorized domains. |
| Firebase đăng nhập được nhưng hồ sơ server lỗi | Kiểm tra PROJECT_ID đúng với project Web; máy chủ cần truy cập chứng thư công khai của Google. |
| Không thấy thư | Kiểm tra email, thư rác và giới hạn gửi thư Firebase; chờ một chút trước khi gửi lại. |
