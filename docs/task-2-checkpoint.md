# Nhiệm vụ 2 — checkpoint khởi đầu, CHƯA HOÀN THÀNH

Ngày 2026-10-23. Nhánh `feat/task-2-career-library`, worktree `D:/khkt/.claude/worktrees/task-2`, tạo từ **88639f8** (đủ Nhiệm vụ 1 và Navbar phương án 2). Checkout task-1 và checkout chính được giữ nguyên. Không push/merge/deploy hoặc kết nối Neon.

## Đã làm thực tế

- Đọc yêu cầu ở attachment b2d789d6-9247-4740-8eb2-1d2e718f9bfc/Pasted text.txt.
- Tạo hợp đồng Pydantic Career/Catalog đủ các trường yêu cầu; 12 nhóm ổn định. Giữ nguyên ID sáu nghề cũ để tương thích truyện.
- Chuẩn hóa tìm kiếm chữ thường/không dấu, kể cả đ; phát hiện trùng ID/tên và nhóm không hợp lệ.
- Năm test hợp đồng dữ liệu PASS. Đây là dữ liệu mẫu unit test, **không phải thư viện 200 nghề**, không phải kiểm thử Guest/UI/AI.
- Chưa nối module mới vào API hoặc frontend. Chưa sửa chức năng đang hoạt động.

## Việc còn lại bắt buộc

1. Biên soạn/kiểm tra đúng 200 nghề thực tế, đủ schema, nội dung riêng, không bịa lương/cấp phép. Bốn đợt 50 nghề. Hiện website vẫn có sáu nghề cũ; dữ liệu sản phẩm mới chưa tạo.
2. API thư viện/categories/detail và phân trang/tìm kiếm; giữ API dùng chung đang hoạt động. UI lĩnh vực trước, không đổ 200 card; modal tái sử dụng với hai CTA.
3. Lưu `career_discovery`/`career_exploration` cùng career_id trong metadata từng phiên tương tự khảo sát; validate career_id backend. Không đổi schema Production. Exploration sau khảo sát chỉ điền draft hỏi nghề để học sinh sửa trước gửi; discovery giữ khảo sát/phân tích từ Nhiệm vụ 1.
4. Thu hẹp ngữ cảnh AI theo nghề/tìm kiếm, **không gửi cả 200 nghề ở mọi lượt**. Không giả lập kết quả AI. Giữ xưng hô và hồi phục mode/nghề/survey khi mở lại.
5. Truyện mở theo ID, không fallback sang nghề khác nếu ID hợp lệ chưa có truyện; thông báo đang cập nhật. Không xây Nhiệm vụ 3.
6. Giữ Firebase Anonymous + token thật mỗi khách, quota 8 và rate limit cũ. Không dùng UID chung, không localStorage làm xác thực, không ép login trước quota. Kiểm thử cách ly guest/member, mode, survey, quota và account switching. Local guest cần PostgreSQL test riêng theo adapter hiện tại; không giải quyết bằng vô hiệu hóa guest.
7. Kiểm thử UI desktop/mobile, route, hai mode AI, danh mục đủ 200, modal/story mapping, bản khảo sát mới; ghi rõ fixture/provider thật. Không gọi lại full Super Board; tối đa hai vòng sửa/thử lại mỗi lỗi.
8. Chạy Preview LOCAL bằng database tách biệt; không lấy secrets/DB Production. Chưa có server Nhiệm vụ 2 mới. `localhost:8002` là server task-1 có AI demo và thiếu cấu hình Firebase, **không được báo là preview đầy đủ Nhiệm vụ 2**.
9. Commit phần hoàn thiện, danh sách file/test/ảnh, checkpoint Nhiệm vụ 3; không push/merge/Production deploy. Không tuyên bố toàn bộ Nhiệm vụ 2 hoàn tất trước khi các mục trên thực sự làm xong.

Yêu cầu đầy đủ: attachment gốc. Các giới hạn phát hành Production của ticket #7 vẫn chưa được giải quyết. Không mở lại hay sửa migration 003 trong nhiệm vụ này.
