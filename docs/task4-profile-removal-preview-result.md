# Preview gỡ Hồ sơ — kết quả thực tế 28/10/2026

## Phiên bản đang xem thử

- **URL:** https://quocan4-1ythgz1nr-khkt3.vercel.app/ai-career-advisor
- **Deployment:** `dpl_9vsD1BPu6FEjodgHKuevpt5BboD4`, **READY**, môi trường Preview (Vercel target null, không phải Production).
- Project/team: `khkt3/quocan4` đã xác minh qua control plane.
- Nguồn: đúng `D:\khkt\.claude\worktrees\task4-remove-profile`, nhánh `feat/task4-remove-profile`, base `1a534b186a9a53aedc7b94d3a01a2d4f6a3b21b4`; **có bản vá chưa commit**. Không lấy checkout D:/khkt hoặc GitHub main làm mã thay thế, không tạo nhánh GitHub.
- Dùng CLI **65.4.0** deploy Preview trực tiếp; không commit/push/merge, không dùng --prod/promote/rollback. Có thể cần đăng nhập Vercel để vượt Deployment Protection; không tắt bảo vệ.

## Hạ tầng cũ đã tái sử dụng

Đã đọc metadata Neon và kết nối **chỉ đọc** trước khi thử ghi: project ID `frosty-math-90753534` (tên thực tế `la-ban-ai.` có dấu chấm), branch **task41-preview-schema-20261025** / `br-morning-tooth-aznv081q`, database **neondb**. Đối chiếu hostname trong cấu hình staging được bảo vệ với endpoint/branch trên Neon; role Preview và TLS khớp; schema check PASS. Branch khác Production `br-delicate-wave-azxcb1jo`.

Không tạo database/schema mới, không reset hoặc chạy migration. Tái sử dụng cấu hình staging đã có, truyền DATABASE_URL **chỉ cho deployment Preview này** từ kho cấu hình mã hóa; không in giá trị, không sửa binding env project. Firebase/DeepSeek kế thừa cấu hình Preview hiện có; Search provider DDGS ở deployment Preview. Không sao chép secrets Production.

CLI65.4 ban đầu tự chọn upload base D:/khkt ngay cả khi truyền đường dẫn tuyệt đối. **Dry-run đã chặn**, chưa upload sai thư mục. Ghim metadata project hiện hữu trong `.vercel/project.json` local (bị ignore) khắc phục việc chọn root. Dry-run tiếp theo chứng minh base chính xác task4-remove-profile, **105 file**, có survey-result.js, không có profile-panel.js hoặc dotenv/artifacts/tests/docs/scripts/secrets. Không tạo project hoặc thay liên kết của checkout khác.

## Lỗi phát sinh đã xử lý trong phạm vi

Preview đầu tiên `dpl_6B5tA47ZpHzhprC6pWMPZEjQHcSS` build/giao diện PASS, nhưng phân tích khảo sát thật thất bại với mã **incompatible_profile_area**. Đây là lỗi hiện tại có bằng chứng từ analysis job, không đồng nhất với Historical ValidationError cũ.

Schema sinh đầu ra còn yêu cầu mô hình phân loại tám area dành cho Hồ sơ đã gỡ, dẫn đến bất tương thích với category. Sửa tối thiểu trong `advisor/survey_analysis.py`: schema **gửi model** yêu cầu `area=null`, bỏ lời nhắc phân loại tám area; vẫn giữ sáu category và dữ kiện có căn cứ. Validator dữ liệu legacy và kiểm tra evidence **không bị nới lỏng**; area không hợp lệ vẫn bị từ chối. Không đổi schema PostgreSQL hay sửa kết quả cũ.

Thêm regression trong `tests/test_analysis_validation.py`; **8/8 PASS**, gồm area legacy sai vẫn bị từ chối và output schema mới chỉ nhận null. Kế thừa những nhóm local đã PASS không bị ảnh hưởng (176 ca trước đó, thêm 1 ca mới), không chạy lại Super Board. Sau sửa, deploy Preview mới nêu trên từ đúng worktree.

## Kiểm thử Preview

| Điều kiện | Kết quả thực tế |
|---|---|
| Build | **PASS / READY** |
| Trang chủ/CTA bắt đầu khám phá, AI Chat, Truyện nghề/video, danh mục 200 nghề/12 nhóm | **PASS** |
| JS mới đúng bản vá, không có nút/modal/công tắc Hồ sơ, giữ xóa dữ liệu sidebar | **PASS** |
| API Hồ sơ cũ với danh tính hợp lệ trả410; token sai/API cũ trả401; đường dẫn riêng tư404; quyền sở hữu404/Origin403 | **PASS** |
| Member Firebase SDK đăng nhập email/password thật bằng tài khoản QA tổng hợp có sẵn | **PASS**, không phải popup Google |
| Hoàn thành 5 câu qua UI, lưu đúng session và khởi chạy phân tích tự động | **PASS** trên Preview đầu; frontend mới giữ nguyên hash |
| DeepSeek phân tích thật sau bản sửa, explicit retry cùng survey request_id | **PASS**, 8,11 giây, **3 hướng nghề**, evidence đúng câu khảo sát |
| Retry kết quả đã hoàn thành | **PASS**, cùng trace/result, không thêm provider attempt |
| Kết quả đọc lại trong chat sau reload ở Preview mới nhất | **PASS**, 1 thẻ phân tích, 3 hướng hiển thị |
| Member lưu hội thoại lâu dài | **PASS** trên Preview đầu, giữ ID/khảo sát; đọc lại dữ liệu đã retain trên Preview mới nhất PASS, routes.py không đổi hash |
| Nghề → truyện → quay lại chat, reload, một tab, bản nháp, không gọi AI/session thêm | **PASS** trên Preview đầu; kế thừa vì frontend/routes hashes không đổi sau sửa backend phân tích |
| Desktop1440/mobile390 của Preview cuối | **PASS**, ảnh đã xem, không tràn ngang, 0 lỗi JS |
| Chat DeepSeek thật + DDGS | **PASS**, HTTP200, 14,94 giây, search_status=ok, 1 nguồn tra cứu; không dùng demo |
| Nút xóa dữ liệu | **PASS** hiển thị/xác nhận/Hủy; **không thực thi DELETE hàng loạt** trên Preview |
| Guest LIVE/quota thực tế | **BLOCKED**: cookie QA Guest cũ trả401 do hết hạn; không tạo danh tính thay thế/reset/lách hạn mức |
| Google popup thật trên Preview này | **CHƯA KIỂM THỬ**; không suy từ email/password thành PASS |

Các phép thử ghi chỉ dùng một hội thoại của Member QA tổng hợp sẵn có trên staging đã xác minh. Lượt phân tích đầu lỗi được retry **cùng session/request_id**, không tạo mới để lách ngân sách. Các phép thử đọc/giữ lịch sử sau đó dùng lại chính dữ liệu này. Không dùng tài khoản hoặc dữ liệu học sinh thật.

HTML runtime được FastAPI chuẩn hóa CRLF→LF; đã so sánh nội dung sau chuẩn hóa. JS được đối chiếu SHA-256 byte-for-byte với bản local. Không nhầm khác biệt xuống dòng với mã cũ. Bằng chứng: `artifacts/reused-db.json`, `reuse-preview-dry.json`, `reuse-preview-deploy.json`, `preview-live-check.json`, `preview-browser-check.json`, `preview-browser-final.json`, `preview-final-live.json`; ảnh `preview-removal-1440.png` và `preview-removal-390.png`. Trạng thái phiên/credentials chỉ nằm trong artifact DPAPI/Chrome profile bị ignore, không upload hoặc ghi vào báo cáo.

## Production và điểm dừng

**Chưa phát hành Production, chưa tạo Production candidate.** Guest LIVE và popup Google thật còn chưa xác minh, nên chưa đủ điều kiện tự chuyển website chính theo cổng phát hành người dùng đặt ra. Không coi READY của Preview là quyền thay Production.

Đối chiếu sau kiểm thử: alias website chính vẫn `dpl_Da9yybCwP9VnHeifXCX3Jo9YdCsd`; metadata binding env project trước/sau không đổi. Không động tới database Production, schema, quota hoặc domain, không migration, không xóa dữ liệu thật, không commit/push/merge. Historical ValidationError vẫn **root cause undetermined**; Task4 tổng thể chưa hoàn thành.

Tiếp theo: chủ dự án xem URL Preview và kiểm thử Google/Guest bằng tài khoản/phiên hợp lệ của mình còn hạn mức; nếu hết lượt thì dừng. Chỉ khi các luồng quan trọng được nghiệm thu mới dùng đúng nguồn đã kiểm thử để chuẩn bị Production candidate --skip-domain và quy trình promote/rollback có kiểm soát.
