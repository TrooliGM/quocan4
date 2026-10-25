# Task 4.2 — DDGS Web Search, Preview trước Production

## Phạm vi và kiến trúc

Tiếp tục trên `feat/task-4-1-advisor-intelligence`, baseline `163e61c`, không chuyển nhánh hoặc sửa checkout chính. Cả Guest/member/QA và ba API AI vẫn dùng chung Task4.1. Thêm DDGS vào `SearchProvider`, giữ Brave tùy chọn; `SEARCH_PROVIDER=ddgs` chỉ được override cho deployment Preview mới. Không sửa biến môi trường project/Production, secret hay schema.

Pin `ddgs==9.16.1` trong cả requirements và pyproject. Đã đọc metadata/wheel upstream: Python>=3.10, phụ thuộc primp/lxml, TLS mặc định bật. Local Python3.14 cài/import được và trả kết quả Internet thật. Nguồn kỹ thuật: https://github.com/deedy5/ddgs và https://pypi.org/project/ddgs/9.16.1/. Khả năng cài/runtime Linux sẽ phải được Vercel build và LIVE xác nhận riêng.

DDGS chạy worker ngoài event loop, tối đa2 tác vụ đồng thời mỗi instance,5 kết quả, safe-search on, backend auto, region vn-vi, request timeout5s và async deadline7s. Slot chỉ hoàn khi worker thực sự kết thúc, kể cả caller bị hủy. Cơ chế auth/rate/quota PG dùng chung giữa các instance không thay đổi. Không có endpoint Search công khai riêng để lách bảo vệ AI. DDGS không bảo đảm tính sẵn sàng hoặc thời hạn tổng của các backend nội bộ; worker quá hạn không bị kill nhưng không tạo hàng đợi vô hạn.

Giữ cache64 mục theo hash owner/query, bổ sung provider vào khóa để không trộn Brave/DDGS. Giữ deadline tổng12s cho truy xuất+xác minh. Nguồn phải HTTPS/public DNS, HEAD ghimIP/SNI/TLS, không redirect/body/fullpage; lọc relevance, ưu tiên gov/edu, loại trùng, tối đa4 nguồn theo schema hiện có. Bổ sung percent-encoding cho đường dẫn Unicode trước HEAD. Link bị403/redirect/timeout bị loại; trạng thái no_verified_sources/unavailable không được coi là tra cứu thành công. Chỉ đọc snippet; không gọi DDGS.extract hoặc fetch URL do LLM tự tạo.

## Ý định, riêng tư, grounding

Nhận biết năm lịch sử, thông tin mới, lương, tra giúp, Google, viết tắt và hỏi nguồn; không mặc định mọi câu Công an là điểm chuẩn. Không Search mọi câu hỏi thường hoặc yêu cầu không tra web. Follow-up chỉ lấy chủ đề câu tra cứu công khai trước hoặc career context, không lấy survey/profile/summary. Chặn truy vấn có định danh rõ ràng, email/điện thoại/URL, thông tin đăng nhập và lời tự giới thiệu cá nhân; không log truy vấn hoặc lỗi upstream có query. Bộ lọc heuristic có giới hạn, chưa phải chứng nhận DLP mọi ngôn ngữ.

Snippet là dữ liệu không tin cậy, đặt trong context có nhãn; prompt yêu cầu bỏ chỉ dẫn từ web, chỉ trích link đã xác minh, phân biệt năm sự kiện và ngày xuất bản, đối chiếu mâu thuẫn và không bịa số liệu. Không có bảo đảm tuyệt đối rằng LLM miễn nhiễm prompt injection. Test injection kiểm boundary/link allowlist; không gọi mock là bằng chứng chống mọi cuộc tấn công LIVE.

API compatibility giữ nguyên sources/search_status trên retry saved_response, không gọi lại AI/Search hoặc trừ thêm quota. UI, 200 nghề, Truyện nghề, auth, quota8 và quyền profile không đổi.

## Kiểm thử hiện có, trước Preview

- 16 test mới về adapter/policy/pipeline PASS, external providers mock, PG local thật.
- Hồi quy Search cũ/context/unified/protection: 35 method PASS qua các lượt trọng tâm; không cộng ca chạy lại. Bộ14 test mới ban đầu có lỗi fixture dùng câu không yêu cầu tra cứu nhưng kỳ vọng privacy_blocked; đã sửa thành câu tra cứu rõ ràng và retest PASS, không thay bảo vệ để làm test xanh.
- Internet local: CNTT2026 và tuyển sinh mới nhất có nguồn đã HEAD; câu Công an2020 timeout7s. Không suy ra Vercel PASS từ kết quả local.
- Vercel build/LIVE, URL, chất lượng câu trả lời, latency và hạn chế: sẽ cập nhật bằng bằng chứng sau triển khai, chưa đánh dấu hoàn thành Search.

## Phát hành và rollback

Chỉ Preview, cùng staging schema-only `task41-preview-schema-20261025`, role riêng như Task4.1, không sao chép dữ liệu người dùng và không chạy migration. Giữ data-profile canary QA-only; AI Search không QA-gated. Giữ Deployment Protection, Firebase authorized domain phải bổ sung đúng hostname nếu cần, không sửa project Firebase.

Rollback Preview: mở lại deployment Task4.1 `dpl_Gooca1fySbMiFkmzANji1bGY2w1x`, hoặc deploy source cũ với staging riêng. Không reset dữ liệu/quota. Production vẫn checkpoint957ffde; phải được phê duyệt riêng, build mới với envProduction, không promote deployment đang dùng database staging. DDGS scraping có thể bị chặn từ datacenter; nếu LIVE thất bại phải báo BLOCKED, không tuyên bố Search hoàn tất hoặc dùng nguồn giả.
