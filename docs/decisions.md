# Quyết định và việc còn mở

## Đã xác nhận trong phiên làm việc

| Ngày | Nội dung | Cơ sở |
| --- | --- | --- |
| 2026-10-06 | Cài frontend-design ở phạm vi dự án. | Yêu cầu trực tiếp của người dùng; tệp đã được sao chép và kiểm tra khớp nội dung. |
| 2026-10-06 | Tạo bộ nhớ dự án từ báo cáo DOCX. | Yêu cầu trực tiếp của người dùng. |
| 2026-10-06 | Triển khai chức năng 1: trang chủ và giới thiệu. | Yêu cầu trực tiếp của người dùng. |
| 2026-10-06 | Python backend, DeepSeek là AI chính, HTML/Bootstrap/CSS/JavaScript, LangGraph, Vercel và GitHub. | Công nghệ người dùng chỉ định. |
| 2026-10-06 | Repository đích: TrooliGM/quocan4. | URL người dùng cung cấp. |
| 2026-10-07 | Setup đăng nhập bằng Firebase. | Yêu cầu trực tiếp của người dùng. |

## Lựa chọn triển khai của trợ lý

- FastAPI cho backend Python; dữ liệu mẫu đặt trong `content.py` để thay đổi dễ dàng.
- Tên hiển thị La Bàn; phong cách sổ tay khám phá với nền kem, xanh bạc hà và cam san hô. Đây là lựa chọn thiết kế, có thể điều chỉnh.
- LangGraph gồm hai node: chuẩn bị ngữ cảnh nghề và gọi DeepSeek. API key chỉ dùng trên server.
- Firebase Web SDK qua CDN cho email/password và Google; thêm quên mật khẩu, xác minh email, đăng xuất. Provider cụ thể là lựa chọn triển khai của trợ lý.
- Backend xác minh ID token bằng google-auth, không dùng service account. Chưa kiểm tra token bị thu hồi/disabled theo thời gian thực; chưa có chức năng quản trị nhạy cảm.
- Chưa lưu Firestore; mặc định chọn phiên theo tab, có lựa chọn giữ đăng nhập trên máy cá nhân.

## Chưa được quyết định

- Tên thương hiệu, logo, bảng màu và phong cách giao diện cụ thể.
- Phạm vi những chức năng tiếp theo sau trang chủ.
- Cơ sở dữ liệu và nơi lưu nội dung đa phương tiện khi mở rộng.
- Hình thức trực quan hóa đầu tiên: comic, hoạt hình hay video; nguồn tài sản hình ảnh.
- Nguồn và cách cập nhật lương, triển vọng nghề, trường đào tạo, thông tin tuyển sinh.
- Bộ câu hỏi, quyền sử dụng nội dung trắc nghiệm, cách tính điểm và ánh xạ kết quả sang nghề.
- Quy trình chuyển câu hỏi cho giáo viên/chuyên gia và phạm vi AI khi mở rộng.
- Cấu hình Firebase project và bật provider trên tài khoản người dùng; Zalo chưa triển khai.
- Vai trò người dùng, quyền quản trị, thông tin học sinh cần thu thập và thời gian lưu dữ liệu.
- Phương pháp đánh giá hiệu quả hướng nghiệp cho báo cáo KHKT; chưa có kết quả khảo sát được cung cấp.

## Hướng triển khai đề xuất, chưa được phê duyệt

1. Chốt phạm vi bản đầu tiên và một số nghề có nội dung đủ tin cậy.
2. Thiết kế hành trình khám phá nghề → xem một ngày làm việc → xem kỹ năng và lộ trình.
3. Xây dựng giao diện responsive cùng nội dung nghề mẫu.
4. Bổ sung trắc nghiệm, cá nhân hóa, tư vấn và quản trị theo phạm vi đã chốt.
5. Kiểm tra trải nghiệm trên điện thoại, hiệu năng nội dung đa phương tiện và tính đúng của dữ liệu.

Danh sách này phục vụ những lượt làm việc tiếp theo; không phải công việc đã hoàn thành hoặc lịch triển khai đã được cam kết.
