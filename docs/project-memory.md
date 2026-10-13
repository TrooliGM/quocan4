# Bộ nhớ dự án: Website Hướng nghiệp KHKT 2027

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
