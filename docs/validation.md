# Xác minh và triển khai

## Chuẩn bị Vercel 2026-10-13

- Backend 26 bài kiểm tra đạt. Chrome browser_login và browser_stories đạt với Firebase/AI giả lập và dữ liệu kiểm thử riêng.
- Đối chiếu dependencies trong requirements.txt với pyproject.toml khớp; phiên bản đã cài nằm trong ràng buộc. Python local 3.14.7 cùng dòng `.python-version` 3.14 được Vercel hỗ trợ.
- Local: 19 trang/API/tài sản trả HTTP 200. Các đường dẫn tài sản HTML và import JS cục bộ tồn tại; không có URL kết nối localhost cố định trong frontend.
- Tiến trình kiểm thử riêng `VERCEL=1`: import app:app và trang HTML/API thành công, không mount assets local để Vercel public CDN phục vụ. Đây không phải Vercel build/deploy thực tế.
- Không commit/push; chưa có deployment mới. SQLite local/RAM chưa phù hợp chat production trên Vercel, cần adapter database bền vững. Xem `vercel-deploy.md`.

## Đăng nhập mở thẳng chat 2026-10-13

- `python tests/browser_login.py` đạt với Firebase giả lập: email/Google mở phiên chat và focus ô nhập, phiên tạm không tự lưu lâu dài, khôi phục phiên, tải lại không tạo trùng, không chuyển trang khi backend lỗi, vẫn quay về trang chủ được.
- Đây là kiểm tra luồng giao diện; chưa xác minh popup Google hoặc tài khoản Firebase thật trong lần thay đổi này.

## Truyện nghề 2026-10-13

- Backend: 26 bài kiểm tra đạt, gồm dữ liệu sáu nghề, nghề/cảnh không hợp lệ, thiếu dịch vụ, lỗi API, ngữ cảnh nghề/cảnh trong lời gọi DeepSeek và các chức năng cũ.
- `tests/browser_stories.py`: Chrome đạt các luồng sáu truyện, chuyển cảnh/phím mũi tên, phản hồi lựa chọn, tự chuyển/dừng, xem cả trang, tổng kết, khởi động lại, DeepSeek giả lập theo cảnh, hủy kết quả cũ, hiển thị an toàn, mobile 390px, giảm chuyển động, nghề không tồn tại và liên kết trang chủ.
- `tests/browser_smoke.py`: các luồng Firebase/chat/mic giả lập cũ đạt. Đã xem ảnh chụp desktop và mobile của trang truyện.
- API hỏi theo cảnh bác sĩ/hội chẩn đã gọi DeepSeek thật, trả HTTP 200 với câu trả lời có nội dung. Chỉ là một câu hỏi tổng hợp, không phải đánh giá đầy đủ chất lượng tư vấn.
- Chưa có video/lồng tiếng; minh họa là SVG/CSS có chuyển động. Nội dung khám phá nghề cần tiếp tục được giáo viên/người làm nghề góp ý. Vercel chưa kết nối và chưa có deployment mới.

## Bản chat và micro trước khi đồng bộ GitHub 2026-10-12

- Sáu lượt DeepSeek thật với dữ liệu tổng hợp đã qua kiểm tra chất lượng bằng `scripts/check_chat_quality.py`; gồm tiếp nối sở thích vẽ và hiểu biết máy tính, hỏi tám nghề, sửa thông tin đã chia sẻ. Kết quả không thay cho thử nghiệm với người dùng thật.
- Backend: `python -m unittest discover -s tests -v` đạt 22 bài kiểm tra. Chrome headless: `python tests/browser_smoke.py` đạt với Firebase và micro giả lập; đã kiểm tra tự dừng sau 3 giây, chèn bản chữ, không tự gửi, hủy và chống callback cũ.
- Google Cloud Speech chưa có credentials; chưa thử micro thật, mạng nhận diện tiếng Việt thật hoặc bản ghi âm trên thiết bị. Vbee đọc giọng không thuộc bản hiện tại.
- Repository GitHub là kho mã nguồn; chưa có deployment công khai. `.env`, credentials, SQLite, `.venv` và artifacts được loại khỏi bản đồng bộ.
- Đã đối chiếu đủ 43 tệp local với cây GitHub sau chuẩn hóa xuống dòng; không thiếu hoặc sai nội dung. Commit `35c2d84ebb234b9984088c9c886b07fa961a51f8` là bản mã chức năng đã đưa lên nhánh `main`.

## AI không đọc thành tiếng 2026-10-12

- Sau khi người dùng reboot: cài lại bằng Windows Update thất bại `0x80200010`; gói vẫn NotPresent. Dịch vụ BITS Stopped/Disabled, wuauserv StopPending/Disabled sau khi khôi phục cấu hình.
- Thử ngắt WARP theo sự đồng ý: lệnh disconnect thành công; chờ Windows Update dừng hết 20 giây nhưng timeout nên chưa chạy lại lệnh cài. WARP được kết nối lại trong finally; xác minh sau cùng Connected, Network: healthy. Không chứng minh WARP là nguyên nhân hay việc ngắt WARP khắc phục được lỗi tải.
- Thử lấy metadata Microsoft bằng HTTPS với xác minh chứng thư thất bại do hostname mismatch; không bỏ xác minh TLS, chưa tải/cài gói ngoại tuyến. Không kill dịch vụ hệ thống hoặc tự reboot.
- Thêm script cài thủ công `scripts/install-windows-vietnamese-voice.ps1`, đã chạy và ghi nhận lỗi thực tế ở trên; chờ trạng thái dịch vụ có giới hạn, khôi phục StartupType trong finally. Không thay đổi mã ứng dụng ở lần thử sau reboot này.
- Chrome headless không stub giọng: danh sách thật 22 giọng, không có vi/vi-VN. Chỉ đọc danh sách, chưa phát tiếng Việt thật.
- Windows capability `Language.TextToSpeech~~~vi-VN~0.0.1.0`: NotPresent. Người dùng cho phép cài; lần đầu thất bại do dịch vụ Disabled. Thử tạm bật Windows Update/BITS nhưng Windows Update kẹt StopPending. Chưa cài được, đã trả StartupType của hai dịch vụ về Disabled; BITS Stopped, wuauserv StopPending. Không reboot hoặc kill dịch vụ hệ thống.
- `python -m unittest discover -s tests -v`: 23 test đạt. `python tests/browser_smoke.py`: đạt hồi quy và ca mới thử giọng, volume/resume, bộ đọc không phát sự kiện start trong 6 giây, thiếu giọng mở hướng dẫn và tắt tự đọc. Test Web Speech này dùng stub.
- Đã sửa một lỗi đóng hộp thử giọng hủy nhầm lần nghe mới, phát hiện qua ca browser. Chưa xác minh nghe được tiếng trên loa người dùng; cần cài xong giọng và thử thật.

## Giọng trình duyệt 2026-10-11

- `python -m unittest discover -s tests -v`: 23 test backend đạt sau tích hợp fallback phía client.
- `python tests/browser_smoke.py`: Chrome headless đạt luồng cũ và Web Speech stub mới. Kiểm tra tiếng Việt, giữ draft, interim không lặp, không tự gửi, hủy không ghi đè, lỗi quyền micro, chọn giọng Việt, đọc nhiều đoạn/dừng, bật micro dừng đọc, thiếu giọng Việt báo rõ và browser không hỗ trợ vẫn chat chữ.
- Chế độ Web Speech không gọi endpoint `/api/voice/*` của ứng dụng. Test dùng giả lập nhận diện/giọng đọc, không xin micro hoặc gửi audio thật. Chưa xác minh giọng Việt đã cài, quyền/thiết bị micro hoặc dịch vụ nhận diện của browser trên máy người dùng.
- Đã khởi động server local ẩn trên cổng 8000 và kiểm tra `/api/health`, `/ai-career-advisor`, `/assets/browser-voice.js` đều HTTP 200; mở URL chat qua trình duyệt mặc định của máy.

## Kiểm tra thật sau nhận khóa dịch vụ 2026-10-11

- DeepSeek `GET /models`: HTTP 200, có model `deepseek-flash` và `deepseek-v4-pro`.
- `scripts/check_live_providers.py`: LangGraph gọi DeepSeek thật thành công với nội dung mẫu, chế độ live và đầu ra JSON hợp lệ. Lượt yêu cầu danh sách nghề trả ba nghề khác nhau; câu trả lời đi qua validator trước khi lưu vào phiên RAM tổng hợp.
- Vbee lấy danh sách giọng tiếng Việt: HTTP 200, 35 giọng trong kết quả; chọn HN - Ngọc Huyền. Request TTS sync thật trả HTTP 400, thông báo `This feature is not supported in user package`. Chưa có audio thành công; không suy diễn token hợp lệ với danh sách giọng thành quyền dùng sync TTS.
- `.env` local đã tắt demo, lưu khóa riêng và tạm tắt Vbee vì hạn chế gói. UI nhận lý do tạm tắt qua API config; không gọi TTS tự động khi bị tắt. Google STT chưa có credentials.
- Sau cập nhật cấu hình: `python -m unittest discover -s tests -v` đạt 23 bài, gồm kiểm tra tắt Vbee vẫn chat được; `python -m compileall -q advisor scripts` thành công. `python tests/browser_smoke.py` chạy lại đạt với Firebase stub và chế độ demo trong tiến trình test riêng.
- Chưa kiểm tra toàn bộ browser dùng Firebase thật + DeepSeek thật, Vbee phát audio thật hoặc Google STT. Các kết quả browser bên dưới dùng fixture; không đổi bản chất của chúng.

## Cập nhật 2026-10-11: chat AI 1:1

- `python -m unittest discover -s tests -v`: 22 bài kiểm tra đạt; giữ nguyên 12 test cũ và thêm 10 test tư vấn/voice.
- Xác minh API yêu cầu đăng nhập; tài khoản khác không thể xem/sửa/xóa/chat/phát giọng từ phiên không thuộc quyền. Header no-store cho dữ liệu tư vấn.
- Demo có nhãn, input rỗng/quá dài bị từ chối; gửi lại cùng UUID không tạo trùng, UUID cùng nội dung khác trả 409.
- SQLite lưu qua instance store mới khi đồng ý; phiên không đồng ý không nằm trong database. Xóa dữ liệu một tài khoản không ảnh hưởng tài khoản khác.
- Test mock DeepSeek xác minh URL/model, lịch sử nhiều lượt, JSON/profile và ít nhất ba nghề khác nhau; phản hồi không hợp lệ không được lưu.
- Test mock Google STT xác minh WAV/base64/vi-VN; âm thanh trống/sai định dạng/quá dài bị từ chối. Mock Vbee kiểm tra App-Id, sync payload, MP3 và chia đoạn/bỏ Markdown.
- `python tests/browser_smoke.py`: Chrome headless chạy thành công với Firebase stub ở tiến trình test riêng trên loopback. Kiểm tra khách về hộp đăng nhập cũ, đăng nhập chuyển sang chat, gửi demo, đổi tên, refresh khôi phục lịch sử, DOMPurify chặn HTML/JavaScript độc hại, mở hồ sơ, drawer mobile/không tràn ngang, WAV client, đăng xuất. Không có exception JavaScript.
- Ảnh kiểm tra nằm trong `artifacts/advisor-desktop-welcome.png`, `advisor-desktop-chat.png`, `advisor-mobile-welcome.png`, `advisor-mobile-history.png`; artifacts và dữ liệu SQLite không đưa lên GitHub.
- Chưa kiểm thử đăng nhập Firebase thật, DeepSeek thật, Google Speech thật, Vbee thật hoặc micro/VAD với thiết bị thật vì chưa có khóa dịch vụ và chưa dùng tài khoản học sinh để thử. Không coi fixture/mock là xác minh provider thật.
- `.env` local bật `AI_DEMO_MODE=true` khi chưa có DeepSeek key; `.env.example` mặc định false. Hướng dẫn ở `docs/ai-advisor.md`.
- Chưa push thay đổi chat hoặc deploy Vercel. Người dùng hiện đã hoãn deployment; SQLite/RAM của bản local cần thay adapter và khóa dùng chung trước khi chạy serverless/nhiều worker.

## Cập nhật 2026-10-07: đăng nhập Firebase

- `python -m unittest discover -s tests -v`: 12 bài kiểm tra đạt (4 trang chủ, 2 luồng AI với mock, 6 Firebase backend).
- Test Firebase dùng khóa RSA sinh tại thời điểm chạy test: xác minh chữ ký hợp lệ, từ chối chữ ký bị sửa, token unsigned/header sai, token hết hạn, audience/issuer/sub/auth_time không hợp lệ.
- Đã kiểm tra cache chứng thư, lỗi kết nối Google, header Bearer, header no-store trên API xác thực và không lộ cấu hình DeepSeek trong endpoint cấu hình Web.
- `python -m compileall -q app.py firebase_auth.py`: thành công.
- Mã giao diện có đăng ký, đăng nhập email/mật khẩu và Google, quên mật khẩu, xác minh email, đăng xuất và lựa chọn lưu phiên. Chưa chạy kiểm thử bằng trình duyệt.
- Người dùng xác nhận trang chủ hiện có chạy tốt trên máy. Đây là xác nhận của người dùng, không phải browser QA của trợ lý cho phần Firebase mới.
- Đã nhận firebaseConfig và thiết lập `.env` cục bộ cho project `khoa-hoc-86942`; kiểm tra `/api/auth/config` trả configured=true và trang chủ trả HTTP 200. Chưa xác nhận provider/authorized domains ở Console, chưa thử tạo tài khoản thật, Google popup hoặc gửi email thật; xem `firebase-setup.md`.
- LangGraph hiện đã có trong môi trường và hai test AI đã chạy; chưa gọi DeepSeek thật.
- Vercel vẫn chưa có deployment được xác nhận.

## Lịch sử 2026-10-06

## Đã chạy thành công

- `python -m unittest discover -s tests -p test_app.py -v`: 4 bài kiểm tra đạt bằng Python và thư viện có sẵn của máy.
- Kiểm tra trang chủ và tài sản CSS/JavaScript/SVG trả HTTP 200.
- Kiểm tra tìm kiếm “bac si” và “BÁC SĨ”, lọc Sáng tạo và kết quả rỗng.
- Kiểm tra ba bài viết có nội dung đầy đủ.
- Kiểm tra AI khi thiếu key trả 503; câu hỏi rỗng, quá ngắn, quá dài trả 422.
- `python -m compileall -q app.py ai.py content.py`: mã Python biên dịch thành công.
- Kiểm tra HTML không trùng ID, selector JavaScript tham chiếu đúng ID và tài sản cục bộ tồn tại.
- Đã lưu 20 tệp mã nguồn/tài liệu lên nhánh `main` của https://github.com/TrooliGM/quocan4; commit ứng dụng `9ead1787bf959bc33557bd45f5b66f38ff982d5d`.
- Đã đọc lại cây tệp GitHub để xác minh mã nguồn được lưu.

## Giới hạn tại ngày 2026-10-06

- Máy có FastAPI/httpx/python-dotenv, chưa có LangGraph. Yêu cầu tải thư viện qua mạng đã bị người dùng từ chối; không tiếp tục cài bằng cách khác.
- Đã viết `tests/test_ai.py` cho luồng LangGraph, payload DeepSeek và xử lý lỗi nhà cung cấp, nhưng chưa chạy vì thiếu LangGraph.
- Chưa gọi DeepSeek thật; chưa có API key được cấu hình.
- Chưa kiểm tra trực quan bằng trình duyệt hoặc chạy JavaScript trong trình duyệt.
- Đã chuẩn bị cấu hình Vercel; chưa có tài khoản/công cụ Vercel khả dụng để xác nhận deployment. Không có URL website đã triển khai trong phiên này.
- Đã tìm thấy plugin Vercel và đề xuất kết nối; chưa xác nhận cài đặt/kết nối tài khoản.

## Kiểm tra tiếp theo trên môi trường đủ dependencies

1. Cài `requirements.txt`, chạy toàn bộ `python -m unittest discover -s tests -v`.
2. Mở trang trên điện thoại và desktop; kiểm tra tìm kiếm, bộ lọc, hộp thoại và menu bằng chuột/bàn phím.
3. Cấu hình key trên server hoặc Vercel, kiểm tra trợ lý bằng câu hỏi nghề nghiệp mẫu.
4. Import GitHub repository vào Vercel và kiểm tra đường dẫn tài sản sau khi deploy.
