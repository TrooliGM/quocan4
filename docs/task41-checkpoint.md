# Task4.1 — checkpoint phát triển

## Quyền và nền

Yêu cầu mới chỉ Preview, không merge/promote Production, không chạy migration006/không thay dữ liệu thật. Production đã kiểm957ffde / dpl_BwthFvvNpNDscwEuKPC744bVe38z. Nhánh feat/task-4-1-advisor-intelligence từ dba80a6 (runtime957ffde + audit docs). Giữ stable fallback/canary QA-only; không sửa200 nghề/Truyện nghề.

## Bước1 — context/search

Đã thêm conversation_context.py: intent/detaiI/output budget, lịch sử bounded, public topic/year reference. Không thêm LLM router; không đổi model/key/temperature và không tăng max_tokens trên mức cũ5000. Memory compression bỏ lượt chat ngắn, vẫn chạy mỗi6turns hoặc khi lịch sử dài. Search route hiểu thiếu dấu/chính sách/tuyển sinh; không chèn survey/profile vào query.11 unit context/search PASS, không gọi đó là chất lượng model LIVE.

Model/chi phí/latency và16tình huống tiếngViệt sẽ được đánh giá trong bước4; chưa tuyên bố thông minh như ChatGPT. Tác vụ phân tích riêng đang xây dựng, chưa hoàn thành; file analysis_jobs chưa có route/frontend/tests nên chưa là checkpoint chức năng.

Preview metadata có DeepSeek/Firebase binding dùng chung targetProduction+Preview do project đã cấu hình; không copy giá trị secret. Chưa có DATABASE_URL chung cho nhánh mới. Cần DB schema-only với credential riêng, kiểm0rows trước thử; không sao chép dữ liệu học sinh. Brave Preview/Production chưa có binding dùng được, LIVE Search còn BLOCKED.


## Bước2 — tác vụ phân tích

Đã triển khai analysis_jobs metadata trong messages hiện có, không migration mới: pending/processing/completed/failed; lease90s và attempt fencing, một model call đồng thời/survey hash. API chỉ QA được verify; cachecompleted dùng lại kể cả khi key tạm thiếu. Budget riêng PostgreSQL UID6/ngày2/phút, IP30/ngày mặc định cấu hình được; không trừ quota chat8. Lỗi cần retry rõ ràng, không autoretry provider âm thầm. Claim/finish khóa usage→session cùng thứ tự claim/quota, không giữ DBtransaction trong lúc gọi model; kết quả chỉ là draft/proposal, confirm từng mục mới vào bảngprofile. Chat chỉ attach insights gọn, không phân tích lại/copy16proposal vào mỗi tin.

13 test jobs mới PASS (PGlocal/LLMfixture);8 personalization+4 validator đã PASS ở lượt trước, sau đó chỉ thêm compactinsights/fencing được kiểm riêng. Sửa false-positive khi5câu đềuEmchưarõ, không hạ kiểm tra quote căn cứ/strength. Analysis25s timeout configurable riêng, max3000tokens giữ nguyên; chưa kết luận latency/LIVE trước Preview.

Đã tạo Neon root schema-only task41-preview-schema-20261025 (br-morning-tooth-aznv081q), mới role task41_preview_app. Kiểm TLS, endpoint đúng branchkhácProduction, cả8 bảng0rows, schema006 có sẵn do schema clone; không chạy migration006/không copy studentdata. Thử tạo đầu bị tài khoản từ chối suspendinterval; bỏ tùy chỉnh để dùng default, không đổi plan. Credential riêng DPAPI/artifacts, chưa bindVercel. Production vẫn957ffde.


## Bước3 — frontend

Sau5câu, UI tự gọi taskendpoint, không gửi technicalprompt vào chat/không trừquota8. Có analysisloading riêng, autorecoverpending khi mởlại; failed mới cóRetry. Không báo đangtìmweb khi chưa cótoolstatus thật. Profile thẻkem/xanh với căn cứ thu gọn, accept/edit/reject, RAMdraft theoowner cóversionfence và xóa khilogout; responsejob chỉmergeanalysismetadata, không ghi đè tinchat mới/flagcủaUI. Đồngbộchat.html/public copy vàcacheversionloader.

Chrome+PGlocal/Firebase+LLMfixture:5 nhóm PASS autoanalysis0chat,0implicitconfirm; accept/edit/reject vàreuse; savefailuregiữdraft; bubble/Copy/mobile vàmanualchat1quota; retrynetworkfailure khônglặpvôhạn. Ảnhartifacts/task41-*; đã xemdesktop, tinhchỉnh nútLàmrõthêm đồngbộpalette. Không gọifixture làLIVE. Node syntaxPASS. CònPreviewbuild/LIVE16eval/GooglePreview cầnnghiệmthu.
