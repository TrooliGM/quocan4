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

## Bước4a — nghiệm thu có kiểm soát

Đã build Preview377a3d7 READY, database schema-only và role riêng; thêm đúng hostname Preview vào Firebase authorized domains, giữ miền cũ. Email/password Firebase SDK và DeepSeek thật qua UI PASS:5câu tự tạo1analysis/0chat,0confirmed trước click,1confirmed sau accept, mở hồ sơ không gọi AI lại, desktop/mobile không tràn. Google popup Preview chưa thử thật; fixture bổ sung giữ exploration/career/step/draft PASS. Tổng6 nhóm browser fixture PASS.

Đã chạy32 mẫu thành công qua DeepSeek thật,16tình huống trước/sau trên hai Preview cùng model deepseek-flash và staging riêng. HTTP200 không đồng nghĩa chất lượng đạt. Đọc mẫu12 phát hiện thiếu tự tin bị xếp strengths dù summary thận trọng: bổ sung validator từ chối kiểu gán này và prompt phân biệt uncertainty với mong muốn rèn kỹ năng; chưa đánh dấu mẫu12 PASS trước khi thử lại bản sửa. Bổ sung parser xưng hô thiếu dấu, giữ ranh giới từ để không nhầm chỉ/chịu với chị.

Hồi quy runtime phát hiện2 fixture cũ giả định compression mọi lượt; đã sửa fixture sang lượt6 để tiếp tục kiểm tra lỗi memory không mất câu trả lời, không thay hành vi mới để chiều test. Các test bị ảnh hưởng chạy lại PASS; thêm kiểm metrics chỉ aggregate và usage hỏng không chặn câu trả lời. Không chạy lại suite toàn diện.

Tắt Git auto-deploy CHỈ nhánh Task4.1 để push checkpoint không tạo Preview thiếu binding database/canary; Preview dùng CLI với staging explicit. Không đổi Production Branch/routes/rewrites hoặc Production env. Còn thử lại mẫu12/xưng hô trên candidate cuối, chấm rubric, tổng hợp kết quả và xác minh Production không đổi. Brave vẫn BLOCKED vì chưa có cấu hình được phép; không giả nguồn.

Previewe2fc257 READY, gates auth/ownership/token/cookie/Origin/static/200nghề/12nhóm PASS LIVE. Mẫu12 thử lại đã phân loại uncertainties/clarify đúng, không strengths; mẫu17 thiếu dấu giữ cặp xưng hô mới nhất. Production deployment vẫn không đổi. Đọc sâu mẫu9 còn thấy suy diễn yêu cầu “được giải thích dễ hiểu” thành mong muốn rèn kỹ năng giải thích; thêm quy tắc giữ nghĩa yêu cầu tư vấn, chỉ đề xuất bài tập dưới dạng lựa chọn. Cần thử lại riêng mẫu9, không chạy lại16mẫu.

Mẫu9 thử lại trên2d0a2ea PASS sau đọc nội dung: dùng Techinterest đãconfirm, bài tập là gợi ý, không gán mong muốn rèn giải thích. Rà soát cuối periodicmemory phát hiện chỉ latestturn được nén, có nguy cơ bỏ các lượt1–5 khi chuyển sang nhịp6; bổ sung recent_turns giới hạn6000ký tự, giữ role/user-evidence, kiểm fixture lượt6. Đây là thay đổi cần thiết để giữ ngữ cảnh dài, không tăng số lần gọi hoặc outputbudget. Tái sử dụng16mẫu ngắn đã PASS vì không chạm nhánh nén; chưa nghiệm thu LLM bộ nén thật cho chat dài.

## Bước4 hoàn tất — bàn giao Preview

Candidate a2a2f76 / dpl_GCno2S2r4NQqqqZswEJVU4jNZej3 READY tại https://quocan4-7x3jqli76-khkt3.vercel.app. Gates cuối PASS LIVE; periodicmemory thật thêm4turn vào phiên QA2turn đã xác minh, lượt6 main+nén2calls và summary giữ thông tin tự nhận/đính chính/xưnghô, không tựconfirm.56PythonuniquePASS/0FAILcuối/0SKIP,6nhómbrowserfixturePASS, UI FirebaseSDKpassword+DeepSeek LIVE PASS kếthừa377;16rubric13PASS/3BLOCKED sau sửa mẫu9/12, thêm17thiếudấuPASS. Median16chatrequest mỗi bản9,17→4,27s, không SLA. Brave/Googlepopup Preview vẫnBLOCKED; cơ chế canary QA-only giữ nguyên. Root checkout/careers/stories/migrations/Production không sửa. Remote đang377, chưapush checkpointcuối. Xem docs/task41-validation.md để duyệt; không merge/promoteProduction.

## Sửa UI Guest Preview theo phản ánh mới

Chrome ẩn danh xác nhận a2a2f76 thực sự tải stable-chat.js/headerlegacy vì UI bị gắn chung QAflag. Đã tách public_premium_ui Preview-only khỏi backendcanary, giữ API nhạy cảm QA-only/stable graph cho user khác; panel và khảo sát giải thích giới hạn thay vì trống/giảphântích, version assets mới.5test mới+3hồi quyPASS. Người dùng đã cho phép push checkpoint/Preview, không Production. Chờ build và nghiệm thu3persona thật; báo cáo docs/task41-preview-ui-fix.md.
