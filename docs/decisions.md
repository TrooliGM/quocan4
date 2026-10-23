# Quyết định và việc còn mở

## Đã xác nhận trong phiên làm việc

| Ngày | Nội dung | Cơ sở |
| --- | --- | --- |
| 2026-10-13 | Chuẩn bị Vercel theo tự nhận diện FastAPI; chỉ chỉnh cấu hình/tài liệu local, không commit/push, không sửa đăng nhập hoặc đổi Firebase project. | Yêu cầu trực tiếp mới nhất. Chưa triển khai; storage chat production còn thiếu. |
| 2026-10-13 | Đề xuất PostgreSQL managed và adapter/phiên TTL dùng chung để thay SQLite/RAM khi lên Vercel. | Đề xuất kỹ thuật, chưa được thực hiện và chưa là quyết định migrate dữ liệu của người dùng. |
| 2026-10-13 | Sau đăng nhập mở sẵn cuộc trò chuyện AI, không cần bấm Bắt đầu lần nữa; khôi phục phiên tab nếu có, phiên mới không tự lưu lâu dài. | Người dùng yêu cầu đi thẳng vào trò chuyện; giữ yêu cầu đồng ý lưu lịch sử hiện có. |
| 2026-10-13 | Dùng bản chạy trên máy trước; tiếp tục lưu mã nguồn GitHub, hoãn deployment. | Người dùng trả lời trực tiếp khi được hỏi về kết nối Vercel. Đây là quyết định mới nhất về triển khai. |
| 2026-10-13 | Xây dựng truyện nghề mô phỏng một ngày làm việc; lưu GitHub và hướng tới Vercel theo yêu cầu mới. | Người dùng yêu cầu trực tiếp, ghi rõ bác sĩ và bộ công nghệ hiện có; Vercel chưa kết nối, chưa triển khai thành công. |
| 2026-10-13 | Bản đầu gồm sáu nghề hiện có, bốn cảnh mỗi nghề, SVG/CSS và comic tương tác; AI giải thích theo cảnh. | Lựa chọn triển khai của trợ lý để cung cấp nội dung dùng được ngay, chưa phải video có lồng tiếng. |
| 2026-10-06 | Cài frontend-design ở phạm vi dự án. | Yêu cầu trực tiếp của người dùng; tệp đã được sao chép và kiểm tra khớp nội dung. |
| 2026-10-12 | Chỉ đưa micro nhận diện lời nói trở lại chat; giọng đọc Vbee không nằm trong bản hiện tại. | Yêu cầu trực tiếp mới nhất của người dùng, thay thế phạm vi voice rộng hơn trước đó. |
| 2026-10-12 | Lưu mã nguồn hiện tại lên GitHub `TrooliGM/quocan4`; chưa deploy website. | Người dùng yêu cầu trực tiếp, repository đã cung cấp trước đó. |
| 2026-10-06 | Tạo bộ nhớ dự án từ báo cáo DOCX. | Yêu cầu trực tiếp của người dùng. |
| 2026-10-06 | Triển khai chức năng 1: trang chủ và giới thiệu. | Yêu cầu trực tiếp của người dùng. |
| 2026-10-06 | Python backend, DeepSeek là AI chính, HTML/Bootstrap/CSS/JavaScript, LangGraph, Vercel và GitHub. | Công nghệ người dùng chỉ định. |
| 2026-10-06 | Repository đích: TrooliGM/quocan4. | URL người dùng cung cấp. |
| 2026-10-07 | Setup đăng nhập bằng Firebase. | Yêu cầu trực tiếp của người dùng. |
| 2026-10-07 | Dùng Firebase project khoa-hoc-86942, ứng dụng Web “la bàn tương lai”; cấu hình đặt ở .env cục bộ. | firebaseConfig người dùng cung cấp. |
| 2026-10-11 | Sau đăng nhập mở chat AI 1:1; bổ sung text/voice và bộ nhớ tài khoản. | Yêu cầu trực tiếp và brief đính kèm. |
| 2026-10-11 | Chưa triển khai website công khai. | Người dùng đã hoãn đưa website lên mạng trong trao đổi trước. |
| 2026-10-11 | Cấu hình khóa DeepSeek và token/App ID Vbee vào môi trường riêng để dùng dịch vụ thật. | Người dùng trực tiếp cung cấp thông tin dịch vụ cho tính năng AI. |
| 2026-10-11 | Thêm nhận diện/giọng đọc trình duyệt để thử voice ngay khi Google/Vbee chưa sẵn sàng. | Người dùng chọn “Thêm giọng trình duyệt để thử ngay”. |
| 2026-10-12 | Cho phép cài gói giọng tiếng Việt từ Windows Update trên máy. | Người dùng chọn “Đồng ý, cài giọng tiếng Việt giúp tôi”. Chưa cài thành công vì dịch vụ Windows Update kẹt; chưa được cho phép reboot máy. |
| 2026-10-12 | Cho phép tạm ngắt WARP để thử tải giọng, rồi kết nối lại. | Người dùng đồng ý trực tiếp. Đã thực hiện và xác minh WARP kết nối lại; Windows Update còn StopPending nên chưa thử lại được bước tải. Không kết luận WARP gây lỗi. |

## Lựa chọn triển khai của trợ lý

- FastAPI cho backend Python; dữ liệu mẫu đặt trong `content.py` để thay đổi dễ dàng.
- Tên hiển thị La Bàn; phong cách sổ tay khám phá với nền kem, xanh bạc hà và cam san hô. Đây là lựa chọn thiết kế, có thể điều chỉnh.
- LangGraph gồm hai node: chuẩn bị ngữ cảnh nghề và gọi DeepSeek. API key chỉ dùng trên server.
- Firebase Web SDK qua CDN cho email/password và Google; thêm quên mật khẩu, xác minh email, đăng xuất. Provider cụ thể là lựa chọn triển khai của trợ lý.
- Backend xác minh ID token bằng google-auth, không dùng service account. Chưa kiểm tra token bị thu hồi/disabled theo thời gian thực; chưa có chức năng quản trị nhạy cảm.
- Chưa lưu Firestore; mặc định chọn phiên theo tab, có lựa chọn giữ đăng nhập trên máy cá nhân.
- Tư vấn mới dùng `advisor/` với DeepSeek Flash configurable, một lời gọi/model mỗi lượt, đầu ra JSON kiểm tra trước khi lưu. Prompt nằm riêng.
- Chọn SQLite bổ sung cho bản local vì dự án chưa có database; không di chuyển/xóa dữ liệu cũ. Lưu lịch sử/hồ sơ khi có đồng ý; phiên không lưu ở RAM. Đây là lựa chọn kỹ thuật, chưa chốt database cloud.
- Voice dùng Google STT REST sau ghi âm WAV/VAD client, transcript sửa trước khi gửi; Vbee v1 sync chia đoạn <=280 ký tự. Không dùng streaming/WebSocket hoặc Vbee batch/webhook. Không tự bật micro sau giọng đọc.
- Thiếu khóa: demo có nhãn; không giả kết quả provider. Voice disabled khi thiếu cấu hình. Các provider thật chưa kiểm thử.
- Cập nhật sau nhận khóa: DeepSeek đã kiểm thử thật thành công và tắt demo local. Vbee lấy danh sách giọng thành công nhưng sync TTS bị gói tài khoản từ chối; tạm tắt bằng `VBEE_TTS_ENABLED=false`, UI giải thích hạn chế. Google STT vẫn chưa cấu hình. Chưa mua/nâng cấp dịch vụ hoặc chuyển sang batch/webhook.
- Sau xác nhận voice trình duyệt: thiếu Google/Vbee thì dùng Web Speech nếu được hỗ trợ. Nhận diện vi-VN cần thao tác xin quyền, transcript sửa trước khi gửi; giọng đọc chỉ chọn giọng Việt có trên máy, tự đọc mặc định tắt. Không coi chế độ này là offline hoặc đã xác minh Google/Vbee. Dừng/hủy/đổi phiên/đăng xuất chặn callback cũ.

## Chưa được quyết định

- Tên thương hiệu, logo, bảng màu và phong cách giao diện cụ thể.
- Phạm vi sau tính năng tư vấn 1:1.
- Cơ sở dữ liệu và nơi lưu nội dung đa phương tiện khi mở rộng.
- Hình thức trực quan hóa đầu tiên: comic, hoạt hình hay video; nguồn tài sản hình ảnh.
- Nguồn và cách cập nhật lương, triển vọng nghề, trường đào tạo, thông tin tuyển sinh.
- Bộ câu hỏi, quyền sử dụng nội dung trắc nghiệm, cách tính điểm và ánh xạ kết quả sang nghề.
- Quy trình chuyển câu hỏi cho giáo viên/chuyên gia và phạm vi AI khi mở rộng.
- Kiểm thử Email/Password và Google thật trên project đã cấu hình (ảnh đã thể hiện provider bật); Zalo chưa triển khai.
- Vai trò người dùng, quyền quản trị, thông tin học sinh cần thu thập và thời gian lưu dữ liệu.
- Phương pháp đánh giá hiệu quả hướng nghiệp cho báo cáo KHKT; chưa có kết quả khảo sát được cung cấp.

## Hướng triển khai đề xuất, chưa được phê duyệt

1. Chốt phạm vi bản đầu tiên và một số nghề có nội dung đủ tin cậy.
2. Thiết kế hành trình khám phá nghề → xem một ngày làm việc → xem kỹ năng và lộ trình.
3. Xây dựng giao diện responsive cùng nội dung nghề mẫu.
4. Bổ sung trắc nghiệm, cá nhân hóa, tư vấn và quản trị theo phạm vi đã chốt.
5. Kiểm tra trải nghiệm trên điện thoại, hiệu năng nội dung đa phương tiện và tính đúng của dữ liệu.

Danh sách này phục vụ những lượt làm việc tiếp theo; không phải công việc đã hoàn thành hoặc lịch triển khai đã được cam kết.


## Nhiệm vụ 1 — 2026-10-23

Yêu cầu đã xác nhận qua tài liệu Nhiệm vụ 1: được phát triển và commit nhánh riêng; không tự merge/deploy Production. Quyết định triển khai: khảo sát gắn session/owner trong metadata messages hiện có; giữ nguyên consent và TTL; không đổi schema, Firebase hay quota 8. Phân tích đi qua API chat hiện có và tính một lượt AI như trước. Chưa có phê duyệt push/triển khai; xem docs/task-1-checkpoint.md.


## Nhiệm vụ 2 — 2026-10-24

Thư viện 200 nghề/12 nhóm, modal chung, hai mode AI và liên kết truyện theo ID đã triển khai trên feat/task-2-career-library. Preview localhost:8003 riêng dùng PostgreSQL local và AI demo. 17 test backend và browser desktop/mobile PASS có fixture; Firebase/DeepSeek thật cho flow mới chưa kiểm chứng. Không push/merge/deploy/Neon; Nhiệm vụ 3 chưa bắt đầu. Xem docs/task-2-checkpoint.md.

### Quyết định QA Nhiệm vụ 1 + 2 — 2026-10-24

Đã xác nhận: chỉ sửa lỗi thực tế, giữ thiết kế và commit bản sửa đã kiểm chứng trên nhánh `feat/task-2-career-library`; không push/merge/deploy. Đã sửa whitelist runtime đúng bốn JSON nghề (không mở toàn bộ data/) và generation fence cho modal. Không đổi Firebase, quota 8 hoặc schema.

Còn mở, **chưa được duyệt triển khai**: bảo vệ `/api/advice` và `/api/career-stories/{career_id}/ask` bằng auth/quota/rate chung, hoặc chốt chính sách vô hiệu hóa legacy AI. Hiện hai API vượt lớp bảo vệ khi có provider key, tái hiện bằng mock; không tự tắt để tránh phá chức năng. Vì vậy kết luận NOT READY FOR VERCEL PREVIEW. Firebase/DeepSeek thật cho hai mode mới và Vercel build thật chưa kiểm chứng; không dùng fixture PASS thay cho bằng chứng live. Chi tiết tại docs/task-2-checkpoint.md và artifacts/super-board-report.md.
