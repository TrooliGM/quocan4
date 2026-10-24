# Task 4 — Production canary, 25/10/2026

Quyền mới: người dùng cho phép Production có kiểm soát và kiểm thử bằng dữ liệu QA riêng. Không mở tính năng chưa nghiệm thu cho mọi tài khoản. Chỉ migration additive 006 sau backup/schema check; không chạy lại 001–005, không reset quota.

Production Branch cấu hình main; deployment thực tế df1c300 / dpl_6Q6muJBTW7kK7owh4m5TJ7XgU2dN từ feat/task-3-1-video-library. Task4 kế thừa đúng nền, không có hotfix mới hơn. Không merge lịch sử main không tương thích.

Backup Neon: backup-before-task4-20261025-014632 / br-mute-mouse-az82u9fl READY, cùng project ID frosty-math-90753534/production/neondb/public; API project name thực tế la-ban-ai. có dấu chấm cuối. Đã xác minh bằng ID/endpoint và bản ghi thử riêng từ runtime Vercel. Source/backup đọc được, toàn bộ bảng cũ fingerprint/count khớp, quota không lệch. Không ghi backup. Snapshot parent LSN 0/2136F78.

Migration006 chỉ thêm bảng/index, không sửa/xóa dữ liệu cũ; guard có target Production riêng (không giả staging), được thử lại trên PG local. Operator kiểm tra TLS/metadata/schema/backup/hash và fingerprint trước/sau cùng transaction repeatable read. Rollback ưu tiên deployment cũ, giữ bảng additive và mọi dữ liệu mới; không tự reset branch hoặc phục hồi đè dữ liệu từ backup.

Canary server: ADVISOR_CONTROLLED_ROLLOUT=true, ADVISOR_TEST_UIDS có đúng một UID Firebase QA được verify thật, chặn anonymous và UID/header/query tự khai. Account khác/khách dùng stable graph/prompt/HTML/CSS/JS của df1c300. Chỉ loader và prefetch config một lần có binding UID, giữ nguyên navigation/Google flow. API profile mới chỉ dành UID allowlist. Không sửa 200 nghề/Truyện nghề.

Tài khoản QA email/password riêng đã tạo qua Firebase thật, ID token được Production xác minh; credentials mã hóa Windows DPAPI trong artifacts, không đưa Git/log/chat. Google popup chưa nghiệm thu. Brave Production chưa cấu hình nên search unavailable, không giả nguồn.

Phát hành: build Production --skip-domain (chưa gán domain), kiểm canary/runtime/AI/schema và account thường, rồi promote. Giữ nguyên Firebase/DeepSeek/DATABASE_URL Production. Overrides mới chỉ flags canary, không thay secret. Nếu nghiêm trọng rollback dpl_6Q6muJBTW7kK7owh4m5TJ7XgU2dN ngay; không rollback database phá hủy.

## Kết quả thực tế

- Production domain: https://labanhuongnghiep.vercel.app/ai-career-advisor
- Runtime commit: `fde7ed2459b948678622d79537fe48a117cddaa4`, deployment `dpl_7ZaE94zBvSeBAps9HgTPkak9Q1aT`, Vercel READY; alias đã đối chiếu API. Không merge main/force push. Production Branch vẫn main, phát hành bằng CLI candidate --prod --skip-domain rồi promote sau kiểm thử.
- Canary chỉ 1 UID Firebase QA email/password, không lưu UID/email/password trong Git. Tài khoản bình thường/khách giữ graph/prompt/UI df1c300. Người dùng chưa nằm allowlist sẽ chưa thấy Task4. Chưa mở đại trà.
- Migration006 COMMIT sau kiểm target, backup READY/readback và đối chiếu SHA256 `9bf716b221e0da35befb6d63a1d453d2a873dd7a1a52603ddeb7eeb651ef4515`. Toàn bộ bảng cũ fingerprint/count không đổi trong cùng transaction; quota mismatch0. Bảng mới rỗng lúc COMMIT; sau đó chỉ dữ liệu QA có xác nhận. Không chạy 001–005. Lần chạy đầu rollback do script hậu kiểm đếm nhầm số cột; sửa assertion danh sách 12 cột và chạy lại thành công, không đổi SQL migration.
- Build/package PASS: 97 file runtime, stable fallback đủ, secrets/artifacts/tests/docs không đóng gói. Runtime/checks trước promote PASS; browser baseline candidate bca4559 PASS, diff tới fde7ed2 chỉ parser xưng hô và 1 regression test. Runtime/policy của candidate cuối đã kiểm lại.
- Firebase thật email/password: REST ID token được backend verify và SDK Chrome đăng nhập thật; không fixture. Chrome domain chính thức desktop1440/mobile390: header, history, dialog, proposal evidence, accept/delete đúng mục QA, logout về stable Guest PASS, 0 exception. Google popup thật chưa kiểm; không ghi PASS thay.
- DeepSeek LIVE: khảo sát 5 câu, 8 đề xuất evidence đúng, 12.5s gồm phân tích và trả lời. Không lưu hồ sơ tự động. Chấp nhận 1 mục, sửa/version409, retry không ghi đè, reload/Neon read-only đối chiếu đúng. Sau promote DeepSeek domain chính thức trả lời thật khoảng3.7s (mẫu, không cam kết latency chung).
- Xưng hô: phát hiện phủ định “không dùng chị–em” có thể ghi đè “tôi–bạn”; sửa parser, 3 unit PASS. Hai lượt DeepSeek thật liên tiếp tự xưng Tôi PASS. Các câu hỏi kiểm chứng dữ liệu năm khi thiếu Brave trả unavailable/sources=[] và nói chưa xác minh, không giả nguồn.
- Guest trên Production candidate dùng đúng database Production và dữ liệu thử riêng: 8 lượt AI thật thành công, câu9 HTTP429; duplicate không thêm lượt; hai request cuối ở hai phiên đồng thời trả200/429, Neon used_questions=completed=8. API advice/story dùng chung quota; IDOR404, giả UID không bật Task4, thiếu identity401, Origin ngoài403, cookie Secure/HttpOnly/SameSite=strict. Không flood Production để đo rate; kế thừa kiểm thử trọng tâm PG shared-rate đã PASS.
- Chỉ kiểm lại bài bị ảnh hưởng, không Super Board toàn diện. 24 kiểm thử local trọng tâm trước checkpoint canary PASS; 3 policy unit sau sửa PASS. Không cộng các lượt chạy trùng thành số test duy nhất.

## Lỗi và giới hạn còn lại

**36 PASS / 16 BLOCKED / 1 FAIL**, đủ53 yêu cầu, xem task-4-requirements.md. Đây là Production canary đang hoạt động, **NOT READY FOR GENERAL RELEASE**.

- ID23 FAIL: phép thử opt-in bằng một giá trị hồ sơ QA mới, OFF không xuất hiện giá trị đó, nhưng ON vẫn trả chưa nhận được hồ sơ. Dữ liệu đã lưu/đọc đúng, bật/tắt metadata hoạt động; nguyên nhân ở luồng ngữ cảnh/model CHƯA được xác minh. Không suy đoán đã sửa. Mục QA đã được trả về giá trị cũ và use_profile OFF; chỉ QA có thể gặp chức năng này. Không thấy mất dữ liệu/cross-account access, nên không phải sự cố buộc rollback toàn website. Cần chẩn đoán riêng trước mở rộng.
- Brave LIVE BLOCKED vì chưa có key được cấp phép. Không đổi secret hoặc giả nguồn.
- Google popup Task4 BLOCKED: cần tài khoản Google QA được chủ tài khoản thao tác và thêm UID đã verify vào allowlist theo lần phát hành được duyệt; không gửi mật khẩu/token vào chat. Chưa có bằng chứng Google Task4 giữ khảo sát, dù hotfix cũ không bị thay và email/password/history đã thử thật.
- Chất lượng tư vấn mở rộng, khảo sát mơ hồ/mâu thuẫn, Guest-profile claim Task4 và kiểm thử đối kháng LIVE còn BLOCKED. Không coi một mẫu tốt là đạt mọi yêu cầu.
- Tài khoản QA và dữ liệu tổng hợp dùng riêng để test; không ghi đè hội thoại/hồ sơ học sinh. Không reset quota. Xóa qua UI chỉ đúng mục QA vừa chấp nhận để kiểm thử xóa, không đụng dữ liệu cũ.

## Rollback

Deployment ổn định: `dpl_6Q6muJBTW7kK7owh4m5TJ7XgU2dN`, source df1c300. Khi lỗi nghiêm trọng: `vercel rollback dpl_6Q6muJBTW7kK7owh4m5TJ7XgU2dN --scope khkt3 --yes`, kiểm lại alias/domain. Giữ bảng006 và dữ liệu mới, không DROP/reset/restore đè. Backup Neon READY ở trên dành khôi phục chọn lọc có phê duyệt nếu thật sự cần; không tự ghi nhánh backup. Hậu kiểm hiện không phát hiện sự cố nghiêm trọng nên chưa dùng rollback.

Bằng chứng local (artifacts không commit): task4-production-backup.json, task4-production-migration.json, task4-production-promotion.json, task4-live-profile.json, task4-live-policy.json, task4-live-guest.json, task4-browser-production.json, task4-official-live.json, task4-live-personalization.json; ảnh task4-live-production-1440.png, task4-live-production-390.png, task4-live-profile-production.png. Payload/credentials thử mã hóa Windows DPAPI, không log/Git.
