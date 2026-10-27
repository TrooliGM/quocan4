# Task 4.2 — Đối chiếu điểm chuẩn trước phát hành

## Bản sửa ngày 25/10/2026

Tiếp tục HEAD 415e245, không sửa giao diện, quota, Firebase hoặc database. Production vẫn là canary 1b1b640, chưa mở Search đại trà.

Nguyên nhân: snippet tổng hợp đưa dải 19,61–23,09 cho nam Học viện CSND 2020, bỏ sót C03=18,88. Link hợp lệ và đúng chủ đề không chứng minh số liệu đúng. LLM còn tự đặt nhãn website thành Cổng Bộ Công an.

- Đọc nội dung công bố công khai bằng HTTPS ghim IP đã kiểm tra, TLS/SNI, không redirect; chỉ HTML UTF-8, tối đa 256 KB, thời gian/worker hữu hạn; không thực thi nội dung trang.
- Reader nhận diện bố cục công bố CAND 2020 trên website Học viện CSND. Giữ riêng năm/trường/ngành/giới/khu vực/tổ hợp/tiêu chí phụ. Không suy diễn giá trị cho chiều dữ liệu không được bài tách.
- Giữ source metadata server của chính phiên để đọc lại công bố đã tìm thấy ở lượt trước; không tải URL tự do từ lời người dùng/LLM.
- Chỉ một dòng khớp chính xác mới được trả điểm. Với yêu cầu số liệu điểm chuẩn CAND, đầu ra số được dựng từ dòng đã xác minh, thay vì tin con số LLM. Thiếu/khác bố cục/năm/diện tuyển sinh: từ chối ước lượng và hỏi làm rõ. Không tự tạo dải điểm từ snippet thứ cấp. Đây là giới hạn có chủ ý; chưa phải reader mọi bảng tuyển sinh.
- Tách website đăng bài, đơn vị cung cấp thông tin, nguồn bài ghi; URL thông báo xuất bản đầu tiên để null khi chưa chứng minh. Nhãn citation lấy từ metadata nguồn, không để model đổi thành cơ quan khác.
- Chung pipeline/guard cho chat và hai API AI tương thích, không thêm lượt AI/quota. Profile QA-only giữ nguyên.

## Kiểm thử đã chạy

- 34/34 PASS: regression số liệu + ngữ cảnh + API/PostgreSQL local; trong đó 11 test mới, có override con số sai từ model cho Guest/member/QA, retry không gọi AI/lấy quota thêm.
- 21/21 PASS: DDGS policy, giới hạn worker, URL/SSRF, quyền riêng tư và citation. Một lỗi tương thích citation thiếu title trong fixture đã sửa fallback hostname; chạy lại đạt.
- Reader HTTPS LIVE trên công bố Học viện CSND: PASS, 0,71 giây, A01 nam Nghiệp vụ Cảnh sát 2020=23,09. C03=18,88 và D01=19,61 được kiểm trong fixture trích dữ kiện của công bố, có nữ và tiêu chí phụ riêng.
- Nguồn: https://hvcsnd.edu.vn/cong-bo-diem-chuan-vao-cac-truong-cand-2020-10051 . Website Học viện ghi nguồn Báo CAND, đơn vị cung cấp Cục Đào tạo/Bộ Công an; không coi website Học viện là cổng Bộ.
- Staging read-only: ngân sách cấp Guest/IP/ngày vẫn 10/10, còn khoảng 59.205 giây ở thời điểm kiểm tra; Guest hiện có đã 8/8. Không reset, nâng hạn mức hoặc tạo định danh thay thế để lách.

## Còn kiểm tra

Build/Preview mới, DeepSeek LIVE số liệu và injection nguồn. Guest Search LIVE còn BLOCKED đến khi có hạn mức hợp lệ; không dùng PASS mock thay cho LIVE. Không mở Search mọi người ở Production trước khi điều kiện này và các điều kiện an toàn hoàn tất. Không migration hoặc ghi thử Production.

## Preview đầu và sửa ngữ cảnh nối nhiều lượt

Preview 58af80c / dpl_6tSqKtWz8XxGpWe2SYeW8LE3AJkL READY. Sáu lượt DeepSeek LIVE thực tế (member/QA × 3): câu rộng hỏi làm rõ, A01 nam 2020 trả đúng 23,09 từ nội dung công bố, attribution chính xác. Lượt đổi tiếp C03 đã mất năm do gặp câu làm rõ trường/tổ hợp trước khi duyệt tới năm ở xa hơn; guard từ chối đưa số nên không trả sai. Đây là FAIL ngữ cảnh cần sửa, không đánh dấu PASS.

Bổ sung duyệt năm công khai gần nhất trong giới hạn lịch sử, không đi qua mốc đổi chủ đề hoặc dữ liệu riêng tư. Thêm regression chuỗi hai lần làm rõ và mốc đổi chủ đề. 30 test số liệu/ngữ cảnh PASS sau sửa (tổng 56 phương thức liên quan đã kiểm, gồm các nhóm trước). Cần xác minh lại riêng lượt C03 trên Preview mới; không chạy lại các ca đã PASS.

Preview a77f077 giữ đúng năm ở query C03, nhưng chưa đọc được bảng: hai link công bố mới có bố cục chưa được reader hỗ trợ đã chiếm ngân sách hai tài liệu trước link bảng từng xác minh trong phiên. Không phải đã chứng minh lỗi DDGS timeout. Guard tiếp tục từ chối số, không đưa sai điểm. Sửa thứ tự ưu tiên tài liệu từng được server đối chiếu và tiêu đề bố cục đã kiểm; bỏ host chưa có parser khỏi ngân sách GET, vẫn ghim HTTPS và đọc lại theo TTL. Regression với 4 link chưa hỗ trợ đứng trước một nguồn đã xác minh: PASS. 13 test số liệu PASS (tổng 57 phương thức đã kiểm). Cần chạy lại đúng ca LIVE C03 trên candidate tiếp theo.

## Kết quả cuối thực tế

- Candidate code: **d8491beff386b14a32d626347ac8943d140840c3**; Preview **dpl_G2gH5FQvHqDpUGnD1Hyc4BXip98N**, READY, target Preview, staging br-morning-tooth-aznv081q. URL: https://quocan4-d4l1v1bx7-khkt3.vercel.app/ai-career-advisor . Deployment Protection giữ nguyên (cần quyền Vercel); không coi endpoint chỉ cần config enabled là đã nghiệm thu.
- LIVE đã gọi 9 lượt chat DeepSeek có kiểm soát qua API staging: 6 lượt ở candidate đầu, 1 lượt kiểm tra lại C03 chưa có bảng, 2 lượt C03 sau sửa. Hai ca A01 member/QA trước đó được kế thừa PASS 23,09; candidate cuối C03 member/QA PASS 18,88 từ đúng dòng 2020 nam Nghiệp vụ Cảnh sát. Các ca chưa xác minh không đưa số ước lượng. Model vẫn được gọi thật; phần trả số là guard xác định từ bảng, không tuyên bố model tự suy luận ra số đúng. Cache được nói rõ trong đáp án.
- Candidate cuối C03: member 4,73 giây, QA 5,55 giây. Retry cùng request_id trả duplicate, giữ nguyên câu trả lời, không thêm lượt gọi AI. Không tuyên bố hết timeout cho mọi câu hỏi/mọi lần DDGS.
- Sau sửa ưu tiên nguồn: 13/13 unit số liệu PASS; test PostgreSQL/API số liệu cho cả ba role và retry được chạy lại PASS. Tổng 57 phương thức liên quan đã chạy đạt; các test bảo vệ quota/concurrency/rate/proxy đã PASS trước đó được kế thừa, không chạy lại toàn Super Board.
- Preview LIVE bảo mật: token sai 401 ở cả 3 API AI; chủ phiên GET200, member/Guest khác chủ404; Origin khác403 ở route guest/session; hai API cũ trả429 với Guest hết8/8 kể cả header giả danh/X-Forwarded-For; đường dẫn secrets/source/artifacts404. 200 nghề/12 nhóm không đổi. Profile vẫn QA-only, Search bật cả ba role trên Preview, dùng cùng Task4.1.
- Chrome thật: Firebase SDK email/password đăng nhập PASS, header/nguồn HTTPS/noopener và không tràn ngang desktop1440/mobile390 PASS; đã xem ảnh C03 đúng18,88 và phần phân biệt nguồn trong phản hồi. Ảnh ở artifacts/task42-score-search-1440.png và -390.png, không commit. Không đánh dấu popup Google mới là PASS; bằng chứng người dùng Google ở Production trước đó vẫn giữ phạm vi cũ.
- Chỉ thêm chính xác hostname Preview vào Firebase authorized domains, giữ toàn bộ miền cũ, không đổi project/key. Không chỉnh Firebase Production logic.
- **BLOCKED Guest Search LIVE**: phiên QA đã8/8, ngân sách cấp phiên/IP ngày10/10; người dùng cũng xác nhận phiên khách của mình hết lượt. Không tạo định danh/IP/DB khác, reset hoặc nâng giới hạn để lách. Chưa có kiểm thử trang bên ngoài mang prompt injection LIVE; parser/injection boundary ngoại tuyến PASS, không thay bằng lời khẳng định LIVE.
- **NOT READY FOR PRODUCTION mở Search mọi role**. Production alias vẫn dpl_EJvYVHp8yYb4Ync29JPu91WXWa6c /1b1b64080a00a389d8b93a0fb8f35d0e7bf91dd8, không deploy/migration/reset/ghi dữ liệu thử Production. GitHub feature remote vẫn fb2eca4; các checkpoint sửa local chưa push do gate còn thiếu.

Bước tiếp: nghiệm thu Guest bằng hạn mức hợp lệ theo chính sách hiện có, hoàn tất phần LIVE còn thiếu; giữ nguyên canary Production đến khi đủ điều kiện. Reader hiện chỉ chứng minh bố cục công bố 2020 đã kiểm, không hứa đọc được mọi bảng/ảnh/PDF/năm khác. Với bố cục chưa hỗ trợ, báo chưa xác minh thay vì đoán.
