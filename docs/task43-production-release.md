# Task 4.3 — Phát hành Production cho Guest, Member và QA

Ngày 26/10/2026 (Asia/Bangkok). Yêu cầu mới của người dùng cho phép phát hành Production sau kiểm thử, thay phạm vi chỉ Preview trước đó. Không viết lại phần đã PASS.

## Phiên bản thực tế

- URL chính thức: https://labanhuongnghiep.vercel.app/ai-career-advisor .
- Deployment: **dpl_G11k5MKTVWNhEAcszbhqGEZm1KiW**, target production, READY, alias đã xác minh.
- Source Production: **608146c144e33c531efb253739bca1560d119ffd**. Code ứng dụng là checkpoint04a67da, sau đó608146c chỉ ghi báo cáo Preview.
- Nhánh GitHub: **feat/task-4-3-ecosystem-actions**, đã push đúng nhánh, không force, không merge/main/staging hoặc đổi Production Branch. Worktree riêng task-4-3; các thay đổi cũ tại checkout chính được giữ nguyên.
- Production trước phát hành: **dpl_CoeNba7iFQNA7412ibdQbCUqqfwP**, source **bd906df5492152c07b991b7f9440cb434209210f**, vẫn READY. Tag local backup/task43-before-production-20261026 giữ đúng source đó.
- Production Branch cấu hình Vercel vẫn main; bản thực tế được phát hành từ feature branch bằng CLI. Đã đối chiếu ancestry với source Production, không lấy main làm baseline hoặc ghi đè lịch sử khác nhau.

## Cách phát hành và bảo toàn dữ liệu

Build mới bằng môi trường Production với --prod --skip-domain, không promote Preview gắn staging, không override bất kỳ DATABASE_URL/Firebase/DeepSeek/Search/profile variable nào. Manifest103 file kiểm tra không chứa dotenv, artifacts, secrets, test hoặc tài liệu riêng. Không migration, thay schema, xóa/ghi đè hội thoại hoặc reset quota.

Candidate được thử trước khi chuyển alias; sau PASS mới push feature branch và promote đúng deployment đã kiểm. Navigation dùng chung pipeline và terminal function cho mọi role, không có flag navigation QA-only. DDGS Search cũng giữ trạng thái mở mọi role từ Task4.2. Quyền dữ liệu hồ sơ riêng và khảo sát giữ nguyên như Production trước đó.

Giải quyết Guest LIVE hợp lệ: phiên QA Production có sẵn còn4/8 được xác minh qua backend trước khi thử. Dùng chính phiên đó với cùng backend Production trên candidate/main, không tạo định danh mới, đổi IP, chuyển sang staging hoặc tăng/reset hạn mức. Không sử dụng dữ liệu người dùng thật làm fixture; chỉ thêm hội thoại tạm/dữ liệu thử tổng hợp thuộc các định danh QA đang có qua API bình thường, không sửa SQL dữ liệu người dùng.

## Bằng chứng trước phát hành

- Kế thừa **62 phương thức Python local PASS** và Preview16 phản hồi LIVE/Chrome đã ghi trong task43-navigation.md; source ứng dụng không thay đổi nên không chạy lại toàn Super Board.
- Candidate Production **6 phản hồi DeepSeek LIVE**, hai câu mỗi nhóm Guest/Member/QA. Guest mở hồ sơ Chuyên viên điều hành tour rồi hỏi nối tiếp một ngày làm việc, trả đúng truyện. Member nhận gợi ý từ vẽ mặt bằng/thiết kế nhà (4 hướng và bài tập an toàn), sau đó mở AI Chuyên viên thương mại điện tử. QA mở thư viện bằng câu viết tắt rồi mở hồ sơ Kỹ sư điện toán đám mây. Không dùng response nghề hardcode.
- Mọi nhóm có nút đúng kind/career_id, lưu và GET lại giữ metadata; retry cùng request_id trả duplicate, không gọi model hoặc tính lượt thêm. Guest4/8 →6/8 sau đúng hai câu.
- Chrome thật cho **cả ba nhóm** trước promote: Guest dùng cookie có sẵn được server xác minh; Member/QA dùng Firebase SDK email/password. Desktop1440/mobile390 không tràn ngang; reload còn nút; bấm mở đúng modal/thư viện/truyện/AI khảo sát theo career_id. AI đích chỉ có greeting và khảo sát chưa gửi, không tự gọi tư vấn khi chỉ bấm nút. Tab cũ và draft giữ nguyên.
- Token sai401 trên cả ba API AI; khác chủ session404; client tự gửi navigation_actions422; Origin khác403; đường dẫn dotenv/backend/artifacts404. Thư viện200 nghề/12 nhóm và các route chính200. Không tắt biện pháp bảo vệ để thử.

## Hậu kiểm trên domain chính

- Guest hỏi mở thư viện để chọn nghề khác: nút /mot-ngay-lam-viec, đúng ý mới, không ép về nghề trước. Guest6/8 → **7/8**, còn1/8; replay không thêm lượt. Bấm các nút trong Chrome không phát sinh lượt chat mới.
- Member hỏi “một ngày làm việc của nghề đó”: nút truyện Chuyên viên thương mại điện tử, đúng lịch sử từ candidate. Hội thoại không cần sao chép hoặc khôi phục thủ công.
- QA hỏi toán ngoài hướng nghiệp: không có navigation_actions hoặc Source giả.
- QA tra cứu prompt injection bằng **DDGS + DeepSeek LIVE**: Search ok,4 nguồn thật,9,38 giây; câu lệnh trong nguồn được giải thích như dữ liệu và không tạo nút nghề trái ý. Đây là mẫu quan sát, không bảo đảm chống mọi injection hoặc mọi đáp án tuyệt đối đúng.
- Trên domain chính: token401/khác chủ404/Origin403/privatepaths404; trang chủ/chat/truyện200, danh mục200/12; asset version task43-navigation-2 đúng.
- Chrome Guest sau promote: nút thư viện/hồ sơ/truyện mở đúng trang thật trên domain chính, giữ draft/tab cũ và lịch sử sau reload, desktop/mobile PASS. Ảnh local không commit: artifacts/task43-production-official-guest-390.png, -1440.png; ảnh ba nhóm trước promote trong task43-production-candidate-*.png.

## Giới hạn và trạng thái

**ĐÃ PHÁT HÀNH — smoke Production PASS trong phạm vi trên, Navigation mở Guest/Member/QA.** Guest LIVE trước đây BLOCKED ở staging đã được đóng bằng hạn mức Production hợp lệ; không gọi test mock là LIVE. Google popup mới chưa được người dùng kiểm lại; không đánh dấu PASS từ SDK password hoặc từ bằng chứng Google cũ. Logic Firebase và authorized domains Production không thay đổi trong đợt phát hành này; đăng nhập token/SDK và helper return-path đã kiểm.

Guest đã dùng hết8 câu vẫn phải đăng nhập; phát hành không cấp lại quota. DDGS có thể lỗi theo thời điểm; hệ thống báo rõ khi không lấy được nguồn. Những cảnh và gợi ý nghề vẫn là mô phỏng/tìm hiểu, không phải kết luận phù hợp chắc chắn hoặc hồ sơ tự xác nhận.

## Rollback

1. Xác minh alias hiện thuộc dpl_G11k5MKTVWNhEAcszbhqGEZm1KiW và project quocan4/khkt3.
2. `vercel rollback dpl_CoeNba7iFQNA7412ibdQbCUqqfwP --scope khkt3 --yes` rồi kiểm tra alias/health. Nếu cơ chế rollback không khả dụng, promote lại đúng deployment Production cũ đang READY. Script có kiểm tra alias/đích: artifacts/task43-production-release.py rollback (không commit).
3. Không thay env hoặc reset/khôi phục DB: Task4.3 không đổi schema/bindings; metadata trong messages JSON tương thích ngược, quota/hội thoại mới phải được giữ. Bản cũ vẫn Task4.2 Search cho mọi role.

Không phát hiện lỗi nghiêm trọng trong hậu kiểm nên chưa dùng rollback. Các checkpoint báo cáo sau608146c không phải source build Production mới; chỉ cập nhật tài liệu và bộ nhớ.
