# Bộ nhớ dự án: Website Hướng nghiệp KHKT 2027

## Task 4 — 25/10/2026, Preview cách ly đã xác minh

Production trước tạo nhánh đã xác minh df1c300/dpl_6Q6muJBTW7kK7owh4m5TJ7XgU2dN (đã có Task3.1), không còn 5aaed6e. Nhánh feat/task-4-ai-advisor-3-0/worktree task-4 từ đúng nền, backup task-4-before-advisor-3. Đã triển khai code giao tiếp/header, Brave adapter/citation/SSRF, phân tích năm câu có schema/evidence và hồ sơ chỉ lưu từng mục đã đồng ý. Migration006 chỉ chạy PG local, không Neon. 86 test backend khác nhau qua các lượt trọng tâm, 11 Node/Chrome7 nhóm PASS với auth/model fixture; không LIVE. Người dùng xác nhận chưa có môi trường/provider thử, chọn Preview cách ly và BLOCKED LIVE. Không đổi Production/200 nghề/Truyện nghề hoặc auth modules, không copy Production secrets. Xem docs/task-4-final-report.md và bảng đủ53ID; Preview5bbc282/dpl_FuHqTyMmFEaAam7x6ipEYAJ2CBxX READY: https://quocan4-gbxablhb0-khkt3.vercel.app/ai-career-advisor?preview=1; HTTP/Chrome desktop-mobile, providers disabled/mutations503 PASS; Production/env không đổi. Tracking19PASS/34BLOCKED, không khẳng định53PASS. NhánhTask4 đã push, chưa PR/merge/Production; checkpoint4.1a0f08dc/4.2 1a48619/4.3 b3e385b/4.4 5bbc282.

## Task 3.1 — 24/10/2026, đang hoàn thiện Preview

Nhánh feat/task-3-1-video-library/worktree task-3-1 từ f95cfde; backup task-3-before-redesign. Đã tách thư viện và chi tiết nghề, reader một cảnh, tab video/comic, schema/import YouTube và handoff video sang AI. Giữ nguyên 200 hồ sơ, 200 truyện/1000 cảnh/400 lựa chọn và auth/quota/DB. Ba ứng viên, hai video CareerOneStop rà metadata/mô tả/toàn bộ storyboard (chưa nghe hết âm thanh), một VTV7 KIDS pending không xuất bản. 26 backend/11 Node/Chrome10 nhóm PASS; hai YouTube player thật ready, một playback PASS, một playback chưa xác minh. Preview cần cách ly DB/providers, chưa có URL mới tại thời điểm ghi. Không Production/Neon/migration. Xem docs/task-3-1-checkpoint.md để phân biệt fixture, provider thật và giới hạn thẩm định.

## Nhiệm vụ3 Truyện nghề2.0 —24/10/2026, mới nhất

Hậu kiểm: Preview c23cdf3/dpl_GpkogjBB59CqFzJ1JEJyUQe3hdsp READY tại https://quocan4-2dx6bup90-khkt3.vercel.app/mot-ngay-lam-viec.200/200HTTP truyện PASS, Chrome desktop/mobile thật PASS qua bảo vệ Vercel. AI/Firebase tắt, guestcreate503/AI401, không dùngDBProduction. Production vẫn5aaed6e/dpl_8SWMtQHuQ7nFnkt3EEs5YVc1tAyQ. READY FOR PREVIEW REVIEW, chưa Production/push/merge. Báo cáo hậu kiểm commit riêng chỉdocs, runtime không đổi sau c23cdf3. Chi tiết checkpoint có URL, kiểm thử và giới hạn provider/thẩm định nội dung.

Theo đặc tả mới, bắt đầu Task3 tại feat/task-3-career-stories-2-0/worktree task-3 từ Production5aaed6e, được Vercel xác minh; giữ hotfix2b4de6e và Chat2.1.200 truyện tĩnh biên tập4x50,1000cảnh/400quyếtđịnh;0video xác minh. Reader tương tác, trạng thái tab, ngữ cảnh AI có câu nháp sửa được và quay lại đúng hồ sơ.6truyệncũ cóAPIversion1.33backend/10Node/Chrome10+Chat2.1 12 checkpoint PASS với localPG/Firebasefixture/AIdemo; không coi là kiểm thử provider thật. Không đổi200hồsơ/UItrangchủ/auth/quota/schema. User cho phép checkpointcommit và Preview, không Production trước duyệt. Nhánh Preview chưa cóDBriêng, chọn Preview chỉđọc với credentials/DB trống, không sao chépProduction. Trạng thái build/URL ghi sau khi thực hiện; xem docs/task-3-checkpoint.md và docs/task-3-editorial-review.md. Các mục Task1/2 không làmTask3 bên dưới là checkpoint cũ, đã được yêu cầu mới thay thế.

## Chuẩn bị Vercel — 2026-10-13

- Người dùng yêu cầu chuẩn bị cấu hình Vercel từ GitHub; không commit/push, không đổi Firebase project hoặc hệ thống đăng nhập, không xóa dữ liệu. Chưa yêu cầu tạo deployment trong lần chuẩn bị này.
- Đã đối chiếu tài liệu Vercel hiện hành: `app.py` xuất `app`, tự nhận diện; giữ entrypoint `app:app` và vercel.json tối giản, không thêm routes/rewrites. Bổ sung dependencies runtime vào pyproject.toml khớp requirements.txt, thêm Pydantic trực tiếp và `.python-version` chọn 3.14 đã thử local.
- Đã cập nhật `.env.example` chỉ có giá trị mẫu, mở rộng `.gitignore`/`.vercelignore` cho các mẫu credentials, service account và private key. Không sửa `.env`, mã Firebase hoặc database hiện có.
- 26 test backend đạt, browser_login và browser_stories với giả lập đạt; 19 đường dẫn local trả 200; kiểm tra import và trang/API khi `VERCEL=1` đạt, assets để Vercel public CDN phục vụ. Kiểm tra tài sản/import JS tồn tại, không có URL localhost cố định trong frontend. Chưa chạy Vercel build/dev hoặc deployment thật do máy không có CLI/Node; chưa xác minh Firebase thật trên domain production.
- SQLite và phiên RAM vẫn là điều kiện chặn chat production trên Vercel. Đề xuất PostgreSQL managed với adapter, phiên tạm TTL và khóa/idempotency dùng chung; chưa triển khai hoặc migrate. Không dùng /tmp làm storage bền vững. Chi tiết và các bước deploy ở `docs/vercel-deploy.md`.

## Đăng nhập mở thẳng chat — 2026-10-13

- Người dùng yêu cầu đăng nhập tài khoản xong chuyển thẳng vào trò chuyện AI. Email/Google và liên kết đăng nhập với phiên đã xác thực chuyển tới `/ai-career-advisor?start=1`.
- Trang chat khôi phục phiên đang mở trong tab; nếu chưa có thì tạo phiên tạm với lời chào, bỏ bước bấm Bắt đầu và đặt focus vào ô nhập sau khi bật lại điều khiển. Không tự đồng ý lưu lịch sử. Tham số start được xóa sau khi mở thành công để tránh tạo trùng khi tải lại.
- Chrome với Firebase giả lập đã kiểm tra email, Google, phiên có sẵn, tải lại không tạo trùng, không chuyển trang khi backend xác thực lỗi và vẫn cho quay về trang chủ. Chưa thử đăng nhập Firebase thật cho thay đổi này. Các thay đổi đăng nhập này hiện ở local, chưa đồng bộ GitHub.

## Trạng thái mới nhất 2026-10-13: truyện nghề

- Người dùng yêu cầu chức năng cốt lõi mô phỏng một ngày làm việc bằng hoạt hình/comic, áp dụng frontend-design, Python, DeepSeek, LangGraph, GitHub và Vercel.
- Đã thêm `/mot-ngay-lam-viec`, sáu nghề với 24 cảnh SVG gốc có chuyển động, lời thoại, kỹ năng, lựa chọn tình huống và phản hồi. Có trình xem từng cảnh, tự chuyển 12/20 giây, chế độ cả trang, tổng kết, giảm chuyển động và bố cục điện thoại. Truyện bác sĩ gồm khám bệnh, hội chẩn, kê đơn, ca trực; không hướng dẫn điều trị.
- Truyện có liên kết từ menu, khối giới thiệu trang chủ, thẻ nghề và hộp chi tiết. Giữ tìm kiếm, bài viết và giới thiệu KHKT 2027.
- API hỏi AI theo cảnh qua `story_ai.py` dùng LangGraph/DeepSeek; hủy hiển thị kết quả cũ khi đổi cảnh. Đã thử một câu hỏi tổng hợp thật về hội chẩn, HTTP 200; không dùng dữ liệu cá nhân.
- 26 bài kiểm tra backend đạt; Chrome đạt các luồng truyện, AI giả lập, mobile, giảm chuyển động. Kiểm thử đăng nhập/chat/mic giả lập hiện có cũng đạt.
- Vercel đã có cấu hình FastAPI và tệp loại trừ dữ liệu local. Người dùng đã xác nhận **dùng bản chạy trên máy trước** trong ngày 2026-10-13; chưa deploy. Chat SQLite còn cần cơ sở dữ liệu bền vững trước triển khai toàn bộ. Xem `docs/career-stories.md`.
- Đã lưu bản truyện lên `TrooliGM/quocan4`, nhánh `main`, commit chức năng `48d485324d863f361f931f054eb870eebc9a85c4`. Đối chiếu 18 tệp thay đổi với cây GitHub đều khớp; cây tổng cộng 53 tệp, không chứa `.env`, dữ liệu local hay artifacts. Server local `/mot-ngay-lam-viec` và API danh mục trả HTTP 200.

## Trạng thái mới nhất 2026-10-12

- Người dùng chốt phạm vi giọng nói hiện tại là **chỉ thêm lại micro** để nhập câu hỏi tiếng Việt, sau đó yêu cầu lưu dự án lên repository GitHub `TrooliGM/quocan4`. Yêu cầu triển khai website công khai vẫn được hoãn.
- Chat chính dùng DeepSeek Flash trả Markdown; một lời gọi riêng nén ngữ cảnh/hồ sơ và lỗi ở bước nén không làm mất câu trả lời. Đã thử sáu lượt DeepSeek thật bằng dữ liệu tổng hợp, gồm sở thích vẽ, thêm hiểu biết máy tính, hỏi nhiều nghề và sửa thông tin.
- Micro mới: Google Speech-to-Text khi có credentials server, Web Speech trình duyệt khi chưa có; tự dừng sau khoảng 3 giây im lặng, hiện bản chữ để sửa rồi gửi thủ công. Hiện chưa có Google credentials, chưa xác minh micro thật; Vbee đọc giọng không thuộc phạm vi bản này. Các ghi chú voice cũ phía dưới là lịch sử đã được thay thế.
- Kiểm thử backend và Chrome giả lập đạt trước khi đồng bộ. Không lưu khóa/token hoặc dữ liệu cá nhân vào repository.
- Đã lưu 43 tệp mã nguồn/tài liệu lên nhánh `main` của `TrooliGM/quocan4`, commit `35c2d84ebb234b9984088c9c886b07fa961a51f8`; đã kiểm tra nhánh và tệp micro trên GitHub. Chưa triển khai website công khai.

## Nguồn và phạm vi

- Nguồn: `C:/Users/Administrator/Downloads/Bao_Cao_Y_Tuong_Website_Huong_Nghiep_KHKT2027 (2).docx`.
- Tên báo cáo: “Báo cáo đề xuất ý tưởng và tính năng website dự án khoa học kỹ thuật 2027”.
- Ngày đọc và tạo bộ nhớ: 2026-10-06.
- Ban đầu người dùng yêu cầu đọc báo cáo và thiết kế bộ nhớ; sau đó yêu cầu xây dựng chức năng trang chủ theo công nghệ cụ thể.
- Các yêu cầu bên dưới được trích lược từ báo cáo; không mặc định rằng mọi tích hợp hoặc lựa chọn kỹ thuật đã được người dùng phê duyệt.

## Mục tiêu và đối tượng

Tên mô tả: Nền tảng Website Hướng nghiệp và Định hướng Tương lai Trực quan hóa cho Học sinh.

Đối tượng: học sinh THCS và THPT. Báo cáo nêu vấn đề học sinh thiếu định hướng, khó hình dung thực tế công việc và thường gặp tài liệu dài, khó hiểu. Đây là nhận định trong báo cáo, chưa kèm dữ liệu khảo sát trong tệp đã đọc.

Giải pháp: dùng hoạt hình, infographic, comic và tương tác để giải thích bản chất công việc, hoạt động hàng ngày, kỹ năng và trách nhiệm nghề nghiệp. Trải nghiệm cần ngắn gọn, dễ hiểu và truyền cảm hứng.

## Tám nhóm chức năng theo báo cáo

| Nhóm | Yêu cầu được mô tả |
| --- | --- |
| 1. Trang chủ và giới thiệu | Giới thiệu mục tiêu KHKT 2027; giao diện thân thiện với học sinh; nghề nổi bật, bài viết hướng nghiệp và tìm kiếm nhanh. |
| 2. Tài khoản và cá nhân hóa | Đăng ký/đăng nhập qua Email, Google, Zalo; quản lý hồ sơ, lưu nghề yêu thích, xem lịch sử trắc nghiệm. |
| 3. Thư viện nghề nghiệp trực quan | Phân nhóm như Y tế, Công nghệ, Giáo dục, Nghệ thuật; mỗi nghề có mô tả, kỹ năng, lương trung bình, triển vọng và trường đào tạo. |
| 4. Hoạt hình và comic nghề nghiệp | Chức năng cốt lõi: mô phỏng một ngày làm việc bằng hoạt hình/comic/video ngắn. Ví dụ bác sĩ: khám bệnh, hội chẩn, kê đơn và trực cấp cứu. |
| 5. Trắc nghiệm định hướng | Báo cáo đề xuất Holland Code và MBTI với ngôn ngữ phù hợp học sinh; gợi ý nghề dựa trên tính cách, sở thích, năng lực. Chưa có bộ câu hỏi hoặc cách tính điểm. |
| 6. Tư vấn và hỏi đáp | Học sinh gửi câu hỏi; đề xuất trợ lý AI 24/7 và kết nối giáo viên/chuyên gia hướng nghiệp. |
| 7. Lộ trình học tập | Môn học THPT, khối thi, hướng đại học/cao đẳng, kỹ năng mềm; gợi ý khóa học ngắn hạn và tài liệu bổ trợ. |
| 8. Quản trị hệ thống | Quản lý bài viết, dữ liệu nghề, tải hình ảnh hoạt hình; thống kê truy cập, tương tác và kết quả trắc nghiệm. |

## Yêu cầu thiết kế và kỹ thuật từ báo cáo

- Giao diện tươi sáng, sinh động, phù hợp học sinh; dùng được trên máy tính và điện thoại.
- Ưu tiên tải trang nhanh; tối ưu dung lượng hình ảnh và hoạt hình để trải nghiệm mượt.
- Dữ liệu nghề nghiệp dễ mở rộng và cập nhật.
- Chưa có chỉ tiêu hiệu năng định lượng, công nghệ cụ thể hoặc thiết kế cơ sở dữ liệu.

## Thành viên theo báo cáo

| Thành viên | Vai trò |
| --- | --- |
| Kiều Anh | Nghiên cứu thực trạng, khảo sát khó khăn, biên soạn kịch bản hoạt hình nghề nghiệp. |
| Kiều Oanh | Tổng hợp ý tưởng, cấu trúc chức năng, lập kế hoạch, mô tả sản phẩm và viết báo cáo. |
| An | Phát triển frontend/backend theo thiết kế và danh sách chức năng. |
| Thầy Trần Quốc Giăng | Hướng dẫn chuyên môn, cố vấn nội dung và chỉ đạo chung. |

## Trạng thái thực tế

- Đã cài skill frontend-design tại `.agents/skills/frontend-design/SKILL.md`.
- Đã đọc nội dung báo cáo và tạo tài liệu bộ nhớ.
- Đã xây dựng trang chủ: giới thiệu, sáu nghề mẫu, ba bài viết, tìm kiếm tiếng Việt không dấu, lọc lĩnh vực, hộp thoại nội dung, giao diện responsive.
- Backend Python FastAPI; frontend HTML, Bootstrap, CSS và JavaScript. DeepSeek qua LangGraph đã kiểm thử lời gọi thật với nội dung mẫu; xem cập nhật khóa dịch vụ bên dưới.
- Đã chuẩn bị cấu hình Vercel và hướng dẫn triển khai. Repository người dùng chỉ định: https://github.com/TrooliGM/quocan4.
- Đã đưa mã nguồn lên nhánh `main` của repository và xác minh cây tệp; commit ứng dụng `9ead1787bf959bc33557bd45f5b66f38ff982d5d`.
- Người dùng đã xác nhận chưa cần đưa website lên mạng; hiện phát triển và chạy local. Chưa có deployment Vercel được xác minh.
- La Bàn là tên giao diện do trợ lý đề xuất khi triển khai, chưa phải tên thương hiệu người dùng xác nhận.
- Nội dung nghề và bài viết là bản mẫu biên soạn, không có số liệu thị trường hoặc bảng xếp hạng tuyển dụng.
- Ngày 2026-10-07, người dùng xác nhận trang chủ chạy tốt trên máy và yêu cầu setup đăng nhập Firebase.
- Đã có mã đăng ký/đăng nhập email/mật khẩu và Google, quên mật khẩu, xác minh email, trạng thái tài khoản và đăng xuất. Backend xác minh Firebase ID token bằng google-auth và khóa công khai của Google; không cần service account.
- Người dùng đã cung cấp cấu hình Web của Firebase project `khoa-hoc-86942`, ứng dụng “la bàn tương lai”. Đã điền các biến FIREBASE_* vào `.env` cục bộ, giữ nguyên các cấu hình khác và kiểm tra endpoint cấu hình trả configured=true. Không lưu API key vào bộ nhớ hoặc GitHub.
- Ảnh người dùng gửi cho thấy đã bật Email/Password và Google, có localhost trong authorized domains. Chưa kiểm thử đăng nhập thật bằng tài khoản của người dùng; hướng dẫn ở `docs/firebase-setup.md`.
- Đã có LangGraph trong môi trường hiện tại; kiểm tra mock thành công và đã có kiểm tra DeepSeek thật qua graph với nội dung mẫu.
- Chưa có trắc nghiệm, quản trị, Firestore hoặc phim hoạt hình nghề nghiệp. Chi tiết xác minh ở `docs/validation.md`.

## Cập nhật 2026-10-11: tư vấn AI 1:1

- Yêu cầu trực tiếp: đăng nhập thành công chuyển tới giao diện chat 1:1 với AI; tài liệu đính kèm bổ sung phạm vi text/voice và bộ nhớ riêng.
- Đã thêm route `/ai-career-advisor`, tái sử dụng Firebase hiện có. Email/Google chuyển trang sau xác thực backend; khách quay về hộp đăng nhập trang chủ. Có liên kết Tư vấn cùng AI.
- Giao diện dùng frontend-design và bộ màu/font cũ: màn hình bắt đầu, bốn gợi ý, chat, sidebar lịch sử/tìm kiếm/đổi tên/xóa, hồ sơ, drawer mobile, Enter gửi/Shift+Enter xuống dòng, lỗi và thử lại, Markdown qua Marked/DOMPurify.
- Module `advisor/` có LangGraph một lời gọi DeepSeek mỗi lượt, ngữ cảnh gần nhất + tóm tắt + hồ sơ, JSON phân tích riêng, kiểm tra tối thiểu ba nghề khác nhau khi có gợi ý.
- Lựa chọn triển khai local: SQLite cho phiên người dùng đồng ý lưu; phiên không lưu chỉ ở RAM, hết hạn sau 2 giờ không hoạt động. Tất cả API kiểm tra Firebase UID và quyền sở hữu; UUID chống trùng trong một tiến trình. Có xóa toàn bộ dữ liệu tư vấn của tài khoản.
- Đã viết adapter Google Speech-to-Text vi-VN và Vbee sync TTS, recorder WAV/VAD dừng sau 3 giây im lặng, sửa transcript trước khi gửi, dừng/phát lại/tắt giọng đọc. Chưa xác minh micro/VAD bằng thiết bị thật hoặc request provider thật.
- `.env` local bật demo có nhãn vì chưa có khóa DeepSeek; không tạo kết luận năng lực hoặc hồ sơ giả. Không lưu khóa trong bộ nhớ dự án. Thiếu cấu hình Google/Vbee thì UI giải thích và vô hiệu hóa chức năng tương ứng.
- Đã chạy 22 test backend thành công. Chrome headless với Firebase stub đã kiểm tra guest guard, login redirect, gửi demo, đổi tên, tải lại lịch sử, chống XSS Markdown, hồ sơ, drawer/mobile không tràn ngang, WAV client và đăng xuất. Đây không phải thử Firebase/AI/voice thật.
- Hướng dẫn dùng/cấu hình/giới hạn ở `docs/ai-advisor.md`. Chưa đồng bộ thay đổi lần này lên GitHub hoặc deploy. Trước khi deploy cần database dùng chung bền vững, distributed idempotency và rate limit theo tài khoản; SQLite không dùng làm kho serverless.

## Cách tiếp tục

### Khắc phục AI không đọc thành tiếng 2026-10-12

- Người dùng xác nhận bấm Nghe nhưng không có tiếng/không thấy lỗi. Đọc danh sách thật từ Chrome kiểm tra riêng thấy 22 giọng, không có `vi`; registry Windows chỉ có giọng tiếng Anh. Đây là kiểm tra browser trên máy này, không phải xem tab đăng nhập của người dùng.
- Đã sửa frontend: kiểm tra giọng Việt khi mở trang, hiển thị trạng thái cạnh ô nhập, hộp hướng dẫn/nghe thử/dừng/kiểm tra lại. Bật tự đọc khi thiếu giọng sẽ mở hướng dẫn. Chờ danh sách giọng cập nhật; resume bộ đọc, đặt âm lượng câu đọc 1; chỉ báo Đang đọc sau sự kiện start, không khởi động sau 6 giây thì báo lỗi rõ. Đóng hộp thử không hủy nhầm lần đọc câu trả lời mới.
- 23 test backend đạt; Chrome stub đạt hồi quy, nghe thử, trạng thái thiếu giọng và bộ đọc không khởi động. Chưa xác minh âm thanh tiếng Việt thật.
- Người dùng đã cho phép cài giọng tiếng Việt từ Windows Update. Gói `Language.TextToSpeech~~~vi-VN~0.0.1.0` hiện vẫn `NotPresent`. Cài đầu lỗi dịch vụ bị tắt; đã thử tạm bật BITS/wuauserv nhưng Windows Update kẹt `StopPending`, chưa cài được. Đã khôi phục kiểu khởi động cả hai về Disabled; BITS Stopped, wuauserv vẫn StopPending. Đã dừng riêng shell cài của trợ lý đang chờ; không kill dịch vụ hệ thống, không reboot máy.
- Người dùng đã khởi động lại Windows. Thử cài lại thất bại với `0x80200010` (bộ tải Windows báo mất kết nối), dù truy cập HTTP thử bằng Python thành công. BITS đã dừng; Windows Update lại kẹt `StopPending`; kiểu khởi động cả hai đã trả về Disabled như ban đầu.
- Người dùng cho phép tạm ngắt WARP để thử. Đã ngắt, nhưng không thể bắt đầu lần tải mới vì Windows Update chưa thoát `StopPending` trong thời gian chờ 20 giây. Khối `finally` đã kết nối WARP lại; kiểm tra sau cùng báo `Connected`, `Network: healthy`. Chưa xác nhận WARP là nguyên nhân. Gói giọng vẫn `NotPresent`.
- Có script cài thủ công `scripts/install-windows-vietnamese-voice.ps1`: lưu/khôi phục kiểu khởi động dịch vụ, giới hạn thời gian chờ trạng thái dịch vụ, xuất kết quả thực tế; không reboot hoặc kill dịch vụ. Lệnh Add-WindowsCapability vẫn phụ thuộc Windows Update. Không chạy script tự động cùng website.
- Còn cần xử lý Windows Update/bộ tải hoặc nguồn gói Microsoft phù hợp trước khi cài được giọng. Không lặp lại cài khi dịch vụ vẫn StopPending. Sau khi cài phải kiểm tra giọng Việt có trong Chrome và playback thật; không coi test stub là nghe được âm thanh.

### Giọng trình duyệt 2026-10-11

- Người dùng yêu cầu mở voice chat và xác nhận chọn thêm giọng trình duyệt để thử ngay. Google/Vbee vẫn được giữ và ưu tiên khi sẵn sàng; không nâng cấp gói hoặc thay credentials.
- Đã thêm `public/assets/browser-voice.js`: SpeechRecognition vi-VN khi browser hỗ trợ/secure context, dừng/hủy/giới hạn thời gian, kết quả sửa trước khi gửi và giữ draft; không tự gửi hoặc tự bật micro sau khi đọc.
- SpeechSynthesis chỉ dùng giọng Việt trên máy, chia đoạn, dừng/nghe lại; chưa có giọng Việt thì báo rõ. Banner phân biệt chế độ trình duyệt và nói rõ nhận diện có thể dùng dịch vụ trực tuyến. Mặc định tự đọc tắt, người dùng bật hoặc nghe từng câu.
- 23 test backend đạt. Chrome headless đạt hồi quy và các ca Web Speech stub: nối draft, thay interim, gửi thủ công, hủy/kết quả cũ, từ chối quyền, chọn giọng Việt, đọc nhiều đoạn/dừng, dừng đọc khi bật micro, thiếu giọng Việt và browser không hỗ trợ. Không gọi Google/Vbee endpoint ở chế độ browser. Chưa thử micro/âm thanh thật trên thiết bị người dùng.

### Cập nhật khóa dịch vụ 2026-10-11

- Người dùng cung cấp khóa DeepSeek và token/App ID Vbee để cấu hình; chỉ lưu ở `.env` riêng, không ghi giá trị vào bộ nhớ, mã nguồn hay kết quả kiểm tra.
- Đã tắt `AI_DEMO_MODE` và xác minh DeepSeek `/models` trả 200 với model `deepseek-flash`. LangGraph trả nội dung thật và JSON hợp lệ; một câu hỏi yêu cầu gợi ý nghề trả ba nghề khác nhau. Dùng tài khoản kiểm thử tổng hợp trong RAM, không dùng dữ liệu học sinh.
- Vbee API danh sách giọng trả 200; chọn HN - Ngọc Huyền. Request tạo âm thanh sync thật trả 400 với thông báo gói người dùng chưa hỗ trợ tính năng. Chưa có âm thanh Vbee thành công.
- Tạm tắt giọng đọc bằng cấu hình `VBEE_TTS_ENABLED=false`, lý do `package_not_supported`; frontend hiển thị đúng lý do và tiếp tục chat chữ. Cần tài khoản hỗ trợ sync TTS hoặc một phương án async có callback phù hợp trước khi bật lại. Không mua/nâng cấp gói dịch vụ.
- Google STT vẫn chưa cấu hình. Sau cập nhật giọng trình duyệt bên trên, micro dùng Web Speech nếu được hỗ trợ. Không thay đổi Firebase hoặc deploy.
- Sau cập nhật đã chạy đạt 23 test backend, biên dịch Python và kiểm tra lại Chrome headless với Firebase stub/demo; chưa kiểm tra đăng nhập Firebase thật nối toàn bộ luồng chat thật trên trình duyệt.
- Công cụ kiểm tra thật ở `scripts/check_live_providers.py`; chỉ chạy chủ động, có dùng quota API, không ghi âm thanh xuống đĩa và không in khóa.

Khi người dùng yêu cầu triển khai, tham khảo `docs/decisions.md`, xác định phạm vi cần làm và cập nhật bộ nhớ theo kết quả thực tế. Giữ chức năng trực quan hóa nghề nghiệp ở vị trí trung tâm của sản phẩm.


## Nhiệm vụ 1 — 2026-10-23

Đã phát triển giao diện điều hướng sau Hero và khảo sát năm bước theo phiên trên nhánh riêng feat/task-1-career-survey, từ Premium 7c07d33. Dữ liệu khảo sát dùng metadata JSON hiện có, không migration; lưu/ownership/row lock và browser local đã kiểm tra. Không thay Neon/Production. Chi tiết, giới hạn kiểm thử thật và checkpoint Nhiệm vụ 2 ở docs/task-1-checkpoint.md. Không thực hiện Nhiệm vụ 2/3.


## Nhiệm vụ 2 — 2026-10-24

### AI Chat 2.1 và hồ sơ200 nghề — cập nhật24/10/2026

Yêu cầu trực tiếp mới cho phép phát triển và commit nhánh riêng, giữ giao diện, không merge/deploy Production/Task3. Đã xác minh domain thực hiện đang trỏ d5f10cc/deployment dpl_6KpjeYiZ7wseuyo7ussQ7eA2ZQbM, khác7c trong báo cáo trước. Làm tại feat/ai-chat-2-1, worktree ai-chat-21 từ đúng source đó. Đã nâng gợi ý6/câu, bản nháp nghề theo dữ liệu và mục tiêu khảo sát, quay lại đúng nơi sau login, draft tab có TTL/owner, retry claim và title có marker manual trong JSON không migration.200 hồ sơ được biên tập4x50, modal disclosure giữ links/IDs. Backend60 method cuối PASS, Node6, Chrome12+2 checkpoint PASS bằng fixture/demo/localPG; Firebase/DeepSeek thật chưa kiểm chứng. Có localhost8004 demo riêng, không Neon/Production/secret changes; xem docs/ai-chat-21-checkpoint.md. Chỉ coi dữ liệu là bản biên tập có đối chiếu mẫu, chưa có thẩm định chuyên gia cho toàn bộ200 nghề.

Thư viện 200 nghề/12 nhóm, modal chung, hai mode AI và liên kết truyện theo ID đã triển khai trên feat/task-2-career-library. Preview localhost:8003 riêng dùng PostgreSQL local và AI demo. 17 test backend và browser desktop/mobile PASS có fixture; Firebase/DeepSeek thật cho flow mới chưa kiểm chứng. Không push/merge/deploy/Neon; Nhiệm vụ 3 chưa bắt đầu. Xem docs/task-2-checkpoint.md.

### QA hồi quy Nhiệm vụ 1 + 2 — 2026-10-24

Đã sửa whitelist bốn JSON runtime Vercel và modal bị phản hồi cũ ghi đè; giữ thiết kế, auth/quota và dữ liệu. Kết quả mới nhất: 79 backend method có outcome cuối PASS (batch 78/79 + retest module 4/4, không phải full batch 79/79), 93 browser assertion PASS trên 1440/768/390/360px. Tổng 172 PASS, 2 FAIL, 5 BLOCKED, 3 chưa kiểm chứng. Chỉ local PostgreSQL/Firebase fixture/AI demo; không chứng nhận Firebase/DeepSeek thật cho flow mới. **NOT READY FOR VERCEL PREVIEW** do hai API AI legacy không dùng auth/quota/rate chung, đã tái hiện mock; cần quyết định xử lý. Chưa deploy/Neon/push/merge; 8003 giữ nguyên. Báo cáo ở artifacts/super-board-report.md; xem checkpoint Nhiệm vụ 2. Không bắt đầu Nhiệm vụ 3.

### Shared AI protection — 2026-10-24, trạng thái mới nhất

High legacy đã được sửa và hai boundary retest401/graph0 PASS; chat/advice/story dùng identity/rate/quota/row lease chung, guest cookie không bắt Firebase, claim giữ lịch sử; voice rate nhưng không trừ quota8. Tổng197 PASS/0 FAIL/5 BLOCKED/3 chưa kiểm chứng, không cộng trùng batch90+security15 (94 method backend), browser101 và2boundary. Chỉ local/mock/demo, chưa live Firebase/DeepSeek. Migration004 nguồn cần phê duyệt riêng; legacy003 và proxy Vercel còn gate, nên NOT READY FOR VERCEL PREVIEW. Server8003 local mới PID16800, không dữ liệu Production. Chi tiết docs/shared-ai-protection.md và checkpoint task-2; không push/merge/deploy/Task3.

### Chuẩn bị tích hợp Production — 2026-10-24

Đã xác minh Production đang chạy 7c07d33, tạo nhánh/worktree integrate/task-12-production từ nền đó và fast-forward đủ Task1+2/349ff92, giữ nguyên migration002; backup Git local và deployment đã ghi. 004 đã PASS trên nhánh thử ticket-7-premium-preview, dữ liệu cũ checksum/counts không đổi; 31 test backend chọn lọc PASS. Production chỉ đọc: request/session ID còn UUID, thiếu004 và có1 completed request thiếu phiên, quota khớp; chưa đủ điều kiện phát hành. DATABASE_URL có tên trong scope/snapshot nhưng binding/định dạng thực chưa xác minh, không tự sửa config bằng suy đoán. Dừng trước PR/merge/deploy; xem docs/release-task12-readiness.md. Checkout chính và mọi thay đổi người dùng giữ nguyên, không sửa Production/backup, không Task3.

## Hotfix điều hướng/hiệu năng —24/10/2026

Tạo hotfix/chat-navigation-performance từ Production6c5ce23 được Vercel xác minh. Đo5create/5open thật: API median create12559,1ms/list7329,9ms/open7260,6ms, Chrome khảo sát sẵn sàng19523,7ms và open7159,7ms;0AIcalls. Sửa sidebar refresh thừa, cacheRAM owner/TTL30s, abort+fencing, one request connection/UNION/COUNT giữauthquota; thêm Server-Timing không dữ liệu nhạy cảm. Login có return_to nội bộ+UUID, chụp target trước listener, tái hiện intent mất; Google thật cần kiểm lại, không phủ nhận báo lỗi mới vì ca trước từngPASS. Local backend37+7, Node7, Chrome12 và perf guest/member/rapid PASS. Không đổi thư viện200/CSS/schema/config. User cho phép commit/push/deploy hotfix có điều kiện; build và đo Production mới còn chờ lúc ghi checkpoint này. Chi tiết docs/chat-performance-hotfix.md.


## Task4 Production canary — 25/10/2026

Đã xác nhận quyền triển khai có kiểm soát theo yêu cầu mới. Đã backup Neon READY/readback, áp migration006 additive trong transaction sau kiểm target/hash và bảng cũ/quota không đổi; không chạy001–005. Phát hành fde7ed2 / dpl_7ZaE94zBvSeBAps9HgTPkak9Q1aT lên domain chính thức, chỉ 1 UID QA Firebase đã verify được Task4; account khác/Guest giữ df1c300 ổn định, không sửa thư viện/Truyện nghề. Firebase email/password, DeepSeek, khảo sát/đề xuất/xác nhận/Neon và Guest8/concurrency LIVE có bằng chứng. Chưa Google popup/Brave; ID23 FAIL khi AI chưa dùng hồ sơ opt-in dù lưu/đọc đúng. 36PASS/16BLOCKED/1FAIL; không mở đại trà. Rollback deployment df1c300, giữ bảng additive/dữ liệu, không reset quota. Xem docs/task-4-production-rollout.md; không ghi secrets/UID/email học sinh vào memory.


## Task4 hotfix cá nhân hóa —25/10/2026

Được duyệt sửa/commit/phát hành QA-only, không migration. Tạo hotfix/task4-profile-context từ Production fde7ed2, kế thừa tài liệu36a5b8e. Hotfix957ffde / dpl_BwthFvvNpNDscwEuKPC744bVe38z đã lên domain chính thức, chỉ3 UID QA verified. Context cũ có dữ liệu nhưng model báo không có; A/B cùng hồ sơ/mode/model:old không đọc nonce, new đọc đúng sau tách block enabled/status/items gần câu hỏi, phân biệt conversation_notes. SELECT tối thiểu readonly/filterconfirmed/TTL/owner, OFF không query hoặc gửi giá trị.26 test local unique +LIVE ON/OFF/edit/2owner/irrelevant/correction và browser checkbox mới/old PASS. ID23 đã đóng,43PASS/10BLOCKED/0FAIL; không mở đại trà. Google popup user-confirmed PASS nhưng mode/career_id chưa khớp metadataNeon, giữ42partialBLOCKED; Brave thiếuenv; khảo sát mơ hồ structuredunavailable; Guest-profile canary chưa mở. Backup cũ READY; rollback về dpl_7ZaE94zBvSeBAps9HgTPkak9Q1aT, không DROP/resetquota/restoređè. Xem docs/task4-profile-hotfix.md. Không lưu email/UID/secrets trong memory.

## Task4.1 — Preview nghiệm thu25/10/2026

Được duyệt code/commit/Preview, không phát hành Production. Nhánh feat/task-4-1-advisor-intelligence từ dba80a6, candidate a2a2f76 có context/intent/boundedhistory, xưng hô thiếu dấu, phân tích5câu tự động bằng tác vụ PGmetadata cóhash/lease/fence/budgetriêng6attempt/ngày2/phútIP30/ngày, không trừ Guest8 hoặc tự lưu confirmed. ProfileUI căn cứ/accept/edit/reject/draft theoowner; nén mỗi6turn có recentturns6000ký tự, chỉ dữ kiện tựnhận. Neon schema-only mới/role riêng ban đầu8bảng0dòng, không copy dữ liệu học sinh/không chạy lại006remote. Preview READY https://quocan4-7x3jqli76-khkt3.vercel.app, QA-only và Vercelprotected.56testPythonuniquePASS/6browserfixturegroupsPASS; FirebaseSDKpassword/DeepSeek/autoanalysis/noautoconfirm/cache/ownership/cookieOrigin/nénlượt6 LIVE PASS.16rubric13PASS/3BLOCKED (Brave thiếukey), GooglepopupPreview cònBLOCKED; median16chatrequest mỗi bản9,17→4,27s là mẫunhỏkhôngSLA. Production vẫn957ffde/deploymentcũ; thưviện/Truyệnnghề/migrations khôngđổi. Remote377, các checkpointcuối chưapush; chờ duyệtPreview. Chi tiết docs/task41-checkpoint.md và docs/task41-validation.md; không lưuPII/secrets/UID trongmemory.

### Sửa Guest vẫn thấy UI cũ

Yêu cầu mới cho phép push/Preview, UI mở cho mọi người nhưng backend nhạy cảm vẫn QA-only. Chrome ẩn danh xác nhận flagcontrolled trước trả stable HTML/JS cho Guest/member. Đã tách ADVISOR_PREMIUM_UI_PREVIEW chỉ hiệu lựcVERCEL_ENVpreview, sửa reload guard, hướng dẫn panel/khảo sát khi chưa được analysis. e933f98 đãpush, Preview READY https://quocan4-bp6m6anvt-khkt3.vercel.app/ai-career-advisor, dpl_GPWPYMsLL3F7MwYsDaFsYzmBihDZ.5unitmới+3hồiquyPASS; Chrome3persona thật header/avatarless/bubbles/desktopmobilePASS có12ảnh; A/B stableDeepSeek+survey,0analysis; QA auto1analysis/đềxuấtcăn cứ/confirmmới lưu. Guest8→7đúng1chat. Không mởbackendchoall, khôngProd/migration/reset. Brave/popupGooglemới vẫnBLOCKED; báo cáo docs/task41-preview-ui-fix.md thay kết luận UIQA-only cũ. Không lưuPII/secrets/UID.

### Quyết định mới nhất: thống nhất AI hội thoại

Người dùng yêu cầu không chia chất lượng AI theo vai trò. Đã bỏ chọn stable_graph; cả /api/ai/chat, /api/advice và hỏi cảnh truyện dùng các node Task4.1 chung. UI và tự phân tích5câu mở cho Guest/member/QA; chỉ quyền bank Hồ sơ chưa phát hành còn QA-only, Guest không đọc confirmed context. Guest8/rate/auth/owner/consent giữ nguyên, không dùng quyền dữ liệu để quay lại AI cũ.

Runtime dee7785 đã push, Preview READY https://quocan4-ju5z22f0t-khkt3.vercel.app/ai-career-advisor / dpl_Gooca1fySbMiFkmzANji1bGY2w1x.57testlocaluniquePASS; Chrome3persona tự1analysis/0chat mỗi5câu, draft có căn cứ và quyền confirm tách riêng. LIVE18turn cùng6câu cho3role có pipeline marker thật, đã đọc chất lượng; 1lỗi đại từ QA được sửa/rerun riêng PASS, không chạy lại cả18. Guest cũ tiếp tục engine mới, đủ8 thì429, retryfree; LIVE concurrencyanalysis200/200/429, headerIPgiảkhôngbypass; ownership/token/cookie/cachedanalysisPASS. Memberexploration LIVE giữcareer_id/mode. Schema8bảng/stagingriêng/Production957ffde không đổi, không migration/reset. Brave thiếukey, Googlepopuphostnamecuối chưa thử. Chờ duyệt Preview; khi được duyệt phải build Production bằng env Production, không promote nguyên Preview bindstaging. Xem docs/task41-unified-preview.md.
## Task4.2 — DDGS Preview25/10/2026

Yêu cầu mới cho phép tích hợpDDGS vàoTask4.1 vàPreview, khôngProduction/đổi nhánh/reset/migration/envproject. Giữbranchfeat/task-4-1-advisor-intelligence từ163e61c. Runtime4aae6f8, Preview READY https://quocan4-b4ajdo1cc-khkt3.vercel.app/ai-career-advisor / dpl_AHoqbo8kkjoo7TifbprKxkd6xJ7o, staging/schema-only/role riêngnhưtrước. ddgs9.16.1 keylessworkerbounded/TLS/HEADpinned/ownerprovidercache; Braveoptional, khôngchiaAItheorole. Nguồnretrycompatgiữđúng, ràngbuộcnguồnlượthiệntạivàcachetruthful.51localuniquePASS;18yêucầutrảlờiLIVE:11/14lượtcầntra cónguồn (1cache),3unavailable;2normalnotneeded/2privacyblocked. Member/QA và2compatAPI cóSearchthật; GuestLIVEBLOCKED quota8cũcạn vàIPissuanceday10cạn, khôngreset/lách. ChromeSDKdesktop/mobilefooternguồnPASS, cacheSearch1599,9→0,4ms; Googlepopup/adversarialLIVEchưa kiểm. Một diễn giải“tỷlệ”từsnippetpháplýchưa đủchi tiếtghiPARTIAL. NOTREADYPRODUCTION, khôngclaimhoàn tấtmọica. Khôngpush. GETProdthựctếdee7785/dpl_EhYXDvrYDNJznoBThVVHZ5Pu7ZDg kháccheckpoint957cũ;TasknàykhôngdeployProd. Xem docs/task42-search-preview.md. KhôngghiPII/secretsvàomemory.

## Task 4.2 Production canary — 25/10/2026

Người dùng đã duyệt push/phát hành DDGS QA-only trên domain chính. Source 1b1b640 đã push vào feat/task-4-1-advisor-intelligence, kế thừa a40bde6; 54 local PASS, schema Production readonly PASS, không migration. Build Production mới rồi promote dpl_EJvYVHp8yYb4Ync29JPu91WXWa6c lên labanhuongnghiep.vercel.app. Ba override Search riêng, chỉ hai UID QA đã xác minh; không đổi profile, DB, Firebase, DeepSeek hoặc secret. Guest/member vẫn Task 4.1, Search tắt, không legacy. Bốn câu cần nguồn có nguồn thật; hai lần đầu unavailable được giữ và retry một lần mỗi câu. Ca2 retry là cache từ QA Truyện nghề, ca3 Search mới nhưng model nhầm nhãn cache, ca4 nhiễm ngữ cảnh tuyển sinh: chất lượng PARTIAL, không mở đại trà. Câu5 không Search; token/owner/Origin, Guest một câu trên quota8 và retry miễn phí, lịch sử, Chrome SDK desktop/mobile PASS. Ngày 25/10/2026 chủ dự án xác nhận đăng nhập Google QA trên domain chính thành công và câu hỏi AI2026 có nguồn (PASS do người dùng xác nhận); không suy ra Search mới hay cache. Guest Search/injection LIVE chưa nghiệm thu. Rollback dee7785/dpl_EhYXDvrYDNJznoBThVVHZ5Pu7ZDg; tag backup local đã giữ. Không merge, đổi Production Branch, migration/reset hoặc sửa authorized domains. Xem docs/task42-production-canary.md; không ghi PII/UID/secrets.

## Sửa chất lượng truy vấn nối tiếp Task 4.2 — 25/10/2026

Đã sửa local từ fb2eca4: câu “Vậy năm 2020 là bao nhiêu ạ?” trong lịch sử điểm chuẩn Công an được khôi phục thành query đầy đủ, thay năm cũ và giữ trường/diện tuyển sinh đã nêu. Lọc nguồn theo chủ đề + điểm chuẩn + năm/trường, không chấp nhận năm nhuận. Kết quả lệch chủ đề tìm lại một lần trong tổng timeout12s, không thêm LLM hoặc lượt Guest; thiếu chủ đề/số liệu thì hỏi làm rõ, không tự điền điểm. Giữ DDGS/DeepSeek/auth/Neon/quota/canary/UI. 70 method local unique PASS qua các lượt trọng tâm; API test với PG local chứng minh hai tin chỉ trừ hai lượt dù có ba lần Search, retry request_id miễn phí. DDGS LIVE local timeout7s, chưa DeepSeek/Vercel LIVE. Chưa commit/push/deploy, Production giữ nguyên. Giữ các tài liệu xác nhận Google từ lượt trước. Xem docs/task42-search-context-fix.md; không lưu PII/secrets.

## Task 4.2 — Preview LIVE và gate mở Search đại trà, 25/10/2026

Người dùng cho phép Production cho mọi role chỉ sau LIVE/an toàn PASS, cấm lách hạn mức. Tiếp tục bản sửa local; chẩn đoán DDGS auto thực tế trả5kết quả sau7,53s khi Mojeek timeout5,99s, adapter7s cắt sớm. Sửa9s nhưng tổngSearch12s/two workers giữ nguyên; local LIVE7,61s có nguồn đúng. Local checkpoint399a46e rồi922983a, khôngpush. Preview cuối dpl_3Kz4eeduVK3wGr2STUKzwijARDGe / https://quocan4-87bqdbdmb-khkt3.vercel.app/ai-career-advisor, source922983a, stagingriêng/Searchmọirole/profileQA-only. 16chatLIVEhaiđợt; sửa được câu nối tiếp2020 và lời làm rõ trường/nam/A01, khôngnămnhuận; đợtcuối6/6yêucầuSearchcónguồn. Nhưng số liệu range thứ cấp khôngkhớp bảng chính thức và có nhãn cơquan nguồn sai: chấtlượngFAIL/PARTIAL, chưaREADYProduction. GuestSearchLIVEBLOCKED do0/8 vàIPissuance10/10, khôngbypass/reset.73localuniquePASS; Previewauth/owner/Origin/privatepathsPASS. Bổ sung đúngdomainPreviewgiữmọimiềnFirebasecũ; khôngđổiproject/secrets. MainGETvẫn1b1b640/dpl_EJvYVHp8yYb4Ync29JPu91WXWa6c QAcanary, khôngdeploy/DBwritesProduction/migration. Cần trích/đốichiếu ô bảng điểm chính thức và kiểmsoát attribution, hoàn tấtGuestLIVEquota hợp lệ trước mởđạitrà. Xem docs/task42-context-live-validation.md; khôngPII/UID/secrets.


## Task 4.2 — Reader điểm chuẩn (25/10/2026)
Bản sửa tiếp nối 415e245: thêm đối chiếu nội dung công bố CAND2020 và guard số liệu theo đủ diện tuyển sinh; bố cục/năm chưa hỗ trợ từ chối ước lượng. 55 kiểm thử local liên quan PASS, reader HTTPS LIVE PASS; Preview/DeepSeek mới chờ xác minh. Guest staging vẫn hết 8/8 và ngân sách cấp phiên 10/10, không reset/bypass. Production chưa thay. Xem docs/task42-score-evidence-validation.md.
