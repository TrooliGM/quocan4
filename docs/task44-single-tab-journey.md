# Task 4.4 bổ sung — Điều hướng cùng tab

Nền: Task4.3 Production608146c, audit4118367. Nhánh riêng feat/task-4-4-continuous-journey; không tìm thấy worktree/checkpoint4.4 đã có. Đang chờ người dùng mô tả riêng lỗi Hồ sơ; không tự coi lỗi đó đã được xử lý.

## Nguyên nhân và thay đổi
- navigation-actions.js cố ý target_blank và ghi mở tab mới. Bỏ target cho nút nội bộ, nguồn Internet giữ tab mới.
- Liên kết thư viện/truyện chưa mang conversation; mode=career_exploration khởi tạo phiên mới. Thêm con trỏ hành trình theo tab/UID, TTL2h, URL conversation; backend vẫn xác minh quyền sở hữu, không coi storage hoặc URL là token.
- Chat luôn ghi ID đã xác minh vào URL; sửa hai đoạn replaceState dùng URL cũ làm mất ID sau khi tạo chat.
- Nút Cùng tìm hiểu nghề trở về phiên gốc; nghề/cảnh là bản nháp câu hỏi, không ghi đè nội dung đã nhập hoặc đổi khảo sát gốc, không tự gửi.
- Bỏ POST phân tích tự động chỉ vì mở lại chat; hoàn tất khảo sát vẫn tự phân tích và người dùng vẫn có thể chủ động thử lại.
- Lưu cả pending request_id vào draft để retry sau điều hướng dùng cùng mã, không tự gọi AI lại. Guest claim chuyển con trỏ sau server xác nhận; logout/new-chat xóa con trỏ.
- Native anchors, không window.open; modifier/middle click do người dùng chọn vẫn hoạt động. Modal nghề có history Back/Forward; truyện giữ conversation qua bộ lọc/route, khôi phục khi BFCache trở lại.
- Không sửa backend/quota/database/schema/catalog/thiết kế Premium. Không đổi quyền hồ sơ hoặc model/search.

## Kiểm thử đã chạy
- 26 phương thức Python: test_navigation_actions + test_shared_ai_protection PASS. Node syntax + git diff --check PASS.
- tests/browser_navigation.py Chrome: XSS/open redirect, cùng tab, UID claim/draft, desktop/mobile PASS; POST0 trong fixture.
- tests/browser_journey.py: trang FastAPI thật + PG local, khảo sát dở, hoàn tất khảo sát, thư viện nhiều nghề, truyện/cảnh, Back/Forward, bản nháp, cùng conversation và một tab PASS. Không có POST chat/create/analysis khi điều hướng; POST /guest/session chỉ xác minh lại cookie hiện có. Google claim ở đây là fixture, KHÔNG phải popup Google thật.

Preview/LIVE chưa thực hiện tại thời điểm checkpoint này. Production vẫnTask4.3. Google popup thật cần người dùng thao tác; không dùng fixture/password để đánh dấu PASS. Các báo cáo bổ sung sau đây ghi kết quả thực tế.

## Rollback dự kiến
Giữ deployment ProductionTask4.3 G11k5MKTVWNhEAcszbhqGEZm1KiW, source608146c; xác minh alias lại trước phát hành. Nếu cần rollback chỉ đổi deployment về bản đã xác minh; không reset/restore DB, không xóa quota/hội thoại.


## Mở rộng theo đặc tả đầy đủ người dùng gửi sau checkpoint93e657e

Không còn chờ mô tả lỗi Hồ sơ: đã nhận đầy đủ Task4.4 và triển khai trên cùng nhánh, kế thừa bản vá điều hướng.

- Mở rộng terminal function của cùng completion DeepSeek bằng profile_updates. Backend chỉ nhận excerpt nguyên văn trong lời nhắn HIỆN TẠI; từ chối nguồn web/lời AI, PII cơ bản, suy kỹ năng từ sở thích, ID thay thế lạ hoặc category không khớp. Không có lượt LLM trích xuất mới cho mỗi tin nhắn. Đề xuất lưu cùng message/quota trong transaction hiện hữu.
- Hợp nhất khảo sát và các cập nhật hội thoại có thứ tự; add bổ sung, correct/withdraw ghi nhận đính chính, không sửa lịch sử hoặc tự sửa hồ sơ chính thức. ID ổn định chống lặp, max80 đề xuất hiện hành; trạng thái đã bỏ qua vẫn được giữ.
- Phân loại8 nhóm bằng metadata area, giữ6 category của schema006 hiện hữu. Không migration, không chạy lại006. Giao diện phân biệt trực tiếp/diễn giải/suy luận, căn cứ hội thoại/khảo sát, nội dung thay đổi và dữ kiện còn thiếu.
- Xác nhận kiểm lại proposal còn hiệu lực trong transaction, khóa cùng thứ tự với Guest claim/recovery, chống mục lặp khác proposal/session. Đính chính mục đã xác nhận yêu cầu Chỉnh sửa/Xóa bằng hành động riêng có version; không tự ghi đè hoặc thêm mục mâu thuẫn.
- Giữ feature flag/QA allowlist cho lưu hồ sơ chính thức. Phân tích/đề xuất trong phiên dùng chung Guest/member/QA; không coi việc mở nghề là sở thích hoặc đồng ý lưu. Không nạp confirmed profile khi OFF.
- PUT exploration xác minh UID/owner, Origin, rate limit chung PostgreSQL, catalog ID; chỉ cập nhật metadata hiện tại +12 nghề đã xem. Không tạo session, không sửa khảo sát, không gọi model, không trừ quota. Frontend chuyển hint theo tab vào phiên đã xác minh khi quay lại, kể cả Back/Forward; model/search nhận đúng nghề vừa khám phá, không suy phù hợp.
- Bản nháp chỉnh sửa đề xuất/hồ sơ lưu trong sessionStorage theo UID và TTL2h, giới hạn120 mục; chuyển sau claim được server xác nhận. Không lưu token, không dùng storage làm bằng chứng quyền.

### Bằng chứng local cập nhật
113 phương thức Python duy nhất trong các nhóm navigation/profile/shared-protection/Task4.2 Search/Task4.1 jobs-context và Task4.4 PASS (có một số nhóm được chạy lại sau sửa đúng phạm vi). 7 ca Task4.4 mới bao gồm3 provider, persistence/retry/đính chính/owner403-404/Origin/quota; 28 profile+Task44 vừa chạy lại PASS sau thay đổi khóa. Chrome browser_task41 PASS6 nhóm, gồm auto analysis, edit/accept/reject, draft, retry và login claim fixture. Chrome journey PASS các trang thật+PG local,1tab; có PUT metadata exploration được phép, không có create/chat/analysis do điều hướng. Chưa gộp test fixture thành chứng cứ LIVE.

Chưa deploy Task4.4, Production giữ nguyênTask4.3. Tiếp theo Preview staging riêng, LIVE member/QA và Guest trong hạn mức hợp lệ; Google popup thật cần thao tác người dùng. Nếu chưa đủ điều kiện thì không deploy Production.


### Previewa02d201: lỗi LIVE đã tìm được, chưa phát hành
Previewdpl_6Vh91KbV4bj92VLzpDt447uXBdYB tại https://quocan4-eoa5yemme-khkt3.vercel.app/ai-career-advisor buildREADY, stagingrole/schema chỉ đọcPASS; Firebase đã thêm đúnghostnamePreview, giữ các domain cũ. InitialsurveyanalysisMemberLIVEcompleted nhưng3lời chia sẻ thật không sinh profile_updates. Không đánh dấuPASS hoặc deployProduction. Hướng dẫn cũ nói bộ nén xử lý hồ sơ, toolauto chỉ dùng khi cần nút nên model có thể trả plaintext mà bỏ đề xuất. Bản sửa chuyển sang một terminalfunction bắt buộc cho cùng completion, profile_updates bắt buộc là mảng (có thể rỗng), intentreply cho trao đổi không cần dữ kiện/nút; không thêmmodelcall. 23test liên quanPASS sau sửa. Đối chiếu tool_choice chỉ định hàm theo tài liệu chính thức DeepSeek https://api-docs.deepseek.com/api/create-chat-completion/ .
Người dùng đã xác nhận trênPreviewa02d201: giữ đúng hội thoại/khảo sát/cùngtab sau luồng đã hỏi gồm đăng nhập Google. Đây là bằng chứng người dùng, không là popup tự động; bản sửa tiếp theo chỉ backendprompt/tool, không đổi logic đăng nhập.


### Preview7da1499 — LIVE đã sinh đề xuất, phát hiện thêm lỗi đối soát đính chính
MemberLIVE tạo2 sở thích/môi trường,2 môn học/trải nghiệm,1 phủ định; excerpt đúng. Model dùng add thay vì correct nên cả hai mong muốn trái nhau còn trong đề xuất. Dừng phát hành. Sửa schema bắt buộc operation/replaces và prompt đối soát; thêm hàng rào hẹp: cùng chính xác nội dung, đối cực phủ định, và lời người dùng có phủ định nguyên văn thì cập nhật bản đề xuất bằng quan hệ correct. Không áp dụng tên nghề hay xóa/sửa hồ sơ đã xác nhận. Thêm regression ngoài trời,17 test thuộc nhóm mới+context PASS. Giữ area khi nạp confirmed context để không diễn giải môn học/trải nghiệm thành kỹ năng muốn rèn.
Kiểm tra chỉ đọc Guest staging cũ: có bản ghi, đã hết hạn TTL tự nhiên, chưa claim;401 hiện tại không phải quota được cấp lại. Không reset/xóa bản ghi đó.

Bổ sung kiểm thử thứ tự commit: kết quả phân tích khảo sát về chậm không được làm sống lại mong muốn đã bị phủ nhận trong chat. Áp dụng cùng hàng rào đối cực khi hợp nhất ở đường đọc, không sửa lịch sử.9testTask44PASS; không có schema mới.


### Đối chiếu ngữ cảnh nghề trên LIVE
Member trả đúng nghề vừa xem; QA một lần trả nghề trong lời AI cũ dù metadata server đã cập nhật đúng. Sửa ưu tiên system ngữ cảnh ngay trước câu hỏi; kiểm tra nút deictic theo ID hiện tại, sai thì thử lại một lần trước khi lưu. Không ép nghề hiện tại khi câu mới so sánh/gợi ý nghề khác hoặc đổi chủ đề; không viết đáp án mẫu. Test PG chứng minh retry2 provider nhưng1 lượt Guest và chỉ lưu nút đúng PASS. Gộp10testTask44 +5testTask42 pipelinePASS. Giữ116 phương thức local đã chạy theo nhóm, không chạy lại toàn bộSuperBoard.

Một mục git.deploymentEnabled=false riêng cho nhánhTask44 nhằm tránh GitHub push tự tạo Preview thiếu bindingDATABASE_URL; các nhánh/Production Branch khác giữ nguyên. CLI Preview vẫn dùng staging override được xác minh; CLI Production khi đủ điều kiện kế thừa môi trườngProduction. Theo https://vercel.com/docs/project-configuration/git-configuration .


### Preview3608c17 — kiểm thử dịch vụ thật
Member/QA giữ đề xuất bổ sung/đính chính có căn cứ và QA xác nhận/đọc lại/bỏ qua/chống trùngPASS; cả hai đã trả đúng nghề cuối cùng sau3lần đổi bằngmetadata riêng. QA DDGS+DeepSeek4nguồn thậtPASS. User xác nhận luồng Google/cùngtab trên a02d201, logic auth không thay đổi sau đó.
Guest cũ đã hết TTL tự nhiên theo SELECT chỉ đọc, chưa claim. Một lần POST luồng mở phiên chuẩn được server chấp nhận, vẫn8câu/rate limit gốc; không sửa quota cũ, không đổiIP hoặc tạo liên tục danh tính. Guest mới nhận phân tích ban đầu và2lần bổ sungLIVE đúng, nhưng đính chính bị bộ căn cứ từ chối; runtime log chỉ ghi supplied1/accepted0, không ghi lời người dùng hay token. Chưa phát hànhProduction.
Hàng rào căn cứ được mở đúng cho khác biệt chữ hoa/spacing, rồi lưu lại nguyên đoạn thực tế của người dùng; không bỏ từ, bỏ dấu câu hay chấp nhận diễn đạt lại. Thêm regression quote giữa câu và quote bị lược từ.11testTask44PASS. Sẽ kiểm lại trên cùng phiênGuest còn5/8, không cấp lại quota.
