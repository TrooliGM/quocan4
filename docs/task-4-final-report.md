# Bàn giao Task 4 — Trợ lý hướng nghiệp 3.0

Ngày 25/10/2026, Asia/Bangkok. **Chưa sẵn sàng Production.** Người dùng đã chọn hoàn thiện code và Preview cách ly, ghi BLOCKED phần LIVE vì chưa có môi trường thử riêng.

## A. Git và bảo toàn nguồn

- Worktree `D:/khkt/.claude/worktrees/task-4`, nhánh `feat/task-4-ai-advisor-3-0`.
- Xác minh Vercel Production thực tế trước tạo nhánh: `df1c300d0fb8f63462642c9673fc5911139adca7`, deployment `dpl_6Q6muJBTW7kK7owh4m5TJ7XgU2dN`. Không giả định main hoặc 5aaed6e còn là Production.
- Backup Git `backup/task-4-before-advisor-3` trỏ đúng nền df1c300. Không đổi checkout chính có thay đổi chưa commit và không sửa nhánh Task 3.
- Checkpoint 4.1 `a0f08dc`; 4.2 `1a48619`; 4.3 `b3e385b`. Checkpoint 4.4/bàn giao code **5bbc282ac36706ee0c75cf5de701c0d48e28285c**. Đây là commit đang chạy trên Preview; commit tài liệu hậu kiểm sau đó không thay runtime. Worktree sạch trước push/deploy; trạng thái cuối kiểm tra sau commit tài liệu.
- Không đổi 200 hồ sơ/career_id, truyện/video, Firebase verifier hoặc auth/account-link/chat-journey. Không sửa hoặc chạy lại migration 001–005. Không ghi Neon Production.

## B. Bảng 53 yêu cầu

Theo dõi từng ID, file và bằng chứng tại [task-4-requirements.md](task-4-requirements.md).

Phần phụ thuộc chất lượng AI, Search, phân tích thực và đồng bộ tài khoản trên Neon/Firebase được đánh **BLOCKED** dù code/kiểm thử local đã có. Đặc biệt không dùng câu trả lời giả lập để kết luận AI tư vấn tốt, không coi Firebase fixture là Google Login thật. Không có yêu cầu bị bỏ khỏi bảng.

Kết quả cuối: **19 PASS, 34 BLOCKED, 0 FAIL, 0 TODO (đủ 53 ID)**. ID 1–32, 42 và 52 còn BLOCKED ở tiêu chí nghiệm thu thật; code và bài thử local tương ứng đã có. Không kết luận hoàn thành 100% hoặc READY FOR PRODUCTION.

## C. Code và API

### Chat và giao tiếp

- Header `Trợ lý hướng nghiệp`, phụ đề chính xác; giữ logo La Bàn, màu/border/radius/padding bubble và Copy. Bỏ avatar/nhãn assistant ở từng tin nhắn.
- `conversation_policy.py` lấy cách xưng hô từ yêu cầu mới nhất trong đúng hội thoại, rồi lịch sử, khảo sát, cuối cùng trung lập. Không thêm lời gọi AI để đổi cách xưng hô; ngôn ngữ tự nhiên thực tế còn cần DeepSeek nghiệm thu.
- Giữ nguyên navigation cache, abort/race guards, Google return-path và Guest claim. Không gọi AI khi tạo/mở/chuyển hội thoại.

### Tra cứu thật khi được cấu hình

- `search_provider.py`: interface provider, adapter **Brave Web Search API** tại endpoint chính thức, key backend `SEARCH_API_KEY`. Không có kết quả tìm kiếm giả hoặc proxy qua công cụ của phiên Codex.
- Tự tra cứu cho câu cần thông tin theo năm/mới/nguồn; không tra cho mọi câu sở thích. Không gửi hồ sơ, khảo sát hoặc UID sang Search. Chặn query rõ ràng có secrets/định danh, bỏ email/điện thoại rõ ràng.
- Cache theo hash UID+query, tối đa 64 mục, TTL 5 phút hoặc 1 giờ cho năm quá khứ. Cache RAM chỉ tối ưu; auth/rate/quota vẫn dùng PostgreSQL chung, không dựa vào RAM.
- Provider timeout, tối đa một retry cho 502/503/504, response 200 KB, tối đa sáu ứng viên/bốn nguồn, excerpt 700 ký tự.
- URL HTTPS công khai; resolve toàn bộ IP, chặn private/link-local/loopback, ghim IP khi HEAD và giữ TLS/SNI hostname, không follow redirect. Không tải body website hoặc thực thi script.
- Loại nguồn không có liên hệ từ khóa tối thiểu, ưu tiên gov/edu; đây chưa phải thẩm định ngữ nghĩa toàn trang. Nguồn lưu title/url/domain/publisher/ngày nếu có/retrieved_at/excerpt/verification_level/temporal_relation.
- **Nguồn chỉ snippet + kiểm link**; UI và prompt nói rõ chưa đọc toàn trang. Năm cần tìm khác ngày xuất bản; snippet nhắc năm không chứng minh thống kê. Citation chỉ được dùng URL trong allowlist thực từ provider; link do model tự tạo bị loại.
- Provider không cấu hình/lỗi/thiếu nguồn: không giả đã tra cứu, trả trạng thái và lời lưu ý rõ, giữ câu hỏi trong luồng chat. Chất lượng tổng hợp/số liệu thực tế chưa thể chứng nhận khi không có provider thật.

### Khảo sát và hồ sơ có đồng ý

- `survey_analysis.py`: một tác vụ riêng nhận đủ năm câu, schema Pydantic, summary có chọn lọc, phân loại đề xuất, quote đối chiếu đúng câu 1–5, qualitative confidence/inference type, tối đa ba câu làm rõ. Reject quote bịa/JSON hỏng/suy năng lực thiếu căn cứ hoặc chép nguyên cả khảo sát.
- Tác vụ nằm trong LangGraph **sau auth/rate/quota/reservation**, không có endpoint AI phân tích miễn phí để vượt quota. Phân tích + phản hồi trong cùng lượt chat. Mở hồ sơ không gọi LLM. Lỗi phân tích không phá khảo sát/response; không tự lặp phân tích lỗi mỗi tin nhắn; thử lại phải do người dùng yêu cầu và tính một lượt chat.
- Phân tích tạm lưu cùng message assistant bằng cơ chế lưu/quota nguyên tử hiện có, không ghi confirmed profile.
- `confirmed_profile.py`: chấp nhận/sửa trước lưu từng mục; source proposal phải từ hội thoại thuộc UID đã xác minh. Retry cùng đề xuất không ghi đè mục đã tự sửa. Sửa có optimistic version; xóa riêng từng mục. Từ chối được ghi metadata phiên và giữ sau refresh.
- Không backfill profile LLM cũ thành đồng ý mới; dữ liệu cũ vẫn ở lịch sử/ngữ cảnh phiên, không bị xóa. Hồ sơ có xác nhận độc lập với việc bật lưu hội thoại.
- Hồ sơ tắt mặc định từng cuộc trò chuyện; khi tắt backend không đọc/chèn confirmed profile. Khi bật, đọc mục hiện tại đã đồng ý, không ghi ngược vào profile qua bộ nén. Tắt chỉ ảnh hưởng lượt tiếp theo, không thu hồi dữ liệu đã gửi trong các lượt trước.
- Khách: TTL 2 giờ; claim chuyển owner cùng transaction lịch sử bằng proof backend, giữ TTL. Tài khoản phải bấm giữ lâu dài từng mục nếu muốn. Không biến đồng ý tạm thành đồng ý lâu dài.
- Tự dọn mục hết TTL khi chủ phiên đọc/xác nhận; có hàm nội bộ `purge_expired(limit<=500)` cho job bảo trì được duyệt, không public endpoint/không tự chạy startup. Cần cấu hình lịch dọn định kỳ cho khách không quay lại trước Production; chưa cài cron/dịch vụ trả phí.
- Lỗi hiển thị phiên tạm: nguồn gốc `remember=false` là lựa chọn lưu, khác trạng thái đăng nhập. Hiển thị đúng khách/tài khoản đang lưu tạm; thêm hành động đồng ý lưu hội thoại với cùng ID. Copy từ bảng tạm sang bảng lưu trong cùng transaction, chỉ xóa bản tạm sau copy, không reset quota/tin nhắn. Không tự lưu lâu dài khi đăng nhập.
- Thêm limiter ghi profile theo UID/IP trong PostgreSQL chung, ngưỡng riêng; không trừ quota chat. Không tin X-Forwarded-For nếu ingress chưa được cấu hình tin cậy.

### API mở rộng

| Endpoint | Contract |
| --- | --- |
| `GET /api/ai/career-profile` | `{enabled, profile, items}`; giữ key profile cũ, nhưng chỉ chứa thông tin có xác nhận |
| `POST /api/ai/career-profile/items` | session_id/proposal_id/value/confirmed=true; UID từ backend |
| `PATCH /api/ai/career-profile/items/{id}` | value/version/retain tùy chọn; reject version cũ |
| `DELETE /api/ai/career-profile/items/{id}` | 204, idempotent theo owner |
| `POST /api/ai/sessions/{id}/profile-proposals/{proposal}/reject` | Ghi từ chối vào metadata, không gọi AI |
| `PUT /api/ai/sessions/{id}/profile-use` | use_profile boolean, lưu theo phiên |
| `POST /api/ai/sessions/{id}/retain` | Chỉ tài khoản đăng nhập; giữ ID/messages/survey, không tự đồng ý lưu hồ sơ |
| `GET /api/ai/preview-info` | Chỉ bool read_only dựa trên env server; query client không bật được bypass |

Chat messages có thêm sources/search_status/survey_analysis/analysis_status; model, token, key không trả frontend. Các API riêng tư trả `Cache-Control: no-store`. Frontend xử lý đúng 204, không parse JSON rỗng gây thông báo lỗi giả.

### Biến môi trường

- Existing: `DATABASE_URL`, Firebase web/project và xác thực backend, `DEEPSEEK_API_KEY`/MODEL/BASE_URL, Origin/proxy/rate hiện có: **không đổi Production**.
- Mới: `SEARCH_PROVIDER=brave`, `SEARCH_API_KEY`; `ADVISOR_PROFILE_ENABLED=false` mặc định, chỉ bật sau migration 006 trên đúng môi trường được duyệt.
- `PROFILE_USER_WRITES_PER_MINUTE=30`, `PROFILE_IP_WRITES_PER_MINUTE=90`; không đổi quota 8.
- Preview-only: `ADVISOR_READ_ONLY_PREVIEW=true`, chỉ có hiệu lực khi `VERCEL_ENV=preview`; `AI_DEMO_MODE=false`, DB/provider keys rỗng, profile disabled. Không dùng demo để giả nghiệm thu LIVE.
- `.env.example` chỉ tên/mẫu, không sửa `.env`, không đưa service account/secret vào Git.

## D. Bằng chứng kiểm thử

- Backend **86 test riêng biệt PASS** qua các lượt trọng tâm (29 mới, 56 hồi quy, một runtime bundle; không cộng lại các lượt chạy trùng). PostgreSQL thật chỉ trên loopback, mỗi fixture schema/cluster riêng; model/auth là stub có nhãn. Một lượt hồi quy trước có hai assert theo contract cũ, đã cập nhật và kiểm lại thành công; không bỏ bảo mật để qua test.
- Lỗi test mới sau khi thêm profile limiter do TestClient dùng peer `testclient` không phải IP; đổi fixture sang loopback thực, không nới proxy validation. 20 test phân tích/hồ sơ cuối PASS.
- Đã đưa nút phân tích dùng chung adapter post_completion để mock bao phủ đầy đủ. Ở lượt đầu, test mới dùng khóa placeholder có thể chạm HTTP thật khi chưa mock đúng nút; đã sửa, không dùng khóa thật hoặc coi là nghiệm thu LIVE.
- Node: **11 PASS** (return path, draft, account claim, TTL, story/video handoff).
- Chrome thật + PG local + auth/model fixture: **7 nhóm PASS**: survey/analysis/header/bubble; chọn/sửa/từ chối; refresh/opt-in/out; timeout/refund/retry; Google fixture claim và responsive; xóa từng mục; đồng ý lưu hội thoại giữ ID sau reload. `artifacts/advisor30-browser.json`, ảnh `advisor30-*.png`. Các response fixture ghi rõ chưa gọi DeepSeek.
- Bảo toàn 200 nghề/Truyện nghề bằng git diff df1c300 bằng 0 và validator 200 truyện/1.000 cảnh/400 tình huống. Runtime bundle không public/dotenv PASS.
- Không chạy lại Super Board toàn diện.

### Hiệu năng local, không phải SLA Production

Cùng Chrome/PG local, baseline code df1c300 so với Task 4. Mỗi bản năm tạo + năm mở, kiểm tra chuyển nhanh và duplicate request; không gọi AI.

| Đo | Trước | Sau |
| --- | ---: | ---: |
| Median tạo đến ready | 43,8 ms | 42,4 ms |
| Median mở từ cache đến ready | 8,5 ms | 14,3 ms |
| Khung hình phản hồi lớn nhất | 12 ms | 16,7 ms |
| API requests trong kịch bản | 7 | 7 |
| AI calls | 0 | 0 |

Không có bằng chứng để tuyên bố nhanh hơn; giữ phản hồi đầu dưới 200 ms trong phép thử local. Không suy rộng thành thời gian request/Neon Production. Server-Timing tiếp tục đo auth/db; thêm web_search/survey_analysis khi có gọi. Tổng deadline vẫn 90s, chừa thời gian lưu nguyên tử.

### LIVE

| Dịch vụ | Trạng thái |
| --- | --- |
| DeepSeek tư vấn/đổi xưng hô/phân tích thật | BLOCKED, chưa có credentials thử riêng được cấp phép |
| Brave Search thật + chất lượng nguồn theo năm | BLOCKED, chưa có Search key |
| Firebase Google popup thật Task4 | BLOCKED, chỉ fixture; không thay Firebase Production |
| Migration/CRUD Neon staging Task4 | BLOCKED; chỉ local PG PASS |
| Neon metadata thử hiện có | READ ONLY PASS ở project `silent-snow-82216939`, branch `ticket-7-premium-preview`, neondb; có 2 phiên lưu/7 phiên tạm/16 requests/4 quota, không đọc nội dung và không sửa |

Không mặc định database thử cũ là staging rỗng hợp lệ để ghi Task4, không copy dữ liệu hay dùng credentials Production. Người dùng đã xác nhận chưa có môi trường mới và chọn Preview cách ly.

## E. Migration, Preview và tiếp tục

`006_confirmed_career_profile.sql` chỉ thêm bảng/index profile, không đổi bảng hội thoại/quota hoặc dữ liệu cũ. Có transaction/lock timeout/statement timeout, cần setting xác nhận staging, dừng nếu bảng đã tồn tại (không coi IF NOT EXISTS là bảo đảm an toàn). Đã thử trên PG local thật và guard/rollback giữ row counts cũ. **Chưa chạy trên Neon**.

Khi có môi trường thử: xác minh project/branch/endpoint/database không phải Production/backup, sao lưu và count schema trước; kiểm tra migration 006, `SET laban.profile_migration_target='task4-staging-approved'` chỉ sau phê duyệt đúng target, thực thi 006, hậu kiểm constraints/count và CRUD; rồi bật profile flag. Không chạy lại 001–005 trên database hiện hữu. DB mới hoàn toàn cần baseline schema được xác minh riêng.

Rollback candidate: tắt profile flag và trở về deployment/checkpoint trước; giữ bảng profile và metadata mới, không DROP hoặc reset quota. Code cũ bỏ qua metadata mới và vẫn đọc hai bảng conversation. Production chưa bị thay đổi nên hiện không cần rollback website.

Preview sẽ push riêng nhánh Task4 và deploy CLI Preview. Git auto-deploy bị tắt **chỉ nhánh Task4** để gắn các override an toàn sau khi nhánh xuất hiện trên GitHub. Không đổi Production Branch, không force push/PR/merge. Giữ Deployment Protection; URL có thể cần tài khoản Vercel được cấp quyền.

### Preview đã xác minh

- URL: https://quocan4-gbxablhb0-khkt3.vercel.app/ai-career-advisor?preview=1
- Deployment **dpl_FuHqTyMmFEaAam7x6ipEYAJ2CBxX**, **READY**, target Preview (Vercel target=null), commit **5bbc282ac36706ee0c75cf5de701c0d48e28285c**.
- 89 file đóng gói, đủ module/runtime/assets và bốn batch career/bốn batch story; không dotenv/artifacts/tests/scripts/docs hoặc secret files.
- HTTP trang chủ/chat/thư viện/truyện/assets PASS; dữ liệu 200 nghề/12 nhóm/200 truyện và video có sẵn không đổi.
- Preview info read_only=true; health ai_configured=false/auth_configured=false. Cả ba API AI, tạo guest và ghi profile **503**, không đến provider/database. Private paths `.env`, Python source, migration SQL, data, artifacts và endpoint fixture `/__qa/advisor30` **404**.
- Chrome thật 1440/390: PASS header/phụ đề/logo, responsive, controls disabled, không có tin nhắn demo. Chỉ một fetch preview-info, không tạo phiên/đọc lịch sử/gọi AI/Firebase. Vercel Deployment Protection vẫn bật; đã kiểm bằng quyền Vercel được cấp, không công khai bypass token.
- Ảnh Preview: `artifacts/advisor30-preview-1440.png`, `advisor30-preview-390.png`. Ảnh local đã có chức năng (auth/model fixture được ghi rõ): `advisor30-chat-desktop.png`, `advisor30-proposals-desktop.png`, `advisor30-account-profile-desktop.png`, `advisor30-profile-mobile.png`.
- Evidence: `artifacts/task4-preview-results.json`, `task4-preview-isolation.json`, `task4-performance-summary.json`, `advisor30-browser.json`; không commit artifacts.
- Hậu kiểm Production alias vẫn **dpl_6Q6muJBTW7kK7owh4m5TJ7XgU2dN / df1c300**, metadata env Production không đổi. Không merge/PR/force push hoặc Production deploy; chỉ nhánh Task4 đã push.

**READY FOR ISOLATED PREVIEW REVIEW — NOT READY FOR PRODUCTION.** Preview chỉ để xem UI, không thể nghiệm thu luồng tư vấn/hồ sơ thật khi chưa có môi trường dịch vụ riêng.

### Điều kiện mở khóa LIVE

1. Cấp Neon staging rỗng, tách Production/backup/dữ liệu học sinh, xác minh project/branch/database rồi kiểm thử migration 006 trên đó; không áp vào database test cũ chỉ vì có kết nối.
2. Cấp DeepSeek test credential và Brave Search key hợp lệ ở biến Preview riêng nhánh, không gửi key qua chat hoặc sao chép Production.
3. Cấp Firebase test project/cấu hình được phép, kiểm authorized domain Preview và thao tác Google popup thật; không thay Firebase Production.
4. Chỉ sau các bước trên mới bật profile/services trên một Preview có kiểm soát, kiểm lại quota/Origin/cookie/proxy/rate cùng 34 yêu cầu LIVE đang BLOCKED, gồm phân tích theo năm/chất lượng tư vấn/xưng hô/đồng bộ qua đăng nhập; cấu hình lịch dọn profile hết TTL cho khách không quay lại.
5. Người dùng duyệt lại trước bất kỳ phát hành Production hoặc migration Production nào.

## File thay đổi

- Backend: `advisor/conversation_policy.py`, `search_provider.py`, `survey_analysis.py`, `confirmed_profile.py`, `graph.py`, `routes.py`, `guest_quota.py`, `postgres_store.py`, `postgres_adapter.py`, `prompt.txt`, `app.py`.
- Frontend: `chat.html`, `public/chat.html`, `public/assets/chat.js`, `chat.css`, `profile-panel.js`.
- Migration/cấu hình: `migrations/006_confirmed_career_profile.sql`, `.env.example`, `vercel.json`.
- Kiểm thử: `test_advisor30_policy.py`, `test_advisor30_search.py`, `test_advisor30_profile.py`, `test_advisor30_preview.py`, `browser_advisor30.py`, `browser_advisor30_fixture.py`, `browser_fixture.py`, `test_advisor.py`, `test_task1.py` trong tests.
- Theo dõi/bộ nhớ: `docs/task-4-requirements.md`, `task-4-checkpoints.md`, báo cáo này, `project-memory.md`, `decisions.md`.

Tài liệu provider: [Brave Web Search API](https://api-dashboard.search.brave.com/app/documentation/web-search/get-started), [Vercel Git deploymentEnabled](https://vercel.com/docs/project-configuration/git-configuration).
