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
