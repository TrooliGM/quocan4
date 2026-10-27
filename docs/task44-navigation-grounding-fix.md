# Task 4.4 — đối soát nghề trong nút điều hướng

## Phạm vi và bằng chứng ban đầu

Nhánh `hotfix/task44-navigation-grounding`, worktree riêng `task44-navigation-fix`, nền `7f45edd` (code giống Production `da6d146`). Không sửa checkout chính hoặc Production. Chỉ Preview; cần người dùng phê duyệt riêng để phát hành Production.

Chưa có toàn bộ hội thoại gốc của tình huống người dùng phản ánh, nên không kết luận hai nghề trong ảnh chắc chắn sai. Đã tái hiện **lỗ hổng kiểm định** bằng hội thoại tổng hợp: câu hỏi bảo tồn động vật và câu trả lời nói kiểm lâm/bảo tồn, nhưng metadata chứa hai nghề cứu hộ khác; backend cũ vẫn nhận cả hai nút. Đổi chủ đề sang lập trình, giữ basis từ câu hỏi cũ, backend cũ vẫn nhận hai nút. Đây không phải truy cập hoặc khôi phục hội thoại riêng của người dùng.

## Nguyên nhân và bản sửa

- `advisor/navigation.py` trước đây xác minh catalog/kind/URL và basis ở bất kỳ lời học sinh gần đây. Nó không chứng minh nghề đó đúng ý định hiện tại hay đúng phần tư vấn; tên/ID hợp lệ vẫn có thể sai ngữ cảnh. Nay basis phải thuộc lời nhắn hiện tại. Lịch sử vẫn dùng để hiểu câu nối tiếp trong bước kiểm định ngữ nghĩa.
- `advisor/navigation_review.py` mới: chỉ khi có nút ứng viên đã canonical, gọi DeepSeek một lần để kiểm định riêng **ngữ nghĩa** của yêu cầu hiện tại, tối đa8 tin gần, ngữ cảnh nghề thuộc phiên và câu trả lời. Phân biệt yêu cầu cụ thể, so sánh, đề xuất có liên hệ, thư viện, phủ định/ví dụ/đổi chủ đề/không cần nút. Không chọn nghề thay thế, không Search, không đọc hồ sơ riêng, không ghi dữ liệu. Chỉ có thể trả tập con của nút server đã dựng; kiểm lại index, trích dẫn thật từ câu hiện tại và câu trả lời, tên nghề catalog. Tìm tên chỉ là kiểm tra bổ sung, không thay kiểm định ngữ nghĩa.
- `advisor/graph.py` giữ bounded retry một lần. Metadata sai ở lượt cuối không còn gây502: giữ câu trả lời/đề xuất hồ sơ và bỏ nút không xác minh. Kiểm định timeout/JSON lỗi thì bỏ nút ngay, không tự gọi lại vô hạn. Lỗi câu trả lời chính rỗng/cắt dở hoặc lỗi dịch vụ chính vẫn xử lý như cũ, không biến thành PASS giả.
- Prompt đồng bộ nội dung tư vấn và metadata, ưu tiên câu hiện tại; không gắn nghề cùng nhóm rộng hoặc lấy nghề từng nhắc làm mục tiêu mới. Không hardcode nghề trả lời/đường dẫn theo các ví dụ thử.
- Không thay frontend, catalog200, Firebase, quyền hồ sơ, Neon/schema, quota8 hoặc hành trình cùngtab. Câu trả lời không có nút không thêm lượt model. Câu có nút thêm tối đa một kiểm định mỗi attempt: timeoutHTTP8s, trần9s, tối đa4nút/1200token; vẫn trong timeout tổng hiện hữu. Nếu cần retry thì tối đa2main+2review cho **một** request/quota, lưu atomic như cũ. Có thêm chi phí/độ trễ cho câu có nút; cần theo dõi trênLIVE. Đây là bản vá kiểm định metadata, không viết lại pipeline AI.

## Kiểm thử đã chạy thực tế

- **58 test Python PASS, 0 SKIP**: 14 kiểm thử mới, 11 navigation,13 Task44,15shared-protection,5Task42pipeline. PostgreSQL local cluster/schema riêng; mock DeepSeek, không dùng Neon. Ban đầu3classPG SKIP vì thiếu đường dẫn binary ở worktree mới; đã đặt đúng bộ local và chạy đủ, không gộp SKIP vào PASS.
- Kiểm thử mới gồm đúng căn cứ/careerID, đổi chủ đề/phủ định có tên nghề, quote giả, index trùng/thiếu/ngoài phạm vi, timeout/truncation, không có nút thì không gọi review, thư viện không thay nghề, metadata sai hai lần vẫn200, đề xuất hồ sơ giữ nguyên, quota chỉ1, replay miễn phí,6tổ hợp ba provider và hai kiểu lưu. Mock không chứng minh model hiểu nghĩa trênLIVE.
- Chrome static navigation: XSS/openredirect, same-tab/tabcount/draft, zeroAIrequests, responsive PASS. Chrome FastAPI+PG thật local: survey/draft/originalID,3nghề,story/scene,BackForward,1→1tab, khôngchat/create/analysis do điều hướng PASS. Google là fixture local; không phải popup thật.
- JSON mode theo tài liệu chính thức DeepSeek: https://api-docs.deepseek.com/guides/json_mode/ . Review sai/cắt dở không được tin cậy.

## Chưa hoàn thành ở checkpoint này

Chưa build hoặc kiểm DeepSeek LIVE Preview của bản vá này. Chưa phát hành Production, chưa push nhánh. Sẽ bổ sung kết quả thực tế sau Preview; giữ nguyên Production `da6d146`/`dpl_9TdB69NsBqWmKssEUQbNhG92jsVS`.

Không tự sửa metadata đã lưu trong hội thoại cũ hoặc gọi AI khi mở lịch sử; bản vá áp dụng cho phản hồi mới. Kiểm định LLM là hàng rào giảm rủi ro, không chứng minh đúng mọi tình huống ngôn ngữ. Nếu không có căn cứ hoặc dịch vụ kiểm định lỗi, ưu tiên không hiện nút.

## Nghiệm thu Preview thực tế — 27/10/2026

Các trạng thái chờ ở checkpoint phía trên được cập nhật bằng bằng chứng sau đây; không suy kết quả LIVE từ mock.

- **Build PASS / READY**, source `3f77005899ce1c728b0a61b2f5cb685896bca29b`, deployment `dpl_33DRW8yLeySY1zSTb4QA7ns7VQfj`. URL: https://quocan4-5lwowvr7w-khkt3.vercel.app/ai-career-advisor . CLI Preview dùng project quocan4, database staging `br-morning-tooth-aznv081q`/neondb và role riêng hiện có, không lấy DATABASE_URL Production. Truy vấn staging READ ONLY xác minh đúng database/role và hai cột TEXT PASS; không migration. Manifest105file đã kiểm loại trừ dotenv/artifacts/secrets.
- **11 ca chat DeepSeek LIVE PASS**: Member7ca (lính cứu hỏa; bảo tồn; so sánh hai nghề; bác sĩ; đổi sang lập trình và phủ định bác sĩ; nghề không có; câu hỏi hệ sinh thái), QA2ca (phủ định/ví dụ hai nghề cũ rồi chọn bảo tồn; không dấu/viết tắt), Guest2ca (nghề cụ thể; bảo tồn). Đây là mẫu kiểm thử, không phải mọi nghề/hội thoại. Không có502 trong11ca này.
- Kết quả cụ thể: bảo tồn dẫn đúng `chuyen-vien-bao-ton-da-dang-sinh-hoc`, không phải hai nghề cứu hộ. So sánh dẫn đúng `linh-cuu-hoa` và `nhan-vien-cap-cuu-ngoai-vien`. Đổi chủ đề dẫn `lap-trinh`, không `bac-si` dù tên bác sĩ xuất hiện trong câu phủ định. Nghề không có và hỏi khái niệm không tạo nút. Nhãn/URL của mọi nút được đối chiếu canonical catalog ở backend và harness.
- Mỗi case được replay cùng request_id, trả duplicate và không đổi quota; không gọi lại model để tạo PASS. Độ trễ tổng HTTP11ca:4,10–13,03s, trung vị6,61s (bao gồm mạng/model/kiểm định, không phải đo riêng reviewer hoặc so sánh before/after). Không tuyên bố hiệu năng dưới200ms cho API AI.
- Guest dùng cookie/định danh staging đã có: **6/8→8/8** đúng hai câu, không cấp Guest mới/reset/đổiIP. Câu thứ9 bị429, quota vẫn8/8. Chỉ tạo session hội thoại thử mới thuộc cùng danh tính vì session tạm QA cũ trả404; đây là bước dựng dữ liệu thử qua API chuẩn, không phải fallback của luồng điều hướng ứng dụng, không cấp lại quota. Member dùng session lưu lâu dài, QA/Guest session tạm; không sửa dữ liệu học sinh.
- **Chrome Preview Guest/Member/QA PASS**, Member/QA dùng FirebaseSDK thật với tài khoản thử được cấp phép. Kiểm chat→hồ sơ→chat; chat→truyện→hồ sơ→chat; hỏi theo cảnh;3nghề;Back/Forward;reload. CùngID/khảo sát/draft, desktop1440/mobile390, tab1→1, khôngchat/create/analysis do điều hướng. Quota Guest trước/sauBrowser8/8 không đổi. Ảnh `artifacts/navigation-preview-*.png`, báo cáo/mẫu hội thoại riêng được mã hóa hoặc để trongartifacts ngoàiGit.
- **Security Preview PASS**: token401, owner404 (cảGET vàPUTexploration), Origin403, privatepaths404, quota429. Unit/PGlocal còn kiểm retry, atomic save và hai API AI cũ. Không thay UI, catalog, quyền lưu hồ sơ, Firebase domains, schema, secrets hoặc dịch vụ Production. DDGS giữ cấu hình bật mọi role, regression Task42PASS; không chạy lại SearchLIVE không liên quan đến thay đổi.

### Giới hạn và việc cần xử lý riêng

1. **Phân tích khảo sát LIVE: FAIL một lần** ở session Member dựng thử: POSTanalysis trảfailed, trạng thái lưu có `error_code=ValidationError`. Không tự retry/cấp thêm budget, không đánh dấuPASS. `advisor/survey_analysis.py` và `advisor/analysis_jobs.py` không đổi, bộ phân tích dùng prompt riêng, không dùng prompt điều hướng mới; chưa xác minh nguyên nhân dữ liệu model không đạt schema. QA/Guest testsetup chỉ đọc trạng thái pending, không coi là nghiệm thu phân tích. Các bảo toàn đề xuất/confirmed-profile được kiểm bằng mock+PGlocalscope58tests, không suy thành PASS phân tích LIVE mới. Lỗi này cần xử lý/nghiệm thu riêng trước tuyên bố Task4 tổng thể hoàn thành.
2. Googlepopup **chưa kiểm lại** trên hostname Preview này; FirebaseSDK password thật đã kiểm, fixtureGoogle local không thay popup. Không tự thay Firebase authorized domains trong bản vá.
3. Metadata cố tình sai/timeout được fault-injection bằng mock/local; không ép modelLIVE sinh lỗi để nhận định đã kiểm đúng toàn bộ lỗi sản phẩm. Hội thoại gốc người dùng chưa có, chỉ chứng minh lỗ hổng và các mẫu regression được cung cấp.
4. Thêm lượt kiểm định có chi phí/độ trễ với câu có nút và có thể bỏ nút đúng khi model không chắc hoặc dịch vụ lỗi. Không làm giả câu trả lời/nút dự phòng, không giảm bảo mật để tăng tỷ lệ nút.

**Kết luận:** bản vá điều hướng đạt kiểm thử trọng tâm và sẵn sàng để người dùng duyệt trên Preview. **Chưa phê duyệt phát hành Production, không tuyên bố Task4 tổng thể hoàn thành.** Production được đối chiếu vẫn `da6d146` / `dpl_9TdB69NsBqWmKssEUQbNhG92jsVS`; không push, merge hoặc deploy Production. Nếu được duyệt sau, rollback bằng deployment hiện hành, không restore/reset database. Nhánh hotfix có thể quay về nền7f45edd; không xóa dữ liệu test hay lịch sử/quota để rollback.
