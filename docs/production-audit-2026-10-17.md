# Kiểm tra và sửa Vercel – La Bàn, 2026-10-17

## A. Tổng quan

Làm việc tại `D:\khkt`. Nhánh sửa mới `fix/vercel-ai-postgres`, bắt đầu từ `ad18135` của `fix-chat-vercel`. Giữ nguyên tài liệu chưa commit, thư mục backup và các tệp lạ chưa được theo dõi. Không stash/reset, không sửa lịch sử `backup-la-ban`, không commit/push/deploy.

Đã sửa trong workspace:

- HTML runtime có bản ở gốc và cấu hình đưa vào Function; xử lý thiếu trang bằng HTTP 503 có hướng dẫn.
- Không fallback SQLite `/tmp` trên Vercel; chuẩn hóa khoảng trắng trong cấu hình database.
- Phân biệt lỗi cấu hình, kết nối, quyền và schema; không log DSN/SQL hoặc trả chi tiết database cho trình duyệt.
- Bổ sung migration hai bảng hội thoại; quota migration có transaction và giới hạn chờ khóa.
- Dùng chung cấu hình/lỗi DeepSeek cho ba endpoint; tổng thời gian sinh câu trả lời và nén bộ nhớ được giới hạn. Lỗi nén, kể cả thiếu prompt, không bỏ câu trả lời hợp lệ.
- Loại thư mục backup và tệp `.backup` khỏi Git/upload Vercel; không xóa các tệp đó.

Chưa xác minh: schema/quyền/kết nối Neon Production, khóa/model DeepSeek thật, Firebase popup/Anonymous thật, Function Bundle và cấu hình Dashboard Vercel của deployment mới. Không gọi AI thật hoặc kết nối database Production trong lần này.

### Bằng chứng phiên bản và website công khai

Đọc ref GitHub bằng `git ls-remote`, không thay đổi ref:

- `backup-la-ban`: `cf4d55dfe5dd`.
- `fix-chat-vercel`: `ad18135b6953`.

GET công khai, không token, không gọi AI:

| Đường dẫn | Kết quả lúc kiểm tra |
| --- | --- |
| `/` | 200 HTML |
| `/ai-career-advisor?start=1` | 200 HTML |
| `/mot-ngay-lam-viec` | 200 HTML |
| `/api/health` | 200 JSON; chỉ chứng minh tiến trình trả lời, không chứng minh database sẵn sàng |
| `/assets/chat.js` | 200 JavaScript |

HTML chat và `chat.js` lấy từ domain công khai trùng byte với file tương ứng tại `backup-la-ban` sau chuẩn hóa CRLF/LF. Chúng chưa có giao diện quota khách. Đây là bằng chứng nội dung đang phục vụ tương ứng bản cũ, không thay thế việc xem Git commit/nhánh trong Vercel Dashboard. Không tái hiện được lỗi 500 cũ trong lần GET này.

## B. Nguyên nhân gốc và bản đồ kiến trúc

### Route và luồng dữ liệu

| Đường dẫn | Mục đích và quyền |
| --- | --- |
| `/`, `/ai-career-advisor`, `/chat`, `/mot-ngay-lam-viec` | HTML công khai; `/chat` là alias bổ sung của trang tư vấn |
| `/assets/*` | Local StaticFiles; Vercel phục vụ qua CDN từ `public/assets` |
| `/api/auth/config` | Chỉ cấu hình Firebase Web công khai |
| `/api/auth/me` | Xác minh ID token Firebase |
| `/api/careers`, `/api/articles`, `/api/career-stories/*` GET | Danh mục và truyện công khai |
| `/api/ai/config`, `/api/ai/sessions`, `/api/ai/chat` | Firebase token; session gắn UID; khách có quota 8 |
| `/api/ai/sessions/{id}`, `/api/ai/career-profile`, `/api/ai/data` | Kiểm tra quyền tài khoản, quản lý lịch sử/hồ sơ |
| `/api/ai/guest/claim` | Hai ID token, chuyển lịch sử khách sau khi đăng nhập tài khoản đích |
| `/api/voice/transcribe` | Firebase token, Google STT nếu cấu hình; chưa có ngân sách chi phí riêng |
| `/api/advice`, `/api/career-stories/{id}/ask` POST | AI công khai cũ; chưa có hạn mức phân tán theo UID/IP |

Nút **Bắt đầu khám phá** hiện trỏ tới `#careers`, không trực tiếp mở chat. Menu **Tư vấn cùng AI** và banner trò chuyện mới đi tới `/ai-career-advisor`. Đăng nhập email/Google thành công dùng `/ai-career-advisor?start=1`. Giữ nguyên điều hướng và thiết kế này; chưa có bài trắc nghiệm hướng nghiệp trong source.

Frontend dùng đường dẫn API cùng origin; không cần mở CORS cho mọi domain. `chat.js` lấy Firebase ID token rồi POST JSON `{session_id, request_id, message}` tới `/api/ai/chat`. Backend xác minh chữ ký/audience/issuer/thời hạn, xác định UID/provider, kiểm tra chủ sở hữu phiên, rate/quota, chạy LangGraph, lưu cặp tin nhắn nguyên tử vào PostgreSQL. Markdown được xử lý bằng Marked + DOMPurify. API key DeepSeek chỉ dùng trên server.

### Lỗi A: HTML không có trong runtime

- **Bằng chứng:** log người dùng cung cấp chỉ rõ không có `/var/task/public/chat.html`; `app.py` ở `backup-la-ban` dùng FileResponse với đường dẫn đó. Có file trong Git không chứng minh nó nằm trong Function Bundle.
- **Điều đã xác nhận:** route cũ phụ thuộc vào file `public/` tại runtime và không bắt lỗi khi thiếu. Source local mới trước lần này đã có chat/stories ở gốc, nhưng trang chủ còn phụ thuộc `public/index.html`.
- **Chưa xác nhận:** chính xác bước build, cache hoặc thiết lập nào từng loại file của deployment lỗi; không có bundle/log Dashboard của bản đó. Hiện GET chat là 200 nên không gán nguyên nhân 500 hiện tại cho một giả thuyết chưa kiểm chứng.
- **Sửa:** `app.py:41` đọc HTML bằng `Path(__file__).resolve()`; ưu tiên file gốc, fallback public cho local/checkout cũ. Lỗi đọc file trả trang 503 có liên kết trang chủ và log tên trang, không lộ đường dẫn máy. Thêm `index.html` trùng bản public. `vercel.json` giữ FastAPI và chỉ thêm `functions.app.py.includeFiles` cho ba HTML + prompt. Không thêm routes/rewrites hoặc hardcode `/var/task`.
- **Rủi ro:** HTML gốc và public có thể lệch nếu sửa riêng. Kiểm thử so sánh byte cả ba cặp. Cần kiểm tra Function Bundle/Preview thực tế; mô phỏng local chưa chứng minh builder Vercel hoạt động.

Đối chiếu [FastAPI trên Vercel](https://vercel.com/docs/frameworks/backend/fastapi), [Python Runtime](https://vercel.com/docs/functions/runtimes/python), [functions/includeFiles](https://vercel.com/docs/project-configuration/vercel-json#functions): `app:app` được nhận diện; public là tài sản CDN; `functions` được cấu hình theo entrypoint `app.py`. Python local 3.14.7 nằm trong các dòng runtime được hỗ trợ, dependencies không đổi framework.

### Lỗi B: chế độ khách/database

- **Nguồn thông báo:** `advisor/routes.py:79`, `guest_usage()`, phát thông báo khi `get_store()` không phải `PostgresConversationStore`. Trong `/api/ai/chat` còn một nhánh kiểm tra tương tự. Đây là kiểm tra chọn adapter, không phải kết quả thử kết nối hay schema Neon.
- **Bằng chứng:** `backup-la-ban` chưa có adapter PostgreSQL/guest quota. Nhánh `fix-chat-vercel` mới có adapter, bảng quota và liên kết tài khoản. Chỉ khai báo DATABASE_URL không bổ sung chức năng còn thiếu ở bản đang deploy.
- **Lỗi code local xác nhận:** `get_store()` trước bản sửa dùng `/tmp/advisor.sqlite3` khi thiếu/để trống DATABASE_URL trên Vercel; không strip URL trước chọn adapter, trong khi hàm kết nối có strip. Một môi trường có thể chọn sai store vì khoảng trắng. Không có cơ chế fallback sau kết nối PostgreSQL lỗi, và giữ nguyên việc không fallback này.
- **Sửa:** `advisor/store.py:183` bắt buộc PostgreSQL trên Vercel, giữ SQLite cho local. `.env` chỉ được nạp ở local, không nạp trong Vercel. `app.py:35` + `advisor/storage_errors.py` trả mã lỗi an toàn phân biệt cấu hình/schema/quyền/kết nối/thao tác. Route chat chuyển lỗi psycopg tới handler chung sau logic đối chiếu/hoàn quota hiện có.
- **Schema thiếu trong repository:** chỉ có `002_guest_quota.sql`, chưa có script tạo `advisor_sessions` và `advisor_temporary_sessions`. `initialize_postgres()` chỉ tạo bảng lâu dài và không được dùng làm migration startup. Bổ sung `001_conversations.sql`; không tự chạy startup DDL.
- **Kết nối:** psycopg3, mỗi context đóng connection và commit/rollback. Thêm statement timeout 10s, lock timeout 3s, idle-in-transaction 15s. Không thêm pool theo từng instance. Production nên dùng URL pooled có TLS do Neon cung cấp, giữ nó trong server environment.
- **Chưa xác nhận:** schema, quyền, URL theo Production/Preview, TLS, trạng thái kết nối Neon thực tế. Script `scripts/check_storage.py` chỉ đọc metadata và chỉ nhận biến riêng `LABAN_CHECK_DATABASE_URL`, không tự nạp `.env` hay lấy DATABASE_URL Production.

### Lỗi C: DeepSeek không ổn định

- Ba endpoint: `/api/ai/chat` qua `advisor/graph.py`; `/api/advice` qua `ai.py`; hỏi theo cảnh qua `story_ai.py` rồi tái sử dụng `ai.ask_deepseek()`.
- **Lỗi xác nhận từ code:** cấu hình URL/model/key xử lý khác nhau giữa các luồng; public AI gom các lỗi provider thành 502; vài dạng response sai gây AttributeError; main chat có thể chờ 2 lần 40s + nén 20s trong route timeout 90s. Thiếu file memory prompt ngoài khối try có thể làm mất một câu trả lời tốt.
- **Sửa:** `deepseek_client.py:25` chuẩn hóa cấu hình, kiểm tra URL HTTPS không chứa credentials/query/fragment; `model_name()` tôn trọng model đã cấu hình, không tự đổi tài khoản. `provider_http_error()` phân biệt 401/403, 402, 429, 5xx, cấu hình request/model và timeout; không trả body provider. Luồng công khai kiểm tra choices/content/finish_reason trước trả lời.
- `advisor/graph.py:120`: tổng bước sinh câu trả lời giới hạn 55s; nén bộ nhớ tối đa 12s, HTTP timeout 10s. Lỗi nén/mất file prompt phụ giữ nguyên câu trả lời/hồ sơ trước đó, không bịa metadata. Timeout route 90s và cơ chế request_id/quota/lưu nguyên tử giữ nguyên.
- **Chưa xác nhận:** API key hợp lệ, số dư, quyền model hoặc model tài khoản thật. `AI_DEMO_MODE=false` cần cấu hình thật; không bật demo để che lỗi Production. [Tài liệu DeepSeek hiện hành](https://api-docs.deepseek.com/) dùng `deepseek-flash`; `deepseek-chat` trong brief chỉ là cấu hình dự kiến, không đủ bằng chứng phải thay model. Chưa gọi API thật.

### Lỗi D: các luồng khác

Không thấy endpoint localhost cố định, đường dẫn ổ D dùng cho request frontend hoặc CORS đa origin cần bổ sung. Trang chủ, assets, đăng nhập/đăng xuất, profile, lịch sử, chat, mic và truyện nghề qua kiểm thử cũ. Không thay HTML/CSS/JS hoặc viết lại xác thực Firebase; bản index gốc chỉ sao chép byte từ public. Không tạo bài trắc nghiệm hoặc chức năng sản phẩm mới.

## C. File đã thay đổi

| File | Mục đích |
| --- | --- |
| `app.py` | Đọc HTML có xử lý lỗi, alias chat, handler storage, lỗi DeepSeek chung; dotenv local |
| `index.html` (mới) | Bản HTML trang chủ trong Function, trùng public |
| `vercel.json` | includeFiles cho HTML/prompt, giữ FastAPI tự nhận diện |
| `.gitignore`, `.vercelignore` | Loại backups và tệp backup khỏi Git/upload, giữ nguyên file |
| `advisor/store.py` | Chọn adapter đúng, từ chối SQLite trên Vercel |
| `advisor/postgres_store.py` | Giới hạn chờ truy vấn/khóa/kết nối idle transaction |
| `advisor/storage_errors.py` (mới) | Mã lỗi storage an toàn |
| `advisor/schema_check.py` (mới) | Đọc metadata và báo schema thiếu/khác kiểu |
| `scripts/check_storage.py` (mới) | Chẩn đoán schema read-only bằng biến môi trường riêng |
| `migrations/001_conversations.sql` (mới) | Hai bảng hội thoại và index, không sửa dữ liệu cũ |
| `migrations/002_guest_quota.sql` | Bọc transaction, giới hạn chờ; giữ SQL bổ sung hiện có |
| `deepseek_client.py` (mới), `ai.py` | Chuẩn hóa provider và lỗi cho AI công khai |
| `advisor/graph.py`, `advisor/routes.py` | Tổng timeout, nén không làm mất answer, phân loại lỗi |
| `tests/postgres_fixture.py` | Khởi tạo schema kiểm thử bằng migration thực tế |
| `tests/test_release_runtime.py`, `tests/test_release_postgres.py` (mới) | Runtime, provider, migration, schema và bảo vệ dữ liệu |
| `tests/test_ai.py`, `tests/test_stories.py` | Kỳ vọng 503 cho lỗi khóa provider thay vì 502 chung |
| Tài liệu báo cáo này, `project-memory.md`, `decisions.md`, `validation.md` | Bằng chứng, quyết định và giới hạn kiểm chứng |

Các thay đổi tài liệu trước phiên và `docs/guest-chat.md` vẫn giữ nguyên, không tự stage. Không đổi `requirements.txt`, `pyproject.toml`, `.python-version`, Firebase project, database hay thiết kế giao diện.

## D. Kết quả kiểm thử

- Backend: `python -m unittest discover -s tests -v` — **59 bài đạt, không có bài thất bại hoặc skip**; gồm 21 bài PostgreSQL local thật, AI mock. Các ma trận trong từng bài kiểm tra nhiều mã HTTP/endpoint. Kết nối runtime thật tại local đã xác nhận đủ ba timeout database.
- `browser_guest.py` — PostgreSQL local + Firebase/AI giả lập: 8 câu, chặn 9, nâng cấp email/Google, giữ lịch sử và thử lại khi chuyển thất bại, mobile.
- `browser_smoke.py` — chat, lịch sử, đổi tên, Markdown/XSS, profile, mic và đăng xuất.
- `browser_login.py` — đăng nhập mở chat, khôi phục phiên, không tạo trùng, backend lỗi, về trang chủ.
- `browser_stories.py` — sáu nghề, cảnh, comic, bàn phím, tự chuyển, AI ngữ cảnh, XSS, mobile/giảm chuyển động.
- Kiểm tra cú pháp 26 file Python; `pip check` không có dependency lỗi; requirements và pyproject khớp, phiên bản đã cài nằm trong ràng buộc. `git diff --check` không có lỗi khoảng trắng.
- Mô phỏng runtime Function tách biệt không có `public/`, không đọc `.env`: ba trang + alias trả HTML 200, API riêng tư không token trả 401. Đây là mô phỏng, không phải `vercel build`.
- Chưa chạy Vercel CLI build/Preview vì máy không có Node/Vercel CLI và chưa có cấu hình môi trường Preview được cấp. Không cài công cụ/dịch vụ ngoài để thay thế bằng một deployment không được duyệt.
- Chưa thử key DeepSeek, đăng nhập Firebase thật, microphone thiết bị thật hoặc Neon Production. Kiểm tra GET công khai chỉ chứng minh một số trang/tài sản hiện trả lời, không chứng minh chat thật.

## E. Cơ sở dữ liệu và migration an toàn

PostgreSQL hiện lưu cả phiên lâu dài, phiên tạm có expires_at, quota/requests, tài khoản nhận lịch sử và rate limit. UID là khóa phân quyền; không lưu token vào dữ liệu hội thoại. SQLite local/dữ liệu sẵn có không bị di chuyển hoặc xóa. Không coi SQLite `/tmp` là nơi lưu lâu dài hoặc tự động cứu dữ liệu đã mất từ deployment cũ.

1. Sao lưu database đang dùng bằng snapshot/PITR của nhà cung cấp hoặc `pg_dump` qua credentials bảo mật, lưu ngoài repository. Không dán URL có mật khẩu vào báo cáo/ảnh/log. Thử phục hồi trên database riêng trước khi dựa vào backup.
2. Tạo branch/database thử riêng theo quyền và gói hiện có của bạn. Không tự tạo dịch vụ trả phí. Bản sao có dữ liệu thật phải được bảo vệ tương đương Production.
3. Cấp URL thử nghiệm cho biến `LABAN_CHECK_DATABASE_URL` bằng cơ chế quản lý secrets của môi trường, chạy `python scripts/check_storage.py`. Script chỉ đọc metadata trong transaction READ ONLY; không đọc hội thoại hoặc xuất URL. Có thể dùng script cho Production chỉ khi bạn chủ động cho phép đọc, chưa thực hiện ở đây.
4. Đối chiếu missing_tables/missing_columns/incompatible_columns. Check hiện dùng kiểu TEXT/INTEGER/TIMESTAMPTZ theo code, không tự chuyển JSONB/UUID hay kiểu khác. Nếu schema thực tế khác, dừng và soạn migration riêng sau khi xem metadata; không chạy mù.
5. Trên database thử, xem lại rồi áp dụng `001_conversations.sql`, sau đó `002_guest_quota.sql`. CREATE IF NOT EXISTS không chỉnh kiểu cột có sẵn. Nếu chỉ thiếu quota có thể chỉ cần 002 sau khi xác nhận 001 đã tương ứng. Cả hai script không xóa/reset dữ liệu.
6. Chạy lại schema check, rồi thử hai tài khoản riêng, cả remember=False/True, đủ 8 câu/9, retry request_id, lỗi AI và nâng cấp giữ lịch sử. Lệnh test tự động chỉ dùng cluster local do fixture tạo.
7. DDL có thể lấy khóa bảng; mỗi migration giới hạn chờ khóa 3s và statement 30s, một transaction/migration. Timeout/lỗi cần dừng, kiểm tra rollback, chọn thời điểm ít tải để thử lại. Index thông thường có thể chặn ghi trong lúc tạo; đánh giá kích thước bảng trước Production.
8. Chỉ chạy migration Production sau khi bạn duyệt schema, backup, SQL và thời điểm thực hiện. Lần làm việc này dừng ở migration đã kiểm thử local, chưa yêu cầu kết nối để sửa Production.

Nếu migration đang chạy lỗi, transaction rollback. Nếu đã commit, không dùng DROP để đảo ngược: giữ bảng/cột bổ sung và rollback tới bản ứng dụng đã xác nhận tương thích PostgreSQL. Không mặc định rollback code về `backup-la-ban`, vì nhánh đó chưa có adapter PostgreSQL. Phục hồi backup phải thử ở môi trường riêng và có kế hoạch dữ liệu phát sinh sau backup; không ghi đè Production tự động.

## F. Triển khai từng bước, chưa thực hiện

1. Xem diff trên `fix/vercel-ai-postgres`, đặc biệt HTML/includeFiles, store và SQL; giữ tệp backup/tệp lạ ngoài danh sách stage. Không dùng `git add .` mà không xem từng tệp. Không có commit hoặc push tự động trong lần này.
2. Kiểm tra Environment Variables theo đúng **Preview** và **Production**, không chỉ nhìn tên biến: `DATABASE_URL` (PostgreSQL pooled/TLS), `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`, `DEEPSEEK_MODEL`, tùy chọn `DEEPSEEK_SUMMARY_MODEL`, `AI_DEMO_MODE=false`, và các biến Firebase Web đang dùng. Không đưa khóa vào public/HTML/JavaScript.
3. Sau khi bạn cho phép lưu/push nhánh sửa, tạo Preview của đúng nhánh/commit; dùng database thử riêng. Dashboard: preset FastAPI, Root Directory đúng gốc repository, không chọn static-only Output Directory, không thêm Build Command/rewrites từ framework khác. Giữ entrypoint `app:app`.
4. Xem Build Logs xác nhận Python/dependencies. Kiểm tra Function Bundle có `index.html`, `chat.html`, `stories.html`, `advisor/prompt.txt`, `advisor/memory-prompt.txt`; assets public nằm trên CDN. File có trên GitHub nhưng không có trong bundle vẫn phải xử lý ở build.
5. Kiểm tra Function duration trong Dashboard đủ cho route chat 90s, hoặc đánh giá lại budget trên gói đang dùng. Fluid compute và giới hạn gói cần xác nhận trên project; không tự mua gói hoặc thay setting trong lần này. Preview phải thử tình huống provider chậm trước Production.
6. Runtime Logs: tìm `html_page_unavailable`, `storage_failure code=...`, `deepseek_failure code=...`, `advisor_memory_failed type=...`; không yêu cầu log key, token, raw response, prompt hoặc DSN. `/api/health` chỉ là liveness.
7. Preview: thử trang chủ/chat/truyện/assets/404; Google/email/đăng xuất; chat/lịch sử/profile; hai tài khoản không đọc được nhau; guest 1–8/9; remember hai chế độ và nâng cấp giữ lịch sử. Bật Anonymous và thêm domain Preview vào Firebase chỉ khi bạn duyệt, giữ project hiện tại.
8. Chỉ khi Preview đạt, bạn xác nhận commit/nhánh sẽ triển khai, các migration và điều kiện rollback, mới chuyển Production. Không mặc định merge hoặc đổi Production branch từ `backup-la-ban`.

## G. Trạng thái cuối cùng và rủi ro còn lại

| Trạng thái | Nội dung |
| --- | --- |
| Đã sửa và kiểm thử local | HTML thiếu, store fail-closed, phân loại lỗi storage, cấu hình/lỗi DeepSeek, timeout và nén bộ nhớ, migration lặp giữ dữ liệu, hồi quy tính năng |
| Đã sửa, cần kiểm thử Vercel | includeFiles thực tế, CDN/build, duration, Firebase đúng domain, kết nối/schema Preview |
| Chưa xác nhận vì thiếu thông tin | Biến môi trường/quyền/schema/bundle/log Dashboard Production, key/số dư/model DeepSeek thật |
| Cần bạn xác nhận riêng | Commit/push, cấu hình Firebase/Vercel, Preview/Production deploy, migration Production và bất kỳ request AI có tính phí |

Các rủi ro có sẵn chưa thay đổi chính sách trong lần sửa kỹ thuật:

- AI công khai `/api/advice` và hỏi AI theo truyện chưa có rate limit phân tán theo UID/IP; STT chưa có ngân sách riêng. Cần thống nhất chính sách bảo vệ trước mở rộng người dùng thật.
- Quota khách theo UID có thể bị né bằng nhiều UID; chưa có App Check/IP/global budget.
- Khóa phiên và semaphore nằm trong RAM mỗi instance; quota và lưu cặp tin nhắn dùng PostgreSQL, nhưng hai câu khác request_id trên nhiều instance vẫn có thể dùng ngữ cảnh cũ. Chưa thêm cơ chế khóa phân tán toàn bộ hội thoại vì cần thiết kế/kiểm tra nguy cơ ảnh hưởng dữ liệu.
- Chứng thư Firebase cache trong RAM được phép tải lại, không phải dữ liệu người dùng. Chưa kiểm tra disabled/revoked token theo thời gian thực bằng Firebase Admin.
- Chưa có lockfile dependency gián tiếp và chưa kiểm thử tải nhiều instance thật. Không tuyên bố website Production đã được sửa chỉ từ kết quả local.
