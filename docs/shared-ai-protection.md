# Bảo vệ AI dùng chung — bản chuẩn bị trên task-2

Áp dụng cho `/api/ai/chat`, `/api/advice`, `/api/career-stories/{career_id}/ask`. `/api/voice/transcribe` dùng cùng rate/budget nhưng không trừ quota tám câu hỏi LLM. Không đổi thiết kế, nội dung 200 nghề, hai mode hoặc truyện.

## Danh tính và giới hạn

- Có Authorization: backend xác minh Firebase ID token; token sai/hết hạn không được fallback sang cookie. Không tin UID, role, quota hay forwarded headers do client tự khai.
- Không có Authorization: cần cookie khách do server cấp qua `POST /api/ai/guest/session`. Cookie ngẫu nhiên 256-bit, HttpOnly, SameSite=Strict, host-only; HTTPS/Vercel dùng Secure và tên `__Host-laban_guest`. PostgreSQL chỉ giữ hash, UID và TTL. GET metadata không xuất token, mọi response auth/AI đều no-store. Cookie hết hạn không tự phục hồi danh tính; cấp phiên mới vẫn chịu IP limit.
- Frontend thử khôi phục tài khoản Firebase đã có; nếu SDK/config không hoạt động hoặc không có user, mở phiên server guest, không gọi Firebase Anonymous signup. Probe browser đã mô phỏng SDK throw; chưa chứng minh mọi tình huống CDN treo/mạng thật. Không bắt học sinh đăng nhập để khảo sát.
- Mặc định: 30 request/phút và 200/ngày/UID; 60/phút và 300/ngày/IP; cấp tối đa 3 phiên khách/phút và 10/ngày/IP; cookie TTL 86400 giây. Tên biến ở `.env.example`; parse có bounds và sai cấu hình phải dừng, không chuyển RAM unlimited. Đây là budget số request được admission, không phải hóa đơn token/tiền thực tế. Mạng trường dùng chung IP có thể bị giới hạn, cần vận hành điều chỉnh có chủ đích.
- Guest Firebase Anonymous và server guest cùng quota 8 câu trả lời thành công trên ba API. Hết quota trả **429 GUEST_LIMIT_REACHED**; member không có quota8 nhưng vẫn chịu rate/day/IP. Retry cached không tăng quota hoặc gọi lại provider. Attempt bị lỗi vẫn có thể tiêu tốn rate budget để chống spam, quota8 được hoàn nếu chưa lưu câu trả lời.
- `request_id` UUID, hash nội dung và session owner được ràng tại server. Legacy tạo session tạm nội bộ theo owner/scope/request_id, không ép khảo sát cho câu hỏi truyện. Các phiên này giữ thời hạn tạm hai giờ. UI retry cùng nội dung giữ request_id trong RAM tới khi thành công. Không lưu credentials vào storage.
- Cả member và guest dùng row lease/fencing PostgreSQL, không dùng session advisory lock hoặc giữ transaction qua provider (tương thích transaction pooling). `charge_quota=false` cho member: không tăng/giảm số câu guest trước đó. Lưu cặp tin nhắn và complete request cùng transaction; worker hết lease không được ghi đè. Giới hạn tốc độ độc lập transaction quota nên có thể tính attempt bị từ chối sau admission, nhưng không vượt quota8.
- Claim sang Google/email xác minh token đích và cookie/token khách nguồn; chuyển owner trong transaction, không xóa hội thoại, không reset quota, không cho chuyển lần hai sang tài khoản khác. Khi có request còn chạy, claim trả pending.

## Proxy và triển khai: còn gate chưa được xác minh

Mặc định chỉ dùng ASGI socket peer, bỏ qua X-Forwarded-For/X-Real-IP. Chỉ khi peer thuộc `AI_TRUSTED_PROXY_CIDRS` mới đọc chuỗi XFF từ phải sang trái, dừng ở hop không tin; từ chối chuỗi sai/duplicate field. Không cấu hình `0.0.0.0/0`. Chạy Uvicorn với **`--no-proxy-headers`** để framework không thay socket peer trước lớp bảo vệ. Đặt `AI_PUBLIC_ORIGIN` bằng origin chính xác để kiểm CSRF cookie.

Vercel có [tài liệu request headers](https://vercel.com/docs/headers/request-headers), nhưng ánh xạ header/socket của Python Runtime dự án này **chưa được kiểm thử trên Preview**. Không tự bật trust rộng để chữa rate limit. Neon transaction pooling không nên dựa vào session state; bản vá dùng row lease ([tham khảo Neon](https://neon.com/blog/inside-lubots-database-per-tenant-architecture)).

## Migration, rollout và phục hồi

`migrations/004_shared_ai_protection.sql` là migration **nguồn mới, chỉ đã chạy local fixture**: thêm cột `guest_ai_requests.charge_quota BOOLEAN NOT NULL DEFAULT TRUE` để giữ nguyên cách tính bản ghi cũ; thêm bảng hash guest-session và index TTL. Không đổi CHECK quota8/status, không DELETE/DROP hoặc tự migrate lúc startup. Không phải script idempotent: chạy lại phải dừng/rollback, không giả định an toàn bằng IF NOT EXISTS.

Trước khi xin chạy trên database thử riêng: xác nhận target và backup, kiểm schema 001/002, các ID/session/message fields đúng TEXT và các cột lease tồn tại; đối soát số lượng/quota hiện có. **Database legacy UUID cần quy trình 003 riêng, bao gồm gate request mồ côi còn mở; không dùng 004 để bỏ qua gate đó.** Sau 004 chạy `inspect_schema`, so baseline hội thoại/quota, kiểm charge_quota bản ghi cũ là true, thử các case mock trên nhánh riêng. Chưa có quyền chạy remote và chưa thực hiện bước này.

Không blind-revert về `b8cef96`: bản cũ không hiểu charge_quota=false và có thể hoàn sai quota khi còn request reserved; còn mở lại hai API chi phí không bảo vệ. Nếu cần rollback: dừng admission paid traffic, chờ/đối soát và settle lease bằng phiên bản hiểu cột mới, ưu tiên forward-fix; giữ schema/data 004, không tự DROP bảng/cột hoặc reset quota. Đây là kế hoạch, chưa thao tác vận hành.

Kết luận hiện tại: **NOT READY FOR VERCEL PREVIEW** cho môi trường dùng chung/provider thật, tới khi migration target được phê duyệt/kiểm thử, proxy mapping và cấu hình origin được xác minh, cùng Firebase/DeepSeek live test riêng được cấp phép. Không phải phê duyệt Production.
