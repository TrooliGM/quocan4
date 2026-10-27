# Task4 hotfix cá nhân hóa — nghiệm thu 25/10/2026

## Kết quả phát hành

Production https://labanhuongnghiep.vercel.app/ai-career-advisor đang chạy `957ffde390f70acbcd63045bc21bf7f3459b5ca6`, deployment `dpl_BwthFvvNpNDscwEuKPC744bVe38z` READY. Nhánh `hotfix/task4-profile-context`, worktree task4-profile-hotfix, tạo từ Production thực fde7ed2. Kế thừa checkpoint tài liệu36a5b8e. Không merge main/force push. Production Branch vẫn main; phát hành candidate --prod --skip-domain, kiểm thử rồi promote. Runtime không lấy commit tài liệu sau đó làm source.

Chỉ canary3 UID đã xác minh: hai tài khoản email/password QA riêng và tài khoản Google QA do người dùng chỉ định. Không ghi UID/email/password/token vào Git. Tài khoản khác và Guest vẫn stable graph/prompt/UI df1c300. Chưa mở Task4 đại trà.

## Nguyên nhân và bằng chứng ID23

Không mất hồ sơ ở Neon, không lấy sai UID và không mất cờ bật. Reproduction API → PGlocal → LangGraph thu exact provider payload cho thấy flagtrue đã lưu và có mục confirmed. Hợp đồng context cũ không phân biệt rõ profile trích xuất phiên (có thể rỗng) với confirmed_profile: đặt chung JSON dài sau danh mục nghề, rồi lịch sử những câu AI nói chưa nhận hồ sơ. Thiếu trạng thái hồ sơ hiện tại rõ ràng và thiếu ưu tiên dữ liệu mới trước câu hỏi.

Đối chứng DeepSeek LIVE cùng tài khoản, cùng conversation, cùng hồ sơ có nonce mới không xuất hiện trong câu hỏi/lịch sử trước đó, cùng model và cùng database: bản fde7ed2 API đọc đúng giá trị/flagtrue nhưng trả không có hồ sơ; candidate957ffde đọc lại đúng nonce. Before3.65s / after3.93s ở mẫu này (không phải benchmark/không cam kết latency). Cùng dữ liệu nhưng đổi cách trình bày context đã sửa lỗi sử dụng hồ sơ. Không khẳng định biết cơ chế suy luận nội bộ của model hoặc rằng bản cũ sai ở mọi lượt.

## Thay đổi tối thiểu

- advisor/confirmed_profile.py: context_items SELECT chỉ category/value của owner đã xác thực, metadata.status=confirmed và TTL còn hiệu lực. Không cache, không DELETE trong đường đọc AI.
- advisor/graph.py: OFF không gọi loader; đo profile_context_load không chứa giá trị/UID; đổi tên ghi chú phiên thành conversation_notes; tách hồ sơ khỏi JSON nghề/survey.
- advisor/profile_context.py: khối enabled/status/items ngắn ngay trước câu hỏi hiện tại, dữ liệu không phải chỉ thị. OFF phòng thủ bỏ cả state đã nạp. Chính sách dùng có chọn lọc, không gán năng lực, ưu tiên đính chính mới, không chèn hồ sơ vào câu hỏi không liên quan.
- tests/test_task4_personalization.py:8 ca API+PG+LangGraph thu exact payload. test_advisor30_profile.py sửa mock đúng loader mới; browser_advisor30_fixture.py cập nhật collector context.
- Tài liệu/bộ nhớ cập nhật bằng chứng, giữ lại checkpoint lịch sử.

Không sửa frontend, dữ liệu200 nghề/Truyện nghề, auth security, quota/rate hoặc schema. Không chạy lại migration006 hay bất cứ migration Production nào. OFF không xóa/viết lại thông tin đã có trong lịch sử; kiểm chứng không tự nạp profile bằng phiên mới không có dữ kiện cá nhân.

## Kiểm thử có thể tái lập

**26 test local duy nhất PASS**:17 regression profile/claim/rate +8 mới +1 runtime bundle. Batch24 đầu là17+7; batch8 sau gồm7 trùng+1 mới, không cộng thành32. Lệnh bundle ban đầu sai tên class/thiếu biến PG bị ERROR/SKIP; đã sửa lệnh và chạy đúng ReleaseRuntimeTests.test_runtime_without_public_folder_or_dotenv PASS, không tính lượt chưa thực thi là PASS.

8 ca mới: exact ON payload đúng3 chiều công nghệ/giải quyết vấn đề/giao tiếp; OFF phiên mới không query/không gửi giá trị; sửa mục được nạp lại lượt kế; hai owner tách biệt; proposal chưa xác nhận/từ chối và row metadata.pending không lọt khối confirmed; logoutGuest không đọc owner cũ; OFF loại stale state; dữ liệu không thành chỉ thị. Provider và Firebase trong nhóm local là fixture, PostgreSQL local thật; không gọi đó là LIVE.

LIVE trên candidate dùng Production env, chỉ dữ liệu hai QA riêng:

- Phân tích khảo sát thật, xác nhận đúng3 chiều; trước xác nhận0 mục, không tự lưu.
- OFF trong phiên mới với khảo sát chưa rõ: không profile_context_load, không biết nonce hồ sơ. ON: có lượt SELECT, gợi hoạt động gắn công nghệ/giải quyết vấn đề/giao tiếp, không kết luận chắc chắn phù hợp CNTT.
- Hai Firebase ID token thật, hai hồ sơ có nonce khác nhau: mỗi phản hồi chỉ có nonce của owner đúng. API truy cập chéo404, thiếu identity/giả UID401.
- Sửa sang nonce mới chưa từng có trong hội thoại: lượt tiếp trả giá trị mới, không lặp bản cũ.
- Khi ON hỏi2+2: trả đúng `4`, không chèn thông tin cá nhân. Đính chính không còn quan tâm công nghệ, muốn sinh học: AI đề nghị quan sát cây5 ngày an toàn, không tự sửa hồ sơ đã xác nhận.
- Khảo sát mơ hồ: structured analysis_status=unavailable; phần chat vẫn gợi trải nghiệm và hỏi mục tiêu. Không đóng ID13/không coi clarification JSON đã PASS.
- Chrome headless thật bằng Firebase SDK email/password, không mock auth/model: UI công tắc khớp API, chuyển sang cuộc trò chuyện mới mặc địnhOFF, quay lại phiên cũ giữ cờ, desktop/mobile/profile/history và logout về stable Guest PASS. Không coi đây là Google popup.

Candidate cuối chỉ khác candidate đã LIVE ở allowlist thêm đúng Google QA; cùng source957ffde. Build READY,98 file runtime, helper mới và stable fallback có trong manifest, không env/artifacts/tests/docs/secret files. Không chạy Super Board toàn diện.

Sau promote, domain chính thức đã có lượt DeepSeek ON/OFF với nonce mới, trả tương ứng có/không có giá trị; profile value và flag QA được khôi phục về trước test. Hậu kiểm Guest cũ lần đầu404 vì đã xác minh expires_at hết hạn, không phải regression. Tạo phiên chat mới của CÙNG Guest đã dùng8 (không cấp identity mới/không resetquota), hoàn tất survey hợp lệ rồi gửi lượt9:429, used_questions trước/sau vẫn8; Task4 shell404. Không gọi AI lại trong bước sửa fixture Guest hết hạn.

## Google và Brave

Đã dùng đúng tài khoản Firebase CLI để đọc UID/providerGoogle, domain được phép; lần đầu token account mặc định thiếu quyền, chọn đúng account đã giải quyết. Không sửa Firebase project. Công cụ duyệt tự động từ chối mở Chrome QA tương tác; popup do người dùng tự thao tác.

Người dùng xác nhận popup Google trên domain chính thức thành công, quay lại hội thoại, giữ khảo sát và thấy header mới. Đây là bằng chứng USER-CONFIRMED, không phải machine capture. **Đối chiếu Neon chỉ thấy phiên QA gần đây career_discovery, chưa thấy career_exploration/thiet-ke tương ứng**, nên chưa chứng nhận giữ mode/career_id. Đã hỏi người dùng đối chiếu riêng; người dùng trả lời chưa xác định được. Giữ gate một phần, không kết luận nguyên nhân do login khi chưa có before/after. ID42 giữ BLOCKED một phần; không bỏ qua khác biệt bằng chứng.

Brave Production thiếu cả SEARCH_PROVIDER và SEARCH_API_KEY. Muốn bật: cấu hình SEARCH_PROVIDER=brave và SEARCH_API_KEY qua Vercel env an toàn; không dán key vào chat, không giả nguồn. Giữ Search LIVE BLOCKED.

## Bảng53 yêu cầu và điều kiện trước mở rộng

**43 PASS /10 BLOCKED /0 FAIL**. ID23 chuyển FAIL→PASS theo exact-payload tests, đối chứng nonce LIVE và kiểm trên domain chính thức. ID6/7/8/30/31/32 được cập nhật theo các mẫu LIVE đã đọc; không phải chứng nhận mọi câu trả lời/tư vấn chuyên môn. Không tự chuyển các mục còn lại.

| Nhóm chính | ID còn BLOCKED | Thiếu gì |
| --- | --- | --- |
| Cấu hình/quyền |1–5| Brave key/provider được cấp phép, truy vấn theo năm và nguồn thật |
| Có thể kiểm chứng thêm bằng QA |10| Trường hợp mâu thuẫn giữa các câu và đánh giá chất lượng mở rộng; chưa chạy |
| Cần chẩn đoán bounded + chất lượng |13| Structured analysis khảo sát mơ hồ chưa thành công; không kết luận do timeout/validator khi chưa có bằng chứng |
| Điều kiện an toàn |22| Canary hiện khóa Guest-profile Task4; cần môi trường/phiên QA Guest được phê duyệt để nghiệm thu TTL/claim, không nới auth/rate |
| Trình duyệt thực và đối chiếu metadata |42| Popup được user xác nhận, nhưng mode/career_id chưa khớp bằng chứng Neon |
| Nghiệm thu tổng hợp còn thiếu |52| Các điều kiện Search/Guest-profile/mode/khảo sát mơ hồ nêu trên |

Các mục đã PASS local/LIVE trước được kế thừa; không dùng kết quả trùng hoặc model giả để tăng số PASS.

## Rollback và bảo toàn

Rollback trực tiếp về `dpl_7ZaE94zBvSeBAps9HgTPkak9Q1aT` / fde7ed2 nếu hotfix gây lỗi nghiêm trọng: `vercel rollback dpl_7ZaE94zBvSeBAps9HgTPkak9Q1aT --scope khkt3 --yes`; kiểm lại alias/domain. Giữ bảng006 và mọi dữ liệu, không DROP/reset/restore đè. Backup Neon backup-before-task4-20261025-014632 READY được kiểm lại qua API, project/parent đúng; đã có readback/fingerprint ở đợt trước. Đợt này hậu kiểm schema/quota bằng read-only, không migration. Chưa cần dùng rollback.

Chỉ ghi dữ liệu thử vào hai QA riêng; không đụng hồ sơ/hội thoại của học sinh. Với Google QA chỉ đọc metadata mode/career, không in nội dung trả lời khảo sát. Không ghi email/UID/token trong tài liệu. Artifacts nhạy cảm dùng Windows DPAPI, không Git.

Bằng chứng local loại khỏi Git: profile-hotfix-ab.json; profile-hotfix-live-cases.json; profile-hotfix-browser-candidate.json; profile-hotfix-promotion.json; profile-hotfix-official.json; profile-hotfix-google.json. Payload/nonce/raw answer QA mã hóa DPAPI. **Hotfix cá nhân hóa đã hoạt động trên Production QA-only; NOT READY FOR GENERAL RELEASE.**
