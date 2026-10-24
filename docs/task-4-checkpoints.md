# Checkpoint Task 4

Nền df1c300 xác minh Production ngày 25/10/2026; backup Git backup/task-4-before-advisor-3. Không sửa Production.

## 4.1 — a0f08dc

Đã đổi header/phụ đề, bỏ avatar/nhãn assistant, giữ bubble/copy; parser xưng hô theo đúng phiên và yêu cầu mới. Hai unittest PASS, JS/import PASS. Browser và DeepSeek thật chưa nghiệm thu.

## 4.2

Adapter Brave thực qua httpx, không có provider giả. Thiếu SEARCH_API_KEY được cấp phép => BLOCKED live search. Truy vấn giữ năm sự kiện, ngày xuất bản tách riêng. Cache TTL theo UID+hash, giới hạn 64 entry, không đưa survey/profile vào query. Kiểm URL/IP public và HEAD ghim IP/TLS chống DNS rebinding, không follow redirect. Nguồn chỉ snippet có kiểm link, không tuyên bố đọc toàn trang. Allowlist citation, bounded timeout/retry/response, tích hợp trong graph sau auth/rate/quota hiện có. Sáu unittest 4.1/4.2 PASS; mock chỉ chứng minh logic, chưa chứng minh chất lượng DeepSeek/Search thật.

## 4.3

17 test phân tích/hồ sơ trên PostgreSQL local riêng PASS (không Neon/provider thật). Migration 006 bổ sung một bảng confirmed items, không sửa schema/dữ liệu cũ, có guard staging/transaction/lock timeout; chưa chạy trên Neon. Không backfill hồ sơ suy luận cũ thành đồng ý. Phân tích năm câu qua một tác vụ riêng trong lượt chat đã có auth/rate/quota, đề xuất có quote đối chiếu câu 1–5; không tự ghi hồ sơ. AI lỗi giữ khảo sát/câu hỏi và không tự phân tích lại mỗi lượt; chỉ retry khi người dùng yêu cầu. Mỗi mục cần xác nhận, sửa/xóa riêng, version chống ghi đè, retry không ghi đè mục tự sửa. Hồ sơ tắt mặc định từng conversation và không được chèn vào prompt khi tắt. Guest chuyển owner trong cùng transaction claim, giữ TTL cho đến khi tài khoản đồng ý giữ lâu dài. Các hạng mục phụ thuộc DeepSeek/Firebase/Neon vẫn BLOCKED LIVE theo lựa chọn người dùng.

## 4.4 — tích hợp và cách ly

Backend tổng 86 trường hợp riêng biệt đạt qua các lượt trọng tâm, 11 Node, Chrome 7 nhóm/PG local. Đã sửa 204 JSON parser, giữ từ chối proposal sau reload, rate ghi profile UID/IP chung không trừ quota, TTL cleanup có lô. Navigation 5 tạo/5 mở/rapid không gọi AI, 7 request như baseline; visual max local 16,7 ms, không cam kết nhanh hơn hoặc SLA mạng Production. Read-only Preview chỉ bật khi VERCEL_ENV=preview + flag server; client ?preview=1 không bật bypass trên Production. Người dùng chọn không có môi trường thử/provider riêng, nên không ghi Neon hoặc sao chép secret Production. LIVE vẫn BLOCKED; xem bảng 53 yêu cầu và báo cáo cuối.

Preview 5bbc282 / dpl_FuHqTyMmFEaAam7x6ipEYAJ2CBxX READY tại https://quocan4-gbxablhb0-khkt3.vercel.app/ai-career-advisor?preview=1. HTTP/Chrome desktop-mobile và isolation PASS. Tracking đủ53: 19 PASS/34 BLOCKED/0 FAIL/0 TODO. Production vẫn df1c300, không ghi/migrate/merge/deploy Production.
