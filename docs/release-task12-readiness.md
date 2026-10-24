# Tích hợp Nhiệm vụ 1 + 2 — checkpoint 24/10/2026

**STOP trước PR/merge/phát hành Production.** Mã tích hợp và kiểm thử local đạt, nhưng database Production chưa tương thích và ngoại lệ legacy chưa được đối soát/phê duyệt. Không kết luận đã sửa xong DATABASE_URL.

## Nền và bảo toàn Git

- Repository `TrooliGM/quocan4`, default branch GitHub vẫn `backup-la-ban`.
- `origin/main`: `346e9757dec7ebce43f74b815ccb138758cfa077`; `backup-la-ban`: `cf4d55d`; remote `fix/vercel-ai-postgres`: `5220429`; local nhánh đó có thêm commit rỗng `99ace5f`. Không thay đổi các nhánh này hoặc các file đang chỉnh ở checkout chính.
- Domain `labanhuongnghiep.vercel.app` hiện trỏ deployment **`dpl_2muzPNTXB2ArmPDXXQjgXoNNmeYm`**, URL `quocan4-mkqxkvbvu-khkt3.vercel.app`, target Production, READY; Git SHA **`7c07d335091e93e7310432b1312172a2379e7302`**, ref `integrate/premium-preview`. Đã đọc từ Vercel API; không lấy tên nhánh cấu hình thay cho SHA đang chạy.
- Tạo worktree `D:/khkt/.claude/worktrees/release-task12`, nhánh `integrate/task-12-production` từ đúng `7c07d33`; fast-forward toàn bộ bảy commit đến `349ff92`. Tree ứng dụng đồng nhất nhánh Nhiệm vụ 2, không cherry-pick thiếu phần và không ghi đè checkout chính.
- Sáu nhánh backup local: `backup/release-20261024-main-346e975`, `backup/release-20261024-backup-la-ban-cf4d55d`, `backup/release-20261024-fix-local-99ace5f`, `backup/release-20261024-fix-remote-5220429`, `backup/release-20261024-task-2-349ff92`, `backup/release-20261024-production-7c07d33`. Chưa push backup hoặc candidate.
- Migration `002_guest_quota.sql` giữ nguyên blob **`dcf61fa79d799cb1bce7b38d2c3573ed547c279a`** so với nền Production. Không chạy lại 001/002 trên Neon.

## Kết quả database thực tế

Đọc metadata/counts bằng kết nối có `default_transaction_read_only=on` từ lúc mở kết nối, xác minh `transaction_read_only=on`, database `neondb`. Không đọc nội dung hội thoại ra báo cáo.

| Môi trường đã xác minh | Kết quả |
|---|---|
| `la-ban-ai.` / `production` (`frosty-math-90753534`, `br-delicate-wave-azxcb1jo`) | Hai cột `guest_ai_requests.request_id` và `session_id` vẫn UUID, không đúng TEXT yêu cầu. Thiếu bảng `advisor_guest_sessions` và cột `charge_quota` của 004. Không đủ prerequisite cho 004. |
| `la-ban-ai.` / `test-migration-5220429` | Vẫn schema legacy UUID, thiếu một số bổ sung của 002; chỉ đọc, không sửa nhánh này hoặc backup. |
| `la-ban-preview` / `ticket-7-premium-preview` (`silent-snow-82216939`, `br-hidden-fire-ao3sed5z`) | Nhánh riêng không mặc định, nguồn parent-schema, đủ prerequisite TEXT/lease. **Đã chạy đúng 004 một lần** theo yêu cầu kiểm thử staging. Sau đó schema ready=true; dữ liệu cũ giữ nguyên counts và checksum. |

Production: 4 hội thoại lưu, 5 phiên tạm, 6 guest requests, 4 guest usage; 0 claim. Có **1 request completed thiếu phiên thuộc owner gốc trong cả hai bảng**; không có quota mismatch. Không có bằng chứng mới xác nhận nguyên nhân thiếu phiên. Không tự coi là đã xóa hợp lệ, không reset quota, không phục hồi nội dung đã có thể bị người dùng xóa.

Staging trước/sau 004: 2 hội thoại, 5 phiên tạm, 8 requests, 3 usage, 0 claim, 2 rate rows; tất cả counts/checksum cũ khớp, 8 requests cũ có charge_quota=true, bảng guest cookie mới rỗng. Không chạy migration hoặc SQL ghi nào trên Production/backup.

## Lỗi DATABASE_URL: điều đã biết và giới hạn

Trong mã Production, thông báo người dùng cung cấp thuộc `StorageConfigurationError`; ở nền này, `get_store()` từ chối URL trống/không có scheme PostgreSQL hợp lệ trên Vercel. Đây không phải bằng chứng để tạo lại database hoặc chạy lại migration.

Đã xác nhận tên `DATABASE_URL` hiện có trong scope Production và snapshot deployment đang chạy. Giá trị sensitive không được in hoặc sao chép; **chưa xác minh được giá trị thực đang bind đúng endpoint Production và đúng định dạng**. Không được kết luận biến thiếu chỉ dựa vào thông báo UI, cũng không được kết luận hợp lệ chỉ vì tên biến tồn tại. Truy vấn log đọc gần nhất không tái hiện lỗi; chưa có kiểm tra request xác thực trên Production để chốt nguyên nhân cụ thể. Không sửa code theo giả định, không đổi biến Production trong lượt này.

Độc lập với cấu hình URL, schema Production nêu trên chắc chắn chưa đạt release mới. 004 chỉ bổ sung bảng/cột, **không chuyển UUID sang TEXT và không giải quyết request mồ côi**.

## Kiểm thử và giới hạn

- **31/31 backend PASS** thực chạy từ worktree tích hợp: migration local, shared protection 15 case, Task 1 và Task 2; mô phỏng Firebase/provider, PG local tách biệt, khóa kết nối ngoài loopback trong runner.
- **004 staging PASS** với schema và checksum trước/sau nêu trên.
- Python AST 48 file, JS syntax 3 file, parity 3 cặp HTML và Git diff check PASS. Tree ứng dụng trước checkpoint tài liệu đồng nhất `349ff92`; kế thừa 197 PASS trước đó, không chạy lại toàn bộ Super Board.
- Chưa build Vercel cho candidate tích hợp, chưa kiểm Firebase/DeepSeek thật cho candidate, chưa xác minh proxy/origin trên runtime Vercel. Không gán test mock thành PASS live. Lần thử Preview trước ở `349ff92` bị Vercel chặn quyền tác giả trước build; chưa xác nhận gate đó đã hết.

## Đường đưa vào main và điều kiện tiếp tục

`main` và feature không có common ancestor. Chưa tạo PR vì gate dữ liệu chưa đạt. Phương án ít rủi ro: giữ nhánh ứng dụng từ Production để kiểm thử; khi đủ điều kiện, tạo nhánh đưa vào main từ **origin/main**, đối chiếu/áp patch đã review từ main đến nền Production rồi phần Task 1+2. Xác nhận tree ứng dụng cuối đúng candidate, rà main-only changes nếu main tiến thêm; không force-push, reset main hoặc nối lịch sử máy móc. Hiện đối chiếu không có file của main bị candidate xóa. Không tự đổi default branch GitHub.

Trước phát hành cần: đối soát/phê duyệt xử lý chính xác request legacy thiếu phiên; kiểm đường nâng UUID→TEXT trên nhánh test với bảo toàn định danh/ràng buộc/quota; xác minh binding DATABASE_URL Production đúng branch/database qua kênh vận hành an toàn; kiểm code cũ/mới với schema nâng cấp; xác minh Firebase/DeepSeek, proxy/origin và quota trên runtime riêng. Chỉ sau các gate này mới PR/main và lịch phát hành, tránh auto-deploy main trước database sẵn sàng.

Điểm khôi phục code/deployment đã ghi ở trên; backup Neon có sẵn chưa bị sửa. Sau khi bản mới phát sinh member lease `charge_quota=false`, không blind rollback về 7c/b8 khi còn request reserved: cần dừng admission, đối soát/settle bằng code hiểu cột mới, ưu tiên forward-fix; giữ schema và dữ liệu, không DROP/reset. Xem `docs/shared-ai-protection.md`.

Bằng chứng vận hành cục bộ (ignored, không có secrets): `D:/khkt/artifacts/release-integration-20261024/`; kết quả backend: worktree này `artifacts/qa/backend-*.json`. Không push, PR, merge main, deploy hoặc bắt đầu Nhiệm vụ 3.
