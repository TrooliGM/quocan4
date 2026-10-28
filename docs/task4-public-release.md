# Task 4 — phát hành bản gỡ Hồ sơ, quyền sản phẩm công khai

**Cập nhật sau phát hành:** Production đã chạy commit43a8337 / dpl_7cdWzerGqdzD3c4Ucjvfb8GaJbfE, hậu kiểm Guest/Member và Google popup PASS. Đây là bản preflight theo mốc; xem [báo cáo Production](task4-public-production-result.md) để biết kết quả mới nhất.

Ngày kiểm tra: 28/10/2026. Repository `TrooliGM/quocan4`, worktree `task4-remove-profile`, nhánh `feat/task4-remove-profile`, base `1a534b186a9a53aedc7b94d3a01a2d4f6a3b21b4`.

## Phạm vi và xác minh nguồn

Người dùng cho phép commit, push/tích hợp main và phát hành Production sau khi các cổng kiểm thử đạt. Không cấp quyền migration, đổi DATABASE_URL Production, reset dữ liệu/quota hoặc mở quyền quản trị. Giữ nguyên các checkout đang dở; không lấy source từ checkout D:/khkt.

Rà soát thực tế cho thấy `advisor/rollout.py` ở base đã bỏ QA allowlist cho sản phẩm; `routes.analysis_user` không phân biệt QA. Không cần thêm công tắc hay sửa lại pipeline đã công khai. Config runtime của Member trên Production cũ và Preview mới đều xác nhận task4_enabled/automatic_analysis/web_search_enabled=true, pipeline=task41, live. Bản vá hiện tại gỡ Hồ sơ riêng, hiển thị phân tích trực tiếp trong chat, giữ cơ chế lưu hội thoại độc lập và sửa output schema gửi model thành area=null. Validator dữ liệu legacy và căn cứ vẫn chặt chẽ.

| Tính năng từng bị giới hạn QA | Guest sau phát hành | Member sau phát hành |
|---|---|---|
| UI và pipeline tư vấn Task 4.1, hai chế độ chat | Có, danh tính Guest do server cấp | Có, Firebase token xác minh phía server |
| Khảo sát 5 câu, tự phân tích và hướng nghề có căn cứ | Có, kết quả trong phiên tạm | Có, trong hội thoại của mình |
| DeepSeek và DDGS có nguồn | Có, quota chat 8 lượt + rate limit | Có, rate limit dùng chung vẫn giữ |
| Retry phân tích | Có, cùng request_id; ngân sách phân tích riêng | Có, cùng cơ chế, không có quyền bypass |
| Reload, ngữ cảnh nhiều lượt và điều hướng cùng tab | Có, phiên còn hiệu lực | Có, quyền sở hữu vẫn kiểm tra |
| Lưu hội thoại lâu dài | Cần đăng nhập | Có, chủ động đồng ý lưu đúng hội thoại |
| Hồ sơ hướng nghiệp cá nhân | Đã ngừng, API 410 | Đã ngừng, API 410 |
| Debug/admin, đọc dữ liệu người khác, bypass quota | Không cấp | Không cấp |

`SEARCH_PUBLIC_ENABLED=false` vẫn là công tắc sự cố cho mọi người, không phải phân tầng QA. Các biến allowlist QA legacy không còn cấp chất lượng AI khác nhau. Micro phụ thuộc cấu hình dịch vụ/trình duyệt, không phải quyền QA; không bật lại Vbee hoặc mua dịch vụ.

## Preview mới và kiểm thử thực tế

- Deployment **dpl_ARVNjK92VvqTVR1FFDw7PW4JsYQW**, READY, Preview; source bản vá local từ đúng worktree, chưa commit ở thời điểm build.
- URL https://quocan4-a6sb4f0fc-khkt3.vercel.app/ai-career-advisor
- Alias thử Google có sẵn trong Firebase: https://quocan4-git-fix-chat-vercel-khkt3.vercel.app/ai-career-advisor , đã xác minh trỏ đúng deployment này; không thêm Firebase domain hay đổi domain chính.
- Tái xác minh Neon staging `task41-preview-schema-20261025`, branch `br-morning-tooth-aznv081q`, `neondb`, role Preview và TLS; schema PASS bằng SQL chỉ đọc trước khi dùng dữ liệu thử. Không chạy migration/tạo/reset database.

| Kiểm tra trên bản mới | Bằng chứng / kết quả |
|---|---|
| Build, trang chủ, 200 nghề/12 nhóm, truyện/video, tài nguyên khớp bản vá | PASS, kiểm trực tiếp Preview mới |
| Guest Chrome ẩn danh sạch, không Firebase fixture | PASS, một lần cấp phiên thông thường; cookie Secure/HttpOnly/SameSite=Strict; giữ nguyên danh tính đến hết bài thử |
| Guest 5 câu khảo sát → DeepSeek phân tích 3 nghề | PASS, tự chạy từ UI, trích dẫn căn cứ đúng câu; không lỗi area |
| Guest retry/cached, reload kết quả | PASS, cùng trace/result, không thêm attempt hay lượt chat |
| Guest DeepSeek + DDGS LIVE | PASS, 2 nguồn thật; lượt đầu 16,18 giây |
| Guest câu 1–8, câu 9, gửi lại request cũ | PASS, used_questions tăng đúng 1–8; câu 9 trả429; duplicate không trừ thêm, không reset quota |
| Guest nghề → truyện → chat, cùng tab, giữ nháp/khảo sát | PASS, Chrome thật; không POST chat/analysis/session mới chỉ vì điều hướng |
| Member email/password SDK thật | PASS trên Preview mới, không gọi là Google popup |
| Member phân tích đã lưu, retry/cache, retain và đọc lại đúng hội thoại | PASS trên Preview mới; không trả dữ liệu tài khoản khác |
| Member DeepSeek LIVE | PASS, 7,71 giây, pipeline task41 |
| Google popup thật, giữ khảo sát, phân tích/lưu/reload | PASS theo xác nhận trực tiếp của người dùng trên alias của Preview mới; không phải phép thử tự động hoặc fixture |
| Token sai, UID/role header giả, phiên người khác, Origin ngoài, quyền lưu Guest | PASS: 401/404/403 tương ứng; không mở quyền mới |
| File private/test/debug, API Hồ sơ cũ | PASS: private paths404, API Hồ sơ410 |
| Desktop1440/mobile390, không Hồ sơ, không lỗi JavaScript | PASS, Chrome thật; ảnh đã kiểm tra |
| Hồi quy Python trọng tâm | **97 PASS** trong hai đợt59+38; local PostgreSQL/provider mock, không gán nhãn LIVE |

Kế thừa phần local176 ca trước đó không bị ảnh hưởng; không tuyên bố vừa chạy lại toàn bộ. Bằng chứng mới trong artifacts (bị ignore): public-release-preflight.json, reused-db.json, reuse-preview-dry.json, reuse-preview-deploy.json, preview-live-check.json, preview-browser-final.json, public-guest-live.json, public-member-live.json; ảnh public-guest-1440.png/public-guest-390.png. Cookie/token và trạng thái thử chỉ lưu DPAPI, không có trong source/upload/báo cáo.

## Cổng Production và rollback

Checkpoint trước phát hành: **dpl_Da9yybCwP9VnHeifXCX3Jo9YdCsd**, source **1a534b186a9a53aedc7b94d3a01a2d4f6a3b21b4**, URL deployment https://quocan4-ml8ai2qxd-khkt3.vercel.app ; Production Branch thực tế main. Domain chính vẫn ở checkpoint này trong toàn bộ kiểm thử Preview.

Các cổng Preview quan trọng đã đạt. Tiếp theo: kiểm staging/diff/secret, commit đúng các file, fast-forward origin/main nếu vẫn cùng tổ tiên; giữ main auto-deploy=false. Dựng candidate bằng môi trường Production hiện hữu với --prod --skip-domain, **không mang DATABASE_URL hoặc env override Preview sang**. Chỉ đọc schema và dữ liệu tài khoản thử riêng để đối chiếu runtime/database, kiểm tài nguyên/config trước promote. Nếu candidate không phù hợp thì không promote.

Khi promote thành công phải ghi deployment/SHA thực tế và hậu kiểm trên domain chính, không suy từ Preview READY. Nếu có lỗi nghiêm trọng đã xác minh: `vercel rollback dpl_Da9yybCwP9VnHeifXCX3Jo9YdCsd --scope khkt3 --yes`, kiểm lại alias và HTTP; không reset database. Không có migration nên rollback mã không cần đảo schema/dữ liệu.

Tại thời điểm tạo checkpoint báo cáo này: **chưa phát hành Production**; kết quả phát hành được cập nhật bằng báo cáo hậu kiểm riêng. Historical ValidationError vẫn root cause undetermined; không đồng nhất với lỗi area đã tái hiện/sửa. Task 4 tổng thể chưa được tuyên bố hoàn thành.
