# Hotfix điều hướng/hiệu năng AI Chat —24/10/2026

## Nền và bằng chứng trước sửa

Vercel xác minh Production thực:6c5ce230b295c6c2c02e6b5761c9c6b66ada63d4, deployment dpl_2RkRuX1MKWiXeUkNZrkXLJ5m6dGG, nhánh feat/ai-chat-2-1. Tạo hotfix/chat-navigation-performance tại worktree chat-perf từ đúng commit. Không sửa checkout/worktree dirty khác, UI/CSS/thư viện/data/migration/config Vercel hoặc Firebase/DeepSeek.

Đo Production bằng phiên khách tổng hợp riêng, không đọc tài khoản/hội thoại người khác và không gọi AI.5 lần POST tạo phiên,5 lần tải phiên và Network/waterfall Chrome:

| Phép đo Production trước sửa | Median |
|---|---:|
|API tạo phiên|12559,1ms|
|API danh sách|7329,9ms|
|API tải một phiên|7260,6ms|
|Click mở cũ → DOM đánh dấu/nội dung dùng được|7159,7ms|
|Click tạo → khảo sát xuất hiện|12387,3ms|
|Click tạo → khảo sát dùng được|19523,7ms|

Nút tạo đã phản ứng bằng disable trong khoảng1ms; không gọi đó là khung khảo sát đã sẵn sàng. Baseline22 request API trong phiên Chrome đo (gồm khởi tạo trang); số liệu HTTP và Chrome là hai phiên đo riêng. Không có /api/ai/chat trong waterfall. Các route tạo/list/get không gọi graph DeepSeek.

Bằng chứng source: createSession chờ POST rồi await refreshHistory; adapter create gọi list ở hai bảng rồi mở kết nối thứ ba để INSERT. Mở phiên tạm lần lượt thử saved rồi temporary qua hai kết nối; list mở hai kết nối. Chưa có cache và loadSession chặn đổi lựa chọn bằng busy trong lúc chờ. Server guest kiểm cookie/claims bằng hai câu SELECT. Các kết nối đều mới, có TLS/transaction/SET; không kết luận toàn bộ thời gian là SQL CPU hoặc cold start. Baseline chưa có Server-Timing để tách DB/Firebase trong Vercel; không suy đoán con số cho phần chưa đo.

Lỗi login: tái hiện nhánh mất record laban.login-return khiến loginDestination fallback '/', dù trước đó một phép thử của người dùng đã PASS. Không có trace để kết luận vì sao record mất trong trình duyệt người dùng. Sửa đường dẫn phục hồi để không phụ thuộc duy nhất record đó: URL có return_to nội bộ và UUID conversation, không chứa token/khảo sát. Auth chụp target trước listener, chỉ dọn intent khi hoàn tất chuyển lịch sử. Không coi ca mock là đã kiểm lại Google thật.

## Thay đổi

- Adapter get/list dùng UNION với owner/expiry đúng cả hai bảng; list chỉ header. Create dùng COUNT và INSERT cùng transaction/kết nối; transaction advisory lock riêng giữ cap100 khi tạo đồng thời, không session lock trên Neon pooler.
- Chỉ tái sử dụng connection trong một request quản lý session, không global pool/auth cache và không giữ transaction lúc chờ LLM. Các context vẫn commit/rollback riêng; SET LOCAL bảo vệ timeout trên từng transaction, không thêm startup options bị pooler từ chối. Đóng connection sau request, giữ lock khi đang dùng; không sửa URL/config database.
- Server guest vẫn xác minh cookie hash, expiry và chưa claim ở mỗi request, gộp thành SELECT với NOT EXISTS; không bỏ kiểm tra.
- Server-Timing chỉ thời lượng app/auth_verify/db_connect/db_sql và số kết nối, không SQL/UID/token/content. auth_verify cho guest bao gồm DB nên các metric chồng lấp, không cộng thành tổng. API AI thật ngoài quản lý session không dùng request connection reuse.
- Frontend cache RAM tối đa20 session/TTL30giây, xóa khi đổi identity; không cache xác thực. Cache được cập nhật khi create/survey/chat/rename và bỏ khi delete. Mọi ghi vẫn cần backend auth/ownership/quota. Cache hết hạn có selected/loading tức thì, abort GET cũ và navigation generation để response cũ không ghi đè.
- Một create promise, không POST song song từ nhiều click; cập nhật đúng một sidebar item thay vì tải lại list. Khảo sát chờ dữ liệu mạng có thông báo, không tự gọi AI do tạo/mở phiên. Giữ welcome/consent và hai mode.
- Khởi tạo list và config song song, không GET auth/me trùng vì config đã xác minh require_user. Lịch sử list chậm không chặn hiển thị shell hoặc phiên được khôi phục.
- return_to chỉ allowlist nội bộ; conversation UUID không cấp quyền, luôn GET có ownership trước restore. Cookie/claim và draft theo UID/session giữ nguyên, mất quyền không phục hồi cache từ identity cũ. Home login vẫn về home.

## Kiểm thử trước phát hành

37 test quota/claim/atomic save/survey/modes/title PASS;5 test PostgreSQL thực local mới PASS cho số connection, rollback, expiry/owner, cap100 đồng thời, không gọi provider;1 bundle runtime và1 payload survey regression PASS. Node7 PASS, gồm intent bị xóa/ghi đè và URL độc hại. Chrome12 checkpoint Chat2.1 PASS, đã sửa ca popup/redirect fixture xóa return-intent để tái hiện fallback cũ. Không chạy Super Board toàn diện.

Local PostgreSQL/Firebase fixture:5 create +5 open cho guest và member; cache open khoảng7–15ms, một POST/create, không list sau mỗi create, không AI. Chuyển5 phiên liên tiếp với response trì hoãn/cancel, kiểm đúng draft cuối; double-click cùng phiên chỉ1 GET. Đây không phải số liệu member Firebase thật ở Production.

Thư viện/data/CSS/migration/vercel.json đối chiếu nguyên byte với6c5ce23. Backup/rollback code là deployment6c hiện hành, không đảo schema hoặc restore database. Người dùng đã cho phép commit/phát hành hotfix trong lượt này; chỉ promote đúng staged Production candidate sau kiểm an toàn, không merge main/force push.

## Còn cần xác minh trực tiếp

Đo lại HTTP/Chrome và Server-Timing sau build/deploy; ghi kết quả thật vào artifacts/perf. Google popup thật và latency xác minh token của tài khoản thật cần người dùng thao tác; chưa có token/account thử được cấp, không dùng mock để báo live PASS. Mục tiêu <200ms cho phản hồi trực quan, không hứa mọi request mạng <200ms.
