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

## Kết quả Preview và quyết định phát hành

**NOT READY cho Production Search không giới hạn QA. Đã dựng Preview, không thay Production hoặc push các checkpoint mới.**

- Preview hiện tại: https://quocan4-87bqdbdmb-khkt3.vercel.app/ai-career-advisor.
- Deployment: **dpl_3Kz4eeduVK3wGr2STUKzwijARDGe**, READY, target=null.
- Source: **922983af856cc41a1da24390272e890b1efa0e24**; checkpoint đầu399a46e. Nhánh vẫn feat/task-4-1-advisor-intelligence. Các commit mới chỉ local để pin source Preview, không push khi gate phát hành chưa đạt.
- Preview bật Search cho cả Guest/member/QA qua SEARCH_QA_ONLY=false, giữ quyền dữ liệu profile riêng. Không chuyển các nhóm về legacy. Bổ sung đúng hostname Preview cuối vào Firebase authorized domains để người dùng mở được Google Login; đọc lại xác nhận tất cả miền cũ được giữ, không đổi project/keys/cấu hình Production khác. Popup trên hostname mới chưa kiểm bằng thao tác người dùng; xác nhận popup Production cũ vẫn là bằng chứng lịch sử riêng.

### DeepSeek LIVE nhiều lượt

Đã có **16 câu trả lời thật**, hai đợt Preview × hai tài khoản (QA và thành viên thường) × bốn lượt. Không mock Firebase/DeepSeek/Search. Nội dung công khai và dữ liệu khảo sát giả, chỉ ghi vào staging riêng. Bộ câu hỏi:

1. Điểm chuẩn các trường đại học Công an năm2024 là bao nhiêu?
2. Vậy năm2020 là bao nhiêu ạ?
3. Học viện Cảnh sát nhân dân, nam, tổ hợp A01 nhé.
4. Đổi chủ đề: giải thích lập trình là gì, chỉ hai câu.

Đợt đầu nguồn399a46e: lượt2 ở cảhai tài khoản giữ đúng chủ đề/năm2020, có4nguồn và không có nguồn nămnhuận. Lượt3 bịnot_needed, chưa nhận ra đó là lời làm rõ; QA có lời mô tả bảng/đối tượng chưa được snippet hỗ trợ. Ghi FAIL cho nhánh làm rõ, không dùng chỉHTTP200 để đánhPASS.

Đã sửa nhánh làm rõ: giữ chủ đề điểm chuẩn, tên trường/diện/tổ hợp bổ sung và **năm gần nhất ở lượt nối tiếp2020**, không quay về năm2024 của câu đầy đủ đầu tiên. Hiểu tên trường viết tắt Học việnCSND nhưng không nhầm với Đại họcCSND; ưu tiên cả subdomain chinhphu.vn. Kiểm thử thêm ngăn câu “giải thích an toàn thông tin là gì” bị hiểu nhầm là lựa chọn ngành. Một assertion chuỗi làm rõ nối tiếp ban đầu FAIL, đã sửa và chạy lại nhóm31method PASS; không ghi thành PASS trước khi sửa.

Đợt hai nguồn922983a: cảhai tài khoản đều có statusok/sources ở ba lượt tra cứu vànot_needed/0nguồn ở lượt đổi chủ đề. Query lượt3 đúng **điểm chuẩn Học viện Cảnh sát nhân dân nam A01 năm2020**. Cả6yêu cầu cầnSearch cónguồn, request5,62–7,57s trong mẫu này. Không có link/đoạntrích nămnhuận. Model không tự chốt một điểm A01 khi snippet chưa có ô tương ứng. Đây là PASS cho sửa truy vấn nối tiếp/làm rõ, không đồng nghĩa mọi nội dung tổng hợp đều đúng.

### Lỗi chất lượng còn lại — chặn mở đại trà

1. **FAIL độ chính xác số liệu nguồn thứ cấp:** snippet trang tổng hợp nói thí sinh nam có dải19,61–23,09. Hai phản hồi đợt2 lặp lại dải này dù người dùng hỏi A01. Đối chiếu [bảng chính thức Học viện CSND](https://hvcsnd.edu.vn/cong-bo-diem-chuan-vao-cac-truong-cand-2020-10051) và [Báo CAND](https://cand.vn/cong-bo-diem-chuan-vao-cac-truong-cand-2020-post583042.html): mục Nghiệp vụ Cảnh sát/nam có A01=23,09; C03=18,88; D01=19,61. Vì vậy dải từ trang tổng hợp không bao quát đầy đủ các tổ hợp, không được khẳng định là dải chung. Nguồn chính thức trong Search chỉ cung cấp snippet phần mở đầu; ứng dụng chưa đọc được bảng đầy đủ. Việc QA độc lập mở trang để đối chiếu không được dùng giả làm kết quả trích xuất của backend.
2. **PARTIAL tên cơ quan nguồn:** một phản hồi QA gán congan.com.vn thành cổng Bộ Công an. Link đúng chủ đề không chứng minh nhãn cơ quan do model tự viết là đúng. Không coi đây là nguồn giả đã bị phát hiện bởi HEAD; đây là thiếu kiểm soát attribution khi tổng hợp.

Phương án tối thiểu tiếp theo: không kết luận điểm/dải điểm từ nguồn tổng hợp khi chưa đối chiếu đúng trường/ngành/diện/tổ hợp/năm với thông báo gốc; bổ sung trích đoạn bảng từ URL chính thức đã xác minh bằng reader có giới hạn kích thước/thời gian, TLS/IP pinning và chống redirect/SSRF. Nếu không trích được ô dữ liệu thì nói rõ thiếu chứng cứ, không điền từ trí nhớ. Nhãn nguồn cần lấy từ metadata đã xác minh hoặc hiển thị domain, không để model tự gán tên cơ quan. Chỉ kiểm lại các ca FAIL và guard an toàn liên quan; không viết lại toàn bộ AI hoặc làm vòng lặp sửa/đánh giá vô hạn.

### An toàn và Guest

- 73method local unique PASS cuối,0FAIL còn lại/0SKIP qua các đợt kiểm trọng tâm; kế thừa các bài đãPASS, không cộng lại lượt chạy. Test mới xác nhận query làm rõ/năm gần nhất/alias trường và deadline. Không dùng con số này che các FAIL chất lượng LIVE nêu trên.
- Preview cuối: QA đọc lại phiên của chính mình200; member/Guest truy cập phiên QA404; invalidtoken401 cả3role; Originkhác403; đường dẫn private404; thư viện200nghề/12nhóm. APIconfig xác nhận Search bật cho cả3role, quyềnprofile vẫnQA-only. Không reset/quy đổi Guest thành member.
- Guest hợp lệ cũ còn0/8; gọiAI bị429 như mongđợi. Budget cấp Guest staging theo IP/ngày10/10 còn khoảng61492giây ở lần đọc cuối. Không suy đoán đó làIPloopback/globalbucket; so với một số địa chỉ runtime chuẩn không khớp. Không thay IP/header/UID, tạo FirebaseAnonymous, đổiDB hoặc sửa hạn mức để lách kiểm thử. **Guest Search LIVE thành công vẫn BLOCKED**, không lấy configenabled/429 thay bằng chứng gọiSearch thật. Cần phiên Guest thử hợp lệ cònlượt hoặc chờ cửa sổ cấp phiên kết thúc tự nhiên.

Không push hoặc phát hành Production do chưa đạt gate. GET Vercel xác nhận main vẫn **dpl_EJvYVHp8yYb4Ync29JPu91WXWa6c / 1b1b64080a00a389d8b93a0fb8f35d0e7bf91dd8**, URL https://labanhuongnghiep.vercel.app/ai-career-advisor, Search canary chỉQA như trước. Không merge/main/forcepush, migration, reset quota hoặc đổi dữ liệu Production. Khi đạt gate mới được dùng envProduction và mởSEARCH_QA_ONLY=false; không promote deployment đang bind staging này.

Artifact: task42-context-initial-deploy.json, task42-context-candidate-deploy.json, task42-context-live-summary.json, task42-context-round2-summary.json, task42-context-security-final.json, task42-context-final-review.json, task42-context-guest-budget-readonly.json và task42-context-firebase-domain.json. Raw16lượt/identities mãhóaDPAPI trongartifacts, khôngGit. Không lưu secrets hoặc dữ liệu học sinh trong báo cáo.
