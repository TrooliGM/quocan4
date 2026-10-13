# Một ngày làm việc — truyện nghề La Bàn

## Sử dụng

Chạy server theo README, mở `http://localhost:8000/mot-ngay-lam-viec`. Trên trang chủ, bấm **Truyện nghề**, **Bước vào một ngày làm việc** hoặc liên kết xem truyện trên thẻ nghề. Trang truyện không yêu cầu đăng nhập.

Sáu nghề gồm bác sĩ, lập trình viên, nhà thiết kế đồ họa, giáo viên, kỹ sư môi trường và người làm truyền thông. Mỗi nghề có 4 cảnh minh họa SVG với chuyển động CSS, giờ minh họa, lời thoại, kỹ năng và câu hỏi có phản hồi. Đây là truyện tranh tương tác có chuyển động, chưa phải video MP4 hay phim có lồng tiếng.

- **Từng cảnh**: nút trước/sau hoặc bấm mốc thời gian; khi trình xem nhận focus, dùng phím mũi tên trái/phải.
- **Tự chuyển cảnh**: 12 hoặc 20 giây/cảnh, dừng khi hết ngày; dừng khi đổi nghề, đổi chế độ, chọn câu trả lời, nhập câu hỏi hoặc chuyển sang tab khác.
- **Cả trang truyện**: xem bốn khung cùng lúc; bấm thử tình huống để trở về cảnh tương ứng.
- **Điều đọng lại**: tóm tắt kỹ năng và một hoạt động nhỏ để bắt đầu tìm hiểu nghề. Lựa chọn tương tác không chấm điểm năng lực và chỉ nằm trong trang đang mở.
- **Hỏi La Bàn về cảnh này**: FastAPI gửi nghề, nội dung cảnh và câu hỏi qua LangGraph đến DeepSeek. Khóa chỉ dùng trên server; thiếu khóa hoặc lỗi dịch vụ có thông báo, truyện vẫn xem được. Đổi cảnh sẽ hủy hiển thị câu trả lời cũ.

## Nội dung và cấu trúc

`career_stories.py` chứa kịch bản hư cấu, tham khảo nhiệm vụ nghề từ [BLS Occupational Outlook Handbook](https://www.bls.gov/ooh/); từng truyện có liên kết trực tiếp tới trang nghề đã tham khảo. Giờ làm và nhân vật là minh họa do dự án biên soạn. Nguồn mô tả nghề tại Hoa Kỳ, không dùng số liệu lương hay lộ trình đào tạo này cho Việt Nam. Truyện bác sĩ trình bày trách nhiệm và hợp tác, không hướng dẫn điều trị hoặc kê thuốc.

`public/assets/story-art.js` chứa minh họa vector gốc. `stories.js` điều khiển trình xem; `stories.css` bố cục responsive và tôn trọng cài đặt giảm chuyển động. `story_ai.py` chuẩn bị ngữ cảnh cảnh truyện và gọi DeepSeek qua LangGraph.

API: `GET /api/career-stories`, `GET /api/career-stories/{id}`, `POST /api/career-stories/{id}/ask` với `question` và `scene_index` bắt đầu từ 0. Nghề/cảnh không tồn tại và câu hỏi không hợp lệ bị từ chối trước khi gọi AI.

## Kiểm tra

```powershell
python -m unittest discover -s tests -v
python tests/browser_stories.py
```

Kiểm thử trình duyệt cần Chrome và package `websockets`. Script khởi chạy môi trường giả lập riêng, không gọi AI trả phí. Kết quả và giới hạn xem `validation.md`.

## GitHub và Vercel

Mã nguồn được đồng bộ vào repository `TrooliGM/quocan4` theo yêu cầu người dùng. Cấu hình Vercel có entrypoint FastAPI và thư mục tài sản `public/assets`; `.vercelignore` loại cấu hình riêng, dữ liệu local và artifacts. Tham khảo [FastAPI trên Vercel](https://vercel.com/docs/frameworks/backend/fastapi).

Ngày 2026-10-13, người dùng xác nhận dùng bản chạy trên máy trước; deployment được hoãn.

Để triển khai cần kết nối tài khoản Vercel, import repository và cấu hình biến môi trường trên Vercel. Tính năng truyện dùng nội dung tĩnh trong mã nguồn; AI cần `DEEPSEEK_API_KEY` và `DEEPSEEK_MODEL`. Website hiện có chat tài khoản sử dụng SQLite local, nên cần cơ sở dữ liệu bền vững dùng chung trước khi công bố toàn bộ chức năng chat trên Vercel. Không dùng `/tmp` để giả lập lưu lịch sử bền vững. Chưa có URL deployment mới được xác minh.
