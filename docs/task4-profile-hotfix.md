# Task4 hotfix cá nhân hóa — 25/10/2026

## Checkpoint và phạm vi

Tạo hotfix/task4-profile-context tại worktree task4-profile-hotfix từ source Production thực fde7ed2459b948678622d79537fe48a117cddaa4 / dpl_7ZaE94zBvSeBAps9HgTPkak9Q1aT đã xác minh API Vercel. Kế thừa báo cáo36a5b8e (chỉ tài liệu), không đổi checkout cũ. Giữ canary QA-only và rollback deployment này. Không migration006, schema, resetquota, auth security, UI/200 nghề/Truyện nghề changes.

## Bằng chứng trước sửa

Toàn luồng API/PGlocal/LangGraph thu payload thực ở biên adapter provider (LLM fixture, không gọi LIVE): flagtrue lưu đúng, payload main có 1 mục đã xác nhận; 2 lời gọi provider và 6 system messages. Không có bằng chứng mất owner/ID/flag ở Neon. Payload cũ đặt profile trích xuất phiên (có thể rỗng) và confirmed_profile trong cùng JSON dài sau dữ liệu nghề; lịch sử lời AI nói chưa nhận hồ sơ nằm sau khối đó. Phép thử LIVE Production trước hotfix ghi nhận AI vẫn nói chưa nhận hồ sơ khi ON. Cần đối chứng candidate LIVE trước khi đóng ID23; không dùng fixture để chứng nhận model.

## Bản sửa tối thiểu

- context_items SELECT đúng owner, statusconfirmed, TTL còn hiệu lực, chỉ category/value; không cache, không DELETE ở đường đọc AI.
- OFF không gọi loader hồ sơ; builder phòng thủ bỏ cả state hồ sơ cũ khi OFF.
- Đổi tên ghi chú suy luận thành conversation_notes, tách hồ sơ đã xác nhận ra khối riêng enabled/status/items ngay trước câu hỏi hiện tại; dữ liệu không được coi là chỉ thị. Chỉ dẫn phân biệt disabled/empty/available, dùng có chọn lọc, ưu tiên đính chính mới và không tự gán năng lực.
- Giữ dữ liệu đã có trong lịch sử; OFF không xóa/viết lại hội thoại. Kiểm thử OFF bảo mật dùng phiên mới không có thông tin cá nhân.
- Không đổi auth, quota, schema, công tắc UI hoặc mở rộng mọi tài khoản. Candidate chỉ hai tài khoản email/password QA riêng; Google QA chỉ được thêm sau xác minh UID thật.

## Kiểm thử

25 trường hợp local duy nhất PASS: 17 regression profile/claim/rate và 8 API+PG+LangGraph mới (lần đầu24 gồm7 mới+17 cũ, lần sau8 gồm7 lặp+1 mới; không cộng thành32). Đã bắt exact main payload qua adapter: ON đúng 3 chiều công nghệ/giải quyết vấn đề/giao tiếp, OFF không SELECT/không có giá trị, sửa đọc mới, hai owner không trộn, chưa xác nhận/từ chối/pending không đưa vào context, logoutGuest không đọc owner cũ, phòng thủ stale-stateOFF. Browser fixture chỉ cập nhật cách thu context, chưa chạy lại browser toàn diện.

LIVE cá nhân hóa vẫn chờ candidate; bảng53 tạm giữ36PASS/16BLOCKED/1FAIL đến khi có bằng chứng. Brave Production thiếu cả SEARCH_PROVIDER và SEARCH_API_KEY; muốn bật phải cấu hình SEARCH_PROVIDER=brave và key qua env an toàn. Google CLI lookup báo INSUFFICIENT_PERMISSION; đã hỏi UID QA và cần popup Google do người dùng thao tác, không ghi email/UID/token vào Git. Không giả lập LIVE.
