# Task 4.1 — sửa Preview đưa Guest về giao diện cũ

## Chẩn đoán đã xác minh

Preview cũ `dpl_GCno2S2r4NQqqqZswEJVU4jNZej3`, commit `a2a2f76`, không phải build nhầm. Chrome thật cửa sổ ẩn danh đã thấy header **La Bàn AI 1:1**, subtitle cũ và tải `stable-chat.js` (ảnh `artifacts/task41-ui-before-guest-desktop.png`). Nhãn1:1 nhìn tương tự1.1 nhưng đây là UI legacy đúng như phản ánh.

`app.html_page()` dùng `controlled()` để trả `stable-chat.html`; `advisor-entry.js` chỉ chuyển sang shell mới khi Firebase member thuộc allowlist. Guest và member ngoài danh sách dùng stable. `chat.js` mới còn tự reload khi `task4_enabled=false`. Vì vậy thay đổi Task4.1 nằm trong bundle nhưng không được Guest dùng. Cùng cờ backend đã bị dùng làm cờ hiển thị.

## Bản sửa giới hạn phạm vi

- Thêm `ADVISOR_PREMIUM_UI_PREVIEW=true`, chỉ có hiệu lực khi `VERCEL_ENV=preview`. Mở HTML/CSS/JS Premium cho mọi người, không xét UID. Cấu hình trả `premium_ui_public` từ server, không tin query/client.
- Backend giữ `ADVISOR_CONTROLLED_ROLLOUT=true`, allowlist, auth, stable graph cho Guest/member; analysis/profile có xác nhận vẫn giới hạn QA. Production bỏ qua cờ UI Preview kể cả nếu đặt nhầm true.
- Không dùng vòng reload khi UI công khai mà backend còn hạn chế. Khảo sát vẫn lưu bình thường; thông báo rõ chưa phân tích tự động, không hứa kết quả. Panel Premium cho Guest/member hướng dẫn tài khoản thử được cấp quyền, không gọi API profile/analysis bị khóa và không sinh đề xuất giả.
- Cache version HTML/chat/profile module cập nhật đồng bộ cả bản runtime và public. Không sửa thư viện, Truyện nghề, quota, dữ liệu hoặc migration.
- Preview mới chỉ allowlist tài khoản QA chính và Google QA đã xác minh. QA phụ được dùng như member ngoài allowlist **chỉ ở Preview này**, giữ nguyên UID/lịch sử/dữ liệu và allowlist Production.

Kiểm thử local5ca mới PASS: Guest/member có UI nhưng không có quyền analysis/confirm; chat member vẫn stable graph; QA giữ quyền; Production không bị mở UI bởi flag/query; Preview phải có cờ riêng.3hồi quy analysis/Guestquota/bundle PASS; Node syntax/diff whitespace PASS. Một assertion test đầu giả định legacy GET profile trả404 đã sửa theo hợp đồng thật: endpoint đó vẫn trả200 conversation_notes của chính owner, không trả confirmed items.

## Preview đã triển khai và kiểm tra

- Runtime: **`e933f981d8a8383d62ef7fd1b4cfaef8ed81ee11`** trên nhánh `feat/task-4-1-advisor-intelligence`, đã push cùng các checkpoint trước.
- Deployment **`dpl_GPWPYMsLL3F7MwYsDaFsYzmBihDZ`**, Vercel **READY / Preview**.
- [Mở AI Chat mới](https://quocan4-bp6m6anvt-khkt3.vercel.app/ai-career-advisor). Link deployment cũ vẫn phục vụ bản cũ; cần dùng URL mới này. Vercel Deployment Protection còn giữ nguyên, tài khoản có quyền project có thể phải đăng nhập Vercel trước; đây không phải đăng nhập ứng dụng/Firebase.
- Header/subtitle và shell mới được trả ngay bởi FastAPI cho Guest/member/QA, `Cache-Control: no-store`, assets `task41-public-ui-1`. Trình duyệt mới không tải `stable-chat.js`. Backend mới vẫn QA-only; cờ UI không cấp quyền API.

Đã dùng **Chrome thật headless với `--incognito`**, profile trình duyệt riêng cho từng trường hợp, không mock Firebase/model/network. B và C đăng nhập bằng Firebase SDK email/password thật; C có UID được allowlist, B không có. Không gọi đây là kiểm thử popup Google.

| Trường hợp | Header/subtitle | Avatar/nhãn cũ ở tin AI | Khung chat | Khảo sát/Hồ sơ | Backend còn giới hạn |
|---|---|---|---|---|---|
| A — Guest ẩn danh | Đúng, đã nhìn thấy | Không còn, đã nhìn thấy | Bo góc + Copy còn | 5câu lưu được; panel giải thích chưa mở phân tích, không hiện kết quả giả | Main chat stable + DeepSeek thật, Guest8; analysis/confirmed profile không mở |
| B — Firebase member ngoài allowlist | Đúng, đã nhìn thấy | Không còn | Bo góc + Copy còn | 5câu lưu được; panel hướng dẫn tài khoản kiểm thử, không gọi API nhạy cảm | Main chat stable + DeepSeek thật; không có quyền Task4.1 backend |
| C — Firebase QA allowlist | Đúng, đã nhìn thấy | Không còn | Bo góc + Copy còn | 5câu→tự gọi1analysis→đề xuất/căn cứ; số mục đã lưu không tăng trước click, tăng đúng1 sau Accept | Task4.1 graph/analysis/confirmed profile được phép |

Cả3trường hợp gửi1tin chat thực tế có phản hồi và Server-Timing ghi provider call; config `mode=live`, model `deepseek-flash`. Không chỉ thay tên UI để giả vờ Guest đã có pipeline Task4.1. Guest từ8/8→7/8 sau đúng1tin; không gửi chat kỹ thuật để phân tích. A/B có **0 lời gọi analysis/profile nhạy cảm từ UI**. C có đúng1POSTanalysis, không cần bấm nút phân tích hoặc nhập tay Hồ sơ.

Hậu kiểm LIVE **PASS**: Guest/member gọi thẳng analysis/confirm bị404; member không đọc được phiên QA; token giả ở cả2API AI cũ bị401, Origin trái phép bị403; cookie Secure/HttpOnly/SameSiteStrict; quota Guest giữ7 sau mọi request bị từ chối; QA mở lại analysis cached có0provider calls. Xác minh chỉ đọc đúng staging role/database, 200nghề/12nhóm; alias Production vẫn `dpl_BwthFvvNpNDscwEuKPC744bVe38z` / runtime957ffde.

Đã chụp **12ảnh sau sửa**, desktop1440 và mobile390 cho cả chat/panel của A/B/C, kiểm không tràn ngang và đã xem ảnh trực tiếp:

- Guest: [desktop chat](../artifacts/task41-ui-guest-chat-1440.png), [mobile chat](../artifacts/task41-ui-guest-chat-390.png), [desktop panel](../artifacts/task41-ui-guest-profile-1440.png), [mobile panel](../artifacts/task41-ui-guest-profile-390.png).
- Member: [desktop chat](../artifacts/task41-ui-member-chat-1440.png), [mobile chat](../artifacts/task41-ui-member-chat-390.png), [desktop panel](../artifacts/task41-ui-member-profile-1440.png), [mobile panel](../artifacts/task41-ui-member-profile-390.png).
- QA: [desktop chat](../artifacts/task41-ui-qa-chat-1440.png), [mobile chat](../artifacts/task41-ui-qa-chat-390.png), [desktop proposals](../artifacts/task41-ui-qa-profile-1440.png), [mobile proposals](../artifacts/task41-ui-qa-profile-390.png).

Ảnh/artifacts chỉ có trên máy trong worktree, không commit. Trước/sau và kết quả browser: `artifacts/task41-public-ui-before.json`, `task41-public-ui-browser.json`. Assertion baseline đầu tiên dùng sai nhãn1.1 thay vì1:1 đã sửa theo HTML thật và chạy lại đạt; không sửa ứng dụng để chiều assertion.

Brave Search vẫn **BLOCKED**, chưa có key được cấp phép. Cần cấu hình `SEARCH_PROVIDER=brave` và `SEARCH_API_KEY` trong **Vercel Preview**, bỏ override Search rỗng ở helper deploy trước khi redeploy và nghiệm thu nguồn/citations. Không gửi secret vào chat. Chưa có bằng chứng Search thật nên không hiển thị nguồn/biểu tượng đã tra cứu giả. Popup Google trên hostname mới vẫn chưa được người dùng thao tác; Firebase authorized domain mới đã thêm, bảo toàn các domain cũ.

## Bảo toàn và file thay đổi

Thay đổi runtime đúng8file: `.env.example`, `advisor/rollout.py`, `advisor/routes.py`, `app.py`, `chat.html`, `public/chat.html`, `public/assets/chat.js`, `public/assets/profile-panel.js`; bổ sung `tests/test_task41_public_ui.py` và tài liệu. Không sửa database schema, chạy migration, reset quota, sửa/xóa dữ liệu cũ hoặc đổi thư viện/Truyện nghề. Các bản ghi mới chỉ là QA tổng hợp trên staging riêng. Production không triển khai lại; kiểm alias/deployment và quyền API ghi trong `artifacts/task41-public-ui-final-gates.json`.
