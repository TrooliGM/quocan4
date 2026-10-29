# Checkpoint tiếp tục — Video Truyện nghề, 29/10/2026

## ĐÃ PHÁT HÀNH VÀ XÁC MINH WEB CHÍNH — 30/10/2026

- Production: **https://labanhuongnghiep.vercel.app/**, trang video **/mot-ngay-lam-viec**; domain đã xác minh trỏ đúng **`dpl_AF4FHHHTCci7dGNLuvyiuCDqMojk`**, READY/target production.
- SHA mã đã phát hành: **`92703d34cdfacff7aa20a7ca37ae092ed3bd73bc`**, merge hai parent giữ main `1a1a4c4` và feature `473b799`. Mã chạy của commit này khớp toàn bộ 100 file Preview `2366ad42a4d9e4130215db999515eaea09dadad1`, phần khác chỉ tài liệu. Đã push main thường, không force; giữ `git.deploymentEnabled.main=false`. Tài liệu hậu kiểm có thể được commit sau mã phát hành mà không deploy lại khi không đổi runtime.
- Neon MCP đã OAuth và đọc thành công đúng project/database hiện có; các công cụ trong phiên đã hoạt động, giữ read-only. Không đổi DATABASE_URL/tạo DB/reset/migration. Production candidate dựng `--prod --skip-domain` bằng env Production hiện hữu, không env override Preview. MCP SQL chỉ đọc xác minh đúng hội thoại tổng hợp QA/owner/câu trả lời/số tin trong nhánh Production `br-delicate-wave-azxcb1jo`/neondb, không lấy connection string qua MCP hoặc đọc dữ liệu người dùng thật.
- Trước promote: candidate PASS cấu hình LIVE, auth, API Hồ sơ410, private paths404, catalog200, truyện/ghi chú mẫu, phân tích/chat DeepSeek LIVE, Member retain/readback và Guest bình thường limit8. Domain giữ rollback cho tới khi các cổng đạt.
- Sau promote trên domain chính: 200 nghề/mỗi nghề một video; 9 ghi chú sửa khớp API và hiển thị UTF-8, 9 truyện mở được; desktop/mobile tìm/lọc đúng nhóm, tìm không dấu/không kết quả, Video/Truyện, cảnh tiếp, Back/Forward cùng tab, không tràn ngang/iframe tải sẵn, 0 JS errors PASS. **3/3 video mẫu khởi chạy mới PASS** đúng ID/PLAYING/thời gian tăng. Member chat DeepSeek LIVE (4,51 giây), retain/fresh-client readback, Firebase password SDK và Chrome desktop/mobile reload cùng hội thoại PASS; Guest chat LIVE, cùng Guest từ candidate đến domain chính dùng2/8/còn6, không reset, Chrome reload PASS. Không khôi phục Hồ sơ, không thay env bindings.
- Bằng chứng Google popup thật + DeepSeek/retain/reload và Guest đủ8/câu9 HTTP429/duplicate-free đã kiểm trên Preview đầy đủ; không tuyên bố popup Google mới trên Production trong lượt hậu kiểm này. Kế thừa 200/200 video khởi chạy cũ; **197 video chưa phát lại trên Production**. Chưa xem/nghe trọn video. Không chạy lại toàn bộ QA khi source runtime không đổi.
- Rollback sẵn có: **`dpl_Gqr6yuuyfyurkBYZJEVuFaqjBs6Z`** (deployment trước phát hành, READY). Chưa cần rollback vì các cổng và hậu kiểm đạt; rollback chỉ đổi deployment, không phục hồi/reset database hoặc quota.
- Báo cáo: `docs/career-video-production-result-20261030.md`; bằng chứng mới `docs/video-research/video-production-{release,database-proof,smoke}.json`, `video-release-production-{member,guest}.json`. Không chứa credentials/UID người dùng thật. Giữ các worktree phát triển khác và thay đổi ngoài phạm vi.

## Cổng phát hành đã PASS — 30/10/2026

- Neon MCP: OAuth thành công; đã đọc `describe_project` và `list_postgres_databases` qua Codex app-server và trực tiếp công cụ Neon trong phiên. Đúng project `frosty-math-90753534`, database `neondb`, nhánh staging có sẵn. Server giữ chế độ chỉ đọc, không thay DATABASE_URL/tạo DB/reset/migration. Lượt OAuth đầu hết hạn; lượt sau hoàn tất callback. Bằng chứng `video-release-neon-mcp.json`.
- Preview đầy đủ `dpl_4kmjZ6KBTQFj3qni4uQedJGgUhtt`: Member Firebase thử riêng PASS phân tích 3 hướng DeepSeek LIVE, chat LIVE (pipeline task41, 12,16 giây), retain và đọc lại bằng client xác thực mới; Chrome password SDK thật, desktop/mobile reload cùng hội thoại PASS, 0 JS errors. Không gọi đây là Google popup.
- Google popup thật trên alias Preview có sẵn `quocan4-git-fix-chat-vercel-khkt3.vercel.app` đã trỏ đúng deployment, không sửa Firebase authorized domains hoặc Production. Người dùng đăng nhập tài khoản Google thử nghiệm; trình duyệt xác minh provider google.com, phân tích 3 hướng, chat DeepSeek LIVE, xác nhận lưu và reload cùng hội thoại PASS, 0 JS errors. Trình kiểm thử ban đầu giả định login vào thẳng chat và thiếu bấm xác nhận lưu; đã đi đúng CTA/hộp đồng ý, giữ phiên để hoàn tất. Không sửa mã website hoặc bỏ qua lỗi ứng dụng.
- Guest: đúng một danh tính cấp thông thường trên Preview, khảo sát/phân tích LIVE, đủ 8 câu dùng quota 1–8, câu 9 HTTP429, duplicate không trừ thêm, cuối limit8/used8/remaining0; không reset/thay Guest vượt quota. Chrome desktop/mobile reload cùng hội thoại và nút gửi bị chặn khi hết lượt PASS.
- Kế thừa bằng chứng video 200/200 khởi chạy trước đó; Preview sửa UTF-8 có 3 mẫu phát mới PASS, không phát lại toàn bộ. Không đổi nguồn/ID hoặc mã chạy sau `2366ad4`.
- Main remote vẫn `1a1a4c4`; đối chiếu manifest Production hiện có và Preview: 99/100 file giống, chỉ catalog cũ khác; catalog Production khớp `0c9ddbb` CRLF. Mốc rollback hiện tại **`dpl_Gqr6yuuyfyurkBYZJEVuFaqjBs6Z` READY**, không dùng ID cũ trong báo cáo lịch sử.
- Đang commit tài liệu hậu kiểm và tích hợp trên worktree riêng `career-video-production-20261030`; chỉ phát hành khi candidate dùng env Production hiện có, source khớp Preview và runtime database Production được xác minh bằng đọc qua MCP. Không mang cấu hình/database Preview sang Production.

## Mốc bắt đầu cổng phát hành Production — 30/10/2026

- Quyền mới cho phép OAuth lại Neon MCP, QA LIVE Preview và phát hành/tích hợp main sau khi cổng quan trọng đạt; không migration/reset/đổi DATABASE_URL hoặc dùng dữ liệu người dùng thật. Kế thừa bằng chứng video, không tìm nguồn hoặc chạy lại toàn bộ.
- Đã bật lại duy nhất `mcp_servers.neon.enabled=true`, giữ URL server hiện có. Khởi chạy đăng nhập OAuth bằng `codex mcp login neon`. Người dùng báo đã đăng nhập, nhưng CLI còn chờ callback; kiểm qua Codex app-server MCP status vẫn `notLoggedIn`, chưa có tools. **Chưa xác nhận Neon MCP kết nối thành công**, đang chờ hoàn tất callback cấp quyền.
- Main remote đọc trực tiếp vẫn `1a1a4c48a6221c7850496038064c066b91aea701`. Production thực tế READY tại **`dpl_Gqr6yuuyfyurkBYZJEVuFaqjBs6Z`**, URL `quocan4-fkx0amrhj-khkt3.vercel.app`, metadata base `1a1a4c4` + gitDirty=1; không dùng mốc rollback cũ trong tài liệu phát hành trước.
- Đối chiếu manifest source Vercel (không rà lại code): Production và Preview đã duyệt đều 100 file, 99 file có cùng UID/hash nguồn; khác duy nhất `data/career-videos.json`. Hash catalog Production khớp blob `0c9ddbb` dạng CRLF, tức chưa sửa ghi chú. Catalog Production đã có 200 nghề/video; không suy đây là lượt phát hành mới. Các mã AI/auth/database hiện tại khớp Preview đã duyệt.
- Chưa tích hợp/push hoặc phát hành trong mốc này. QA Google/DeepSeek/Member/Guest mới chưa hoàn tất. Không coi cấu hình health hoặc video PASS là bằng chứng auth/AI LIVE.

## Kết quả mới nhất — Preview từ commit sửa UTF-8, 30/10/2026

- Đã commit riêng 9 file sửa ghi chú/tài liệu/bằng chứng liên quan: **`2366ad42a4d9e4130215db999515eaea09dadad1`**, nhánh `feat/career-video-pilot`, cha `0c9ddbb`. Không đổi ID/URL hoặc logic AI/auth/database/quota; không push/merge main.
- Preview mới **`dpl_4kmjZ6KBTQFj3qni4uQedJGgUhtt`**, READY, target null: **https://quocan4-ii7vcyh80-khkt3.vercel.app/mot-ngay-lam-viec**. API Vercel xác nhận `gitCommitSha` chính xác như trên, không có cờ `gitDirty=1`. Working tree sạch trước upload; dry-run xác minh 100 file thực đều thuộc commit, đúng worktree, loại secrets/docs/tests/scripts/artifacts. Bằng chứng định danh: `docs/video-research/utf8-preview-deployment.json`.
- Dùng cấu hình Preview đầy đủ hiện có: AI demo false, advisor/story read-only false, DDGS, database staging cũ `task41-preview-schema-20261025`. Xác minh lại branch/endpoint độc lập Production, schema và TLS qua SQL chỉ đọc; không migration, không ghi/reset database/quota. Không dùng cấu hình pilot tắt dịch vụ. Health trả `ai_configured=true`, `auth_configured=true`, Firebase config configured; không gọi DeepSeek hoặc thực hiện đăng nhập LIVE trong smoke này.
- **Kiểm trực tiếp trên Preview mới:** API và ghi chú hiển thị UTF-8 của đúng 9 video sửa đều khớp commit; 9 truyện mở được. Catalog đủ 200 nghề/mỗi nghề một video; ba asset video khớp source commit sau chuẩn hóa xuống dòng. Desktop/mobile PASS tìm không dấu/không kết quả, lọc đúng nhóm theo catalog, hai liên kết Video/Truyện, cảnh tiếp, Back/Forward cùng tab, không tràn ngang, không tải iframe sẵn, 0 lỗi JavaScript.
- **Phát mẫu trên Preview mới: 3/3 PASS** — Lập trình viên `_WQ_VV4pXPc`, Ngân quỹ `AQz3pSPYk0k`, Phát triển nông thôn `4I_GSf3nWaU`; đúng ID, PLAYING=1, thời gian tăng và chuyển về Truyện gỡ iframe. Không có lỗi tái hiện cần sửa mã.
- **Kế thừa, không chạy lại:** 200/200 video khởi chạy PASS trên Preview cũ `dpl_DfarPXsrAJjGpgbGWh2qiVZ4q6DH`, lưu `preview-resume-playback.json`. Trên Preview mới chỉ phát lại 3 video mẫu; 197 video còn lại chưa phát lại trên hostname mới. Không ghi thành 200/200 LIVE mới. Không tìm lại nguồn hoặc chạy toàn bộ bộ kiểm thử.
- Project env metadata và alias Production đối chiếu trước/sau không đổi. Chỉ tạo Preview, không deploy/promote Production, không thay bindings dịch vụ hoặc dữ liệu.
- Báo cáo smoke: `docs/video-research/utf8-preview-smoke.json`; receipt deployment như trên. Tài liệu/bằng chứng hậu kiểm mới được ghi **local sau commit source** để HEAD vẫn đúng commit đã deploy; chưa stage/commit tiếp hoặc push. Bằng chứng 200/200 cũ và bảng kiểm kê đã nằm trong commit `2366ad4`.
- **Còn chưa kiểm trong lượt này:** 197 player trên hostname mới, Google/email login LIVE và hội thoại DeepSeek LIVE; xem/nghe trọn nội dung video; Production. Không có thay đổi liên quan cần chạy lại toàn bộ QA.

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

1. Lỗi mã hóa tiếng Việt ở ghi chú của 7 nguồn pilot và hai nghề Ngân quỹ/Phát triển nông thôn đã sửa, commit `2366ad4`, triển khai và kiểm trực tiếp PASS trên Preview mới `dpl_4kmjZ6KBTQFj3qni4uQedJGgUhtt`.
2. Đã hoàn thiện kiểm kê đủ 200 nghề và kiểm phát từng video trên Preview hiện có, kết quả cuối 200 PASS. Nếu có deployment mới cần hậu kiểm đúng deployment mới; không kế thừa tự động từ nghiên cứu hoặc Preview cũ.
3. Đã PASS desktop/mobile, tìm/lọc, hai nút Video/Truyện, Back/Forward và cùng tab trên cả Preview cũ và Preview mới chứa bản sửa UTF-8. Phạm vi phát mẫu mới và phát đầy đủ kế thừa ghi riêng ở đầu file.
4. Báo riêng tình trạng Firebase/DeepSeek/Guest/Member LIVE; không tự đánh dấu PASS từ mock hoặc từ build READY.
5. `docs/career-video-production-release.md` có kế hoạch phát hành, nhưng chưa có kết quả deployment cuối trong tài liệu này. **Trạng thái Production/push/main chưa được xác minh lại trong lượt checkpoint; không kết luận đã phát hành từ tài liệu kế hoạch.**

## Cách tiếp tục

Ưu tiên kết quả mới nhất ngày 30/10 ở đầu file, kiểm tra Git và deployment thực tế trước thao tác tiếp. `docs/career-video-200-checkpoint.md` và `docs/career-video-production-release.md` là lịch sử, không dùng trạng thái Git/quyền phát hành cũ để thay yêu cầu mới. Đã commit và triển khai Preview sửa UTF-8 theo quyền mới, chưa push/merge main hoặc Production. Kế thừa bằng chứng, không tìm lại nguồn hoặc chạy lại toàn bộ kiểm thử khi không có thay đổi liên quan. Kết quả các lượt trước dưới đây là lịch sử, không thay kết quả mới nhất.

Bản sao local chỉ chứa các file mã nguồn/dữ liệu nghiên cứu được chỉ định nằm tại `artifacts/checkpoints/career-video-resume-20261029/`; không bao gồm dotenv, credentials hoặc toàn bộ artifacts.
