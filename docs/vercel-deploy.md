# Chuẩn bị Vercel cho La Bàn

Kiểm tra ngày 2026-10-13. Đây là hướng dẫn chuẩn bị và triển khai, chưa phải xác nhận đã deploy. Không có commit/push tự động. `.env`, mã đăng nhập Firebase, project Firebase và database hiện có được giữ nguyên trong lần chuẩn bị này.

## 1. Entrypoint và runtime

Entrypoint chính xác: **`app.py`, biến `app`, đường dẫn import `app:app`**. `app.py` là tên Vercel tự nhận diện khi tìm ứng dụng FastAPI. Giữ `[tool.vercel] entrypoint = "app:app"` hiện có để khai báo rõ. Không cần thêm `api/index.py`, `handler`, cấu hình `routes`, `rewrites` hoặc đổi framework.

`vercel.json` chỉ có schema và `framework: "fastapi"`. Không có Build/Output Directory tùy chỉnh. Python 3.14 được chọn trong `.python-version`, cùng dòng phiên bản đã kiểm thử local; `requires-python` cho phép 3.12–3.14. Vercel hiện hỗ trợ cả ba dòng này.

Dependencies runtime có trong `requirements.txt` và `[project].dependencies` của `pyproject.toml`; giữ hai danh sách đồng bộ khi thêm thư viện. Thêm Pydantic trực tiếp vì mã ứng dụng import thư viện này. Các ràng buộc phiên bản hiện là khoảng tương thích, chưa phải lockfile đầy đủ cho dependencies gián tiếp.

Nguồn đối chiếu:

- [FastAPI trên Vercel](https://vercel.com/docs/frameworks/backend/fastapi)
- [Python Runtime và dependencies](https://vercel.com/docs/functions/runtimes/python)
- [Chọn phiên bản Python](https://vercel.com/docs/functions/runtimes/python/python-version)

## 2. Giao diện và tài sản

- `/` phục vụ `public/index.html`; `/ai-career-advisor` phục vụ `public/chat.html`; `/mot-ngay-lam-viec` phục vụ `public/stories.html`.
- Vercel tự phục vụ `public/assets/*` qua CDN tại `/assets/*`. Local dùng StaticFiles khi không có biến `VERCEL`.
- Giữ các tệp HTML trong bundle vì FileResponse cần đọc chúng. Không thêm excludeFiles loại `public/**` khỏi bundle.
- Frontend gọi API theo đường dẫn cùng origin `/api/...`; không có endpoint localhost cố định. Các chữ localhost trong thông báo micro không phải URL kết nối. `http://www.w3.org/2000/svg` là namespace SVG.
- Bootstrap/font/Firebase SDK/Marked/DOMPurify lấy qua HTTPS CDN, cần kiểm tra trên deployment thực tế.
- Frontend và backend ở chung một project/tên miền nên không cần mở CORS cho domain ngoài.

## 3. Firebase và biến môi trường

Backend hiện **không dùng Firebase Admin SDK**. `firebase_auth.py` dùng `google-auth` và chứng thư công khai của Google để xác minh Firebase ID token. Không cần `FIREBASE_PRIVATE_KEY`, service account hay private key cho luồng đăng nhập này. Nếu sau này thêm Admin SDK cho chức năng quản trị, cần cấu hình secrets riêng; chưa thay đổi ở đây.

Trong **Vercel > Project > Settings > Environment Variables**, đặt các biến theo cấu hình `.env` local đã có; không sao chép giá trị minh họa từ `.env.example` lên production:

| Biến | Mục đích |
| --- | --- |
| `FIREBASE_API_KEY` | Firebase Web API key của ứng dụng đang dùng |
| `FIREBASE_AUTH_DOMAIN` | Auth domain hiện tại của Firebase |
| `FIREBASE_PROJECT_ID` | Project hiện tại, phải khớp token dùng cho backend |
| `FIREBASE_APP_ID` | ID ứng dụng Web hiện tại |
| `FIREBASE_MESSAGING_SENDER_ID` | Sender ID trong cấu hình Web hiện tại |
| `DEEPSEEK_API_KEY` | Khóa server cho AI thật; đánh dấu sensitive nếu nền tảng cho phép |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | `deepseek-flash` hoặc model được tài khoản hỗ trợ |
| `DEEPSEEK_SUMMARY_MODEL` | Tùy chọn; bỏ qua để dùng model chính |
| `AI_DEMO_MODE` | `false` cho AI thật; `true` chỉ để thử bản mẫu có nhãn |

`DATABASE_URL` cần phương án lưu trữ được hỗ trợ trước khi mở chat công khai; xem mục 4. Không nhập URL PostgreSQL vào code hiện tại rồi cho rằng đã chuyển database.

`GOOGLE_CLOUD_PROJECT_ID` và `GOOGLE_APPLICATION_CREDENTIALS` chỉ dành cho Google Speech khi có cấu hình tương ứng, không phải Firebase Authentication. Mic trình duyệt không cần chúng. Vbee không thuộc chức năng hiện tại, không cần đưa token Vbee lên Vercel.

Không tự đặt `VERCEL`: nền tảng cung cấp biến này. Sau khi thêm/sửa Environment Variables, redeploy để áp dụng. Chỉ cấp biến cho Production/Preview cần thiết; không đưa secrets vào frontend hoặc `public/`.

## 4. Điều kiện còn thiếu: dữ liệu chat bền vững

**Chưa thể công bố toàn bộ chat tài khoản trên Vercel với storage hiện tại.** SQLite dùng `data/advisor.sqlite3`; phiên tạm, khóa phiên và giới hạn đồng thời nằm trong RAM một tiến trình. Hệ thống Vercel có nhiều instance và không cung cấp ổ file local dùng chung bền vững. Ngay việc liệt kê phiên chat cũng truy cập SQLite; vì vậy đăng nhập có thể xác thực thành công nhưng trang chat gặp lỗi lưu trữ.

Không di chuyển SQLite vào `/tmp` để xử lý production. `/tmp` không làm dữ liệu thành bền vững hoặc dùng chung. `AI_DEMO_MODE=true` cũng không giải quyết vấn đề storage vì chat vẫn dùng store hiện tại.

Đề xuất: **PostgreSQL managed** qua nhà cung cấp phù hợp (ví dụ Neon/Supabase), kết nối có TLS/pooling, viết adapter thay lớp lưu trữ hiện tại. Giữ Firebase Authentication và ánh xạ dữ liệu theo Firebase UID; không cần đổi sang hệ thống đăng nhập của nhà cung cấp database. Cần xử lý cả phiên tạm có TTL và idempotency/khóa giao dịch dùng chung trước khi chạy nhiều instance. Firestore là lựa chọn khác, cũng cần adapter và credentials/permissions tương ứng.

Đây chỉ là đề xuất: chưa tạo database ngoài, chưa migrate, chưa sửa hoặc xóa database local. Dữ liệu hiện có cần được sao lưu và có kế hoạch chuyển riêng nếu muốn giữ lịch sử cũ.

[Vercel giải thích giới hạn SQLite](https://vercel.com/kb/guide/is-sqlite-supported-in-vercel).

## 5. Loại trừ bí mật

`.gitignore` và `.vercelignore` loại `.env`/biến thể, dữ liệu SQLite, credentials, service-account JSON theo các mẫu tên thường gặp, `secrets/`, `.secrets/`, `.pem` và `.key`. `.env.example` được phép lưu Git vì chỉ có giá trị minh họa.

Ignore không tự gỡ file đã từng được Git theo dõi. Trước commit do người dùng chủ động thực hiện, xem danh sách staged files và quét secrets, cả lịch sử khi cần. Credentials có tên khác các mẫu cũng phải để ngoài repository. Khóa dịch vụ từng được chia sẻ cần thay trước production; không in lại giá trị.

## 6. Kiểm tra local và triển khai từ GitHub

1. Hoàn tất lựa chọn/triển khai storage bền vững và giới hạn API AI trước khi cho người dùng thật sử dụng chat. Hai endpoint AI công khai hiện chưa có hạn mức theo tài khoản/IP.
2. Kiểm tra local như mục 7. Khi người dùng tự quyết định lưu bản mới lên GitHub, commit/push các thay đổi đã xem lại; lần chuẩn bị này không thực hiện bước đó. Vercel chỉ lấy bản trên GitHub, không lấy file chưa push trong VS Code.
3. Trong Vercel chọn **Add New > Project**, import `TrooliGM/quocan4`, Root Directory là gốc repository.
4. Xác nhận preset **FastAPI** được nhận diện. Giữ mặc định Install/Build/Output, không chọn preset HTML static/Next.js, không thêm catch-all rewrite và không dùng lệnh Uvicorn làm Build Command.
5. Thêm Environment Variables ở mục 3 cho đúng môi trường. Xác nhận Build Logs chọn Python 3.14 và cài đủ dependencies. Nếu cần chỉ thử trang chủ/Firebase trước khi hoàn thiện database, dùng preview có bảo vệ; không xem đây là bản chat production hoạt động đầy đủ.
6. Sau deploy, lấy hostname `ten-du-an.vercel.app`. Trong **Firebase Console > Authentication > Settings > Authorized domains**, thêm đúng hostname này, không có `https://` hoặc đường dẫn. Giữ nguyên Firebase project và authDomain hiện có. Thêm domain riêng nếu có; tránh phải thêm mọi hostname preview bằng cách dùng một domain thử ổn định.
7. Kiểm tra `/`, `/mot-ngay-lam-viec`, `/api/health`, `/api/auth/config` và `/assets/compass.svg`. Không chia sẻ bản chụp chứa giá trị cấu hình/secrets khi kiểm tra.
8. Thử tạo tài khoản, email/password, Google popup, quên mật khẩu, đăng xuất và chuyển thẳng chat bằng tài khoản thử. Sau khi có storage mới, kiểm tra hai tài khoản không đọc dữ liệu nhau, reload/deploy không mất lịch sử đã đồng ý lưu, phiên tạm hết hạn đúng và yêu cầu gửi lại không tạo trùng.

Vercel cung cấp HTTPS cho domain deployment. Kiểm tra micro trên HTTPS và quyền trình duyệt. Chưa có kết quả build/deploy Vercel thực tế được xác nhận trong lần chuẩn bị này.

## 7. Chạy local

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app:app --reload
```

Mở `http://localhost:8000`. Không ghi đè `.env` đang có. Nếu máy mới chưa có `.env`, sao chép `.env.example` rồi điền cấu hình riêng.

Kiểm tra backend bằng `python -m unittest discover -s tests -v`; kiểm thử trình duyệt bằng `python tests/browser_login.py` và `python tests/browser_stories.py`. Các script browser dùng Firebase/AI giả lập và database kiểm thử riêng. Không thay thế kiểm thử Firebase thật trên domain Vercel.
