# Task 4.4 — Final QA trước phát hành

Ngày nghiệm thu: 27/10/2026. Worktree `D:/khkt/.claude/worktrees/task44-navigation-fix`, nhánh `hotfix/task44-navigation-grounding`. Kế thừa `3f77005` và báo cáo `f581e39`, không xây lại điều hướng.

**Kết luận: NOT READY FOR PRODUCTION.** Nguyên nhân chính xác của ValidationError lịch sử vẫn chưa xác minh đầy đủ. Google popup thật đã được người dùng xác nhận thành công trên Preview; không đồng nhất xác nhận thủ công này với kiểm thử tự động hoặc phép đo quota. Task 4 tổng thể vẫn CHƯA hoàn thành. Không push, merge hoặc deploy Production.

## Candidate và môi trường

- Source mới: `3df3897303aa757ffd3b989d252e4723c57f02a8`; checkpoint chẩn đoán trước đó: `873264b`.
- Preview READY: `dpl_DA5F6cd6xQNNcDjCuzpj7nR96tVL`, https://quocan4-ojnfhtstk-khkt3.vercel.app/ai-career-advisor .
- Alias dùng kiểm Google: https://quocan4-git-fix-chat-vercel-khkt3.vercel.app/ai-career-advisor . **Tên alias cũ nhưng hiện trỏ đúng candidate3df3897**, không phải codefix-chat cũ. Đây là alias Preview cùngproject, trước/sau đều targetPreview; checkpoint mapping cũ lưu trongartifacts. Không tái gán alias integrate-premium-preview vì kiểm tra thấy target của nó làProduction.
- Hostname candidate riêng chưa nằm trong Firebase authorized domains. Alias Preview ở trên đã được cấp phép sẵn; chỉ đổi mapping của aliasPreview, **không sửa Firebase domains**, ProductionBranch, environment Production hoặc domain chính.
- Database staging vẫn `br-morning-tooth-aznv081q`/neondb, role thử riêng hiện có. Chỉ thao tác session QA tổng hợp được cấp phép qua API; truy vấn chẩn đoán hạn mức dùng READ ONLY. Không sửa schema/migration/quota hay dữ liệu học sinh.
- Production giữ `da6d146` / `dpl_9TdB69NsBqWmKssEUQbNhG92jsVS`.

## Điều tra ValidationError: bằng chứng và giới hạn

Lần lỗi lịch sử chỉ ghi `survey_analysis_failed type=ValidationError`; job lưu tên loại lỗi. Không có stack trace, raw output DeepSeek hoặc chi tiết trường lỗi được lưu. Vì vậy **không thể khôi phục chính xác stack trace/dữ liệu gây lỗi lịch sử từ bằng chứng hiện có**. Không gán lỗi đó cho model, category hay một validator cụ thể chỉ từ tên ngoại lệ.

Đối chiếu mã xác định đường gọi tĩnh: `analysis_jobs.execute` → `survey_analysis.generate_analysis` → `validate_analysis` → `Analysis.model_validate`. Đây là đường gọi qua source, **không phải stack trace đã thu lại từ lần lỗi cũ**. SchemaAnalysis chứa summary, proposed_profile_items và clarification_questions; từngProposal có category/area/value/evidence/confidence/inference_type/proposed_action. Evidence kiểm question_id1–5 và excerpt nguyên văn của đúng câu, cùng các hàng rào chống suy diễn năng lực.

Đã tái hiện local một PydanticValidationError thật với dữ liệu tổng hợp: `category="subjects"` gây `literal_error` tại `proposed_profile_items[0].category`; subjects làarea, category tương ứng phải làinterests. Đây là **fixture kiểm tương thích schema**, không nhận đó là output lịch sử của DeepSeek. Test còn kiểm enumconfidence lạ, excerpt quá dài, keylạ, căn cứ bịa và khác chữ hoa/khoảng trắng. Mọi trường hợp không hợp lệ vẫn bị từ chối; không đổi Literal/extra='forbid' hoặc chấp nhận diễn đạt lại.

Lần retry thực tế của chính session Member từng lỗi trên bản chẩn đoán873264b lại thất bại với **ValueError**, không phải ValidationError; khảo sát/lịch sử/analysis_request_id giữ nguyên. Log lúc đó chưa có mã ValueError đủ chi tiết để xác định căn cứ nào sai. Hai lần lỗi khác loại **không được gộp thành một nguyên nhân**.

Một lỗi ứng dụng xác minh chắc chắn và đã sửa là: mọi exception phân tích đều bị biến thành `provider_unavailable` và chỉ log tên loại, khiến lỗi dữ liệu/schema không thể phân biệt với lỗi mạng/provider. Nay lỗi dữ liệu được phân loại an toàn, có chẩn đoán schema/trường/kiểu/độ dài và framefile/function/line; không log input, context, exceptionmessage tùy ý, tênfield lạ, locals, rawoutput hoặc câu trả lời học sinh. Chỉ giá trị enum thuộc taxonomy công khai mới có thể xuất hiện trong diagnostic. Chẩn đoán của lỗi nguyên văn có thêm cờ case_whitespace_equivalent, nhưng **không tự chấp nhận quote khác định dạng**.

## Bản sửa và retry

- Tối đa2providerattempt cho một tác vụ phân tích trong timeout tổng cũ25s. Chỉ retry một lần khi output không đạt JSON/schema/căn cứ, dùng lại năm câu gốc và diagnostic an toàn; không sinh dữ liệu dự phòng, không nới validator. Kết quả hợp lệ ngay thì chỉ1call. Không có vòng lặp hoặc nâng ngân sách.
- `AnalysisRetryInput.request_id` làUUID tùy chọn để tương thích clientcũ. Clientmới gửi **survey.analysis_request_id cố định**. Backend đối chiếu với survey của đúng owner trước khi giữ lượt; ID khác trả409 trước model/ngân sách, UUID sai trả422. Retryfailed phải chủ động `retry=true`; completed được trả từcache. Lease/transaction/worker-token cũ vẫn chống hai lần lưu và worker cũ ghi đè.
- Retry không tính quota8câu chat; attempt phân tích thực sự vẫn chịu ngân sách analysis hiện có. Không tự xác nhận hồ sơ. Không xóa survey/history/draft, không thêm message nhân tạo để lưu phân tích.
- Cachekey chat.js đổi sang task44-finalqa-1 ở shell chính và advisor-entry. Không đổi thiết kế, xác thực hoặc điều hướng.

## Bảng nghiệm thu thực tế

| Điều kiện | Kết quả | Bằng chứng và giới hạn |
| --- | --- | --- |
| Nguyên nhân/stack/input chính xác của ValidationError lịch sử | **BLOCKED** | Chứng cứ cũ không lưu chi tiết. FixturePydantic không thay thế bằng chứng lịch sử. |
| Schema và kiểm tra căn cứ không bị nới | **PASS local** | Kiểm enum/extra/quote giả/khác định dạng; raw output không hợp lệ không được lưu. |
| Diagnostic không lộ nội dung | **PASS local** | Assert log không chứa câu khảo sát, markeremail tổng hợp hoặc tênkey lạ; frame và field được giới hạn. |
| Retry cùngrequest_id, cache, cạnh tranh | **PASS local** | Nhóm phân tích28test: saiID không tiêu ngân sách; song song mộtlease; failed→retry→completed; replaykhôngmodel; survey/historygiữ nguyên; khôngconfirmedprofile tự động. |
| Retry chính session lỗi trên Preview | **PASS LIVE** | Source3df3897, HTTP200 completed4,05s, survey/history/request_idgiữ nguyên. POSTreplaycùngID trả cùngkết quả, attemptkhông tăng. Đây là lần model trả hợp lệ; **chưa chứng minh boundedrepair đã được kích hoạt trênLIVE**. |
| Thêm mẫu LIVE để xác định lỗi ngẫu nhiên | **BLOCKED** | HTTP429. READONLY xác minh bộđếm Memberanalysisday6/6, khoảng4giờcòn lại ởlúcđo; minuteđãhếtcửa sổ. Không đổiUID/IP hoặc reset để tiếp tục. |
| Điều hướng nghề, metadata lỗi, quota/profile | **PASS local** | Nhóm hồi quy27test, gồm mismatch2lầnvẫn200, unknownIDbỏnút, không lưu/trừ lượt trùng,3provider và hai kiểu lưu. Tổng **55testPython thực chạy lần này,0SKIP**. |
| Chất lượng nghề DeepSeek thật | **PASS kế thừa** |11chatLIVE tại3f77005 (bảo tồn,so sánh,đổi chủđề,phủđịnh,không dấu,không cầnnút). graph/navigation/reviewer/prompt không đổi trongFinalQA; không gọi lại phần đãPASS chỉ để tăng sốtest. |
| APIsecurity trên candidate mới | **PASS Preview** | Token401, owner404, Origin403, privatepaths404, câuGuestthứ9bị429. Ngân sách và quyềnprofilekhông bị mở rộng. |
| Desktop/mobile và hành trình3nhóm | **PASS Preview Chrome** | Guestcookiecũ8/8, Member/QA FirebaseSDKpassword thật. SameID/survey/draft/reload,3nghề,Truyện nghề,Back/Forward;tab1→1;0POSTchat/create/analysisdođiều hướng. Guestvẫn8/8 trước/sau. Không nhận SDKpassword làGooglepopup. |
| Khảo sát/frontendautoflow | **PASS Chrome local** |6nhóm browser_task41:5câuautoanalysis,edit/accept/reject,draftsavefailure,retrygiánđoạn,zerochatquota vàauthfixture. Mô hình/Firebaseởđây làfixture. |
| Googlepopup QA thật | **PASS — người dùng xác nhận** | Người dùng trả lời “Popup thành công; giữ đúng hội thoại và cùng tab” cho luồng trên aliasPreview gồm bản nháp/khảo sát, Google popup và Truyện nghề/BackForward. Ghi nhận bằng chứng thủ công cho luồng đã hỏi; không dùng fixture/SDKpassword thay thế, không suy thành phép đo request/quota độc lập. Alias đã đối chiếu vẫn đúng candidate3df3897/DA5F6cd6 khi ghi nhận. |
| Production không thay đổi | **PASS control-plane** | Domainchính vẫndeployment9TdB69Ns. Khôngpush/merge/deployProduction, migration, thayFirebase/secrets hoặcresetquota. |

## File sửa trong Final QA

1. `advisor/survey_analysis.py`: phân loại lỗi, diagnostic an toàn, boundedrepair; giữ nguyên schema và validator.
2. `advisor/analysis_jobs.py`: chuyển mã lỗi phù hợp; nhận/đối chiếu/trảrequest_id, giữ lease/cache/transactions.
3. `advisor/routes.py`: request_idUUID tùy chọn cho POSTanalysis.
4. `public/assets/chat.js`: gửi surveyanalysis_request_id cố định.
5. `chat.html`, `public/assets/advisor-entry.js`: cachekey modulechat.
6. `tests/test_analysis_validation.py`, `tests/test_task41_analysis_jobs.py`: regression/schema/privacy/retry/concurrency.
7. Báo cáo này và bộnhớ/decisions. Artifacts/DPAPI/screenshots không commit, không có secrets hoặc dữ liệu học sinh trongGit.

## Điều kiện tiếp tục và rollback

1. GooglepopupQA đã được người dùng xác nhận thành công trên aliasPreview; đã cập nhật PASS thủ công. Các phép đo không gọi AI/quota do điều hướng giữ bằng chứng Chrome/API riêng, không suy từ thao tác popup của người dùng.
2. Chờ ngân sách analysis tự hết cửa sổ rồi thử có kiểm soát, tối đa sốlần cần thiết, để thu diagnostic thực nếu lỗi tái diễn. Nếu không có rawinput/trace cũ thì ghi rõ giới hạn; không thể tuyên bố hồi tố nguyên nhân lịch sử. Không tạo tài khoản/IP/budgetkhác để né429.
3. Chỉ đề xuất phát hành khi các mục liên quan được xác minh và người dùng duyệt; Task4tổngthể vẫnchưa hoànthành.
4. Rollback Preview vềsource3f77005/deployment`dpl_33DRW8yLeySY1zSTb4QA7ns7VQfj` trêncùngstaging, hoặc khôi phục mappingaliasPreviewđãghi trướcQA. KhôngresetDB/survey/history/quota. Với quyền phát hànhProduction riêng sau này, giữ rollbackdeploymenthiệnhành9TdB69Ns; không tự thực hiện bâygiờ.
5. Nếu rollbackbackendvềbảncũ, clientđangmởcần tải lại để dùngcachekey/scriptcũ vì schemaAPIcũkhôngnhậnrequest_id. Không xóa sessionStorage; bản nháp vẫn được giữ theo cơchếTask44.

## Điều tra bổ sung theo yêu cầu mới

Giữ GooglepopupPASS, không kiểm lại khi codeauthkhôngđổi. Bổ sung ma trận dữ liệu giả, schema version và trace server ngẫu nhiên; kiểm39testlocalPASS0SKIP, khôngnớivalidator. Kết luận cho lỗi cũ: **Historical ValidationError – root cause undetermined**. Bằng chứng và theo dõi lần sau nằm ở `docs/task44-validation-investigation.md`; không nhận fixture là tái hiện nguyên nhân lịch sử.
