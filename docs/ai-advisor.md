# Tư vấn hướng nghiệp 1:1

Sau khi đăng nhập Firebase, mở `/ai-career-advisor` để trò chuyện với La Bàn AI. Người dùng có thể gõ hoặc bấm biểu tượng micro, nói tiếng Việt, sửa văn bản nhận diện rồi bấm **Gửi**. Micro tự dừng sau khoảng 3 giây im lặng; có thể dừng hoặc hủy thủ công. Tin nhắn không tự gửi.

Máy chủ dùng DeepSeek Flash qua LangGraph để trả lời bằng Markdown. Một lời gọi AI khác rút gọn thông tin người dùng tự chia sẻ và ngữ cảnh cũ để duy trì cuộc trò chuyện. Lịch sử và hồ sơ được tách theo tài khoản Firebase. Chỉ lưu vào SQLite khi người dùng chọn lưu; phiên không lưu nằm trong RAM. Lỗi rút gọn ngữ cảnh không làm mất câu trả lời chính.

## Chạy thử

Trong PowerShell tại thư mục dự án:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app:app --reload
```

Mở `http://localhost:8000`, đăng nhập, vào **Tư vấn cùng AI**, bấm micro và cho phép trình duyệt sử dụng micro. Khi chữ xuất hiện trong ô nhập, sửa nếu cần rồi bấm **Gửi**. Nếu micro không hoạt động, kiểm tra quyền micro của trình duyệt và thử Chrome trên `localhost`.

## Cấu hình dịch vụ

Tạo `.env` từ `.env.example` và điền `DEEPSEEK_API_KEY` trên máy chạy server; không đưa khóa vào JavaScript hoặc GitHub. Dùng `DEEPSEEK_MODEL=deepseek-flash`, `AI_DEMO_MODE=false` cho AI thật. [Tài liệu DeepSeek](https://api-docs.deepseek.com/quick_start/pricing/) mô tả model hiện hành.

Nếu chưa cấu hình Google Cloud Speech-to-Text, micro dùng Web Speech của trình duyệt khi được hỗ trợ. Chế độ này phụ thuộc vào trình duyệt và có thể cần mạng. Để dùng Google Speech-to-Text trên server, bật API trong Google Cloud, cấp quyền cho ứng dụng và đặt tệp credentials **ngoài repository**, rồi khai báo:

```dotenv
GOOGLE_CLOUD_PROJECT_ID=project_google_cloud
GOOGLE_APPLICATION_CREDENTIALS=C:/duong-dan-ngoai-du-an/credentials.json
```

Khi đã cấu hình, trình duyệt ghi WAV mono 16-bit/16 kHz và gửi đến endpoint có xác thực `/api/voice/transcribe`; server gọi [Google Speech-to-Text recognize API](https://docs.cloud.google.com/speech-to-text/docs/reference/rest/v1/speech/recognize). Chưa kiểm thử micro hoặc Google Cloud thật trên thiết bị người dùng. Tính năng đọc câu trả lời bằng Vbee chưa thuộc bản mic hiện tại; gói Vbee đã từng từ chối yêu cầu sync TTS.

## Kiểm tra và giới hạn

`python -m unittest discover -s tests -v` kiểm tra backend; `python tests/browser_smoke.py` kiểm tra giao diện bằng trình duyệt và dữ liệu giả. Kiểm thử Chrome dùng giả lập nhận diện, không chứng minh micro hoặc Google Cloud thật hoạt động. Xem `docs/validation.md` để biết kết quả mới nhất. Trước khi triển khai chat trên Vercel, cần chuyển lịch sử SQLite sang cơ sở dữ liệu bền vững dùng chung.
