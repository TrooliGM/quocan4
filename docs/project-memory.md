# Bộ nhớ dự án: Website Hướng nghiệp KHKT 2027

## Nhánh lưu thay đổi điều hướng — 2026-10-17

- Người dùng đã xác nhận lưu các thay đổi hiện tại lên một nhánh GitHub mới; yêu cầu này cho phép commit/lưu mã, thay cho giới hạn không commit/push ở các lượt triển khai trước. Vẫn không merge hoặc deploy.
- Đã tạo nhánh `feat/ai-career-story-navigation` của `TrooliGM/quocan4` từ `fix-chat-vercel` tại commit `ad18135b6953d164f387f2c3260248eaceda1153`.
- Nội dung mốc lưu gồm điều hướng Hero/Navbar, nhận diện ý định Truyện nghề, frontend CTA an toàn, các kiểm thử mới và bộ nhớ/tài liệu. Loại `.env`, dữ liệu local, credentials, artifacts và caches; giữ các nhánh gốc nguyên trạng.

## Chat gợi ý Truyện nghề theo ý định — 2026-10-17

- Yêu cầu trực tiếp trong tệp đính kèm: nhận diện câu hỏi về một ngày/ca làm việc và trải nghiệm thực tế, đề xuất mở Truyện nghề bằng nút xác nhận, giữ chat/lịch sử/Firebase và không commit/push/deploy.
- Phân tích route thật: `/mot-ngay-lam-viec` phục vụ `stories.html`; `stories.js` đã hỗ trợ `?nghe=<career_id>` và API `/api/career-stories`. Có sẵn liên kết quay về `/ai-career-advisor`, tự khôi phục phiên theo UID/sessionStorage. Không tạo trang, route hoặc cơ chế đăng nhập khác.
- Đã mở rộng bước `compress_context` hiện có trong LangGraph để DeepSeek trả `story_intent` gồm intent, các tên nghề và confidence; dùng tám tin nhắn gần nhất, summary và danh mục truyện để hiểu đồng nghĩa/nghề từ ngữ cảnh. Không thêm lời gọi LLM ngoài hai lời gọi chat + metadata vốn có. Node `suggest_career_story` đối chiếu danh mục sáu truyện, chuẩn hóa tên (kỹ sư phần mềm → lập trình viên), ngưỡng confidence 0.75; có quy tắc dự phòng khi metadata lỗi/demo, không dựa duy nhất vào từ khóa.
- Xử lý thiếu nghề bằng câu hỏi làm rõ; nghề chưa có truyện không nhận URL giả; nhiều nghề có lựa chọn riêng. Câu hỏi chỉ về lương/kỹ năng/cơ hội và lời từ chối không thêm nút. Kết quả semantic `none` có độ tin cậy cao được tôn trọng.
- Frontend tạo nút bằng DOM/textContent, xác minh ID qua API danh mục và tự ghép route cố định `/mot-ngay-lam-viec?nghe=<id>`, bỏ qua href/HTML/ID lạ trong metadata. Không tự chuyển trang. CSS nút giữ nền kem/xanh rêu/cam san hô hiện có và hỗ trợ focus/giảm chuyển động.
- `story_navigation` được lưu trong JSON của tin nhắn assistant cho cả SQLite/RAM và đường lưu PostgreSQL; không đổi schema hoặc chạy migration. Không sửa `.env`, Firebase, Navbar, route/trang Truyện nghề hoặc cấu hình Vercel.
- 35 bài backend đạt; nhóm PostgreSQL skip vì thiếu PostgreSQL kiểm thử. Ba script Chrome headless `browser_story_intent.py`, `browser_smoke.py`, `browser_stories.py` đều đạt: đủ các trường hợp chính, nút chỉ điều hướng khi nhấn, mở đúng truyện, quay lại giữ lịch sử đã lưu và phiên tạm, mobile, danh mục/Navbar và chống URL/HTML giả mạo.
- Một lời gọi DeepSeek thật bằng dữ liệu tổng hợp đã nhận đúng nghề lập trình từ câu hỏi không có cụm từ khóa cố định, nhờ ngữ cảnh trước đó. Không dùng tài khoản/dữ liệu người dùng. Chưa kiểm tra PostgreSQL/Firebase thật hoặc mọi cách diễn đạt với model thật; phiên tạm vẫn chịu TTL/RAM như kiến trúc hiện hữu. Health/trang chat/trang truyện/API nghề local đều HTTP 200.

## Điều hướng Hero và Navbar — 2026-10-17

- Yêu cầu trực tiếp: chuyển toàn bộ hành vi đang hoạt động của mục Navbar “Tư vấn cùng AI” sang nút Hero “Bắt đầu khám phá”, sau đó bỏ mục Navbar này trên desktop/mobile; giữ thiết kế và toàn bộ hệ thống khác, không commit/push/deploy.
- Phân tích mã: Hero trước đây là liên kết `href="#careers"` cuộn tới thư viện nghề, không có onclick hoặc handler riêng. Mục AI là liên kết `href="/ai-career-advisor"`; listener chung `#nav-links a` chỉ đóng menu mobile. Xác thực/lịch sử được xử lý trong trang chat qua `initialize()`, `getFirebase()`, `restoredUser()`, API hiện hữu và sessionStorage theo UID, không nằm ở mục Navbar.
- Đã đổi duy nhất hai dòng mã trong `public/index.html`: Hero dùng `href="/ai-career-advisor"`, giữ nguyên nội dung, class, icon và thiết kế; xóa liên kết AI khỏi `#nav-links` dùng chung desktop/mobile. Các mục còn lại và nút tài khoản giữ nguyên; CSS flex hiện có tự phân bố lại, không cần sửa CSS. Không thêm JavaScript listener.
- Giữ đúng luồng nhánh hiện tại: chưa có người dùng thì chat thử Firebase Anonymous; guest cần PostgreSQL, còn API 401 quay về `/?login=1`. Sau email/Google thành công, logic cũ chuyển `/ai-career-advisor?start=1`. Không thêm cổng đăng nhập hoặc viết lại logic chat.
- Chrome headless/Firebase giả lập đã so sánh Navbar cũ → Hero trước khi xóa Navbar → trạng thái cuối: desktop 1440px/mobile 390px, Hero giữ nguyên nội dung/style/kích thước/vị trí; menu còn đúng năm liên kết và nút tài khoản, mobile mở/đóng; cùng luồng khách/401, email vào chat, giữ nguyên UUID phiên và nội dung lịch sử khi trở lại qua CTA, một lần điều hướng mỗi lần nhấn, không có exception JS ứng dụng. Script và ảnh QA nằm trong `artifacts/navigation-change/` và `artifacts/navigation-*.png`, không thuộc mã triển khai.
- 26 bài backend đạt; nhóm PostgreSQL skip do chưa có PostgreSQL kiểm thử. Fingerprint xác nhận mọi tệp backend/JS/CSS/.env/Vercel/dữ liệu local không đổi. Chưa thử Firebase/Google thật hoặc guest PostgreSQL thật; các hạn chế có sẵn của nhánh vẫn giữ nguyên.

## Bản local từ fix-chat-vercel — 2026-10-17

- Người dùng yêu cầu cập nhật dữ liệu từ nhánh `fix-chat-vercel` của `TrooliGM/quocan4`. Đã cập nhật 35 tệp theo commit `ad18135b6953d164f387f2c3260248eaceda1153` ngày 2026-10-15, thông điệp “Add PostgreSQL guest chat and account linking”. Đây là snapshot mã đang chạy local, thay cho snapshot `main` trước đó; thư mục vẫn không có `.git` nên không phải Git checkout.
- Đủ 67 tệp của nhánh trên máy: 64 tệp khớp Git blob SHA sau chuẩn hóa xuống dòng; ba tệp bộ nhớ/quyết định/xác minh được hợp nhất để giữ các ghi nhận local. Giữ nguyên tài liệu Excel chỉ có trên máy. Không push, deploy hoặc thay đổi nhánh trên GitHub.
- Đã sao lưu các tệp local cần thay thế tại `artifacts/branch-sync/fix-chat-vercel-ad18135-20261017/`; đối chiếu SHA-256 xác nhận `.env` và tệp dữ liệu local không đổi. Đã cài `psycopg[binary]` theo requirements của nhánh.
- Nhánh bổ sung adapter PostgreSQL, lưu chat bằng PostgreSQL, chat khách giới hạn 8 câu, quota/rate limit và chuyển lịch sử khách khi liên kết tài khoản; đây là tính năng có trong mã, chưa xác nhận chạy đầy đủ trên môi trường hiện tại. `DATABASE_URL` local vẫn là SQLite; không migrate dữ liệu, không tự tạo/kết nối Neon hoặc chạy migration production. Chat khách yêu cầu PostgreSQL và Firebase Anonymous; tài khoản đăng nhập vẫn có đường chạy SQLite.
- Kiểm tra lại: 26 bài backend đạt; nhóm PostgreSQL bị bỏ qua do thiếu PostgreSQL kiểm thử local. `browser_smoke.py` và `browser_stories.py` đạt với dữ liệu giả. `browser_login.py` chưa đạt ở lượt đăng nhập Google giả lập, timeout khi chờ mở chat sau Google; chưa sửa mã nhánh hoặc kết luận đăng nhập Google thật bị lỗi. Không thử provider trả phí hay tài khoản người dùng.
- Server ở `127.0.0.1:8000` đã nạp route mới `/api/ai/guest/claim`; trang chủ, chat, truyện và tài sản account-link trả HTTP 200. Health vẫn xác nhận AI/Firebase có cấu hình. Cần tải lại trình duyệt để lấy frontend mới.
- Một số tài liệu của nhánh còn ghi lịch sử “chưa có adapter PostgreSQL” hoặc “chưa đồng bộ”; đọc cùng ghi nhận mới nhất ở đây. Chưa có deployment Vercel hoặc kết nối PostgreSQL thật được xác minh trong lần cập nhật này.

## Đối chiếu GitHub 2026-10-17

- Theo yêu cầu cập nhật tệp từ GitHub và xem tiến độ, đã đọc nhánh `main` của `TrooliGM/quocan4`. Commit mới nhất là `346e9757dec7ebce43f74b815ccb138758cfa077`, ngày 2026-10-13, thông điệp “Record career comics validation and local-first deployment decision”.
- Đã đối chiếu SHA Git blob sau chuẩn hóa CRLF/LF: đủ 53 tệp của repository trên máy; 51 tệp khớp hoàn toàn. Hai tệp `docs/project-memory.md` và `docs/decisions.md` có thêm ghi nhận local về cấu hình Firebase/DeepSeek, không thiếu dòng nào của bản GitHub; giữ các cập nhật local. Không có mã nguồn mới cần tải đè.
- Giữ nguyên `.env`, thư mục dữ liệu local và hai tệp tham khảo chỉ có trên máy (`docs/ai-career-requirements.md`, `docs/sources/8_chuc_nang_AI_tu_van_viec_lam.xlsx`). Không push hoặc deploy trong lần kiểm tra này.
- Chạy lại `python -m unittest discover -s tests -v`: 26 bài đạt. Lượt đầu trong sandbox bị chặn thư mục tạm Windows; chạy lại ngoài sandbox sau khi được cấp quyền thì đạt. Không chạy lại browser QA hoặc gọi provider thật ngày 2026-10-17.
- Tiến độ: đã có trang chủ/tìm nghề/bài viết, Firebase, chat AI 1:1 với bộ nhớ/lịch sử theo lựa chọn, micro và sáu truyện nghề gồm 24 cảnh SVG/CSS tương tác, có AI giải thích theo cảnh. Chưa có trắc nghiệm hoàn chỉnh, tìm tin tuyển dụng/phân tích CV hoặc quản trị; chưa có deployment công khai được xác nhận. Hướng local trước và yêu cầu database bền vững khi triển khai chat vẫn được giữ.

## Khôi phục cấu hình AI 2026-10-13

- Người dùng cung cấp lại khóa DeepSeek để bật gửi câu hỏi. Đã điền khóa vào `.env` cục bộ, đặt `AI_DEMO_MODE=false`, giữ cấu hình Firebase và các thiết lập khác; không ghi giá trị khóa vào tài liệu hoặc repository.
- Đã kích hoạt nạp lại server local; `/api/health` xác nhận `ai_configured=true` và `auth_configured=true`. Đã gửi một câu hỏi tổng hợp về khám phá nghề lập trình tới `/api/advice`: HTTP 200, có câu trả lời thật, model `deepseek-flash`.
- Người dùng cần tải lại trang chat để nhận trạng thái mới. Chưa kiểm thử gửi câu hỏi qua phiên Firebase của người dùng; không sử dụng dữ liệu cá nhân trong kiểm tra AI.

## Cập nhật Firebase 2026-10-13

- Theo cấu hình và yêu cầu trực tiếp mới nhất của người dùng, đã cấu hình Firebase project `khkt-b8fdd` trong `.env` cục bộ, thay cho project `khoa-hoc-86942` được ghi nhận trước đây. Tại thời điểm kiểm tra chưa có `.env`, nên tạo từ `.env.example`, điền năm biến Firebase và giữ các thiết lập khác của mẫu. Không khôi phục hoặc tự thay đổi các khóa dịch vụ khác.
- Hàm cấu hình và `/api/auth/config` qua FastAPI TestClient xác nhận `configured=true`, đúng project mới; endpoint trả HTTP 200. Chưa kiểm thử đăng ký/đăng nhập thật, chưa xác nhận provider và authorized domains trên project mới. Cần khởi động lại server đang chạy để nhận cấu hình mới.
- Chỉ lưu cấu hình trong `.env` đã được `.gitignore` loại trừ; không ghi API key vào bộ nhớ dự án. Không di chuyển tài khoản hoặc dữ liệu giữa hai Firebase project.
- Khi người dùng báo nút đăng nhập bị khóa, đã kiểm tra server thật ở `127.0.0.1:8000`: ban đầu `/api/auth/config` trả `configured=false` dù `.env` đủ cấu hình. Đã kích hoạt Uvicorn `--reload` bằng thời gian sửa của `app.py` (không đổi nội dung mã). Endpoint server thật sau nạp lại trả HTTP 200, `configured=true`, đúng project `khkt-b8fdd`. Cần tải lại trang trình duyệt; chưa thử đăng ký/đăng nhập thật của người dùng.

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
