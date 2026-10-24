# Task 3.1 — Thư viện video và truyện nghề

Ngày: 24/10/2026 (Asia/Bangkok). Nhánh `feat/task-3-1-video-library`, worktree `.claude/worktrees/task-3-1`.

## Nguồn và phạm vi

- Bắt đầu từ `f95cfde` (runtime Task 3 `c23cdf3`), đã tạo backup Git `backup/task-3-before-redesign`.
- Production xác minh đang ở `5aaed6e3f6ea955d89feeec0e1b8e23b33772bbe`, deployment `dpl_8SWMtQHuQ7nFnkt3EEs5YVc1tAyQ`. Không coi main là nguồn Production.
- Giữ nguyên dữ liệu 200 hồ sơ nghề, 200 truyện/1.000 cảnh/400 tình huống, sáu truyện legacy API version=1, đăng nhập, Guest/quota, migrations, hotfix mở chat và khảo sát.
- `chat.js` chỉ đổi nhãn liên kết quay lại video; không thay logic đăng nhập, lịch sử hoặc gọi AI.

## Đã triển khai

- Thư viện riêng: tìm kiếm có/không dấu, lọc 12 nhóm, 12 thẻ mỗi lượt, 3/2/1 cột; thumbnail YouTube thật chỉ ở nghề có video được rà soát. Nghề khác dùng SVG gốc, không có Play giả.
- Link `?nghe=...` / `?career_id=...` mở thẳng chi tiết, không render thư viện 200 nghề; có đường quay về đúng hồ sơ nghề.
- Hai tab Video/Truyện; nghề chưa có video mặc định truyện. Nhúng chính thức `youtube-nocookie.com`, chỉ sau click, autoplay=0, hủy player khi chuyển tab/nghề, fallback lỗi 100/101/150 hoặc mất kết nối.
- Reader một cảnh, lựa chọn ở cảnh 2/4, phản hồi sau lựa chọn, tổng kết sau cảnh cuối, chơi lại; không timeline hoặc lưới năm cảnh. Giữ minh họa vector hiện có, không tuyên bố có 1.000 tranh riêng theo nghề.
- Hỏi AI là hành động phụ: câu nháp sửa được, mang career/scene hoặc ID video/nguồn/ngữ cảnh biên tập, không tự gửi, có đường quay lại đúng vị trí. Tiến độ chỉ trong tab với TTL, không phải dữ liệu xác thực.
- Schema `CareerVideo`, catalog tĩnh, API `GET /api/career-videos/{career_id}` chỉ trả nội dung verified có trạng thái truy cập phù hợp. Candidate/pending/rejected/unavailable không ra thư viện công khai.

## Video và giới hạn thẩm định

Tổng cộng **3 ứng viên, 2 đã rà theo phương pháp ghi trong dữ liệu, 2 nghề có video, 1 pending không công khai**.

| Nghề | YouTube thật | Nguồn | Kết quả |
| --- | --- | --- | --- |
| Lập trình viên (`lap-trinh`) | https://www.youtube.com/watch?v=_WQ_VV4pXPc | CareerOneStop, Software Developers Career Video, 89 giây, 25/08/2017 | Metadata + mô tả nguồn + toàn bộ storyboard; player thật onReady PASS; chưa xác nhận phát liên tục trong kiểm thử tự động |
| Nhà thiết kế đồ họa (`thiet-ke`) | https://www.youtube.com/watch?v=dt6td67yF9E | CareerOneStop, Graphic Designer Career Video, 97 giây, 08/11/2018 | Metadata + mô tả nguồn + toàn bộ storyboard; player thật onReady và thời gian phát tăng PASS |
| Đầu bếp (`dau-bep`) | https://www.youtube.com/watch?v=7HALFANL7N4 | VTV7 KIDS, 722 giây theo metadata | Pending; chưa đủ thẩm định nội dung/nhóm tuổi nên không xuất bản |

Hai video CareerOneStop là tiếng Anh, bối cảnh Hoa Kỳ; không áp triển vọng hoặc điều kiện đào tạo từ video cũ cho Việt Nam. Đã đối chiếu tiêu đề, kênh, thời lượng, ngày đăng, playability, playableInEmbed, isFamilySafe và xem tám bảng storyboard bao phủ toàn thời lượng. **Chưa nghe trọn âm thanh; caption không truy xuất thành công. Không coi đây là thẩm định đầy đủ âm thanh hoặc chứng nhận chuyên gia.** Cần người dùng duyệt ngôn ngữ/âm thanh trước Production. Không lưu bản sao video/storyboard vào nguồn phát hành.

API Data YouTube chưa có credential được cấp cho nhiệm vụ này, không giả lập có key. Playback có thể thay đổi theo mạng, vùng, chính sách hoặc chủ video. Trạng thái được rà tại thời điểm ghi `last_checked_at`, không đảm bảo tồn tại vĩnh viễn.

## Bổ sung video

1. Chọn career_id thực từ catalog 200 nghề.
2. Chạy `python scripts/import_youtube.py --career-id lap-trinh --url https://www.youtube.com/watch?v=ID_THAT --output artifacts/candidate-new.json` (thay bằng URL thật).
3. Import chỉ gọi endpoint cố định oEmbed; optional `YOUTUBE_DATA_API_KEY` backend bổ sung metadata/status. Không fetch host người nhập, không log key; output mở chế độ `x`, không ghi đè.
4. Dù có Data API, kết quả chỉ `candidate/pending_review`. Kiểm nguồn, nội dung hình/tiếng, lứa tuổi, liên quan nghề, quyền nhúng và vùng trước duyệt; ghi phương pháp/người/thời điểm trung thực.
5. Biên tập vào `data/career-videos.json`; chạy `python scripts/validate_videos.py`. Không tự phê duyệt từ tiêu đề và không bắt buộc đủ 200 video.

## Kiểm thử thực tế

- Backend trọng tâm: **26 PASS, 0 SKIP** (8 video, 10 Stories 2, 4 legacy, 3 mode, 1 runtime bundle không public/dotenv). Không gọi AI thật.
- Node Chat2.1 + story/video handoff: **11 PASS**, gồm ràng buộc career/conversation, TTL, chống URL redirect sai, video ID sai và câu nháp sửa được.
- Chrome thật với PostgreSQL local riêng: **10 nhóm PASS**, thêm kiểm tra tablet 2 cột, desktop 3/mobile 1. Firebase/AI là fixture/demo; vòng đời/error player có fixture rõ ràng, không coi là provider thật.
- YouTube thật: 2 player onReady, 1 video xác nhận phát/tiến thời gian; video Lập trình viên ở trạng thái cued trong phép thử tự động, chưa xác nhận playback. Đã có screenshot và evidence riêng với test player fixture.
- `validate_stories`: PASS 200/1.000/400; `verified_videos=0` của script này chỉ đếm trường video_sources legacy, catalog mới có hai video riêng. `validate_videos`: PASS 3/2/2/1; script offline không tự kiểm mạng.
- Không chạy lại Super Board hoặc toàn bộ test không bị ảnh hưởng. Kết quả QA bảo vệ API của Task 3 được kế thừa vì không sửa auth/quota/store/proxy.

Ảnh local trong `artifacts/` (không commit): `stories31-library-desktop.png`, `stories31-library-tablet.png`, `stories31-library-mobile.png`, `stories31-video-desktop.png`, `stories31-video-mobile.png`, `stories31-no-video-mobile.png`, `stories31-comic-choice.png`, `stories31-summary.png`. Evidence JSON: `stories31-browser.json`, `stories31-youtube-live.json`.

## Preview và điều kiện phát hành

- Nhánh chưa có PostgreSQL/Firebase thử riêng; Preview chỉ xem video/thư viện/truyện, không dùng database Production hoặc gọi AI thật.
- Vercel từ chối tạo env cho nhánh chưa có trên GitHub. Vì vậy `vercel.json` chỉ tắt Git auto-deploy cho đúng `feat/task-3-1-video-library`; các nhánh khác giữ mặc định. Sau push sẽ tạo sáu override Preview riêng nhánh rồi CLI deploy với cùng override lần nữa. Không đổi Production Branch hoặc env Production.
- Override: `DATABASE_URL`, `DEEPSEEK_API_KEY`, `FIREBASE_API_KEY`, `FIREBASE_PROJECT_ID` rỗng; `AI_DEMO_MODE=false`; `STORIES_PREVIEW_READ_ONLY=true`. Không copy secret Production.
- Không tắt Vercel Deployment Protection. Người xem có thể cần đăng nhập Vercel được cấp quyền. Firebase/DeepSeek thật và quota end-to-end trên Preview **BLOCKED** tới khi có môi trường thử riêng được phép.
- Lần deploy đầu bị Vercel từ chối vì includeFiles vượt 256 ký tự. Rút gọn bằng glob careers/batch, giữ whitelist bốn file trong `.vercelignore`; bổ sung test độ dài cấu hình và kiểm tra runtime. Không đổi dữ liệu hoặc mở rộng tập file bí mật.
- Chưa merge/deploy Production, không kết nối Neon hoặc chạy migration. Trạng thái URL/build/hậu kiểm sẽ bổ sung sau khi deployment thực tế hoàn thành.

Nguồn vận hành: [Vercel Git deploymentEnabled](https://vercel.com/docs/project-configuration/git-configuration), [env theo nhánh](https://vercel.com/docs/environment-variables), [YouTube IFrame API](https://developers.google.com/youtube/iframe_api_reference).
