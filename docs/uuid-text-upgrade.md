# UUID → TEXT: migration cấu trúc 005

Hai cột là `guest_ai_requests.request_id` và `guest_ai_requests.session_id`. Metadata Production đã đọc: UUID NOT NULL, không default; PK trên request_id; CHECK status ba giá trị và các NOT NULL vẫn giữ; index PK, `(uid,created_at)`, `(uid,status)`; không có FK, user trigger hoặc view phụ thuộc.

`migrations/005_uuid_text_compat.sql` chỉ đổi kiểu, dùng `USING column::text` bảo toàn biểu diễn UUID chuẩn. Không DELETE/UPDATE bản ghi, không sửa quota, không tạo phiên giả, không đánh dấu phiên đã xóa. Script bắt đầu transaction, timeout lock3s/statement30s; khóa theo usage → request → session. PostgreSQL rebuild index/PK khi cần nhưng script không DROP CONSTRAINT. Default UUID (nếu có ở môi trường khác) được giữ biểu thức và ép kết quả TEXT.

Migration dừng khi kiểu lạ, inheritance/partition, FK tham chiếu/có tham chiếu từ cột đổi, CHECK/exclusion phụ thuộc cột, trigger, expression/partial index hoặc view cần review. Hậu kiểm so nguyên checksum JSON/count ledger, quota, constraint definitions và số request thiếu phiên; lỗi phải rollback toàn transaction. Chạy lại khi đã TEXT là no-op, không chạy lại002.

Phạm vi khác migration003 cũ: 003 là đối soát toàn schema/semantics và đang ở checkout chính chưa tích hợp; 005 là chuyển kiểu độc lập, giữ nguyên cả ngoại lệ legacy đã tồn tại. **Không coi 005 là xác nhận request mồ côi hợp lệ hoặc phê duyệt bỏ qua gate dữ liệu.**

## Bằng chứng

- 9 test local trên PostgreSQL: cast/default/PK/CHECK, no-op, FK hai chiều, view/custom CHECK, trigger/expression index, lock timeout, cố ý làm hậu kiểm lỗi để xác nhận rollback cả type/default/dữ liệu, và chạy module store/quota thực của7c07d33 trước/sau đổi kiểu cùng store mới sau đổi.
- Neon staging riêng `la-ban-preview / ticket-7-premium-preview`, schema synthetic mới (không copy dữ liệu thật): thêm created_at/index/CHECK như Production, gồm request có phiên và request thiếu phiên, quota2. 005 → 004 PASS; checksum/count, định danh và quota không đổi; schema ready=true. Không đổi public schema cho thử UUID và không chạm Production/backup.

## Quy trình Production dự kiến — CHƯA THỰC HIỆN

1. Đối chiếu deployment/code và chốt ngoại lệ legacy; xác minh nhánh `production`/`neondb`, current_schema=public, quyền/backup có thể khôi phục, metadata không phát sinh dependency mới.
2. Kiểm tra runtime binding với `scripts/check_storage.py --runtime --expected-host <host đã xác minh> --expected-database neondb` trong môi trường vận hành có sẵn biến bí mật. Công cụ không in host/password/URL, không đọc dotenv; cưỡng chế read-only từ startup, phân biệt URL sai, target sai, kết nối và schema. Không thể giải mã Sensitive Vercel từ API metadata để giả xác minh.
3. Sau khi người dùng phê duyệt riêng: ngừng nhận AI request, chờ/đối soát các request đang chạy; lưu schema dump và backup/Neon recovery point mới. Không thay nhánh backup đã có.
4. Thực hiện005 trên đúng database/schema; không chạy lại001/002/003. Sau đó thực hiện004 nếu chưa có. Đường005→004 đã kiểm thử; database mới đã có004 và ID TEXT chỉ cần005 no-op. Không dùng IF NOT EXISTS để suy ra schema đúng.
5. Hậu kiểm schema/counters/checksums/dependencies, verify old7c đọc/ghi tương thích trên TEST; chỉ deploy candidate sau các gate dịch vụ thật/runtime. Giữ dữ liệu gốc, không chuyển Production sang database staging.

Rollback khi transaction005 lỗi: PostgreSQL rollback type/default/data, không cần script reset. Nếu đã COMMIT005, ưu tiên giữ schema TEXT và rollback code đã kiểm tương thích; không tự ép TEXT về UUID khi có thể có giá trị mới ngoài UUID. Chỉ đổi ngược khi dừng traffic, kiểm tất cả giá trị cast được, đối chiếu dependency/default và có phê duyệt; nếu không, forward-fix. Không restore backup đè lên dữ liệu mới. Khi candidate đã tạo member leases charge_quota=false, phải settle/fence bằng code hiểu cột đó trước bất kỳ rollback về7c; không DROP004/005 hoặc hoàn sai quota.
