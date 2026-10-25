# Task 4.3 — Hành động trong hệ sinh thái La Bàn

Checkpoint nền b2d55e0 (Production runtime bd906df). Worktree riêng task-4-3 / feat/task-4-3-ecosystem-actions; không sửa checkout chính đang dirty hoặc Production.

## Thiết kế

Cùng completion DeepSeek hiện tại có thể trả lời Markdown như cũ hoặc gọi hàm kết thúc present_laban_actions với answer tự viết, ý định, trích lời học sinh làm căn cứ và tối đa4 đề xuất kind/career_id. Không thêm một lượt phân loại LLM, không thực thi công cụ tùy ý. Danh mục rút gọn ID/tên của đủ200 nghề (8.651 ký tự) và tham chiếu các nhóm nút trước được cung cấp để model hiểu ngữ nghĩa/viết tắt/thứ tự; không hardcode câu trả lời hoặc router hiểu ý chỉ dựa từ khóa. Nghề chưa rõ cần hỏi lại; không chuyển mọi lời nhắn thành hướng nghiệp.

Backend đối chiếu ID/name và truyện có thật, tự dựng nhãn và URL theo ba kind: career_profile, career_story (gồm một ngày làm việc), career_exploration. ID null chỉ được mở thư viện nghề/truyện. Không có trường URL trong proposal. Backend chặn key thừa, ID không tồn tại, URL giả, nhãn/đường dẫn không canonical và căn cứ chỉ có trong web/lời AI. Việc này không cấp quyền hồ sơ, không tự xác nhận nghề suy luận.

Metadata navigation_actions đi cùng câu trả lời trong JSON messages hiện có, bảo toàn qua save PostgreSQL atomic, chế độ tạm/lâu dài, nén ngữ cảnh và retry; tin nhắn cũ mặc định danh sách rỗng. Hai API tương thích cũng trả metadata khi lưu/retry. Không migration.

Frontend dùng DOM textContent và kiểm lại hình dạng URL theo kind/ID, nút xanh/kem nhỏ cùng hệ Premium, focus rõ và vùng nhấn tối thiểu46/48px. Nút là anchor mở tab mới noopener/noreferrer, lưu draft tại tab chat trước khi mở, không POST AI hoặc tự chuyển trang. Hội thoại và khảo sát trong tab cũ giữ nguyên. Helper login-return giữ thêm tham số career cho modal hồ sơ; vẫn loại URL ngoài/return_to tùy ý. Cache version HTML/chat.js/chat.css được đổi cho đúng bản mới.

## Kiểm thử đã chạy

- 15 test PASS: unit builder/metadata/security, PG local thật lưu/read/retry cho Guest/Member/QA, tạm/lâu dài, owner404, cùng completion một lần; cộng regression pipeline Task4.2.
- Local Chrome fixture PASS: XSS/open redirect, tab cũ và draft, target mới đúng route, không POST, helper auth-return và viewport1440/390. Fixture này không phải xác minh Google popup hoặc khả năng hiểu tiếng Việt của model LIVE. Lỗi mở tab đầu tiên do fixture không cấp userGesture đã sửa trong harness, không sửa sản phẩm.
- Đang chạy nhóm regression bảo vệ/quota/Search. Chưa có Preview hoặc LIVE Task4.3 tại checkpoint này; không đánh dấu đã hoàn tất.

## Phạm vi phát hành

Chỉ Preview dùng staging riêng và cấu hình Firebase/DeepSeek được cấp phép hiện có. Không dùng database Production để thử tính năng, không reset quota, không chạy migration, không push/deploy Production. Guest staging trước đó đã hết quota; chỉ thử LIVE nếu có hạn mức hợp lệ, không tạo/đổi định danh để lách. Google popup mới cần thao tác người dùng, báo BLOCKED nếu chưa xác minh. Chi tiết kết quả thực tế sẽ bổ sung sau Preview.

Bổ sung checkpoint: nhóm regression bảo vệ/Search 46/46 PASS, tổng61 phương thức Python PASS. Các log storage/timeout là tình huống mock dự kiến, không lỗi dịch vụ thật.

## Preview đầu và lỗi phát hiện qua LIVE

Preview b2a5adf / dpl_B3hGcrwKwyrukJFADRuNDTGLb9aB READY (staging riêng). 10 phản hồi model thật: mở thư viện viết tắt không dấu, hồ sơ Chuyên viên phân tích nghiệp vụ, truyện Kỹ sư hàng không, AI Nhân viên buồng phòng; tham chiếu Nhà sử học và nghề thứ hai đều đúng ID. Gợi ý từ vẽ mặt bằng/thiết kế nhà đưa Kiến trúc sư, Thiết kế nội thất và trải nghiệm an toàn, hỏi chọn nghề trước, không mặc định nút ở lượt đó. Toán ngoài chủ đề không có nút; metadata giữ qua GET lịch sử/retry.

Thêm3 ca LIVE: source OWASP thực chứa lệnh prompt injection được xử lý như dữ liệu, có nguồn và không có navigation_actions; chọn rõ Kiến trúc sư mở đúng truyện. Nhưng câu “nghề đó” sau hai lựa chọn còn ưu tiên Kiến trúc sư trước: FAIL yêu cầu làm rõ tham chiếu mơ hồ. Không đánh dấu toàn bộ LIVE là PASS.

Bản sửa: hàng rào tham chiếu hẹp dựa vào tên/ID thật vừa xuất hiện (không nghề hardcode), cung cấp reference.status=ambiguous cho model và bỏ hành động chọn nghề khi chưa rõ. Nếu model vẫn chọn, hỏi làm rõ bằng danh sách tên thật; không thêm lượt LLM. Ý định/nội dung hội thoại vẫn do DeepSeek xử lý, đây chỉ là kiểm tra tính nhất quán của tham chiếu. Unit mới với hai nghề ngẫu nhiên PASS; nhóm navigation11/11 PASS sau sửa, tổng62 phương thức đã kiểm. Cần kiểm lại đúng ca này trên Preview mới, không làm lại các ca đã PASS.

Guest staging được xác minh chỉ đọc:8/8, ngân sách cấp phiên/IP10/10 còn khoảng49.733 giây tại lần kiểm tra. Không dùng Guest Production hoặc tạo định danh/staging khác để lách. Guest LIVE Task4.3 vẫn BLOCKED; role Guest được kiểm trong PostgreSQL local có mock model. Người dùng trả lời chưa kiểm tra được Google popup, giữ BLOCKED mục này. Chrome Member đã mở đúng thư viện/hồ sơ thật, reload nút và draft, desktop/mobile PASS; QA đang kiểm tra trang đích và khảo sát đúng nghề.

## Hoàn thiện sau kiểm tra

Preview ceef90d / dpl_8CamYvNpyftiMbMLnKVrg3XuzTHt đã kiểm lại3 lượt DeepSeek LIVE: nêu2 nghề, “nghề đó” hỏi làm rõ/không phát nút chọn thay, rồi “nghề thứ hai” mở đúng truyện Kỹ sư điện tử. Guard đạt đúng ca đã FAIL trước. Các luồng cũ không làm lại toàn bộ.

Chrome thực trên Preview đầu đã mở đúng thư viện Truyện nghề, modal Chuyên viên phân tích nghiệp vụ, truyện Kỹ sư hàng không và AI Nhân viên buồng phòng. AI đích hiện khảo sát5 bước, đúng career_context và chỉ có lời chào, chưa gửi câu hỏi AI. Đổi trang/newtab giữ draft/tab cũ; metadata hiện sau reload, desktop/mobile PASS. Hai lỗi harness (selector dialog và so sánh URL trước khi ứng dụng đổi sang conversation) đã sửa trong script QA, không sửa sản phẩm để làm test PASS.

Rà soát liên kết Markdown: DOMPurify ngăn script, nhưng href tương đối/protocol-relative cũ có thể đi vòng lớp nút điều hướng. Bổ sung kiểm tra chỉ giữ citation URL trong sources đã kiểm, mọi link Markdown tự tạo khác thành văn bản; nút điều hướng nội bộ vẫn qua metadata riêng. Chrome fixture với //evil.test, /?career=unknown và một citation HTTPS được kiểm: chỉ citation thật còn là link, navigation/draft/newtab không đổi. Tăng version asset tránh cache. Cần build Preview cuối và kiểm giao diện/citation thực tế.
