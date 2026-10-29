# Kết quả phát hành video 200 nghề — 30/10/2026

Đã xác minh bản mới trên **https://labanhuongnghiep.vercel.app/mot-ngay-lam-viec**.

- Deployment: **`dpl_AF4FHHHTCci7dGNLuvyiuCDqMojk`**, READY, target production; alias domain chính trỏ đúng ID.
- SHA đã phát hành: **`92703d34cdfacff7aa20a7ca37ae092ed3bd73bc`**. Merge giữ main trước đó `1a1a4c48a6221c7850496038064c066b91aea701` và feature hậu kiểm `473b79905d10cdfac5f375e5fda532529ddb1249`.
- Nguồn mã đã kiểm: `2366ad42a4d9e4130215db999515eaea09dadad1`, Preview `dpl_4kmjZ6KBTQFj3qni4uQedJGgUhtt`. Cả 100 file upload Production khớp source Preview; tích hợp chỉ thêm tài liệu/bằng chứng, không thay mã chạy.
- Rollback trước phát hành: **`dpl_Gqr6yuuyfyurkBYZJEVuFaqjBs6Z`**, READY, URL `quocan4-fkx0amrhj-khkt3.vercel.app`. Deployment cũ đã có200video nhưng catalog còn ghi chú lỗi; không dùng mốc rollback cũ hơn trong báo cáo lịch sử.

## Neon MCP và dữ liệu

Đã bật lại đúng server hiện có, OAuth bằng `codex mcp login neon`; lượt đầu hết hạn callback, lượt sau thành công. Đã đọc project `frosty-math-90753534` và database `neondb` qua app-server MCP và công cụ Neon trực tiếp trong phiên. Server giữ quyền chỉ đọc. Không đổi URL website, tạo database, reset hoặc chạy migration; không ghi credentials vào Git/tài liệu.

Candidate Production dùng **environment Production hiện có**, `--prod --skip-domain`, không truyền override hoặc DATABASE_URL Preview. Chỉ chuyển domain sau khi cổng đạt. MCP SQL chỉ đọc trên nhánh Production `br-delicate-wave-azxcb1jo` xác minh đúng hội thoại tổng hợp QA, owner, câu trả lời và số tin được runtime candidate ghi qua API sản phẩm. Không đọc hội thoại học sinh hoặc lấy connection string qua MCP. Bindings environment project trước/sau không đổi.

## Kết quả và phạm vi bằng chứng

| Kiểm tra | Kết quả/phạm vi |
|---|---|
| Google popup thật bằng tài khoản thử, phân tích/chat DeepSeek và retain/reload | PASS trên alias Preview trỏ đúng bản đã kiểm; không đổi Firebase domains |
| Member Firebase thật, DeepSeek, retain/fresh client và browser reload desktop/mobile | PASS Preview và domain Production; chat mới trên domain chính 4,51 giây, pipeline task41 |
| Guest đủ8 lượt, lượt9 HTTP429, duplicate không trừ thêm | PASS Preview bằng một Guest cấp thông thường, không reset/thay danh tính vượt hạn mức |
| Guest trên candidate và web chính | PASS cùng Guest thử riêng: dùng1/8 tại candidate, dùng2/8/còn6 sau promote; browser reload cùng hội thoại PASS |
| Catalog Production | 200 nghề, mỗi nghề một video công khai; catalog giữ một ứng viên Chef pending không công khai |
| Chín video sửa ghi chú | API khớp commit và hiển thị tiếng Việt đúng; truyện vẫn mở được |
| UI web chính | Desktop1440/mobile390, tìm không dấu/không kết quả, lọc đúng nhóm, Video/Truyện, cảnh tiếp, Back/Forward cùng tab PASS; 0 lỗi JavaScript |
| Video mẫu mới trên web chính | 3/3 PASS: Lập trình viên `_WQ_VV4pXPc`, Ngân quỹ `AQz3pSPYk0k`, Phát triển nông thôn `4I_GSf3nWaU`; đúng ID, PLAYING và thời gian tăng |
| Bằng chứng phát đầy đủ | Kế thừa200/200 PASS từ `dpl_DfarPXsrAJjGpgbGWh2qiVZ4q6DH`; 197video chưa phát lại trên Production, không tuyên bố200/200 LIVE mới |
| AI/auth/quota/Hồ sơ | Cấu hình LIVE giữ nguyên, API Hồ sơ410, không khôi phục Hồ sơ; không reset quota/database hoặc sửa biến dịch vụ |

Trình kiểm thử Google ban đầu giả định login vào thẳng chat và chưa bấm xác nhận lưu; đã sửa helper đi đúng CTA/đồng ý lưu và hoàn tất bằng phiên Google thật. Không sửa website để làm kiểm thử đạt. Không tìm lại nguồn hoặc chạy lại toàn bộ kiểm thử khi mã chạy không đổi. Chưa xem/nghe trọn nội dung video; không kiểm lại popup Google trên Production trong lượt hậu kiểm.

## Bằng chứng và rollback

`docs/video-research/video-production-release.json` tổng hợp deployment/commit/cổng candidate/hậu kiểm; `video-production-database-proof.json` chỉ chứa kết quả đọc QA dạng boolean, `video-production-smoke.json` lưu kiểm video/UI mới, `video-release-production-member.json` và `video-release-production-guest.json` lưu browser reload. Các báo cáo Preview/Neon/Google đã được commit trong lịch sử main. Artifacts/profile trình duyệt/DPAPI và credentials không được upload.

Không ghi nhận hồi quy nghiêm trọng, chưa cần rollback. Nếu phát sinh hồi quy do bản mới, rollback deployment của cùng project về `dpl_Gqr6yuuyfyurkBYZJEVuFaqjBs6Z`; không phục hồi/reset database, quota hoặc force-push. Main giữ `git.deploymentEnabled.main=false`. Tài liệu hậu kiểm được lưu bằng commit riêng sau mã phát hành; không triển khai lại khi chỉ đổi tài liệu, SHA mã chạy vẫn là92703d3 nêu trên.
