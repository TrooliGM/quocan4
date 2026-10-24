# AI Chat 2.1 và 200 hồ sơ nghề chuyên sâu — 24/10/2026

## Nền phát triển và phạm vi

Đã đọc alias/deployment Vercel lúc bắt đầu: labanhuongnghiep.vercel.app trỏ tới deployment `dpl_6KpjeYiZ7wseuyo7ussQ7eA2ZQbM`, READY, source `d5f10cc1ce093442acf4674ba5cd151727a619a2`, ref integrate/task-12-production. Khác trạng thái7c07d33 trong báo cáo cũ; không lấy main hoặc e86da48 làm nền theo suy đoán. Tạo nhánh `feat/ai-chat-2-1` và worktree `D:/khkt/.claude/worktrees/ai-chat-21` từ đúng d5f10cc. Không sửa checkout/worktree đang có thay đổi dở.

Người dùng cho phép phát triển và commit riêng, chưa cho merge/deploy Production. Áp dụng frontend-design để bảo toàn giao diện; không đổi Hero/Navbar, màu, bố cục chat, khảo sát5 bước, 200ID nghề, 12 nhóm hoặc hai liên kết nghề. Chỉ thêm disclosure native cho nội dung modal dài. Không Task3, không chạy Super Board, không gọi/migrate/ghi database Production, không thay secrets.

## Các thay đổi

1. Mỗi câu khảo sát có6 gợi ý tự nhiên, gồm lựa chọn chưa xác định. Chip chỉ nối nội dung vào textarea, không chọn trước/gửi tự động; vẫn sửa/xóa/kết hợp/quay lại được. Giữ câu hỏi, anh–em/chị–em, giới hạn400 ký tự và lưu server theo session.
2. Câu mở đầu career_exploration tạo từ nhiệm vụ chi tiết của đúng nghề và góc tìm hiểu học sinh nêu ở câu5. Nhân sự dùng hồ sơ/đào tạo; lập trình dùng chia yêu cầu/đọc log; bác sĩ dùng khai thác triệu chứng/hội chẩn. Không gọi AI khi mở modal hoặc tạo nháp; nháp không tự gửi, chỉnh sửa hoặc xóa trắng được giữ khi reload. Chặn phản hồi dữ liệu nghề cũ ghi vào session mới bằng epoch+sessionID.
3. Luồng đăng nhập lưu đường quay lại theo allowlist nội bộ. Từ chat trở về chat, từ trang chủ trở về trang chủ; không chấp nhận open redirect hoặc endpoint API. Không đưa token/khảo sát lên query string.
4. Draft lưu sessionStorage theo chủ phiên/session trong cùng tab, TTL2h; không localStorage. Chỉ chứa bước khảo sát, câu trả lời, cách xưng hô và nháp câu hỏi, không auth proof. Storage bị chặn thì thao tác hiện tại vẫn chạy nhưng không bảo đảm phục hồi sau reload/đổi trang. Backend luôn kiểm ownership trước khi phục hồi UI.
5. Claim Guest dùng cookie xác minh server hoặc bằng chứng Firebase Anonymous sẵn có. Chỉ chuyển pointer/draft sau server xác nhận; retry có ràng buộc tài khoản. Khi phản hồi COMMIT bị mất và cookie đã vô hiệu, chỉ phục hồi draft nếu GET session bằng token tài khoản đích được backend chấp nhận. Không tin UID từ storage để cấp quyền, không reset quota, không tạo lại session. Token khách không ghi storage; Anonymous proof cũ chỉ ở RAM nên mất RAM không được tự coi là có bằng chứng để claim.
6. Tiêu đề suy ra từ mode, career_id và chủ đề thực; không từ câu trả lời khảo sát/bootstrap. Metadata title_source/manually_renamed dùng JSON messages hiện có, không migration. Rename PostgreSQL khóa hàng và cập nhật metadata trên messages mới nhất, tránh mất lượt chat đồng thời. Không backfill tên hội thoại cũ; kể cả tên do học sinh đặt lại bằng tên mặc định cũng được giữ.
7. AI nhận khảo sát của đúng session như cơ chế có sẵn; bổ sung yêu cầu chọn ví dụ dựa trên lời tự chia sẻ, không suy diễn hoặc kết luận chắc chắn. Exploration vẫn tập trung đúng nghề. Projection tham chiếu AI loại phần nguồn/lộ trình dài khỏi từng lượt để giảm context không cần thiết.

## Biên tập dữ liệu: 4 đợt × 50

| Đợt | Phạm vi | Kết quả |
|---|---|---|
|1|careers-1.json: công nghệ, y tế, phần đầu giáo dục|50/50 cập nhật|
|2|careers-2.json: giáo dục, kỹ thuật, kinh doanh, tài chính|50/50 cập nhật|
|3|careers-3.json: tài chính, sáng tạo, truyền thông, tư pháp|50/50 cập nhật|
|4|careers-4.json: công vụ, môi trường, dịch vụ, khoa học|50/50 cập nhật|

Mỗi hồ sơ có giới thiệu vai trò, 5 nhiệm vụ, ít nhất3 thử thách, môi trường cụ thể,3 nhịp công việc minh họa, giải thích kỹ năng và3 bước tìm hiểu cho THCS/THPT. Nhiệm vụ/môi trường/giới thiệu khác nhau ở200 nghề. Các nguyên tắc an toàn, gợi ý môn học và lưu ý nghề có thể giống nhau khi cùng lĩnh vực; không tuyên bố từng câu toàn bộ dữ liệu là độc nhất. Giữ ID/tên/nhóm/thứ tự bằng4 fingerprint từ Production baseline, không cần Git history trong test sau khi clone nông.

Lịch ngày làm việc là minh họa thay đổi theo vị trí/môi trường, không phải lịch chuẩn bắt buộc. Học tập và trải nghiệm không tạo quyền hành nghề. Không đưa lương, điểm tuyển sinh hoặc hứa phù hợp nghề.

### Đối chiếu chuyên môn mẫu và giới hạn

- **Kiểm sát viên:** làm rõ công tố/kiểm sát tư pháp, chứng cứ buộc và gỡ tội, không thay thẩm phán quyết định hình phạt. Đối chiếu [Luật tổ chức VKSND hợp nhất](https://vanban.chinhphu.vn/?classid=2629&docid=215229&pageid=27160) và [VKSNDTC về căn cứ truy tố](https://vksndtc.gov.vn/tintuc/Pages/lists.aspx?ItemID=119). PDF hợp nhất từng timeout qua công cụ, giữ link trang thông tin chính thức thay cho báo đã tải PDF thành công.
- **Y tế:** phân biệt bác sĩ/điều dưỡng/kỹ thuật y, dinh dưỡng hoặc tâm lý lâm sàng với vai trò hỗ trợ ngoài lâm sàng; không đồng nhất mọi người tư vấn dinh dưỡng với chức danh có giấy phép. Nguồn [Luật khám chữa bệnh](https://chinhphu.vn/?classid=1&docid=207396&orggroupid=1&pageid=27160), [quy định chi tiết cấp phép](https://xaydungchinhsach.chinhphu.vn/toan-van-nghi-dinh-quy-dinh-chi-tiet-mot-so-dieu-cua-luat-kham-benh-chua-benh-119240115115947657.htm), [đối chiếu hoạt động trị liệu](https://www.bls.gov/ooh/healthcare/occupational-therapists.htm).
- **Nhân sự:** bổ sung quan hệ lao động, hồ sơ, đào tạo, khác với tuyển dụng thuần túy. [Nguồn BLS](https://www.bls.gov/ooh/business-and-financial/human-resources-specialists.htm).
- **Phần mềm:** phân tích yêu cầu, sửa lỗi và bảo trì; [nguồn BLS](https://www.bls.gov/ooh/computer-and-information-technology/software-developers.htm).
- **Thiết kế đồ họa và môi trường:** rà khác biệt truyền đạt hình ảnh với công nghệ xử lý ô nhiễm. [Thiết kế](https://www.bls.gov/ooh/arts-and-design/graphic-designers.htm), [môi trường](https://www.bls.gov/ooh/architecture-and-engineering/environmental-engineers.htm).
- Giấy phép/thẻ/bổ nhiệm ở một số vai trò đã có nguồn Chính phủ/Cổng dịch vụ công/Cục Hàng không ngay trong hồ sơ. Những vị trí chưa đối chiếu đầy đủ ghi `verify_specific_role`, không khẳng định không cần chứng chỉ. Nguồn quốc tế chỉ tham khảo nhiệm vụ, không áp điều kiện hành nghề Hoa Kỳ sang Việt Nam.

Đây là biên tập có đối chiếu nguồn và kiểm tra dữ liệu, **không phải chứng nhận200 hồ sơ đã được chuyên gia ngành hoặc luật sư thẩm định đầy đủ**. Trước công bố rộng nên duyệt thêm các nghề có trách nhiệm y tế/pháp lý/tài chính; yêu cầu tuyển dụng, điều kiện hành nghề và các sửa đổi văn bản phải kiểm theo vị trí thực tế.

## Kiểm thử thực tế

- Backend:60 method khác nhau có kết quả cuối PASS,0 còn FAIL/0 SKIP:50 method ở test_chat21/task1/task2/shared_ai_protection/guest_postgres và10 test_advisor. Có1 lỗi quy tắc title nội bộ bị từ khóa kỹ năng ảnh hưởng, đã sửa và retest4 ca liên quan PASS; không chạy lại toàn bộ bộ197.
- Node:6 test PASS, gồm redirect allowlist, TTL và ownership draft,200 câu mở đầu khác nhau, mục tiêu khảo sát, claim retry/reload/tài khoản khác/phản hồi sau COMMIT.
- Chrome:12 checkpoint chính và2 checkpoint mobile/nháp trắng PASS. Có1 lần harness kiểm DOM trong lúc chuyển trang bị null; sửa predicate chờ DOM, chạy lại PASS. Fixture Firebase và AI demo; PostgreSQL là cluster riêng trên loopback, không Neon.
- Khảo sát/mode, claim/quota8 và concurrency/rate/Origin/proxy cũ được kiểm hồi quy trong các suite liên quan. Backend payload dùng mock provider để kiểm đúng khảo sát/career; không tính là DeepSeek live PASS.
- JSON200/12,5 nhiệm vụ,>=3 thử thách, đủ kỹ năng/lộ trình/nhịp ngày, fingerprint ID, không trùng cả hồ sơ; rà mẫu nghề liên ngành PASS. Thêm1 test đóng gói runtime mô phỏng PASS (tổng61 backend method khác nhau); Python compile, Node syntax và git diff --check PASS. Chọn nhầm tên class test runtime ở lần gọi đầu đã được sửa lệnh chạy, không sửa ứng dụng để bỏ kiểm tra.
- Ảnh thực: artifacts/chat21-desktop-draft.png, chat21-mobile-survey.png, chat21-mobile-career-draft.png, chat21-profile-1440.png, chat21-profile-390.png. Các ảnh dùng nội dung kiểm thử, không dữ liệu học sinh.
- **CHƯA KIỂM CHỨNG:** Firebase Google/email/redirect thật và câu trả lời DeepSeek thật của Chat2.1; chưa có cấu hình thử riêng được xác nhận. Không dùng secrets Production để thay thế. Chưa chạy Vercel build/deploy mới; mô phỏng bundle không phải build Vercel thật.

## Chạy thử và bàn giao

Local Preview: **http://localhost:8004/**; chat **http://localhost:8004/ai-career-advisor**. Server từ đúng worktree này, PostgreSQL local riêng, AI demo có nhãn, Firebase chưa cấu hình. Không ảnh hưởng8000/8002/8003. Không công khai qua tunnel hoặc deploy; không dùng Production resource. Dữ liệu preview lưu trong artifacts bị loại khỏi Git. Thông tin tiến trình tại artifacts/chat21-local-preview.json.

Sau khi duyệt: kiểm dịch vụ thật trong môi trường được cấp phép, review diff/commit rồi mới quyết định push/Preview/phát hành riêng. Không tự merge, push hoặc deploy theo checkpoint này. Không cần và không được chạy migration Production cho các thay đổi Chat2.1.
