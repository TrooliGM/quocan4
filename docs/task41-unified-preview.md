# Task4.1 — cùng pipeline hội thoại cho mọi người

## Quyết định mới thay thế giới hạn trí tuệ QA

Người dùng yêu cầu Guest/member/QA cùng engine Task4.1, kể cả phiên đã có và cả hai mode. Giới hạn QA chỉ còn áp dụng tính năng dữ liệu chưa phát hành, không dùng để quay lại AI cũ. Chỉ Preview và chuẩn bị phát hành; không được tự deploy Production hoặc chạy migration/reset quota.

Đã xác minh worktree sạch ở `e624285`, nhánh `feat/task-4-1-advisor-intelligence`. Production trước thao tác là957ffde; điểm quay lại Preview trước sửa: `e933f98` / `dpl_GPWPYMsLL3F7MwYsDaFsYzmBihDZ`, URL `https://quocan4-bp6m6anvt-khkt3.vercel.app`. Chưa thay Production.

## Mã thực tế đã sửa

- `/api/ai/chat` gọi duy nhất graph Task4.1, bỏ chọn stable_graph theo allowlist. `task4_enabled=true`, `chat_pipeline=task41`, automatic analysis cho mọi phiên xác thực hợp lệ. Model/tham số/prompt không chia theo vai trò.
- `/api/advice` và `/api/career-stories/{career_id}/ask` dùng lại các node answer của Task4.1 (context, history, retrieval, analysis draft, generation, validation). Giữ wrapper xác thực/quota/idempotency/atomic save; tên module legacy_ai là compatibility protocol, không còn mô hình/prompt cũ. Giữ bối cảnh/safety cảnh truyện. Hai API này vẫn là hợp đồng hỏi đơn lẻ theo request_id, không tự ghép lịch sử từ các request khác của cùng người.
- Server-Timing `ai_pipeline=task41` được đặt tại node tạo câu trả lời thật, cùng số provider calls/token; response mới có pipeline. Retry đã lưu trả `saved_response`, không gọi lại AI hoặc gắn nhãn kết quả cũ như vừa tạo mới.
- Nén/hồ sơ hội thoại chỉ dữ liệu của phiên hiện tại. Confirmed profile context có cờ quyền server riêng và OFF mặc định; Guest không đọc profile bank dù metadata cũ đã opt-in. Member/QA có quyền dữ liệu mới đọc confirmed của chính mình; không tin UID/role client.
- Analysis draft owner-scoped mở cho cả3vai trò sau5câu, ngân sách PG riêng6/ngày2/phút/IP30/ngày, không trừ Guest8; chỉ cache cùng survey hash. Confirm/edit/delete private profile còn QA-only theo cờ dữ liệu hiện hành. UI hiển thị draft cho mọi người, khóa thao tác chưa có quyền và giải thích rõ, không biến thành AI legacy.
- UI mới không còn phụ thuộc QA trong candidate. Compatibility loader cho HTML cũ tải UI hiện hành, lỗi thì báo lỗi rõ, không import stable-chat.js. Cache version `task41-unified-1`. Production hiện hữu chưa thay đổi vì chưa triển khai candidate.
- Đổi chủ đề rõ ràng không kéo thêm survey/career refs không liên quan. Không hardcode câu trả lời; dùng chung DeepSeek/prompt/tool cho mọi vai trò. Brave chưa có key được phép, không giả nguồn.

## Kiểm thử trước Preview

Các test liên quan đã chạy bằng PostgreSQL local và provider/Firebase fixture; không dùng kết quả này thay LIVE. Đã kiểm chung engine của3vai trò/3endpoint, chat cũ/mới, cả2mode, temporary/durable, quota8/câu9, retry miễn phí, lỗi không fallback, owner isolation và analysis không tự confirm/không trừ chat. Hồi quy shared protection/token/IP/rate/lease, personalization ON/OFF và analysis jobs đã kiểm các phần bị ảnh hưởng.

Hai lỗi harness phát hiện và xử lý: test lease seed INSERT trùng rowusage0 nay do pendinganalysis tạo; sửa fixture local thành seed UPDATE có kiểm rowcount, không sửa dữ liệu thật. Header Server-Timing trước chỉ có ở /api/ai; bổ sung cho2API compatibility để nghiệm thu đường gọi thật. Những ca FAIL/ERROR đã chạy lại đạt. Không chạy toàn bộ Super Board.

Đang chờ build Preview và so sánh DeepSeek LIVE cùng6câu cho3vai trò, kiểm UI autoanalysis và kiểm quota/rate/phân quyền thật. Chưa kết luận PASS LIVE/READY trước khi có kết quả.
