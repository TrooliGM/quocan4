# Xác minh và triển khai — 2026-10-06

## Đã chạy thành công

- `python -m unittest discover -s tests -p test_app.py -v`: 4 bài kiểm tra đạt bằng Python và thư viện có sẵn của máy.
- Kiểm tra trang chủ và tài sản CSS/JavaScript/SVG trả HTTP 200.
- Kiểm tra tìm kiếm “bac si” và “BÁC SĨ”, lọc Sáng tạo và kết quả rỗng.
- Kiểm tra ba bài viết có nội dung đầy đủ.
- Kiểm tra AI khi thiếu key trả 503; câu hỏi rỗng, quá ngắn, quá dài trả 422.
- `python -m compileall -q app.py ai.py content.py`: mã Python biên dịch thành công.

## Giới hạn hiện tại

- Máy có FastAPI/httpx/python-dotenv, chưa có LangGraph. Yêu cầu tải thư viện qua mạng đã bị người dùng từ chối; không tiếp tục cài bằng cách khác.
- Đã viết `tests/test_ai.py` cho luồng LangGraph, payload DeepSeek và xử lý lỗi nhà cung cấp, nhưng chưa chạy vì thiếu LangGraph.
- Chưa gọi DeepSeek thật; chưa có API key được cấu hình.
- Chưa kiểm tra trực quan bằng trình duyệt hoặc chạy JavaScript trong trình duyệt.
- Đã chuẩn bị cấu hình Vercel; chưa có tài khoản/công cụ Vercel khả dụng để xác nhận deployment. Không có URL website đã triển khai trong phiên này.

## Kiểm tra tiếp theo trên môi trường đủ dependencies

1. Cài `requirements.txt`, chạy toàn bộ `python -m unittest discover -s tests -v`.
2. Mở trang trên điện thoại và desktop; kiểm tra tìm kiếm, bộ lọc, hộp thoại và menu bằng chuột/bàn phím.
3. Cấu hình key trên server hoặc Vercel, kiểm tra trợ lý bằng câu hỏi nghề nghiệp mẫu.
4. Import GitHub repository vào Vercel và kiểm tra đường dẫn tài sản sau khi deploy.
