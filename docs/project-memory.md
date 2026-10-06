# Bộ nhớ dự án: Website Hướng nghiệp KHKT 2027

## Nguồn và phạm vi

- Nguồn: `C:/Users/Administrator/Downloads/Bao_Cao_Y_Tuong_Website_Huong_Nghiep_KHKT2027 (2).docx`.
- Tên báo cáo: “Báo cáo đề xuất ý tưởng và tính năng website dự án khoa học kỹ thuật 2027”.
- Ngày đọc và tạo bộ nhớ: 2026-10-06.
- Ban đầu người dùng yêu cầu đọc báo cáo và thiết kế bộ nhớ; sau đó yêu cầu xây dựng chức năng trang chủ theo công nghệ cụ thể.
- Các yêu cầu bên dưới được trích lược từ báo cáo; không mặc định rằng mọi tích hợp hoặc lựa chọn kỹ thuật đã được người dùng phê duyệt.

## Mục tiêu và đối tượng

Tên mô tả: Nền tảng Website Hướng nghiệp và Định hướng Tương lai Trực quan hóa cho Học sinh.

Đối tượng: học sinh THCS và THPT. Báo cáo nêu vấn đề học sinh thiếu định hướng, khó hình dung thực tế công việc và thường gặp tài liệu dài, khó hiểu. Đây là nhận định trong báo cáo, chưa kèm dữ liệu khảo sát trong tệp đã đọc.

Giải pháp: dùng hoạt hình, infographic, comic và tương tác để giải thích bản chất công việc, hoạt động hàng ngày, kỹ năng và trách nhiệm nghề nghiệp. Trải nghiệm cần ngắn gọn, dễ hiểu và truyền cảm hứng.

## Tám nhóm chức năng theo báo cáo

| Nhóm | Yêu cầu được mô tả |
| --- | --- |
| 1. Trang chủ và giới thiệu | Giới thiệu mục tiêu KHKT 2027; giao diện thân thiện với học sinh; nghề nổi bật, bài viết hướng nghiệp và tìm kiếm nhanh. |
| 2. Tài khoản và cá nhân hóa | Đăng ký/đăng nhập qua Email, Google, Zalo; quản lý hồ sơ, lưu nghề yêu thích, xem lịch sử trắc nghiệm. |
| 3. Thư viện nghề nghiệp trực quan | Phân nhóm như Y tế, Công nghệ, Giáo dục, Nghệ thuật; mỗi nghề có mô tả, kỹ năng, lương trung bình, triển vọng và trường đào tạo. |
| 4. Hoạt hình và comic nghề nghiệp | Chức năng cốt lõi: mô phỏng một ngày làm việc bằng hoạt hình/comic/video ngắn. Ví dụ bác sĩ: khám bệnh, hội chẩn, kê đơn và trực cấp cứu. |
| 5. Trắc nghiệm định hướng | Báo cáo đề xuất Holland Code và MBTI với ngôn ngữ phù hợp học sinh; gợi ý nghề dựa trên tính cách, sở thích, năng lực. Chưa có bộ câu hỏi hoặc cách tính điểm. |
| 6. Tư vấn và hỏi đáp | Học sinh gửi câu hỏi; đề xuất trợ lý AI 24/7 và kết nối giáo viên/chuyên gia hướng nghiệp. |
| 7. Lộ trình học tập | Môn học THPT, khối thi, hướng đại học/cao đẳng, kỹ năng mềm; gợi ý khóa học ngắn hạn và tài liệu bổ trợ. |
| 8. Quản trị hệ thống | Quản lý bài viết, dữ liệu nghề, tải hình ảnh hoạt hình; thống kê truy cập, tương tác và kết quả trắc nghiệm. |

## Yêu cầu thiết kế và kỹ thuật từ báo cáo

- Giao diện tươi sáng, sinh động, phù hợp học sinh; dùng được trên máy tính và điện thoại.
- Ưu tiên tải trang nhanh; tối ưu dung lượng hình ảnh và hoạt hình để trải nghiệm mượt.
- Dữ liệu nghề nghiệp dễ mở rộng và cập nhật.
- Chưa có chỉ tiêu hiệu năng định lượng, công nghệ cụ thể hoặc thiết kế cơ sở dữ liệu.

## Thành viên theo báo cáo

| Thành viên | Vai trò |
| --- | --- |
| Kiều Anh | Nghiên cứu thực trạng, khảo sát khó khăn, biên soạn kịch bản hoạt hình nghề nghiệp. |
| Kiều Oanh | Tổng hợp ý tưởng, cấu trúc chức năng, lập kế hoạch, mô tả sản phẩm và viết báo cáo. |
| An | Phát triển frontend/backend theo thiết kế và danh sách chức năng. |
| Thầy Trần Quốc Giăng | Hướng dẫn chuyên môn, cố vấn nội dung và chỉ đạo chung. |

## Trạng thái thực tế

- Đã cài skill frontend-design tại `.agents/skills/frontend-design/SKILL.md`.
- Đã đọc nội dung báo cáo và tạo tài liệu bộ nhớ.
- Đã xây dựng trang chủ: giới thiệu, sáu nghề mẫu, ba bài viết, tìm kiếm tiếng Việt không dấu, lọc lĩnh vực, hộp thoại nội dung, giao diện responsive.
- Backend Python FastAPI; frontend HTML, Bootstrap, CSS và JavaScript. AI có mã tích hợp DeepSeek API qua LangGraph, chưa kiểm thử lời gọi thật vì chưa có API key.
- Đã chuẩn bị cấu hình Vercel và hướng dẫn triển khai. Repository người dùng chỉ định: https://github.com/TrooliGM/quocan4.
- Đã đưa mã nguồn lên nhánh `main` của repository và xác minh cây tệp; commit ứng dụng `9ead1787bf959bc33557bd45f5b66f38ff982d5d`.
- Triển khai Vercel đang chờ kết nối tài khoản. Plugin Vercel đã được tìm thấy và đề xuất, chưa xác nhận kết nối.
- La Bàn là tên giao diện do trợ lý đề xuất khi triển khai, chưa phải tên thương hiệu người dùng xác nhận.
- Nội dung nghề và bài viết là bản mẫu biên soạn, không có số liệu thị trường hoặc bảng xếp hạng tuyển dụng.
- Chưa có tài khoản, trắc nghiệm, quản trị, cơ sở dữ liệu hoặc phim hoạt hình nghề nghiệp. Chi tiết xác minh ở `docs/validation.md`.

## Cách tiếp tục

Khi người dùng yêu cầu triển khai, tham khảo `docs/decisions.md`, xác định phạm vi cần làm và cập nhật bộ nhớ theo kết quả thực tế. Giữ chức năng trực quan hóa nghề nghiệp ở vị trí trung tâm của sản phẩm.
