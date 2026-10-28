# Task 4 — kết quả Production ngày 28/10/2026

**Đã phát hành và hậu kiểm trên domain chính. Không đồng nghĩa toàn bộ Task 4 đã hoàn thành.**

- Website: https://labanhuongnghiep.vercel.app/ai-career-advisor
- Deployment: **dpl_7cdWzerGqdzD3c4Ucjvfb8GaJbfE**, target **production**, **READY**.
- Commit mã nguồn thực tế: **43a8337f694c6931fcf26805a9349841ddabf93c** — `Remove career profile and publish shared survey results`.
- Đã commit đúng35 file, kiểm secrets/diff; push fast-forward `1a534b1 → 43a8337` lên `origin/main`, không force/ghi đè lịch sử. Checkout gốc và worktree khác giữ nguyên.
- Project/team **khkt3/quocan4**, Production Branch main. Giữ cấu hình chặn auto-deploy main; phát hành thủ công bằng CLI65.4.

## Bản đã triển khai

Nguồn từ worktree `task4-remove-profile`, kế thừa toàn bộ bản vá gỡ Hồ sơ và area=null. Preview mới **dpl_ARVNjK92VvqTVR1FFDw7PW4JsYQW** được kiểm thử LIVE trước phát hành. Dry-run Production đối chiếu **100 file nguồn khớp chính xác** bản Preview đã kiểm thử (105 mục manifest gồm5 thư mục rỗng). Không đưa dotenv, credentials, artifact, dữ liệu local hoặc test vào deployment.

Đã dựng Production candidate riêng với **--prod --skip-domain**, giữ domain cũ trong lúc kiểm tra. Candidate dùng environment Production hiện hữu, **không truyền env override/DATABASE_URL Preview**. Kiểm schema Neon Production bằng kết nối TLS, SQL read-only; so khớp nguyên dữ liệu hội thoại của tài khoản thử riêng giữa SQL và runtime candidate, xác nhận dùng đúng database Production. Tạo đúng một hội thoại tạm của tài khoản thử qua API khi không tìm thấy hội thoại thử cũ còn hiệu lực; không viết SQL dữ liệu hoặc đọc hội thoại học sinh.

Sau smoke/config/owner/schema/binding PASS mới promote. Control plane xác nhận domain chính trỏ **dpl_7cdWzerGqdzD3c4Ucjvfb8GaJbfE**, metadata SHA đúng **43a8337…**, target production/READY. Metadata các binding environment trước/sau không đổi.

## Quyền sử dụng sản phẩm

Rà soát cho thấy QA gate của pipeline/search/analysis đã được bỏ ở base; không thêm vai trò QA giả hoặc refactor lại những phần đã công khai. Bản phát hành bảo đảm backend/API và UI thống nhất:

| Chức năng từng QA-only | Guest | Member/QA |
|---|---|---|
| Khảo sát, tự phân tích, 3 hướng nghề có căn cứ | Có trong phiên Guest | Có trong hội thoại riêng |
| DeepSeek, ngữ cảnh, DDGS có nguồn | Có, tối đa8 lượt chat | Có, rate limit giữ nguyên |
| Retry phân tích, reload kết quả | Có, cùng request_id/ngân sách | Có, cùng cơ chế |
| Nghề/truyện/chat trong cùng tab | Có, giữ phiên/khảo sát/nháp | Có, giữ phiên/khảo sát/nháp |
| Lưu hội thoại lâu dài | Phải đăng nhập | Có, đồng ý lưu đúng hội thoại |
| Hồ sơ cá nhân đã gỡ | Không khôi phục; API410 | Không khôi phục; API410 |
| Admin/debug/bypass/đọc dữ liệu người khác | Không cấp | Không cấp |

## Kiểm thử đã thực hiện

| Kiểm tra | Preview mới | Production chính thức |
|---|---|---|
| Build, source/assets đúng bản vá, trang chủ/200 nghề/12 nhóm/truyện/video | PASS | PASS |
| Guest sạch Chrome, cấp phiên bình thường, cookie Secure/HttpOnly/Strict | PASS | PASS |
| Guest hoàn thành5 câu → tự phân tích,3 hướng có căn cứ, không lỗi area | PASS LIVE | PASS LIVE |
| Guest retry cached không thêm attempt/chat quota; reload giữ kết quả | PASS | PASS |
| Guest DeepSeek + DDGS có nguồn | PASS,2 nguồn | PASS,4 nguồn, lượt đầu17,45s |
| Guest câu1–8, câu9 trả429, duplicate ở hạn mức không trừ thêm | PASS LIVE | PASS LIVE |
| Member Firebase SDK email/password thật | PASS | PASS |
| Member hoàn thành khảo sát mới, tự phân tích,3 hướng, retain, đọc lại | PASS đọc/cache; Google user thử đầy đủ | PASS Chrome/API LIVE, cùng ID và khảo sát |
| Member DeepSeek + DDGS | PASS chat7,71s; nguồn được kiểm trước | PASS LIVE,10,25s/4 nguồn |
| Popup Google thật, giữ hội thoại/khảo sát/lưu/reload | PASS người dùng xác nhận | **PASS người dùng xác nhận** trên domain chính |
| Guest/Member nghề → truyện → chat, cùngtab/nháp/khảo sát, không POST AI/session thêm | PASS | PASS Chrome thật |
| Người khác/UID hoặc role giả, token sai, Origin ngoài | PASS401/403/404 | PASS401/403/404 |
| API AI cũ vẫn từ chối token sai; private paths không xuất bản; Hồ sơ410 | PASS | PASS |
| Desktop1440/mobile390, không UI Hồ sơ,0 JavaScript errors | PASS | PASS, ảnh đã xem |
| Nút xóa dữ liệu sidebar | PASS hiển thị/xác nhận/Hủy | PASS hiển thị/xác nhận/Hủy; không thực thi xóa hàng loạt |

**97 kiểm thử Python trọng tâm PASS** (59+38), PostgreSQL local và provider mock. Kế thừa các bài local/LIVE còn phù hợp, không chạy lại toàn Super Board và không biến mock thành LIVE. Popup Google là bằng chứng người dùng xác nhận, không phải thao tác tự động của Codex.

Bằng chứng máy: artifacts/public-production-dry.json, public-production-candidate.json, public-production-gates.json, public-production-promote.json, public-production-member-browser.json, public-production-guest-live.json, public-production-post.json. Ảnh production-member-1440.png/390.png và production-guest-1440.png/390.png. Artifact/Chrome profiles/DPAPI bị ignore, không đưa lên GitHub hoặc deployment. Không ghi token, DATABASE_URL, nội dung học sinh hoặc danh tính tài khoản vào báo cáo.

## Dữ liệu, giới hạn và rollback

- Không migration, đổi schema/DATABASE_URL/Firebase/DeepSeek env, tạo database, reset quota hoặc xóa dữ liệu. Chỉ API thử trên danh tính tổng hợp riêng; không dùng dữ liệu học sinh.
- Mỗi môi trường dùng một Guest được cấp phiên thông thường, giữ đến hết8 lượt, không thay Guest để vượt hạn mức. Ngân sách phân tích/rate limit và quyền sở hữu vẫn giữ.
- Công tắc sự cố Search toàn cục vẫn được tôn trọng; không tạo nguồn giả khi provider thiếu/lỗi. Micro Web Speech/Google STT phụ thuộc cấu hình hiện hữu, không thêm Vbee hay mua dịch vụ.
- Historical ValidationError: **root cause undetermined**. Lỗi area hiện tại có tái hiện riêng, bản sửa và regression/LIVE PASS; không tuyên bố đã xử lý mọi lỗi lịch sử hoặc độ chính xác của mọi câu trả lời AI.
- Chưa kiểm thử thao tác xóa dữ liệu hàng loạt LIVE; chỉ kiểm xác nhận/Hủy và các bài local quyền sở hữu.
- Không gặp lỗi nghiêm trọng cần rollback.

Rollback đã giữ: **dpl_Da9yybCwP9VnHeifXCX3Jo9YdCsd**, source **1a534b186a9a53aedc7b94d3a01a2d4f6a3b21b4**. Lệnh `vercel rollback dpl_Da9yybCwP9VnHeifXCX3Jo9YdCsd --scope khkt3 --yes`; kiểm lại alias/HTTP. Không cần đảo migration hoặc reset database. Git backup local `backup/task4-before-public-profile-removal-20261028` giữ origin/main trước phát hành. Báo cáo hậu kiểm được commit riêng chỉ tài liệu; không thay commit mã đang phục vụ Production.
