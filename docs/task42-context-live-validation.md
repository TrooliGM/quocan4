# Task 4.2 — Kiểm thử LIVE trước khi mở Search cho mọi người

## Quyền và trạng thái bắt đầu

Ngày 25/10/2026 người dùng cho phép tiếp tục bản sửa ngữ cảnh hiện có, triển khai Preview và chỉ phát hành Production cho Guest/member/QA khi LIVE và an toàn đạt. Không được lách hạn mức. Quyền này thay chính sách chỉ QA nếu và chỉ nếu các gate phát hành hoàn tất; không tự coi việc cho phép là bằng chứng nghiệm thu.

Worktree `.claude/worktrees/task-4-1`, branch `feat/task-4-1-advisor-intelligence`, bắt đầu HEAD fb2eca4 với bản sửa local đã PASS và ba tài liệu xác nhận Google chưa commit. Giữ toàn bộ các thay đổi này, không làm lại phần đã PASS. Checkpoint local cần để gắn source chính xác cho Preview, chưa push hoặc thay Production trước khi gate LIVE đạt.

## Điều tra DDGS timeout

Đã đọc source **ddgs9.16.1 đang được cài**, không suy đoán từ status unavailable. Backend auto có thể chờ nhiều engine trong ThreadPoolExecutor; timeout5s là timeout engine/wait, không bảo đảm toàn bộ text() kết thúc sau5s. Chẩn đoán chỉ dùng query công khai, không log exception text hoặc URL/query nhạy cảm.

Đo thực tế trên máy: Mojeek báo TimeoutException tại5,99s, nhưng DDGS auto sauđó vẫn trả5kết quả sau**7,53s**. Adapter ứng dụng cũ dừng ở7s, bỏ lỡ bộ kết quả hợp lệ. Đây là nguyên nhân được xác minh cho mẫu local, không đủ để kết luận mọi unavailable trên Vercel đều có cùng nguyên nhân; chống bot/rate/network của từng engine vẫn có thể ảnh hưởng.

Tăng deadline adapter lên9s, giữ timeout engine5s/TLS, hai worker và release slot khi worker thực sự xong; tổng retrieve vẫn12s, có tối đa một lần chỉnh query khi tất cả nguồn sai chủ đề. Không tăng route timeout, quota hoặc số lần LLM.

Sau sửa, DDGS LIVE local trả nguồn đúng chủ đề sau**7,61s**, gồm Học viện Cảnh sát và báo CAND; không có trang năm nhuận. Bộ nguồn là snippet+HEAD, không giả đã trích toàn trang trong ứng dụng. Rà thủ công bằng công cụ web độc lập: bài chính thức tại hvcsnd.edu.vn và cand.vn thực sự có bảng điểm2020; hai giá trị trong snippet nguồn tổng hợp khớp mục Học viện CSND/nam/A01,C03. Việc đối chiếu thủ công này không được nhập vào kết quả DDGS hoặc coi như adapter đã đọc toàn trang. Trang tổng hợp không mở được bằng công cụ web đó; chỉ kết luận giá trị mẫu đã được đối chiếu với nguồn chính thức.

Artifact: artifacts/ddgs-timeout-diagnostic.json và task42-context-local-live-after.json. 71method local unique PASS kế thừa các lượt trước và test mới; không cộng trùng. Thử worker hoàn tất sau mốc7 nhưng trước9s, deadline tổng12s và slot sau cancel đều PASS. Không chạy lại toàn bộ Super Board.

## Preview và gate Production

Preview dùng staging/schema-only `task41-preview-schema-20261025`, role riêng hiện có; SEARCH_PROVIDER=ddgs, SEARCH_QA_ONLY=false để kiểm cùng năng lực cho mọi role. Không đổi quyền Hồ sơ, Firebase, secrets hoặc database Production; không migration/reset. Chưa đánh dấu LIVE DeepSeek PASS trước khi có câu trả lời và nguồn thực tế.

Kiểm PG staging bằng transaction readonly: budget cấp Guest theo IP/ngày đang **10/10**, còn khoảng62356giây tại lần kiểm. Guest thử cũ đã hết8câu. Không tạo FirebaseAnonymous, đổiIP/header, đổiDB/role hoặc tăng/reset giới hạn để vượt gate này. Nếu không có phiên thử hợp lệ còn lượt, Guest Search LIVE phải ghi BLOCKED và không mở Search đại trà trên Production.

Production hiện là source1b1b640, deployment dpl_EJvYVHp8yYb4Ync29JPu91WXWa6c, Search canary QA-only. Phải kiểm lại alias trước mọi phát hành và giữ rollback. Preview không được promote nguyên trạng vì đang bind DB staging. Chi tiết kết quả LIVE/deployment sẽ bổ sung sau khi kiểm, chưa tuyên bố đủ điều kiện Production.
