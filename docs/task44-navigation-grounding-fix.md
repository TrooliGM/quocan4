# Task 4.4 — đối soát nghề trong nút điều hướng

## Phạm vi và bằng chứng ban đầu

Nhánh `hotfix/task44-navigation-grounding`, worktree riêng `task44-navigation-fix`, nền `7f45edd` (code giống Production `da6d146`). Không sửa checkout chính hoặc Production. Chỉ Preview; cần người dùng phê duyệt riêng để phát hành Production.

Chưa có toàn bộ hội thoại gốc của tình huống người dùng phản ánh, nên không kết luận hai nghề trong ảnh chắc chắn sai. Đã tái hiện **lỗ hổng kiểm định** bằng hội thoại tổng hợp: câu hỏi bảo tồn động vật và câu trả lời nói kiểm lâm/bảo tồn, nhưng metadata chứa hai nghề cứu hộ khác; backend cũ vẫn nhận cả hai nút. Đổi chủ đề sang lập trình, giữ basis từ câu hỏi cũ, backend cũ vẫn nhận hai nút. Đây không phải truy cập hoặc khôi phục hội thoại riêng của người dùng.

## Nguyên nhân và bản sửa

- `advisor/navigation.py` trước đây xác minh catalog/kind/URL và basis ở bất kỳ lời học sinh gần đây. Nó không chứng minh nghề đó đúng ý định hiện tại hay đúng phần tư vấn; tên/ID hợp lệ vẫn có thể sai ngữ cảnh. Nay basis phải thuộc lời nhắn hiện tại. Lịch sử vẫn dùng để hiểu câu nối tiếp trong bước kiểm định ngữ nghĩa.
- `advisor/navigation_review.py` mới: chỉ khi có nút ứng viên đã canonical, gọi DeepSeek một lần để kiểm định riêng **ngữ nghĩa** của yêu cầu hiện tại, tối đa8 tin gần, ngữ cảnh nghề thuộc phiên và câu trả lời. Phân biệt yêu cầu cụ thể, so sánh, đề xuất có liên hệ, thư viện, phủ định/ví dụ/đổi chủ đề/không cần nút. Không chọn nghề thay thế, không Search, không đọc hồ sơ riêng, không ghi dữ liệu. Chỉ có thể trả tập con của nút server đã dựng; kiểm lại index, trích dẫn thật từ câu hiện tại và câu trả lời, tên nghề catalog. Tìm tên chỉ là kiểm tra bổ sung, không thay kiểm định ngữ nghĩa.
- `advisor/graph.py` giữ bounded retry một lần. Metadata sai ở lượt cuối không còn gây502: giữ câu trả lời/đề xuất hồ sơ và bỏ nút không xác minh. Kiểm định timeout/JSON lỗi thì bỏ nút ngay, không tự gọi lại vô hạn. Lỗi câu trả lời chính rỗng/cắt dở hoặc lỗi dịch vụ chính vẫn xử lý như cũ, không biến thành PASS giả.
- Prompt đồng bộ nội dung tư vấn và metadata, ưu tiên câu hiện tại; không gắn nghề cùng nhóm rộng hoặc lấy nghề từng nhắc làm mục tiêu mới. Không hardcode nghề trả lời/đường dẫn theo các ví dụ thử.
- Không thay frontend, catalog200, Firebase, quyền hồ sơ, Neon/schema, quota8 hoặc hành trình cùngtab. Câu trả lời không có nút không thêm lượt model. Câu có nút thêm tối đa một kiểm định mỗi attempt: timeoutHTTP8s, trần9s, tối đa4nút/1200token; vẫn trong timeout tổng hiện hữu. Nếu cần retry thì tối đa2main+2review cho **một** request/quota, lưu atomic như cũ. Có thêm chi phí/độ trễ cho câu có nút; cần theo dõi trênLIVE. Đây là bản vá kiểm định metadata, không viết lại pipeline AI.

## Kiểm thử đã chạy thực tế

- **58 test Python PASS, 0 SKIP**: 14 kiểm thử mới, 11 navigation,13 Task44,15shared-protection,5Task42pipeline. PostgreSQL local cluster/schema riêng; mock DeepSeek, không dùng Neon. Ban đầu3classPG SKIP vì thiếu đường dẫn binary ở worktree mới; đã đặt đúng bộ local và chạy đủ, không gộp SKIP vào PASS.
- Kiểm thử mới gồm đúng căn cứ/careerID, đổi chủ đề/phủ định có tên nghề, quote giả, index trùng/thiếu/ngoài phạm vi, timeout/truncation, không có nút thì không gọi review, thư viện không thay nghề, metadata sai hai lần vẫn200, đề xuất hồ sơ giữ nguyên, quota chỉ1, replay miễn phí,6tổ hợp ba provider và hai kiểu lưu. Mock không chứng minh model hiểu nghĩa trênLIVE.
- Chrome static navigation: XSS/openredirect, same-tab/tabcount/draft, zeroAIrequests, responsive PASS. Chrome FastAPI+PG thật local: survey/draft/originalID,3nghề,story/scene,BackForward,1→1tab, khôngchat/create/analysis do điều hướng PASS. Google là fixture local; không phải popup thật.
- JSON mode theo tài liệu chính thức DeepSeek: https://api-docs.deepseek.com/guides/json_mode/ . Review sai/cắt dở không được tin cậy.

## Chưa hoàn thành ở checkpoint này

Chưa build hoặc kiểm DeepSeek LIVE Preview của bản vá này. Chưa phát hành Production, chưa push nhánh. Sẽ bổ sung kết quả thực tế sau Preview; giữ nguyên Production `da6d146`/`dpl_9TdB69NsBqWmKssEUQbNhG92jsVS`.

Không tự sửa metadata đã lưu trong hội thoại cũ hoặc gọi AI khi mở lịch sử; bản vá áp dụng cho phản hồi mới. Kiểm định LLM là hàng rào giảm rủi ro, không chứng minh đúng mọi tình huống ngôn ngữ. Nếu không có căn cứ hoặc dịch vụ kiểm định lỗi, ưu tiên không hiện nút.
