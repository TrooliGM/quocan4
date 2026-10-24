# Truyện nghề 2.0 — checkpoint triển khai

Nền Production được đọc trực tiếp từ Vercel: `5aaed6e`, deployment `dpl_8SWMtQHuQ7nFnkt3EEs5YVc1tAyQ`, region sin1. Nhánh feat/ai-chat-2-1 là tổ tiên của hotfix. Làm tại nhánh `feat/task-3-career-stories-2-0`, worktree task-3 riêng; checkout dirty khác được giữ nguyên.

Đợt 1: 50 bản thảo có biên tập, dữ liệu JSON tĩnh, 5 cảnh/truyện, hai quyết định/truyện có phản hồi và hệ quả riêng. Bộ biên dịch tái sử dụng nhiệm vụ/kỹ năng từ hồ sơ đã có; không tự tạo kịch bản bằng cách thay tên. Validator là kiểm tra kỹ thuật, không chứng nhận chuyên gia cho toàn bộ nội dung. 0 video được xác minh, không có URL video giả. Sáu truyện cũ giữ nguyên dữ liệu, mở lại bằng `?version=1` trên API; giao diện 2.0 dùng bản mới.

Đang hoàn thiện các đợt 2–4 và kiểm thử tích hợp. Chưa được coi 200/200 hoàn tất ở checkpoint đợt 1. Không migration, không đổi database/Firebase/quota/rate limit, không tự deploy Production. Người dùng cho phép checkpoint commit và Vercel Preview để duyệt; không cho phát hành Production trước duyệt Preview. Không chạy Super Board.
