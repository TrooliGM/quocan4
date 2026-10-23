# Nhiệm vụ 1 — giao diện và khảo sát hướng nghiệp

Ngày 2026-10-23. Nhánh `feat/task-1-career-survey`, worktree `.claude/worktrees/task-1`, nền `7c07d33` Premium. Không tích hợp các thay đổi chưa commit từ checkout chính. Không push, merge hoặc deploy.

## Đã thực hiện

- Brand đầu trang; thanh điều hướng bốn mục nằm ngay sau Hero, cuộn ngang trên mobile. CTA Bắt đầu khám phá đến `/ai-career-advisor`; nút tài khoản dùng nguyên Firebase/dialog/logout hiện có, chuyển vào Hero.
- Bỏ section/API/client loader Góc hướng nghiệp; giữ nguyên Khám phá nghề, Truyện nghề và API tư vấn dùng chung. Mẫu nội dung tĩnh `ARTICLES` trong `content.py` không còn endpoint phục vụ; không xóa dữ liệu người dùng.
- Phiên mới có khảo sát năm bước: gợi ý thêm vào văn bản, sửa/xóa/tự nhập, quay lại/tiếp tục, tiến trình, chọn anh/chị. Mỗi câu 1–400 ký tự; có thể trả lời “chưa rõ”. Gợi ý starter được chuyển vào câu mong muốn tư vấn.
- `PUT /api/ai/sessions/{session_id}/survey`, Bearer Firebase như các API hiện có. Session ID chính là conversation_id, owner UID là user_id; không nhận UID từ client.
- Lưu khảo sát trong metadata `messages[0].survey` của từng phiên: answers, address, version, analysis_request_id. Cờ survey_required chỉ được đặt khi tạo phiên mới. Không backfill lịch sử cũ. Không cần bảng/cột mới hoặc migration.
- PostgreSQL khóa hàng trong transaction, chỉ cập nhật messages, kiểm tra owner/hạn phiên tạm; SQLite/RAM dùng khóa store hiện có. Submit giống nhau có tính idempotent, submit khác sau hoàn tất trả 409. Không ghi nội dung khảo sát vào log. Xóa phiên sẽ xóa cả khảo sát theo cơ chế hiện hành.
- LangGraph nhận cặp câu hỏi/câu trả lời ở mọi lượt cùng cấu hình xưng hô; chỉ thị gợi ý khoảng ba nhóm nghề, lý do, môn học/kỹ năng/trải nghiệm, tránh kết luận chắc chắn. Không bổ sung kết quả giả hoặc thuật toán từ khóa.
- Sau khảo sát, UI gửi yêu cầu phân tích qua `/api/ai/chat` hiện có. Một phân tích thành công dùng một lượt AI khách theo quota cũ. Lưu khảo sát không tiêu hao quota. Retry phân tích dùng request_id đã lưu trong khảo sát; khi AI lỗi vẫn giữ khảo sát và cho thử lại.

## Kiểm thử thực tế

- `test_task1.py`: 7 PASS, gồm xác thực/IDOR, validation, immutable/idempotent, hai loại phiên, legacy không backfill, route/CTA, LangGraph payload với model HTTP mock, PostgreSQL local với hai submit khác nhau đồng thời.
- `test_advisor.py`: 10 PASS sau khi cập nhật helper hoàn tất khảo sát trước tư vấn; kiểm tra cách ly tài khoản, consent, retry, provider lỗi/đầu ra sai, lịch sử, mic và xóa dữ liệu local.
- `test_guest_postgres...test_guest_1_to_8_then_9_both_session_types`: 1 PASS, PostgreSQL local riêng, Firebase/graph mock; lưu khảo sát trước khi thực hiện quota 8/9, không thay chính sách quota.
- `browser_task1.py`: PASS desktop 1440x1000 và mobile 390x844, Firebase stub và AI demo, SQLite test riêng. Kiểm tra vị trí nav, bốn mục, dialog tài khoản, CTA, gợi ý/tự sửa/quay lại, nộp năm bước, gọi chat, reload không lặp khảo sát, không tràn ngang và không lỗi JS. Ảnh ở `artifacts/task1-{home,survey,chat}-{1440,390}.png` trong worktree.
- Python compileall, Node syntax checks, git diff --check đã chạy. Không có frontend build bundler riêng.
- Kiểm tra route Góc hướng nghiệp đã bỏ trong `test_app.HomepageTests.test_removed_career_corner`: 1 PASS. Tổng 19 test backend nêu trên; không cộng các lần chạy lại thành test mới.
- QA phát hiện trạng thái busy lúc tạo phiên có thể giữ nút Tiếp tục bị khóa; đã sửa đồng bộ trạng thái các điều khiển khảo sát và kiểm thử lại bằng click nút thật. Bản nháp và ô nhập khảo sát được dọn khi đổi danh tính/đăng xuất. Hai bản HTML root/public đã đồng bộ; asset thay đổi có phiên bản cache mới.
- Không chạy toàn bộ pipeline Super Board. Không truy cập Neon, database Production hoặc provider thật trong Nhiệm vụ 1. Kiểm thử Firebase/DeepSeek thật của bản Premium trước đây không được coi là kiểm thử thật cho flow khảo sát mới.

## Giới hạn và việc còn lại

- Chưa kiểm tra end-to-end khảo sát mới với Firebase/DeepSeek thật, chất lượng tư vấn thực, Safari hoặc điện thoại thật. Không tự tuyên bố PASS các phần này.
- Bản thử local mặc định chưa cấu hình Firebase/DeepSeek cần môi trường phát triển riêng. Không sao chép dotenv/credentials vào worktree hoặc Git.
- Khảo sát chưa hoàn tất chỉ giữ bản nháp trong RAM của tab; tải lại có thể phải nhập lại. Sau nộp đã lưu vào store theo consent/thời hạn phiên. Nếu trang đóng ngay sau lưu nhưng trước gửi phân tích, mở lại cho phép tiếp tục chat, không tạo lại khảo sát; chưa có background job tự gọi AI.
- Các rủi ro phát hành Production của ticket #7 (binding DATABASE_URL, tương thích schema legacy, chuỗi nâng cấp khách tám câu) không được xử lý hay cho là đã giải quyết bởi Nhiệm vụ 1.
- Chưa triển khai Nhiệm vụ 2/3. Khi tiếp tục, đọc file này và Git HEAD tại nhánh trên, giữ nguyên các worktree khác. Phải được người dùng duyệt riêng trước merge/push/deploy.


## Tinh chỉnh Navbar/Hero — 2026-10-23

Bổ sung SVG icon nội tuyến cho bốn mục, nền kem active, hover/focus, sticky và scroll spy hỗ trợ hash/URL trực tiếp. Hero căn trái hai nút cùng chiều cao, gap 14px, bỏ margin auto từ CSS cũ. Chromium desktop 1440 và mobile 390 PASS: vị trí dưới Hero, icon, spacing, warm cream, sticky/clearance, hash/direct URL active, không overflow hoặc exception. Đã xử lý scroll-padding-top cũ trong tính active; có một lần browser bị đóng do hai phiên QA trùng cổng, kiểm tra lại tuần tự PASS. Không đổi AI/Firebase/database. Script và ảnh QA ở artifacts/check_navhero.py và artifacts/navhero-{1440,390}.png. Chưa kiểm tra điện thoại thật/Safari hoặc đăng nhập Firebase thật trong đợt chỉ sửa Navbar/Hero. Commit giao diện này là nền Nhiệm vụ 2; Nhiệm vụ 2/3 chưa bắt đầu.


## Navbar phương án 2 — 2026-10-23

Theo yêu cầu đã duyệt: Navbar căn giữa max-width 768px, bốn ô grid bằng nhau, icon trên chữ, nền #183F34 và active #F3E5C9. Chỉ thay CSS Navbar. Chromium 1440/390 PASS: chiều rộng, bố cục dọc, icon, màu active, sticky/section clearance, hash/direct URL và không overflow/JS exception. Node syntax và git diff --check PASS; dự án không có bước bundle riêng. Không sửa Hero/AI/khảo sát/Firebase; không push/merge/deploy.
