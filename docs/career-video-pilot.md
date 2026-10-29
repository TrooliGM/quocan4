# Video nghề nghiệp — đợt mẫu 5 nghề, 28/10/2026

## Preview để duyệt

- https://quocan4-jyif073q7-khkt3.vercel.app/mot-ngay-lam-viec
- Deployment **dpl_wphLppAA9bb2uTsb5hc6f348uRfw**, **READY**, target Preview.
- Worktree `D:\khkt\.claude\worktrees\career-video-pilot`; nhánh `feat/career-video-pilot`; base `1a1a4c48a6221c7850496038064c066b91aea701` (mã sản phẩm đã phát hành43a8337 + báo cáo). **Bản vá chưa commit/push/merge.**
- Chỉ deploy Preview bằng CLI65.4, project `khkt3/quocan4`. AI/Firebase/database bị tắt bằng override riêng cho deployment để kiểm video/truyện không ghi dữ liệu. Không sao chép credentials Production, không tạo database/schema/migration. Có thể cần đăng nhập Vercel để mở Preview.

## Kết quả kiểm kê: thiếu video khác lỗi phát

Đã đối chiếu dữ liệu Git và **GET /api/career-stories trên Production**:

| Phạm vi | Có video công khai | Chưa gắn video công khai | Lỗi phát quan sát được |
|---|---:|---:|---|
| Production hiện tại,200 nghề | 2 | 198 | 0/2 video đã thử trong Chrome |
| Preview đợt mẫu,200 nghề | 7 | 193 | 0/7 video đã phát nhúng thật trên Preview |

Hai nghề cũ có video là **Lập trình viên** (`_WQ_VV4pXPc`) và **Nhà thiết kế đồ họa** (`dt6td67yF9E`), nguồn CareerOneStop, tiếng Anh. Hai video đều đạt PLAYING=1, thời gian chạy tăng; không chỉ kiểm iframe ready. Không thể bảo đảm video bên ngoài luôn hoạt động ở mọi mạng/khu vực/thời điểm.

Trước thay đổi, **Kỹ sư dữ liệu và Nhà khoa học dữ liệu đều có video_count=0**. Đó là **chưa được gắn video**, không có ID nào để kết luận bị lỗi phát. Trong Preview này, Kỹ sư dữ liệu đã được gắn video đúng Data Engineer; Nhà khoa học dữ liệu vẫn chưa gắn, tiếp tục có truyện. Không lấy video Data Engineer dùng chung cho Data Scientist.

Catalog ban đầu có3 bản ghi:2 đã duyệt và1 Đầu bếp/VTV7 KIDS **pending_review**, chưa công khai. Bản pending này giữ nguyên; không âm thầm duyệt. Sau đợt mẫu:8 bản ghi,7 đã duyệt và1 pending. Danh sách200 nghề và nguồn từng nghề: [CSV kiểm kê](career-video-inventory-pilot.csv). `NOT_ATTACHED` không có nghĩa video hỏng; `recorded_availability_issues` chỉ là dữ liệu đã ghi nhận, không thay cho kiểm thử LIVE.

## 5 nghề mẫu và nguồn gốc

| Nghề / nhóm | Nguồn xuất bản gốc | Video | Thời lượng metadata | Loại nội dung |
|---|---|---|---|---|
| [Kỹ sư dữ liệu](https://quocan4-jyif073q7-khkt3.vercel.app/mot-ngay-lam-viec?nghe=ky-su-du-lieu&tab=video) / Công nghệ | Báo Tuổi Trẻ; khách mời Duy Luân | [Nghề GenZ: Data Engineer](https://www.youtube.com/watch?v=aNyGaxNzt9k) |19:33| Phỏng vấn người làm nghề, không phải video quay cả ca làm việc |
| [Điều dưỡng](https://quocan4-jyif073q7-khkt3.vercel.app/mot-ngay-lam-viec?nghe=dieu-duong&tab=video) / Y tế | Kênh Bệnh viện Đa khoa Thủ Đức | [Một ngày của điều dưỡng](https://www.youtube.com/watch?v=RgwsLjr2jZo) |2:54| Giao ban, chăm sóc người bệnh, môi trường bệnh viện |
| [Giáo viên](https://quocan4-jyif073q7-khkt3.vercel.app/mot-ngay-lam-viec?nghe=giao-vien&tab=video) / Giáo dục | Trường THPT FPT Hà Nội | [Một ngày làm việc của giáo viên FSchool](https://www.youtube.com/watch?v=ROdxHd6Fjq0) |2:15| Hướng dẫn học sinh thực hành, hoạt động chuyên môn tại trường |
| [Kỹ sư xây dựng](https://quocan4-jyif073q7-khkt3.vercel.app/mot-ngay-lam-viec?nghe=ky-su-xay-dung&tab=video) / Kỹ thuật | Coteccons | [Một ngày ở Coteccons](https://www.youtube.com/watch?v=zZlop6W27s0) |6:59| Vlog/góc nhìn của giám sát tại dự án, chia sẻ đồng nghiệp |
| [Đầu bếp](https://quocan4-jyif073q7-khkt3.vercel.app/mot-ngay-lam-viec?nghe=dau-bep&tab=video) / Du lịch–dịch vụ | Hướng Nghiệp Á Âu | [Chef’s stories — Nguyễn Văn Lập](https://www.youtube.com/watch?v=kXaIZNZ2HZg) |3:49| Phỏng vấn nghề và cảnh chế biến món ăn thật |

Mỗi video có ID riêng, channel_id, URL canonical, ngày đăng, thời lượng, mô tả và ghi chú phạm vi. Không đặt lại tiêu đề để giả video khác. Tuổi Trẻ là đơn vị xuất bản, Duy Luân là người được phỏng vấn; không đánh đồng hai vai trò. Các video trường/doanh nghiệp/cơ sở đào tạo có bối cảnh giới thiệu thương hiệu; mô tả đã nêu rõ. Không dùng thông tin tuyển dụng/tuyển sinh cũ hoặc lời quảng bá làm cam kết hiện tại.

Điều dưỡng có hình ảnh chăm sóc y tế, Đầu bếp có bếp nóng, Xây dựng có môi trường công trường: chỉ quan sát để tìm hiểu nghề, không hướng dẫn học sinh tự thao tác nguy hiểm.

## Phương pháp chọn và kiểm chứng

1. Tìm kiếm video công khai trên YouTube; ưu tiên kênh gốc của bệnh viện/trường/báo/doanh nghiệp/đơn vị đào tạo. Không dùng URL đoán từ tên nghề.
2. Đối chiếu trang watch + oEmbed thật: ID, tiêu đề, kênh/channel_id, ngày đăng, duration, metadata cho phép nhúng và family-safe. Các dữ kiện này **không tự đủ** để duyệt.
3. Đọc mô tả gốc và xem các mẫu hình ảnh trong video, đối chiếu nghề. Loại nội dung thiếu đặc trưng, chỉ tuyển dụng/học khóa học hoặc hoạt hình khi cần hình ảnh công việc thật. Chọn đúng một nghề theo vai trò, không phân phối một video chung ra nhiều nghề.
4. Chrome ẩn danh dùng chính module YouTubePlayer của La Bàn, mạng YouTube thật. Sau thao tác phát kiểm tra state=1, currentTime tăng; không mock sự kiện hoặc chỉ nhận onReady.
5. Sau deploy, **cả5 video mới +2 video cũ phát nhúng thật trên Preview**. Đồng thời xác minh video_id của player đúng ID từ API, đổi sang truyện dừng/destroy iframe.

Giới hạn rà nội dung: đã đọc mô tả gốc, xem mẫu hình ảnh/phụ đề xuất hiện tại các thời điểm kiểm tra; **chưa nghe toàn bộ âm thanh hoặc xem trọn từng video**. Một số thao tác seek phải buffer, không xem ảnh đang buffer là chứng cứ đã xem phân đoạn đó. Endpoint captions trả200 nhưng body rỗng nên không tuyên bố đã có toàn bộ transcript. Cần người dùng duyệt nội dung/âm thanh của5 mẫu trước khi xét Production hoặc mở rộng.

## Ứng viên bị loại, không gắn vào thư viện

Trong Chrome nhúng local, các video sau trả **error150**, dù watch metadata báo playableInEmbed=true. Đây là lý do phải phát thử thật, không gắn nhãn PASS từ metadata:

- VTV24 Điều dưỡng: `3-YTu-kPwa4`.
- VTV7 Giáo viên: `JZyIvCufvRs`.
- VTV24 Kiến trúc sư: `bLfNrAr23j4`.
- VTV24 Hướng dẫn viên du lịch: `slcSHeHG6mw`.
- Unicons Giám sát an toàn: `Js-1FbF-7yU`.

Không kết luận các video này bị xóa; lỗi quan sát là **không phát nhúng trong môi trường thử**. Chúng **không phải5 nghề đang bị lỗi trên Production**, vì chưa từng gắn vào catalog công khai. Video Đông Á `GrIrlS_Bzu4` phát được nhưng chủ yếu minh họa hoạt hình nên không chọn cho mẫu công việc thực tế. MindX `eMlEJd8larQ` phát được nhưng nghiêng về học/ứng tuyển nên chọn phỏng vấn Tuổi Trẻ có trọng tâm nghề hơn. Không coi các trường hợp nội dung chưa phù hợp là lỗi kỹ thuật.

## Cơ chế tìm/chọn/lưu hiện có và phần đã đổi

- Runtime vẫn đọc JSON biên tập tĩnh `data/career-videos.json`; không gọi YouTube Search hoặc AI khi học sinh mở nghề. `public_for()` chỉ trả video đã duyệt và availability phù hợp.
- `scripts/import_youtube.py` nhập **ứng viên** từ URL YouTube; oEmbed hoặc YouTube Data API nếu có key chỉ bổ sung metadata, **không tự verified**. Hiện không có tìm kiếm/duyệt video tự động trong sản phẩm; đợt này tìm nguồn ngoài runtime và duyệt có chứng cứ.
- Giữ schema và player hiện hành; siết catalog để không tái dùng một YouTube ID cho nhiều nghề. Không thêm dependency/API key hoặc database.
- Card thư viện có hai link riêng **Xem video** và **Đọc truyện**, không lồng thẻa. Cả hai dùng đường dẫn nội bộ cùng tab, chỉ định tab rõ ràng; nghề chưa gắn giữ nhãn thiếu video và link truyện. Chi tiết có hai tab cùng nhãn.
- Giữ cả200 truyện/1000 cảnh, không sửa nội dung hoặc career_id. Giữ lazy-load YouTube sau thao tác phát, fallback lỗi/external link; không tự phát khi mở trang.
- Có script kiểm kê offline `scripts/video_inventory.py`, xuất CSV bằng chế độ không ghi đè file có sẵn. Không đánh đồng count metadata với kiểm thử LIVE.

## Kiểm thử và phạm vi bàn giao

- **21 Python PASS** (20 ca ban đầu +1 regression phân biệt missing/embed issue), **4 Node PASS** cho handoff/journey; syntaxJS và diff check PASS.
- Chrome Preview: **7/7 video LIVE PASS**,5 video mới đúng nghề/ID; truyện vẫn đọc được, đổi tab destroy player; Back/Forward, một tab, vùng nhấn mobile≥44px, không overflow,0 lỗi JS. Ảnh desktop/mobile đã xem.
- Library trả200 nghề/7 nghề có video/193 nghề chưa có video; Nhà khoa học dữ liệu thử trạng thái chưa gắn, không tạo iframe/player giả. Bằng chứng JSON/ảnh trong artifacts bị ignore; báo cáo và CSV không chứa secrets.
- Preview cách ly tắt AI, đăng nhập và database theo env riêng; không gọi DeepSeek/không trừ quota, không ghi dữ liệu. Không lấy đây làm nghiệm thu lại AI/Firebase.
- Production vẫn deployment **dpl_7cdWzerGqdzD3c4Ucjvfb8GaJbfE**, chỉ2 nghề có video; **không deploy Production, không commit/push/merge, không mở rộng200 nghề**.

File sửa: `career_videos.py`, `data/career-videos.json`, `stories.html`, `public/stories.html`, `public/assets/stories.js`, `public/assets/stories-31.css`, `scripts/validate_videos.py`, `scripts/video_inventory.py`, `tests/test_story_videos.py`, `tests/browser_video_pilot.py`, CSV/tài liệu/bộ nhớ. Bước tiếp theo: người dùng xem5 mẫu trên Preview, duyệt nội dung và lựa chọn video trước đợt tiếp theo.
