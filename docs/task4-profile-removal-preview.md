# Preview bản gỡ Hồ sơ — BLOCKED trước deploy (28/10/2026)

**Cập nhật sau yêu cầu tiếp tục:** quyền mới cho phép tái sử dụng cấu hình staging cũ qua env riêng deployment. Đã xác minh database và deploy thành công Preview `dpl_9vsD1BPu6FEjodgHKuevpt5BboD4`: https://quocan4-1ythgz1nr-khkt3.vercel.app/ai-career-advisor . Trạng thái BLOCKED phía dưới là biên bản lịch sử, được thay bằng kết quả trong `docs/task4-profile-removal-preview-result.md`. Production chưa phát hành.

## Nguồn và quyền

Đã đọc brief và thao tác Terminal tại đúng `D:\khkt\.claude\worktrees\task4-remove-profile`, nhánh `feat/task4-remove-profile`, base `1a534b186a9a53aedc7b94d3a01a2d4f6a3b21b4`. Bản vá vẫn chưa commit/stage; không chuyển sang checkout D:/khkt hoặc main để thay thế. Các thay đổi dở được giữ nguyên.

Kiểm tra nguồn thực tế: HTML không còn nút/modal/công tắc Hồ sơ; chat.js không import/gọi module Hồ sơ; có surveyResult trong log chat; API cũ trả 410 sau xác thực; giữ nút retain và xóa dữ liệu; homepage/dữ liệu nghề/Vercel config không đổi. Báo cáo local 176 Python PASS/6 nhóm Chrome được kế thừa, không coi đó là LIVE/Preview PASS.

## Vercel và đóng gói

- CLI **65.4.0** đã cài/kiểm tra. Dùng `npx.cmd` do PowerShell chặn npx.ps1; không thay ExecutionPolicy.
- Đăng nhập có quyền; API xác minh đúng project **quocan4**, team **khkt3**, repository TrooliGM/quocan4.
- Đã chạy CLI `link --yes --scope khkt3 --project quocan4` ngay tại worktree. Luồng CLI này cập nhật `.env.local` chứa tên biến VERCEL_OIDC_TOKEN, không tạo `.vercel/project.json` như dự kiến của helper kiểm tra. Không in giá trị token.
- `.env.local`, `.vercel/` và `artifacts/` được Git/Vercel ignore. Đã kiểm tra `.vercelignore` loại trừ dotenv, credentials/service-account, key/pem, SQLite, artifacts/log thử, tests/scripts/docs và dữ liệu local; giữ các JSON danh mục/truyện cần cho ứng dụng. Không cần sửa ignore.
- **Chưa có manifest upload/build được xác minh bằng CLI dry-run**: helper dừng ở bước kiểm tra file liên kết; sau khi xác minh gate database thiếu bắt buộc, không tiếp tục deploy/dry-run hay tự cấu hình thay thế. Không ghi kiểm tra tĩnh ignore thành build PASS.

## Blocker database đã xác minh

Đã đọc **metadata** biến môi trường Vercel; không đọc/in giá trị secret. Với target Preview và gitBranch là null hoặc `feat/task4-remove-profile`, **không có DATABASE_URL**.

DATABASE_URL Preview hiện có chỉ gắn các nhánh cũ: feat/task-4-ai-advisor-3-0, feat/task-3-1-video-library, integrate/premium-preview, fix-chat-vercel và fix/vercel-ai-postgres. Chúng không tự áp dụng cho nhánh hiện tại. DATABASE_URL Production có target production riêng; không sao chép nó sang Preview.

Do đó chưa có database Preview hiệu lực cho bản này và chưa thể xác minh endpoint/branch/database thử độc lập. Không giả định các giá trị của nhánh cũ là staging an toàn, không dùng lại chúng ngầm, không tạo database hay đổi biến môi trường để vượt gate. **Dừng trước deploy theo yêu cầu bắt buộc của người dùng.**

Các biến Firebase/DeepSeek Preview dùng chung có metadata hiện diện; không coi sự hiện diện này là kiểm thử LIVE hoặc cấp quyền thử dữ liệu học sinh. Chưa có cấu hình SEARCH_PROVIDER áp dụng nhánh mới; kiểm thử DDGS LIVE cũng chưa được xác minh.

## Kết quả

| Điều kiện | Kết quả |
|---|---|
| Đúng thư mục, nhánh, base, bản vá gỡ Hồ sơ | PASS |
| CLI65.4, xác thực, project/team/repository | PASS |
| Quy tắc loại trừ dữ liệu nhạy cảm trong ignore | PASS tĩnh |
| DATABASE_URL Preview hiệu lực, database thử độc lập | **BLOCKED** |
| Manifest dry-run / build Vercel | CHƯA THỰC HIỆN |
| Preview API / desktop-mobile / Guest-Member LIVE | BLOCKED — chưa có deployment |

**Deployment ID: chưa có. URL Preview: chưa có.** Không lấy deployment cũ làm bằng chứng bản mới.

Production alias được đọc trước/sau, vẫn **dpl_Da9yybCwP9VnHeifXCX3Jo9YdCsd**, source **1a534b1**, READY ở thời điểm kiểm tra. Không deploy/promote/rollback/redeploy Production, không đổi alias/domain, không commit/push/merge hoặc tạo nhánh GitHub. Không chạy migration, không kết nối/ghi/xóa/reset database hoặc quota thật. Chỉ CLI tạo token môi trường local bị ignore; không thay cấu hình env dịch vụ Production/Preview.

Bằng chứng metadata an toàn: `artifacts/preview-release-gates.json`, `artifacts/preview-blocked.json`. Không chứa giá trị secrets.

## Điều kiện để tiếp tục

Cần cấu hình **DATABASE_URL target Preview áp dụng cho feat/task4-remove-profile**, trỏ đến database thử nghiệm đã có và được cấp phép, độc lập Production; cần xác minh project/branch/database/schema/quyền trước mọi bài test ghi. Không gửi connection string hoặc API key qua chat. Sau khi cấu hình, đọc lại binding, hoàn tất liên kết/manifest CLI, deploy Preview từ đúng worktree rồi smoke API/trình duyệt và phân biệt rõ các phần LIVE còn thiếu. Chưa có quyền tự tạo database hoặc tự thay cấu hình để giải quyết blocker trong lượt này.
