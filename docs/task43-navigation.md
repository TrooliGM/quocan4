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
