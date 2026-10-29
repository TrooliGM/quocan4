# Checkpoint tiếp tục — Video Truyện nghề, 29/10/2026

## Mốc chuẩn bị commit và Preview UTF-8 — 30/10/2026

- Quyền mới: commit riêng sửa tiếng Việt và tài liệu/bằng chứng video liên quan; tạo Preview từ commit cuối, không push/merge main hoặc Production. Giữ AI/auth/database/quota và thay đổi ngoài phạm vi.
- Đã rà diff: chỉ 20 trường ghi chú/nhiệm vụ của 9 video và 2 quyết định rà nguồn; phần còn lại là tài liệu/bằng chứng video. Không có thay đổi mã AI/auth/database hoặc ID/URL/video được chọn.
- Kế thừa 200/200 khởi chạy PASS từ deployment `dpl_DfarPXsrAJjGpgbGWh2qiVZ4q6DH`, không gọi đó là kết quả trên Preview mới. Chỉ smoke phần bị ảnh hưởng sau deploy; chưa có deployment mới tại mốc chuẩn bị này.
- Kết quả deployment/QA sẽ ghi sau khi có SHA và ID thực; không tự ghi trước. Tài liệu hậu kiểm có thể được bổ sung local sau commit source; SHA deployment luôn ghi theo source thực đã upload.

## Kết quả mới nhất — hoàn tất kiểm Preview hiện có, 30/10/2026

- Worktree/nhánh giữ nguyên `career-video-pilot` / `feat/career-video-pilot`, HEAD `0c9ddbb`. Không stage/commit/push/merge/deploy hoặc migration. Hai thay đổi tài liệu local ban đầu được giữ, chỉ bổ sung tiến độ vào bộ nhớ/checkpoint.
- Sửa UTF-8 local: 20 trường ghi chú/nhiệm vụ trên đúng 9 bản ghi catalog (7 pilot + Ngân quỹ/Phát triển nông thôn), đồng bộ đúng 2 bản ghi `content-review.json`. Đối chiếu HEAD xác nhận mọi trường khác, ID/URL, trạng thái duyệt và bằng chứng cũ giữ nguyên. Schema + `scripts/validate_videos.py` PASS: 201 bản ghi, 200 verified/200 nghề, 1 pending không công khai. Các trường ghi chú/nhiệm vụ của nhóm verified không còn dấu hỏi lỗi. Tên Phàng A Minh đối chiếu metadata nguồn đã lưu, không tìm lại nguồn.
- Preview đã kiểm: `https://quocan4-qw4kjv0wi-khkt3.vercel.app/mot-ngay-lam-viec`, deployment `dpl_DfarPXsrAJjGpgbGWh2qiVZ4q6DH`. Vercel metadata xác nhận base `1a1a4c4` + `gitDirty=1`, READY/target null; **không thể gọi đây là deployment của commit sạch `0c9ddbb`**. Nội dung công khai 200/200 API video khớp catalog HEAD; ba asset video khớp HEAD sau chuẩn hóa CRLF/LF. Chỉ xác nhận phạm vi đã đối chiếu, không kết luận toàn bộ source deployment giống HEAD.
- **Phát nhúng LIVE trên Preview: 200 PASS / 200 video riêng**, đúng ID, PLAYING=1, thời gian tăng. Lượt đầu 174 PASS/26 chưa xác nhận; thử lại tuần tự 26/26 PASS, giữ kết quả lần đầu trong `previous_attempts`. Kết quả cuối: **0 EMBED_ERROR, 0 PLAYBACK_UNCONFIRMED, 0 AUDIT_ERROR, 0 NOT_CHECKED**. Không xác định nguyên nhân chờ/buffering ban đầu; chưa có bằng chứng lỗi app để sửa code hoặc thay video. Đây là kiểm khởi chạy vài giây, không xem/nghe trọn nội dung hay bảo đảm nguồn sẽ luôn phát được sau này.
- Chrome desktop/mobile: tìm có dấu/không dấu/không kết quả, lọc nhóm khớp API, hai liên kết Video/Truyện, chuyển tab, cảnh tiếp, Back/Forward cùng tab, không tràn ngang PASS. 200/200 truyện mở lại được và iframe được gỡ sau khi đóng player. 0 lỗi JavaScript trong hai lượt UI. Không tải iframe trên thư viện ban đầu; trình duyệt kiểm thử chặn fetch ghi, không gọi AI để kiểm chức năng video.
- Bằng chứng mới: `docs/video-research/preview-resume-playback.json` (từng nghề + lịch sử thử), `preview-resume-source-comparison.json` (hash/CRLF), `preview-resume-ui.json` (UI bổ sung); bảng kiểm kê đủ 200 nghề `docs/career-video-preview-resume-inventory.csv` ghi URL/tiêu đề/kênh/ngôn ngữ/phụ đề/phạm vi rà và trạng thái LIVE. Ghi chú trong CSV lấy bản sửa local; không ngụ ý đã đưa bản sửa lên Preview.
- **Còn lại:** bản sửa UTF-8 chưa được triển khai nên Preview hiện có vẫn giữ ghi chú cũ. Chưa xác minh toàn bộ source deployment theo commit sạch. Chưa xem/nghe toàn bộ video; AI/Firebase/đăng nhập/database/quota và Production không được kiểm hoặc thay đổi trong lượt này. Không dùng kết quả LIVE video này để tuyên bố LIVE các phần đó PASS.
- Một lượt kiểm UI bổ sung đầu dùng nhầm selector `h3` trong helper kiểm thử; đã sửa helper thành `h2`, chạy lại PASS. Không sửa mã ứng dụng vì lỗi helper.

## Mốc tiếp tục: sửa ghi chú UTF-8 local — 29/10/2026

- Tiếp tục từ HEAD `0c9ddbb`, giữ nguyên hai thay đổi tài liệu local có sẵn.
- Đã sửa đúng ghi chú phụ đề/phạm vi rà của 7 video pilot và mô tả/nhiệm vụ/ghi chú của Ngân quỹ, Phát triển nông thôn trong catalog; đồng bộ hai quyết định trong `content-review.json`. Không sửa ID/URL, trạng thái duyệt hoặc bằng chứng phát cũ.
- Kiểm tra schema catalog PASS: 200 verified, 1 pending; các trường ghi chú/nhiệm vụ của 200 video verified không còn dấu hỏi lỗi; `git diff --check` PASS. Chưa deploy bản sửa.
- Đang xác minh Preview đã có và kiểm thử runtime. Chưa có kết quả LIVE mới; không coi nhãn verified là PASS phát nhúng trên deployment đích.

## Mốc Preview hiện có: định danh và giao diện — 29/10/2026

- Vercel API chỉ đọc xác nhận `dpl_DfarPXsrAJjGpgbGWh2qiVZ4q6DH`, hostname `quocan4-qw4kjv0wi-khkt3.vercel.app`, READY, target null (Preview). Metadata: `gitCommitSha=1a1a4c48a6221c7850496038064c066b91aea701`, `gitDirty=1`, nhánh `feat/career-video-pilot`; được upload trước commit video, không gán deployment này SHA `0c9ddbb`.
- API thư viện trả đủ 200 nghề, mỗi nghề một video. Ba asset `stories.js`, `stories-31.css`, `youtube-player.js` khớp HEAD khi chuẩn hóa CRLF/LF; không khớp byte vì xuống dòng. Bằng chứng hash/HTTP: `docs/video-research/preview-resume-source-comparison.json`. Đây là đối chiếu phạm vi video, không chứng minh toàn bộ deployment giống HEAD.
- Chrome thật: tìm kiếm, lọc nhóm, hai liên kết Video/Truyện, chuyển tab, đọc cảnh tiếp, desktop/mobile 390px, Back/Forward cùng tab PASS; không iframe tải sẵn, 0 lỗi JavaScript trong lượt UI, không fetch ghi/AI. Không kiểm thử AI/auth/database/quota.
- Đang kiểm từng video trên chính hostname Preview; ghi liên tục `docs/video-research/preview-resume-playback.json`. `NOT_CHECKED` là chưa thử, `PLAYBACK_UNCONFIRMED` là đã thử nhưng chưa đủ bằng chứng, `EMBED_ERROR` là player báo lỗi, `PASS` cần đúng ID + PLAYING + thời gian tăng. Không thay thế bằng chứng nghiên cứu cũ.
- Bản sửa UTF-8 mới chỉ ở local; Preview hiện có vẫn có thể chứa ghi chú cũ. Không deploy trong mốc này.

## Mốc phát nhúng giữa lượt — 29/10/2026

- Tại thời điểm ghi mốc: đã thử 119/200 video, 109 PASS, 10 PLAYBACK_UNCONFIRMED, 81 NOT_CHECKED, chưa có EMBED_ERROR. Số liệu đang tiếp tục cập nhật trong báo cáo JSON, không dùng mốc giữa lượt làm kết quả cuối.
- Lập trình viên `_WQ_VV4pXPc` và Đầu bếp `kXaIZNZ2HZg` đã PASS trên hostname Preview này (đúng ID, state=1, thời gian tăng); đóng đúng hai mục phát chưa xác nhận từ checkpoint cũ.
- Những trường hợp chưa xác nhận đang chờ/buffering, chưa có mã lỗi player; sẽ thử lại riêng, không tự đổi video hoặc sửa app khi chưa tái hiện lỗi ứng dụng.

## Mốc hoàn tất lượt phát đầu — 30/10/2026

- Đã thử 200/200 trên Preview: 174 PASS, 26 PLAYBACK_UNCONFIRMED, 0 EMBED_ERROR, 0 NOT_CHECKED. Không đánh đồng đã thử với phát thành công. Lượt thử lại tuần tự đang thực hiện, giữ lịch sử lần đầu.
- Đối chiếu 200/200 API video công khai khớp catalog trong HEAD; 200/200 truyện vẫn mở và iframe được gỡ sau khi chuyển sang Truyện. Metadata deployment vẫn là dirty upload trên base `1a1a4c4`, không phải một deployment gắn SHA `0c9ddbb`.
- Kiểm UI bổ sung desktop/mobile PASS: tìm không dấu, không kết quả, lọc đúng nhóm theo API, bấm cả hai liên kết Video/Truyện trong cùng trang, không tràn ngang, 0 lỗi JavaScript. Báo cáo `docs/video-research/preview-resume-ui.json`; ảnh local `artifacts/preview-resume-*.png` đã kiểm thư viện mobile và truyện desktop.

## Trạng thái Git đã kiểm tra trực tiếp

- Worktree: `D:\khkt\.claude\worktrees\career-video-pilot`.
- Nhánh: `feat/career-video-pilot`.
- HEAD: `0c9ddbbb2091de764f88832e880cb11eb766c382` — `Add reviewed career videos for all 200 careers and preserve interactive stories`.
- Working tree sạch trước khi ghi checkpoint này. Commit trên đã tồn tại khi kiểm tra; thao tác lưu checkpoint này không tạo commit, push, merge hay deployment.
- Không dùng thông tin HEAD/chưa commit trong checkpoint cũ làm trạng thái Git hiện hành.

## Dữ liệu và bằng chứng đã lưu

- Catalog: **200 video verified / 200 nghề**, các YouTube ID riêng biệt; giữ **200 truyện tương tác**. Một video Chef pending cũ vẫn không công khai.
- `docs/video-research/` giữ truy vấn, ứng viên, lựa chọn, quyết định rà nội dung và bằng chứng player thật. Tổng PASS của mọi ứng viên không phải số video đã nghiệm thu trên Preview/Production.
- Phạm vi rà: mô tả nguồn, mẫu hình và phụ đề/chữ đầu–giữa; **chưa xem/nghe toàn bộ video**.
- Kiểm thử đã ghi nhận: nhóm video/truyện/thư viện **32 PASS, 413 subtests**; nhóm bảo vệ API/rollout/điều hướng **34 PASS**, có giao nhau; JavaScript **4 PASS**. Đây là kết quả kế thừa, không chạy lại trong lượt checkpoint.
- Preview theo receipt local: `https://quocan4-qw4kjv0wi-khkt3.vercel.app/mot-ngay-lam-viec`, deployment `dpl_DfarPXsrAJjGpgbGWh2qiVZ4q6DH`, trạng thái build được ghi là READY. **Chưa hậu kiểm lại URL/runtime trong lượt này.**

## Còn phải xử lý hoặc xác minh

1. Lỗi mã hóa tiếng Việt ở một số ghi chú của 7 nguồn pilot và hai nghề Ngân quỹ/Phát triển nông thôn đã sửa và kiểm định local trong lượt tiếp tục; chưa đưa bản sửa lên Preview.
2. Đã hoàn thiện kiểm kê đủ 200 nghề và kiểm phát từng video trên Preview hiện có, kết quả cuối 200 PASS. Nếu có deployment mới cần hậu kiểm đúng deployment mới; không kế thừa tự động từ nghiên cứu hoặc Preview cũ.
3. Đã PASS desktop/mobile, tìm/lọc, hai nút Video/Truyện, Back/Forward và cùng tab trên Preview hiện có. Bản sửa UTF-8 local chưa triển khai, chưa có kiểm thử trên một deployment chứa bản sửa.
4. Báo riêng tình trạng Firebase/DeepSeek/Guest/Member LIVE; không tự đánh dấu PASS từ mock hoặc từ build READY.
5. `docs/career-video-production-release.md` có kế hoạch phát hành, nhưng chưa có kết quả deployment cuối trong tài liệu này. **Trạng thái Production/push/main chưa được xác minh lại trong lượt checkpoint; không kết luận đã phát hành từ tài liệu kế hoạch.**

## Cách tiếp tục

Ưu tiên kết quả mới nhất ngày 30/10 ở đầu file, kiểm tra Git và deployment thực tế trước thao tác tiếp. `docs/career-video-200-checkpoint.md` và `docs/career-video-production-release.md` là lịch sử, không dùng trạng thái Git/quyền phát hành cũ để thay yêu cầu mới. Kế thừa nghiên cứu, không tìm lại 193 nghề từ đầu. Lượt tiếp tục đã sửa văn bản local và kiểm Preview hiện có; không có thao tác Git xuất bản, database hoặc triển khai mới. Bước tiếp nếu được yêu cầu là triển khai bản sửa lên Preview với source được định danh rõ và hậu kiểm lại; chưa Production.

Bản sao local chỉ chứa các file mã nguồn/dữ liệu nghiên cứu được chỉ định nằm tại `artifacts/checkpoints/career-video-resume-20261029/`; không bao gồm dotenv, credentials hoặc toàn bộ artifacts.
