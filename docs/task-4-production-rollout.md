# Task 4 — Production canary, 25/10/2026

Quyền mới: người dùng cho phép Production có kiểm soát và kiểm thử bằng dữ liệu QA riêng. Không mở tính năng chưa nghiệm thu cho mọi tài khoản. Chỉ migration additive 006 sau backup/schema check; không chạy lại 001–005, không reset quota.

Production Branch cấu hình main; deployment thực tế df1c300 / dpl_6Q6muJBTW7kK7owh4m5TJ7XgU2dN từ feat/task-3-1-video-library. Task4 kế thừa đúng nền, không có hotfix mới hơn. Không merge lịch sử main không tương thích.

Backup Neon: backup-before-task4-20261025-014632 / br-mute-mouse-az82u9fl READY, cùng project ID frosty-math-90753534/production/neondb/public; API project name thực tế la-ban-ai. có dấu chấm cuối. Đã xác minh bằng ID/endpoint và bản ghi thử riêng từ runtime Vercel. Source/backup đọc được, toàn bộ bảng cũ fingerprint/count khớp, quota không lệch. Không ghi backup. Snapshot parent LSN 0/2136F78.

Migration006 chỉ thêm bảng/index, không sửa/xóa dữ liệu cũ; guard có target Production riêng (không giả staging), được thử lại trên PG local. Operator kiểm tra TLS/metadata/schema/backup/hash và fingerprint trước/sau cùng transaction repeatable read. Rollback ưu tiên deployment cũ, giữ bảng additive và mọi dữ liệu mới; không tự reset branch hoặc phục hồi đè dữ liệu từ backup.

Canary server: ADVISOR_CONTROLLED_ROLLOUT=true, ADVISOR_TEST_UIDS có đúng một UID Firebase QA được verify thật, chặn anonymous và UID/header/query tự khai. Account khác/khách dùng stable graph/prompt/HTML/CSS/JS của df1c300. Chỉ loader và prefetch config một lần có binding UID, giữ nguyên navigation/Google flow. API profile mới chỉ dành UID allowlist. Không sửa 200 nghề/Truyện nghề.

Tài khoản QA email/password riêng đã tạo qua Firebase thật, ID token được Production xác minh; credentials mã hóa Windows DPAPI trong artifacts, không đưa Git/log/chat. Google popup chưa nghiệm thu. Brave Production chưa cấu hình nên search unavailable, không giả nguồn.

Phát hành: build Production --skip-domain (chưa gán domain), kiểm canary/runtime/AI/schema và account thường, rồi promote. Giữ nguyên Firebase/DeepSeek/DATABASE_URL Production. Overrides mới chỉ flags canary, không thay secret. Nếu nghiêm trọng rollback dpl_6Q6muJBTW7kK7owh4m5TJ7XgU2dN ngay; không rollback database phá hủy.

Kết quả thực tế sẽ bổ sung sau kiểm thử; không tự chuyển 34 BLOCKED thành PASS.
