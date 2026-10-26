# Task 4.4 bổ sung — Điều hướng cùng tab

Nền: Task4.3 Production608146c, audit4118367. Nhánh riêng feat/task-4-4-continuous-journey; không tìm thấy worktree/checkpoint4.4 đã có. Đang chờ người dùng mô tả riêng lỗi Hồ sơ; không tự coi lỗi đó đã được xử lý.

## Nguyên nhân và thay đổi
- navigation-actions.js cố ý target_blank và ghi mở tab mới. Bỏ target cho nút nội bộ, nguồn Internet giữ tab mới.
- Liên kết thư viện/truyện chưa mang conversation; mode=career_exploration khởi tạo phiên mới. Thêm con trỏ hành trình theo tab/UID, TTL2h, URL conversation; backend vẫn xác minh quyền sở hữu, không coi storage hoặc URL là token.
- Chat luôn ghi ID đã xác minh vào URL; sửa hai đoạn replaceState dùng URL cũ làm mất ID sau khi tạo chat.
- Nút Cùng tìm hiểu nghề trở về phiên gốc; nghề/cảnh là bản nháp câu hỏi, không ghi đè nội dung đã nhập hoặc đổi khảo sát gốc, không tự gửi.
- Bỏ POST phân tích tự động chỉ vì mở lại chat; hoàn tất khảo sát vẫn tự phân tích và người dùng vẫn có thể chủ động thử lại.
- Lưu cả pending request_id vào draft để retry sau điều hướng dùng cùng mã, không tự gọi AI lại. Guest claim chuyển con trỏ sau server xác nhận; logout/new-chat xóa con trỏ.
- Native anchors, không window.open; modifier/middle click do người dùng chọn vẫn hoạt động. Modal nghề có history Back/Forward; truyện giữ conversation qua bộ lọc/route, khôi phục khi BFCache trở lại.
- Không sửa backend/quota/database/schema/catalog/thiết kế Premium. Không đổi quyền hồ sơ hoặc model/search.

## Kiểm thử đã chạy
- 26 phương thức Python: test_navigation_actions + test_shared_ai_protection PASS. Node syntax + git diff --check PASS.
- tests/browser_navigation.py Chrome: XSS/open redirect, cùng tab, UID claim/draft, desktop/mobile PASS; POST0 trong fixture.
- tests/browser_journey.py: trang FastAPI thật + PG local, khảo sát dở, hoàn tất khảo sát, thư viện nhiều nghề, truyện/cảnh, Back/Forward, bản nháp, cùng conversation và một tab PASS. Không có POST chat/create/analysis khi điều hướng; POST /guest/session chỉ xác minh lại cookie hiện có. Google claim ở đây là fixture, KHÔNG phải popup Google thật.

Preview/LIVE chưa thực hiện tại thời điểm checkpoint này. Production vẫnTask4.3. Google popup thật cần người dùng thao tác; không dùng fixture/password để đánh dấu PASS. Các báo cáo bổ sung sau đây ghi kết quả thực tế.

## Rollback dự kiến
Giữ deployment ProductionTask4.3 G11k5MKTVWNhEAcszbhqGEZm1KiW, source608146c; xác minh alias lại trước phát hành. Nếu cần rollback chỉ đổi deployment về bản đã xác minh; không reset/restore DB, không xóa quota/hội thoại.
