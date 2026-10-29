# Checkpoint video 200 nghề — 29/10/2026

## Nguồn để tiếp tục

- Repository: `TrooliGM/quocan4`.
- Worktree: `D:\khkt\.claude\worktrees\career-video-pilot`.
- Nhánh: `feat/career-video-pilot`.
- HEAD/base: `1a1a4c48a6221c7850496038064c066b91aea701`.
- Toàn bộ bản vá hiện tại **chưa commit, chưa stage, chưa push/merge**. Checkpoint này là tài liệu và bản sao local, không phải Git commit.
- Không dùng checkout gốc `D:\khkt` để thay thế worktree này.

## Đã thực hiện

- Tìm nguồn qua toàn bộ 193 nghề thiếu từ pilot; đã bổ sung và biên tập dữ liệu cho **200/200 nghề**, mỗi nghề một YouTube ID khác nhau. Catalog có 201 bản ghi: 200 verified và một bản Chef/VTV7 cũ vẫn pending, không công khai.
- Kế thừa 7 nguồn pilot; 193 nguồn mới có quyết định rà nội dung và bằng chứng Chrome thật: đúng video ID, `PLAYING=1`, thời gian tăng. Không dùng HTTP 200/oEmbed/thumbnail thay cho phát thật.
- Có nhiều nguồn bị loại hoặc thay thế vì sai nghề, thiếu định danh, chỉ giới thiệu chung, thiếu phụ đề hoặc chưa phát được. Không gán cùng video cho nhiều nghề.
- Rà mô tả nguồn, hai đoạn hình và phụ đề/chữ hiện được ở đầu–giữa; ghi thời gian thực của mẫu. **Chưa nghe/xem toàn bộ video**, không khẳng định đã kiểm duyệt trọn nội dung/âm thanh.
- Thêm metadata phụ đề và phạm vi đã rà; giữ 200 truyện và hai lựa chọn Xem video/Đọc truyện. Không sửa AI/Firebase/quota/database/migration.
- Tối ưu serialize metadata công khai: một lần dump cho mỗi video.
- Sửa test AI theo cảnh đang dùng hợp đồng cũ để kiểm tra ngữ cảnh được chuyển đến shared answer graph; không sửa mã AI để làm test đạt.

## Bằng chứng và dữ liệu tiến độ

- `data/career-videos.json`: catalog sản phẩm hiện tại.
- `docs/video-research/progress.json`: đủ 200 nghề, truy vấn và các ứng viên đã tìm.
- `docs/video-research/shortlist.json`: nguồn được chọn gần nhất cho 193 nghề mới.
- `docs/video-research/content-review.json`: quyết định rà nội dung, lý do, nhiệm vụ, mức rà và mẫu theo nghề.
- `docs/video-research/playback.json`: kết quả kiểm tra thật cho các ứng viên; gồm cả nguồn bị loại. Không lấy tổng PASS ở đây làm số video công khai.
- Các `playback-*-attempt*.json` và `treasury-first-attempt.json`: giữ kết quả trước khi thử lại, không xóa lịch sử lỗi.
- `docs/video-research/integration-receipt.json`: lượt tích hợp gần nhất; số added chỉ tính lượt chạy cuối, không phải toàn đợt.
- Bằng chứng 7 nguồn cũ: báo cáo `docs/career-video-pilot.md`, `artifacts/video-pilot-browser.json`, `artifacts/baseline/video-pilot-browser.json`.
- Ảnh, metadata thô, contact sheet và helper triển khai nằm trong `artifacts/video-research/` và `artifacts/`; không đưa cả thư mục này vào Git/deployment.

## Kiểm thử đã chạy

| Nhóm | Kết quả thực tế |
|---|---|
| Video, truyện, thư viện nghề — Python với PostgreSQL local | 32 PASS, 413 subtests PASS |
| Truyện/API protection/rollout/navigation — PostgreSQL local | 34 PASS; có phần giao nhau với nhóm trên, không cộng thành 66 test độc lập |
| JavaScript `tests/stories2.test.mjs` | 4 PASS |
| `node --check public/assets/stories.js` | PASS |
| `git diff --check` | PASS tại lượt kiểm tra trước checkpoint |
| Dry-run Vercel | PASS, đúng worktree, 105 file; loại secrets/docs/tests/scripts/artifacts |
| Database staging dùng cho Preview | PASS: xác minh project/branch/endpoint, TLS, `neondb`, role, schema bằng kết nối chỉ đọc; không migration |
| Phát nhúng trên Preview mới đủ 200 | **CHƯA kiểm thử** |
| Desktop/mobile, Back/Forward trên Preview đủ 200 | **CHƯA kiểm thử**; không lấy QA pilot thay kết quả mới |
| Firebase popup/DeepSeek LIVE trên Preview mới | **CHƯA kiểm thử**; mã liên quan giữ nguyên, không tuyên bố LIVE PASS |

Lần chạy Python đầu có một lỗi test kiểm kê mới (đọc nhầm `career_id` thay `id`) và một test scene dùng cấu trúc trước khi hợp nhất pipeline; đã chỉnh test và chạy lại đạt như trên. Không sửa backend AI.

## Preview hiện có

- Bản 199 nguồn trung gian: `https://quocan4-6x12fj8tj-khkt3.vercel.app`, deployment `dpl_FJ2ymGbTdumKVeF375a7zxpMdXuQ`, READY.
- Bản upload đủ 200 gần nhất: `https://quocan4-qw4kjv0wi-khkt3.vercel.app/mot-ngay-lam-viec`, deployment `dpl_DfarPXsrAJjGpgbGWh2qiVZ4q6DH`, READY theo CLI receipt.
- **READY chỉ xác nhận build; chưa nghiệm thu giao diện/runtime/bản mã thực tế trên Preview này. Chưa coi đây là bản bàn giao cuối.**
- Đã dùng cấu hình đầy đủ Preview và database staging có sẵn: nhánh `task41-preview-schema-20261025`, database `neondb`; không dùng các override tắt AI/auth/database của pilot.
- Cấu hình/kiểm tra nằm ở helper local `artifacts/full-video-preview.py`; thông tin xác thực chỉ đọc từ kho DPAPI sẵn có, không ghi vào checkpoint.
- Không thay đổi Production hoặc database Production; chưa phát hành chính thức.

## Lỗi đang biết — phải xử lý trước bàn giao

Một số chuỗi tiếng Việt được sinh từ PowerShell pipe bị chuyển dấu thành `?` trong **dữ liệu thực sự**, khác với việc PowerShell chỉ hiển thị UTF-8 sai:

1. `review_scope` và `subtitle_note` của 7 video kế thừa pilot.
2. `description`/`relevance_notes` và một số trường ghi chú/nhiệm vụ của Ngân quỹ, Phát triển nông thôn trong catalog và `content-review.json`.

Đã phát hiện bằng kiểm đếm dấu hỏi trong JSON; **chưa sửa**. Preview đủ 200 nói trên có thể đang chứa các chuỗi lỗi này. Cần sửa bằng file Python UTF-8 tạo qua `apply_patch`, không dùng literal tiếng Việt qua PowerShell stdin; xác minh dữ liệu, rồi deploy lại Preview. Không che lỗi bằng thay toàn bộ dấu `?` vì tiêu đề/câu hỏi hợp lệ có thể chứa dấu hỏi.

Hai video kế thừa Lập trình viên/Đầu bếp có bằng chứng pilot PLAYING thật, nhưng lần bulk mới nhất chưa xác nhận lại khởi chạy; đây là **kết quả chưa xác nhận**, không kết luận bị xóa/chặn nhúng. Cần kiểm lại trên Preview mới và ghi đúng trạng thái.

## Việc tiếp theo

1. Sửa đúng các trường tiếng Việt lỗi mã hóa; rà lại ngôn ngữ/phụ đề theo nguồn và giữ nguyên URL/ID.
2. Hoàn thiện CSV kiểm kê đủ 200 nghề với URL, tiêu đề, kênh, ngôn ngữ/phụ đề, lý do phù hợp, phạm vi rà, bằng chứng nhúng; CSV pilot cũ không đại diện số liệu mới.
3. Kiểm thử bị ảnh hưởng, deploy lại Preview từ đúng bản đủ 200 đã sửa. Không dùng override pilot; không tạo DB/migration.
4. Kiểm API catalog/video và đối chiếu nguồn upload; thử phát trên hostname Preview, kiểm desktop/mobile, tìm/lọc, hai nút, truyện, Back/Forward/cùng tab, không phát sinh lượt AI do điều hướng.
5. Kiểm tra cấu hình AI/Firebase còn hoạt động; báo rõ luồng LIVE nào chưa kiểm, không đổi thành demo hoặc tự ghi PASS.
6. Cập nhật báo cáo cuối với số nguồn/nhúng PASS và trường hợp chưa đạt. Chỉ bàn giao Preview, **không commit/push/merge/Production** theo phạm vi hiện tại.

Không chạy lại toàn bộ phần tìm nguồn đã lưu, không tự khởi động Super Board/agent và không bắt đầu lại từ pilot 5 nghề.
