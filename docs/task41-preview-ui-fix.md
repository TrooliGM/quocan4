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

## Nghiệm thu sau triển khai

Đang chờ build và kiểm Chrome thật cho Guest, Firebase member ngoài allowlist, Firebase QA. Chưa tính PASS trước khi quan sát UI và lưu ảnh. Brave Search vẫn BLOCKED vì thiếu `SEARCH_PROVIDER=brave` và `SEARCH_API_KEY` hợp lệ ở Preview; không yêu cầu gửi secret qua chat. Không đưa fallback hoặc header mới thành bằng chứng model mới cho Guest: Guest/member tiếp tục DeepSeek qua stable graph, QA mới dùng pipeline Task4.1.
