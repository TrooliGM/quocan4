# Task 4.2 — Sửa truy vấn nối tiếp và nguồn sai chủ đề

## Phạm vi

Sửa local trên `feat/task-4-1-advisor-intelligence`, HEAD `fb2eca4`, worktree `.claude/worktrees/task-4-1`. Ba thay đổi tài liệu xác nhận Google Login của lượt trước đã có sẵn và được giữ nguyên. Không đổi DDGS/DeepSeek/dependency, Firebase, Neon, quota Guest, canary Search hay giao diện. Không gọi database hoặc deploy Production trong nhiệm vụ này; bản chính thức vẫn là runtime đã phát hành trước đó.

## Nguyên nhân từ code

`public_search_query()` cũ chỉ nhận vài tham chiếu như “ngành đó”, “năm ấy”, “còn năm”; không nhận “Vậy năm 2020 là bao nhiêu ạ?”. Vì thế query có thể bị gửi nguyên văn mà mất chủ đề điểm chuẩn Công an.

`relevant()` cũ chấp nhận bất kỳ một từ chung trùng nhau, có thể là “bao”, “nhiêu”; không yêu cầu cả chủ đề Công an và thông tin điểm chuẩn. Có năm 2020 không đủ để xác nhận mức liên quan. Truy xuất cũ cũng chưa có lần tìm lại có điều kiện khi toàn bộ kết quả lệch chủ đề.

## Bản sửa

- Khôi phục câu nối tiếp từ tối đa 16 tin gần nhất. Ưu tiên chủ đề người dùng nêu; không lấy survey, profile, summary hoặc sao chép nguyên văn assistant làm query. Assistant chỉ có thể đóng góp các tên chủ đề công khai đã chuẩn hóa.
- Ví dụ hội thoại: “Điểm chuẩn các trường đại học Công an năm 2024 là bao nhiêu?” → “Vậy năm 2020 là bao nhiêu ạ?” tạo query **“điểm chuẩn các trường đại học Công an nhân dân năm 2020”**. Năm mới thay năm cũ. Giữ tên trường cụ thể, diện nữ/nam rõ ràng, miền và tổ hợp khi đã được nêu.
- Chủ đề mới rõ ràng như CNTT/Bách khoa hoặc năm nhuận không bị kéo về Công an. Phản hồi sai về năm nhuận từ assistant không được phép tự thay chủ đề do người dùng đặt trước. Nếu chỉ có một năm mà chưa biết số liệu/chủ đề nào, hỏi làm rõ thay vì search lịch.
- Với query điểm chuẩn Công an, nguồn phải cùng chủ đề và loại thông tin; loại trang năm nhuận, nguồn thống kê Công an không nói điểm chuẩn, trường khác khi đã biết tên trường, hoặc nguồn chỉ nói năm khác. Query chung cũng cần khớp nhiều từ có nghĩa hơn, không chỉ một từ hỏi.
- Nếu provider trả kết quả nhưng toàn bộ lệch chủ đề, tìm lại **tối đa một lần**, ưu tiên domain Bộ Công an với query rõ hơn. Cả hai lần và kiểm link dùng chung timeout 12 giây; không thêm lần gọi LLM hoặc tính thêm lượt Guest. Không tự retry sau lỗi provider/timeout.
- Giữ HTTPS, ghim DNS/IP, TLS và kiểm HEAD như trước. Nguồn sai chủ đề bị bỏ trước khi kiểm link, không đưa vào Sources của phản hồi mới. Các tin cũ không bị sửa/xóa.
- Phân biệt có link đúng chủ đề với có điểm số trong snippet. Khi chưa thấy điểm số, thêm `score_data_not_in_snippets` và hướng dẫn AI không tự điền điểm từ trí nhớ; hỏi ngắn gọn trường/ngành/diện tuyển sinh còn thiếu. Không gộp điểm của mọi trường thành một con số.
- Truyền `resolved_query` của câu nối tiếp vào ngữ cảnh LLM, cùng ràng buộc chỉ dùng chứng cứ của lượt hiện tại. Cache thêm namespace chính sách `topic-v2`; kết quả không có nguồn chỉ cache 15 giây thay vì một giờ đối với năm cũ. Query có thông tin riêng tư vẫn bị chặn.

File runtime sửa: `advisor/conversation_context.py`, `advisor/search_provider.py`, `advisor/graph.py`. Test mới `tests/test_task42_search_context_quality.py`; bổ sung API/PG end-to-end trong `tests/test_task42_pipeline.py`.

## Kiểm thử thực tế

**70 method local unique PASS, 0 FAIL còn lại, 0 SKIP**, tổng hợp qua các lượt kiểm tra, không cộng trùng. Lượt đầu 66 PASS; sau bổ sung test chạy đúng 18 rồi 33 method liên quan và hai ca bị ảnh hưởng cuối. Không chạy Super Board toàn diện.

Các ca mới bao gồm câu nối tiếp đúng nguyên văn, nhiều lần đổi năm, phản hồi năm nhuận sai của assistant, đổi chủ đề rõ ràng, thiếu chủ đề, tên trường/diện tuyển sinh, nguồn sai trường/sai năm/sai chủ đề, tìm lại đúng một lần, hủy theo deadline chung, nguồn đúng nhưng không có số liệu, ưu tiên nguồn chính thức, cache rỗng ngắn và không đưa dữ liệu riêng vào query.

API integration dùng PostgreSQL local thật, identity/provider mock: hai tin chat là hai lượt Guest, dù Search có ba lần gọi (một cho tin đầu, hai cho tin nối tiếp). Gửi lại cùng request_id không gọi lại Search/AI hoặc trừ thêm lượt; Sources mới chỉ chứa nguồn đúng chủ đề. Query đầy đủ và `resolved_query` được kiểm ngay trong payload của graph. Hồi quy vẫn có canary/role/ownership/token/rate/quota/concurrency và các API compatibility. Đây không phải chứng cứ chất lượng DeepSeek LIVE.

Đã thử DDGS Internet thật trên máy với query đã khôi phục đúng. Kết quả **unavailable sau 7,00 giây**, không có nguồn; ghi rõ chưa xác minh LIVE thành công, không dùng mock hoặc công cụ Search khác để thay bằng chứng DDGS. Report local: `artifacts/task42-context-search-local-live.json`. Không gọi DeepSeek thật hoặc kiểm bản sửa trên Vercel trong lượt này.

## Giới hạn và bước tiếp

Bộ khôi phục hiện là heuristic có giới hạn, không bảo đảm hiểu mọi cách diễn đạt hoặc mọi tên trường/viết tắt. Có số trong snippet không đồng nghĩa điểm đó phù hợp mọi đối tượng; prompt vẫn yêu cầu đối chiếu trường/ngành/diện/năm, và cần nghiệm thu bằng DeepSeek thật. Không trích toàn trang hoặc tạo bảng điểm giả khi snippet thiếu dữ liệu.

Bản sửa chưa commit/push/deploy. Cần kiểm trên Preview cách ly với DeepSeek thật, đúng hội thoại nhiều lượt và bộ nguồn trả về, rồi mới xem xét cập nhật Production canary. Không tự mở Search cho Guest/member, không reset dữ liệu hoặc chạy migration để kiểm thử.
