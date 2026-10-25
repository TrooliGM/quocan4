# Task4.1 — checkpoint phát triển

## Quyền và nền

Yêu cầu mới chỉ Preview, không merge/promote Production, không chạy migration006/không thay dữ liệu thật. Production đã kiểm957ffde / dpl_BwthFvvNpNDscwEuKPC744bVe38z. Nhánh feat/task-4-1-advisor-intelligence từ dba80a6 (runtime957ffde + audit docs). Giữ stable fallback/canary QA-only; không sửa200 nghề/Truyện nghề.

## Bước1 — context/search

Đã thêm conversation_context.py: intent/detaiI/output budget, lịch sử bounded, public topic/year reference. Không thêm LLM router; không đổi model/key/temperature và không tăng max_tokens trên mức cũ5000. Memory compression bỏ lượt chat ngắn, vẫn chạy mỗi6turns hoặc khi lịch sử dài. Search route hiểu thiếu dấu/chính sách/tuyển sinh; không chèn survey/profile vào query.11 unit context/search PASS, không gọi đó là chất lượng model LIVE.

Model/chi phí/latency và16tình huống tiếngViệt sẽ được đánh giá trong bước4; chưa tuyên bố thông minh như ChatGPT. Tác vụ phân tích riêng đang xây dựng, chưa hoàn thành; file analysis_jobs chưa có route/frontend/tests nên chưa là checkpoint chức năng.

Preview metadata có DeepSeek/Firebase binding dùng chung targetProduction+Preview do project đã cấu hình; không copy giá trị secret. Chưa có DATABASE_URL chung cho nhánh mới. Cần DB schema-only với credential riêng, kiểm0rows trước thử; không sao chép dữ liệu học sinh. Brave Preview/Production chưa có binding dùng được, LIVE Search còn BLOCKED.
