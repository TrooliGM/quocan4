# Gỡ Hồ sơ hướng nghiệp riêng — bàn giao local 28/10/2026

Repository `TrooliGM/quocan4`; nhánh **feat/task4-remove-profile**; worktree `D:\khkt\.claude\worktrees\task4-remove-profile`; commit gốc **1a534b186a9a53aedc7b94d3a01a2d4f6a3b21b4** từ origin/main. Giữ nguyên checkout D:/khkt và các worktree có thay đổi dở. Không mặc định chúng trùng main/Production; không reset/clean/pull/checkout ghi đè.

## Chức năng đã xử lý

- Gỡ nút/modal Hồ sơ riêng, công tắc dùng Hồ sơ, đề xuất/xác nhận/sửa/từ chối, thông báo và tự mở modal sau khảo sát. Xóa module profile-panel.js và selector/listener/CSS liên quan. Giữ hộp xác nhận dùng chung, lịch sử, đăng nhập/đăng xuất và dọn UI khi đổi danh tính. HTML canonical/fallback đồng nhất, đổi cache token JS/CSS.
- Các API quản lý Hồ sơ cũ yêu cầu xác thực rồi trả **410**, không đọc/ghi dữ liệu cũ. Config luôn `profile_enabled=false`, kể cả env cũ bật. Chat không đọc `context_items`, không gửi khối Hồ sơ xác nhận đến model và không sinh `profile_updates` mới (trường tương thích luôn rỗng). Không thay pipeline DeepSeek/LangGraph/Search hay công cụ điều hướng.
- **Retain độc lập:** `account_write_actor` giữ danh tính server, Origin và rate limit PG dùng chung. Giữ tên biến/bucket giới hạn cũ để không tự đổi ngưỡng. Retain giữ transaction/khóa, ID, khảo sát, tin nhắn và chống trùng khi đồng thời. Chỉ password/google.com được lưu lâu dài; Guest không thể dùng retain hoặc tạo mới remember=true. Hội thoại Guest lâu dài legacy vẫn đọc/chuyển chủ được, không xóa.
- Nút **Lưu hội thoại vào tài khoản** được giữ ngay dưới header, độc lập Hồ sơ.
- Nút **Xóa lịch sử và dữ liệu của tôi** chuyển vào khu vực tài khoản sidebar. Phải xác nhận; Hủy không gọi DELETE. `/api/ai/data` có Origin/rate limit, chỉ xóa theo UID xác thực. Khi người dùng chủ động xóa, dọn cả dữ liệu Hồ sơ cũ đúng chủ kể cả cờ đã tắt; không có bảng 006 vẫn lưu/xóa hội thoại được. Dọn cache UI sau xóa. Không tự xóa gì khi gỡ tính năng.
- Giữ cột profile và các module lưu trữ/metadata legacy cho tương thích, chuyển chủ và quyền xóa. **Hồ sơ cá nhân** đã ngừng; `career_profile`/“Xem hồ sơ nghề” vẫn là **thông tin nghề trong thư viện 200 nghề**, được giữ nguyên.

## Kết quả khảo sát trực tiếp trong chat

Sau câu 5, frontend lưu khảo sát đúng session và chạy analysis job hiện có. `survey-result.js` dựng **một thẻ kết quả** từ `analysis_job.result` hoặc `survey_analysis` đã lưu, không ghi tin nhắn trùng hoặc gọi model trong hàm render. Có tổng hợp, căn cứ trích nguyên văn, gợi ý nghề/lý do/môn học/kỹ năng/trải nghiệm nhỏ và câu hỏi làm rõ. Không xác nhận từng mục, không modal.

Thêm trường JSON tùy chọn `career_directions` (tối đa 3) để đọc được kết quả cũ: career_id phải thuộc danh mục, không trùng; evidence phải nằm trong đúng câu khảo sát. Giữ validator căn cứ/điểm mạnh tự nhận và bounded repair. Prompt gợi ý khoảng ba hướng; khi thiếu căn cứ phải hỏi làm rõ, không bịa thêm để đủ số. Kết quả cũ thiếu trường mới vẫn hiển thị phần có sẵn, không tự gọi AI lại để bổ sung.

Lỗi/thử lại hiển thị ngay trong chat, giữ năm câu và cùng survey request_id, ngân sách/lease/trace hiện hành; không trừ thêm quota chat Guest. Reload hoặc quay lại từ nghề/truyện chỉ dựng dữ liệu đã lưu. Ghi chú phiên, summary, lịch sử, khảo sát và nghề vừa khám phá tiếp tục là ngữ cảnh; không đọc Hồ sơ riêng hoặc thông tin từ session/tài khoản khác.

## Bằng chứng kiểm thử

**176 ca Python PASS cuối cùng qua các đợt kiểm thử tăng dần**, không chạy lại toàn Super Board. Assert chức năng Hồ sơ cũ được chuyển sang 410/bảo toàn dữ liệu legacy; không bỏ qua lỗi bằng skip. Fixture Member có provider đúng như Firebase; Guest lâu dài legacy chỉ seed trực tiếp trong PG local để thử đọc dữ liệu cũ, không tái cấp quyền tạo qua API. Ca memory cũ nay thực sự chạy đến lượt nén thứ sáu và kiểm tra lỗi nén không mất phản hồi; không sửa thuật toán nén ứng dụng để chiều test.

| Nhóm | PASS |
|---|---:|
| Gỡ Hồ sơ, retain/xóa/quyền/rate limit, không cần 006 | 10 |
| Analysis jobs + validation/matrix | 35 |
| Navigation actions/grounding | 25 |
| Shared protection + quota/PostgreSQL | 31 |
| Search context quality + pipeline | 23 |
| Public UI/rollout | 9 |
| Legacy data/analysis, journey, cá nhân hóa phiên, unified, advisor | 43 |
| **Tổng** | **176** |

**Chrome thật + FastAPI/PG local: 6 nhóm PASS; Firebase/model là fixture, KHÔNG LIVE:**

1. Guest đủ 5 câu → tự phân tích một lần trong chat, ba hướng, quota vẫn 8, retain403, không Hồ sơ.
2. Gửi một tin → quota7; nghề/truyện/quay lại, Back/Forward/reload giữ ID/khảo sát/bản nháp/một thẻ/một tab; không thêm AI/session POST do điều hướng.
3. Đăng nhập Google **fixture** qua UI → claim lịch sử Guest, giữ ID; Member retain và reload hội thoại lâu dài.
4. Member khảo sát, lỗi provider fixture → thông báo; retry thành công một lần, không trùng phân tích/không tự gọi lại khi reload.
5. Desktop1440/mobile390 không tràn ngang hay DOM Hồ sơ; ảnh đã được xem.
6. Xóa ở sidebar: Hủy không DELETE, xác nhận mới xóa dữ liệu fixture đúng chủ; không JS exception, không gửi Hồ sơ xác nhận đến model.

Node syntax, Python AST/FastAPI import, HTML fallback và git diff --check: **PASS**. Git đối chiếu không đổi trang chủ, thư viện/dữ liệu 200 nghề, Truyện nghề/video, chat-journey.js, Firebase, migrations hay vercel.json.

Bằng chứng local: `artifacts/profile-removal-validation.json`, `artifacts/profile-removal-browser.json`, `artifacts/profile-removal-1440.png`, `artifacts/profile-removal-390.png`. Cluster PG chỉ bind loopback, tạo mới và dừng sau test; không đọc kết nối/credentials Neon Production.

## File thay đổi

- Backend: `advisor/routes.py`, `advisor/graph.py`, `advisor/analysis_jobs.py`, `advisor/navigation.py`, `advisor/postgres_adapter.py`, `advisor/profile_context.py`, `advisor/prompt.txt`, `advisor/survey_analysis.py`.
- Frontend: `chat.html`, `public/chat.html`, `public/assets/chat.js`, `public/assets/chat.css`; thêm `public/assets/survey-result.js`; xóa `public/assets/profile-panel.js`.
- Test: `tests/browser_fixture.py`; thêm `tests/browser_profile_removal.py`, `tests/test_profile_removal.py`; cập nhật `tests/test_advisor.py`, `tests/test_advisor30_profile.py`, `tests/test_analysis_validation_matrix.py`, `tests/test_guest_postgres.py`, `tests/test_navigation_actions.py`, `tests/test_navigation_grounding.py`, `tests/test_task41_analysis_jobs.py`, `tests/test_task41_public_ui.py`, `tests/test_task41_unified.py`, `tests/test_task44_profile_journey.py`, `tests/test_task4_personalization.py`.
- Tài liệu: báo cáo này, `docs/project-memory.md`, `docs/decisions.md`.

## Giới hạn và điểm dừng

**Chưa xác minh LIVE:** Google popup/Firebase, chất lượng DeepSeek/DDGS thật, quyền database runtime Neon. Cần môi trường thử được cấp phép nếu nghiệm thu dịch vụ thật; không suy từ fixture thành PASS. Chưa tạo Preview hoặc thử Production cho bản vá này.

Không thay schema/migration, secret, Firebase project, domain hay cấu hình dịch vụ. Không xóa/reset dữ liệu/quota thật; thao tác xóa trong test chỉ áp dụng dữ liệu giả ở PG local riêng. Historical ValidationError vẫn **root cause undetermined**.

Bản vá local đã hoàn tất phạm vi và có thể review; **chưa stage/commit/push/merge/deploy**. **Task 4 tổng thể chưa hoàn thành; chưa kết luận READY Production.** Dừng ở phát triển local theo yêu cầu; việc phát hành cần yêu cầu riêng.
