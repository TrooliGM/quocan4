# Truyện nghề 2.0 — checkpoint triển khai

Nền Production được đọc trực tiếp từ Vercel: `5aaed6e`, deployment `dpl_8SWMtQHuQ7nFnkt3EEs5YVc1tAyQ`, region sin1. Nhánh feat/ai-chat-2-1 là tổ tiên của hotfix. Làm tại nhánh `feat/task-3-career-stories-2-0`, worktree task-3 riêng; checkout dirty khác được giữ nguyên.

Đợt 1: 50 bản thảo có biên tập, dữ liệu JSON tĩnh, 5 cảnh/truyện, hai quyết định/truyện có phản hồi và hệ quả riêng. Bộ biên dịch tái sử dụng nhiệm vụ/kỹ năng từ hồ sơ đã có; không tự tạo kịch bản bằng cách thay tên. Validator là kiểm tra kỹ thuật, không chứng nhận chuyên gia cho toàn bộ nội dung. 0 video được xác minh, không có URL video giả. Sáu truyện cũ giữ nguyên dữ liệu, mở lại bằng `?version=1` trên API; giao diện 2.0 dùng bản mới.

Đang hoàn thiện các đợt 2–4 và kiểm thử tích hợp. Chưa được coi 200/200 hoàn tất ở checkpoint đợt 1. Không migration, không đổi database/Firebase/quota/rate limit, không tự deploy Production. Người dùng cho phép checkpoint commit và Vercel Preview để duyệt; không cho phát hành Production trước duyệt Preview. Không chạy Super Board.

Đợt 2: thêm đúng 50 nghề tiếp theo, tổng 100 truyện/500 cảnh/200 quyết định; còn hai đợt sau. Đã sửa lỗi encoding khi tạo một số nhãn HTML qua PowerShell; dữ liệu bản thảo viết bằng apply_patch không bị ảnh hưởng.

## Kết quả sau bốn đợt — trạng thái mới nhất

Các checkpoint nội dung: `8195749` (đợt1 + bộ đọc), `6dd0f16` (đợt2), `0857948` (đợt3), `97a5582` (đợt4). Đã đủ 200 ID/1.000 cảnh/400 quyết định, validator PASS. Không còn thiếu hai đợt như trạng thái ghi ở trên. Bản rà 12 nhóm và giới hạn chuyên môn ở docs/task-3-editorial-review.md. Chưa có video được xác minh.

Bộ đọc tìm không dấu, lọc nhóm, từng cảnh/comic, phản hồi riêng, hệ quả cảnh kế/tổng kết, quay lại/chơi lại, hủy response cũ, lỗi ID và tiến độ trong tab. Không autoplay; không lưu lựa chọn vào database. Truyện mới mở từ cảnh1; quay từ AI về có scene_id và khôi phục lựa chọn trong tab. Minh họa SVG do dự án tạo, tái dùng có kiểm tra; bổ sung records trung tính để nghề pháp lý/tài chính không mang ống nghe bác sĩ.

AI: nút chuyển câu hỏi có thể sửa cùng career_id/title/scene/tóm tắt qua tab-local handoff tới career_exploration; khảo sát5 bước hiện hành giữ nguyên, chỉ gửi khi bấm Send, dùng auth/quota/rate sẵn có. Thêm liên kết trở lại truyện trong chat; không thay auth callback hay hotfix hiệu năng. Thư viện chỉ bổ sung hai dòng nhận query `career` để mở lại đúng modal, không đổi UI, nội dung hoặc hai nút đang có.

Kiểm thử trọng tâm: 33 backend method PASS/0 SKIP, gồm đọc 200 payload đúng ID (<20KB/truyện), giữ6 legacy, graph provider mock, ownership/quota/rate protection, bundle không public/dotenv và cổng Preview fail-closed. Node10 PASS (gồm7 hồi quy hotfix/Chat2.1). Chrome10 checkpoint truyện PASS, Chat2.1 thêm12 checkpoint PASS; Firebase fixture/AI demo có nhãn/PostgreSQL local tách biệt, không gọi DeepSeek thật. Lần đầu harness đợi Send bật sau gửi đã sai vì input rỗng; đã sửa điều kiện chờ câu trả lời. Đã sửa link quay lại bị render chat xóa sau Send và nhãn HTML bị encoding PowerShell. Có ảnh desktop/mobile trong artifacts, không commit artifacts. Không coi fixture là live Google/DeepSeek; Google hotfix Production trước đó đã được người dùng xác nhận thành công.

Preview: project khkt3/quocan4 đã xác minh. Nhánh mới chưa có DATABASE_URL Preview riêng; không dùng binding Production hay lấy secrets Production để khắc phục. Chọn Preview chỉ đọc truyện/thư viện, AI và đăng nhập bị khóa bằng override riêng cho deployment (DATABASE_URL rỗng, DeepSeek/Firebase key và project rỗng, AI_DEMO_MODE=false, STORIES_PREVIEW_READ_ONLY=true). Frontend hiển thị đúng giới hạn; backend vẫn fail-closed, không sửa cơ chế bảo mật. Không phải AI demo giả DeepSeek. URL/build thực tế sẽ ghi sau deploy, chưa tuyên bố hoàn tất ở checkpoint này. Không đổi Production Branch, env Production, schema hay domain chính thức.
