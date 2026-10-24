# Checkpoint Task 4

Nền df1c300 xác minh Production ngày 25/10/2026; backup Git backup/task-4-before-advisor-3. Không sửa Production.

## 4.1 — a0f08dc

Đã đổi header/phụ đề, bỏ avatar/nhãn assistant, giữ bubble/copy; parser xưng hô theo đúng phiên và yêu cầu mới. Hai unittest PASS, JS/import PASS. Browser và DeepSeek thật chưa nghiệm thu.

## 4.2

Adapter Brave thực qua httpx, không có provider giả. Thiếu SEARCH_API_KEY được cấp phép => BLOCKED live search. Truy vấn giữ năm sự kiện, ngày xuất bản tách riêng. Cache TTL theo UID+hash, giới hạn 64 entry, không đưa survey/profile vào query. Kiểm URL/IP public và HEAD ghim IP/TLS chống DNS rebinding, không follow redirect. Nguồn chỉ snippet có kiểm link, không tuyên bố đọc toàn trang. Allowlist citation, bounded timeout/retry/response, tích hợp trong graph sau auth/rate/quota hiện có. Sáu unittest 4.1/4.2 PASS; mock chỉ chứng minh logic, chưa chứng minh chất lượng DeepSeek/Search thật.
