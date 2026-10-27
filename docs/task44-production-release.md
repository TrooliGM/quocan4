# Phát hành Task 4.4 từ main — 27/10/2026

## Phiên bản và phạm vi

Người dùng đã cho phép deploy Production thật, tạo candidate chưa gán domain rồi smoke test và promote. Checkout phát hành riêng, detached và sạch tại `D:\khkt\.claude\worktrees\task44-production-main`, lấy đúng `origin/main` **3b2f7041530df3a220853f3f8537a0e94c4950db**. Không lấy thay đổi chưa commit từ worktree phát triển; không sửa mã ứng dụng để phát hành.

- Project: `quocan4`, team `khkt3`, repository `TrooliGM/quocan4` đã xác minh.
- URL chính thức: https://labanhuongnghiep.vercel.app/
- Deployment mới: **dpl_6avJjUZdcAS95Rg2BsDRqUqutHrE**, target **production**, **READY**.
- URL deployment: https://quocan4-kqvw0rlks-khkt3.vercel.app
- Đã dùng Vercel CLI `deploy --prod --skip-domain`, không truyền override biến môi trường; smoke candidate đạt rồi mới `promote` đúng deployment này.
- Alias domain chính đã đối chiếu qua Vercel API, trỏ đúng deployment mới và SHA nêu trên. Sáu file JS trên domain chính có SHA-256 khớp checkout sạch main: chat, chat-journey, navigation-actions, career-library, stories, profile-panel.
- Metadata binding Production trước/sau không thay đổi; Firebase, DeepSeek và DATABASE_URL được kế thừa Production, không lấy staging. Không ghi giá trị secret vào báo cáo.
- `git.deploymentEnabled.main=false` vẫn giữ nguyên. Không push, merge, bật Git auto-deploy hoặc chạy migration trong đợt phát hành này.

## Kết quả thực tế

| Phạm vi | Candidate | Domain chính |
|---|---|---|
| Trang chủ, AI Career Advisor, Truyện nghề, tài nguyên frontend | PASS | PASS |
| Danh mục 200 nghề / 12 nhóm, API truyện và API video `/api/career-videos/lap-trinh` | PASS | PASS |
| Runtime có cấu hình AI/Firebase; chung pipeline Task 4.1, Search bật; quyền lưu hồ sơ giữ nguyên | PASS | PASS |
| Firebase token thật cho QA tổng hợp và thành viên thử nghiệm | PASS | PASS |
| Khảo sát đủ 5 câu lưu/đọc lại; không bị yêu cầu làm lại khi điều hướng | PASS | PASS |
| DeepSeek thật tạo phản hồi và nút đúng nghề Lập trình viên | PASS — một request thực có kiểm soát | Đọc lại/replay kết quả candidate trên domain chính, không gọi model lại |
| Lịch sử và retry cùng request_id không tạo câu trả lời trùng | PASS | PASS |
| Token sai 401; phiên người khác 404; Origin ngoài 403; trường giả owner 422; đường dẫn riêng tư 404 | PASS | PASS |
| Chrome thật: chat → hồ sơ → chat; truyện/cảnh → hồ sơ → chat; khám phá 3 nghề, Back/Forward và reload | PASS | PASS |
| Conversation ID, khảo sát hoàn thành, bản nháp giữ nguyên | PASS | PASS |
| Điều hướng chỉ dùng 1 tab, không tạo session/chat/analysis POST ngoài ý muốn | PASS — 1 → 1 tab, 0 lời gọi AI do điều hướng | PASS — 1 → 1 tab, 0 lời gọi AI do điều hướng |
| Desktop 1440px / mobile 390px, không tràn ngang | PASS | PASS |

Mỗi phase có 20 kiểm tra smoke API/runtime PASS, cùng một suite Chrome hành trình PASS. Khảo sát được gửi bằng API với dữ liệu giả lập, trình duyệt kiểm tra giữ trạng thái sau chuyển trang; không đánh đồng với việc chạy mới toàn bộ pipeline phân tích khảo sát. Kế thừa 115 kiểm thử Python liên quan đã PASS ở bản main tích hợp, không chạy lại Super Board.

Chỉ tạo một hội thoại tạm của tài khoản QA tổng hợp đã có, dùng dữ liệu kiểm thử riêng. Không sửa/xóa hội thoại học sinh, hồ sơ đã xác nhận, schema hoặc quota. Không thao tác SQL trực tiếp, không chạy migration 001–006.

## Giới hạn xác minh

- Google popup thật kế thừa PASS do người dùng đã xác nhận ở Preview; lần này kiểm thử Firebase SDK email/password thật, không tuyên bố vừa tự động kiểm thử popup Google.
- Guest LIVE không gọi lại: phiên QA Production cũ hết hạn/hết lượt. Không cấp phiên thay thế, reset quota hoặc lách giới hạn. Các kiểm thử Guest/quota trước đó được kế thừa, không ghi thành LIVE Production mới PASS.
- Không kiểm thử mới tìm kiếm DDGS hay quy trình lưu hồ sơ chính thức; giữ nguyên cấu hình/quyền Production đã có, không mở rộng allowlist.
- **Historical ValidationError – root cause undetermined**. Chẩn đoán hiện tại đã có trong source; không có bằng chứng xác định nguyên nhân lỗi lịch sử và không tuyên bố đã sửa triệt để.
- Task 4 tổng thể **chưa hoàn thành**. PASS ở đây là smoke phát hành đúng phạm vi, không thay thế toàn bộ nghiệm thu Task 4.

## Rollback

Điểm khôi phục đã đọc lại và vẫn READY: **dpl_9TdB69NsBqWmKssEUQbNhG92jsVS**, source **da6d14669a96e6a4c30b718d348ee3235a35f2cb**, đúng project/team Production.

Nếu có lỗi nghiêm trọng: `vercel rollback dpl_9TdB69NsBqWmKssEUQbNhG92jsVS --scope khkt3 --yes`, sau đó xác minh alias và smoke lại. Chỉ chuyển deployment; không reset/khôi phục database hay quota. Người dùng tải lại trang nếu còn bundle cũ. Không cần rollback trong đợt này vì hậu kiểm đạt.

Bằng chứng máy cục bộ nằm trong `artifacts/` của checkout phát hành: preflight, dry manifest, deploy, promote, smoke-candidate/official, browser-candidate/official, final-verification và ảnh desktop/mobile. Trạng thái phiên QA được mã hóa DPAPI, không commit hay đưa vào gói deploy. Tại thời điểm phát hành, báo cáo và ghi nhớ chỉ lưu local; không tạo commit/push thay đổi SHA phát hành.

## Lưu GitHub theo yêu cầu tiếp theo

Người dùng sau đó yêu cầu lưu dự án lên GitHub. Kiểm tra cho thấy `origin/main` đã tiến lên **88d8fd9482b1867d8ed653dbe97f70bd69e6a8b2**, kế thừa 3b2f704. Không thay đổi hoặc lùi main. Ba tài liệu này được lưu trên nhánh riêng `docs/task44-production-release` từ origin/main. Đây là lưu tài liệu; không merge hoặc deploy phiên bản mới. Các kết quả Production phía trên thuộc đợt triển khai 3b2f704, không phải kết luận nghiệm thu/deploy cho 88d8fd9.
