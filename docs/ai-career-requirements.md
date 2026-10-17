# Tám chức năng AI tư vấn nghề nghiệp và việc làm

## Nguồn và phạm vi ghi nhận

- Ngày đọc và lưu: 2026-10-11.
- Tệp người dùng cung cấp: `C:/Users/Admin/Downloads/8_chuc_nang_AI_tu_van_viec_lam.xlsx`.
- Bản nguồn được lưu trong dự án: [8_chuc_nang_AI_tu_van_viec_lam.xlsx](sources/8_chuc_nang_AI_tu_van_viec_lam.xlsx).
- Workbook có một sheet tên `Chức năng ứng dụng`, vùng dữ liệu `A1:C9`: ba cột `STT`, `Chức năng`, `Mô tả chức năng – dùng để làm gì`; một hàng tiêu đề và tám hàng chức năng. Không có công thức trong vùng dữ liệu.
- SHA-256 của bản nguồn và bản sao: `C79C9B81EAB716B45D78F1D8EDC217419D28E917124AA7076E6311FC45220A37`.
- Yêu cầu đã xác nhận của người dùng là đọc và lưu thông tin vào bộ nhớ dự án. Các mô tả bên dưới là nội dung tham khảo yêu cầu sản phẩm; chưa phải yêu cầu triển khai toàn bộ hoặc xác nhận thay thế định hướng KHKT 2027 trước đây.
- Bộ nhớ được lưu bằng tệp trong repository để các lần làm việc tiếp theo có thể đọc lại; chưa đồng bộ bản lưu này lên dịch vụ bên ngoài.

## Nội dung đầy đủ từ Excel

| STT | Chức năng | Mô tả chức năng – dùng để làm gì |
| --- | --- | --- |
| 1 | Đăng ký / Đăng nhập tài khoản | Cho phép người dùng tạo tài khoản và đăng nhập vào ứng dụng. Thông tin tài khoản được dùng để lưu hồ sơ, kết quả tư vấn nghề nghiệp, lịch sử trò chuyện với AI và các công việc đã quan tâm. |
| 2 | Hồ sơ cá nhân & định hướng nghề nghiệp | Người dùng nhập độ tuổi, trình độ học vấn, ngành học, kỹ năng, sở thích, kinh nghiệm và mục tiêu nghề nghiệp. AI dựa vào thông tin này để đưa ra tư vấn phù hợp với từng người. |
| 3 | AI tư vấn và khám phá nghề nghiệp | Chức năng chính của ứng dụng. Người dùng có thể hỏi AI về nghề nghiệp hoặc công việc mình quan tâm. AI giải thích công việc đó làm gì, yêu cầu kỹ năng, môi trường làm việc, cơ hội phát triển và kiến thức cần chuẩn bị. |
| 4 | Trắc nghiệm tìm nghề phù hợp | Cung cấp các câu hỏi về sở thích, năng lực, tính cách, kỹ năng và mục tiêu. Hệ thống phân tích kết quả và đề xuất một số nhóm nghề có thể phù hợp để người dùng tham khảo. |
| 5 | Tìm kiếm & lọc việc làm | Cho phép người dùng tìm việc theo vị trí, ngành nghề, mức lương, hình thức làm việc, kinh nghiệm hoặc trình độ. Bộ lọc giúp người dùng nhanh chóng tìm được công việc phù hợp. |
| 6 | AI phân tích mức độ phù hợp với công việc | Người dùng có thể cung cấp CV hoặc thông tin kỹ năng. AI so sánh với yêu cầu của công việc, chỉ ra điểm phù hợp, kỹ năng còn thiếu và những nội dung nên cải thiện. |
| 7 | Lộ trình học tập & phát triển kỹ năng | Sau khi xác định nghề muốn theo đuổi, AI xây dựng lộ trình học tập và phát triển kỹ năng, gồm kiến thức cần học, kỹ năng cần rèn luyện và thứ tự thực hiện. |
| 8 | Trang chủ & giới thiệu ứng dụng | Trang chủ giới thiệu mục đích của ứng dụng, các chức năng chính và cách sử dụng. Người dùng có thể nhanh chóng truy cập AI tư vấn, trắc nghiệm, tìm việc và hồ sơ cá nhân. |

## Đối chiếu với mã nguồn hiện có

Đối chiếu này dựa trên việc đọc mã nguồn ngày 2026-10-11, không phải kết quả chạy thử mới. Lịch sử kiểm tra và các giới hạn môi trường được ghi riêng tại [validation.md](validation.md).

| STT | Tình trạng trong dự án |
| --- | --- |
| 1 | Đã có mã Firebase đăng ký/đăng nhập Email và Google, quên mật khẩu, xác minh email, đăng xuất và xác minh ID token ở backend. Chưa có lưu hồ sơ nghề nghiệp, kết quả tư vấn, lịch sử AI hoặc công việc quan tâm. Theo bộ nhớ hiện tại, còn chờ cấu hình Firebase và thử đăng nhập thật. |
| 2 | Có thông tin tài khoản cơ bản và tên hiển thị; chưa có biểu mẫu hồ sơ nghề nghiệp hoặc cơ sở dữ liệu cho các trường mô tả trong Excel. AI chưa nhận hồ sơ cá nhân. |
| 3 | Có `/api/advice` và luồng DeepSeek qua LangGraph, dùng câu hỏi cùng ngữ cảnh sáu nghề mẫu. Mỗi lần gọi độc lập, chưa có lịch sử hội thoại hoặc tư vấn theo hồ sơ. Chưa kiểm chứng cuộc gọi DeepSeek thật theo bộ nhớ hiện tại. |
| 4 | Chưa có bộ câu hỏi, cách tính điểm hoặc chức năng trắc nghiệm trong mã. |
| 5 | Đã có tìm kiếm tên/mô tả/kỹ năng nghề và lọc lĩnh vực trên danh sách sáu nghề mẫu. Chưa có tin tuyển dụng, nguồn dữ liệu việc làm hoặc các bộ lọc việc làm theo Excel. |
| 6 | Chưa có tải/đọc CV, dữ liệu yêu cầu công việc hoặc chức năng phân tích độ phù hợp giữa CV/kỹ năng và công việc. |
| 7 | Nội dung nghề mẫu có kỹ năng và gợi ý bước đầu. Chưa có chức năng chuyên biệt tạo, lưu hoặc theo dõi lộ trình học tập cá nhân theo thứ tự. |
| 8 | Đã có trang chủ responsive, giới thiệu, nghề mẫu, bài viết, ô hỏi AI và giao diện tài khoản. Chưa có đầy đủ luồng truy cập các chức năng trắc nghiệm, tìm việc và hồ sơ nghề nghiệp nêu trong Excel. |

## Điểm khác với định hướng KHKT 2027 trước đây

- Báo cáo DOCX trước đây xác định đối tượng là học sinh THCS/THPT và chức năng cốt lõi là mô phỏng một ngày làm việc bằng hoạt hình/comic/video. Excel gọi AI tư vấn và khám phá nghề nghiệp là chức năng chính, nhưng không nêu rõ nhóm tuổi và không nhắc đến mô phỏng trực quan.
- Excel bổ sung tìm kiếm việc làm, phân tích CV so với yêu cầu công việc và cá nhân hóa tư vấn theo hồ sơ. Đây là phần mở rộng so với mã và định hướng đã ghi nhận.
- Excel không nhắc đến quản trị hệ thống hoặc kết nối giáo viên/chuyên gia; việc không nhắc đến chưa xác nhận loại bỏ các yêu cầu cũ.
- Chưa có chỉ định rằng Excel thay thế báo cáo cũ. Tiếp tục giữ mục tiêu hướng nghiệp trực quan cho học sinh; dùng Excel làm nguồn yêu cầu bổ sung và chờ xác nhận nếu cần đổi đối tượng hoặc trọng tâm sản phẩm.

## Những điểm còn cần xác định khi triển khai

- Tám mục trong Excel bổ sung hay thay thế các nhóm chức năng cũ; thứ tự ưu tiên thực hiện.
- Đối tượng chỉ gồm học sinh hay mở rộng sang sinh viên/người tìm việc; vai trò của AI và mô phỏng trực quan trong trải nghiệm chính.
- Nguồn tin tuyển dụng, các trường dữ liệu việc làm, cách cập nhật và phạm vi tích hợp.
- Những trường hồ sơ thực sự cần thu thập; nơi lưu, quyền truy cập, thời hạn lưu và cách xóa hồ sơ, lịch sử AI, CV.
- Bộ câu hỏi/cách tính điểm trắc nghiệm; tiêu chí phân tích độ phù hợp công việc; cấu trúc và dữ liệu tham khảo cho lộ trình học tập.

Đây là các quyết định còn mở, không phải danh sách công việc đã thực hiện. Tài liệu chỉ ghi nhận danh mục trường hồ sơ đề xuất, không chứa dữ liệu cá nhân thực tế của học sinh hoặc CV.
