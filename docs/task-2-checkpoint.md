# Nhiệm vụ 2 — đã triển khai, chờ duyệt giao diện

Cập nhật 2026-10-24. Nhánh feat/task-2-career-library, worktree D:/khkt/.claude/worktrees/task-2. Nền 88639f8/b41f45c; giữ Navbar/Hero và Nhiệm vụ 1. Không push/merge/deploy/Neon. Không triển khai Nhiệm vụ 3.

## Xem trước

**http://localhost:8003/** đã được xác minh HTTP và Chromium desktop/mobile. Đây là task-2, không phải task-1 cổng 8002. Runtime FastAPI thật, PostgreSQL local mới riêng trên loopback, cấu hình Firebase Web công khai (không phải secrets), **AI_DEMO_MODE=true, có nhãn demo, không gọi DeepSeek thật**. Không dùng service account/dotenv/DATABASE_URL Production hoặc shared UID giả trong runtime. Chỉ khởi tạo schema 001/002 trong cluster local mới; không sửa migration/Production.

## Hoàn thành

- Đúng 200 nghề, 12 nhóm; bốn JSON, mỗi file 50 nghề, tất cả trường schema, ID/tên không trùng, mô tả khác nhau. Nguồn biên soạn tên/nhiệm vụ/thử thách trong career-seeds.txt. Giữ ID sáu nghề cũ.
- API mới categories/list/detail, tìm không dấu/hoa thường/lĩnh vực/từ khóa, trang mặc định 12 và tối đa 24. API /api/careers cũ giữ tương thích.
- Thư viện: danh mục trước, không đổ 200 card; tìm/lọc/xem tất cả, Xem thêm, trạng thái rỗng/lỗi, một modal chung và hai CTA. Navbar/Hero CSS không sửa.
- Mode discovery/exploration và career_id/tên nghề được backend kiểm tra, lưu ngay khi INSERT trong metadata phiên. Không migration mới. Legacy session hoạt động. Quyền owner, consent, TTL, Firebase Anonymous, quota 8, rate limit và account linking cũ được giữ.
- Discovery giữ khảo sát/phân tích; exploration hoàn tất khảo sát rồi điền draft hỏi nghề, học sinh sửa trước gửi. Khôi phục mode/nghề/survey và draft mặc định khi mở lại. Draft tự sửa chưa gửi chỉ ở RAM.
- LangGraph nhận câu hỏi/câu trả lời khảo sát. Exploration chỉ gửi nghề đang chọn và prompt tư vấn chuyên sâu, không xếp hạng. Discovery tham khảo tối đa 8 nghề thay vì gửi cả 200. Keyword retrieval chỉ chọn ngữ cảnh, không thay model bằng thuật toán khớp từ để kết luận nghề.
- Liên kết truyện theo ID, có truyện mở cảnh đầu, thiếu truyện báo “Truyện nghề này đang được cập nhật”, không fallback; hỗ trợ Back/Forward. Không tạo 200 truyện.

## Kiểm thử đã chạy

**17 test backend PASS**: 5 schema/search; 4 API/context/ownership/payload AI mock; 7 khảo sát Nhiệm vụ 1; 1 quota guest PostgreSQL local (1–8 được, 9 chặn). Không cộng lần chạy lại thành test mới. Test gồm xác thực và cách ly guest A/guest B/member, survey, idempotency, immutable, row lock, hồi phục context. Python compileall/Node syntax/git diff --check PASS; frontend static không có bundler riêng.

Browser Chromium 1440/390 PASS với **Firebase stub + AI demo + PostgreSQL local riêng**: 12 nhóm, danh sách ban đầu rỗng, lọc/tìm, modal/ID CTA, hai mode, khảo sát, draft sửa được và reload trước gửi, chat/history, member chat/logout, truyện đúng/thiếu, không overflow hoặc JS exception. Một lỗi harness trả DOM object làm điều kiện wait đã sửa thành Boolean; không sửa sản phẩm để che lỗi. Log JSONDecodeError trong memory ở test HTTP mock là nhánh nonfatal đã dự kiến.

Chromium truy cập trực tiếp **8003**: home/library/list/modal desktop/mobile PASS, tám ảnh. Không gọi full Super Board hoặc provider AI thật. Các test browser không chứng minh Firebase/DeepSeek thật.

## Ảnh trong worktree

- artifacts/preview-home-{1440,390}.png
- artifacts/preview-library-{1440,390}.png
- artifacts/preview-list-{1440,390}.png
- artifacts/preview-modal-{1440,390}.png
- artifacts/task2-career_discovery-{1440,390}.png
- artifacts/task2-career_exploration-{1440,390}.png
- artifacts/task2-exploration-draft-{1440,390}.png

Ảnh chat dùng fixture, không phải provider thật. Script preview local: artifacts/run_preview.py; lấy cấu hình Web công khai, không sao chép secrets vào Git. Test tái lập: tests/browser_task2.py, tests/test_task2.py.

## Giới hạn còn mở

Chưa kiểm chứng trọn luồng Firebase Google/email/Anonymous thật trong flow mới, DeepSeek thật/chất lượng ngữ nghĩa/xưng hô, Safari hoặc thiết bị vật lý. Firebase config health=true không phải bằng chứng login PASS. Preview AI demo chỉ để duyệt UI, không tạo kết luận năng lực thật.

Nội dung nghề được biên soạn ngắn gọn, có kỹ năng/môn học/môi trường dùng chung theo lĩnh vực. Không bịa lương/điều kiện tuyển dụng/cấp phép, không khẳng định phù hợp. Chưa được chuyên gia thẩm định từng nghề; cần biên tập trước phát hành rộng, nhất là y tế/pháp lý. Tham khảo nguyên tắc phân biệt nghề theo nhiệm vụ của https://isco.ilo.org/ và https://esco.ec.europa.eu/en/classification/occupation_main ; 12 nhóm UI không phải phân loại pháp lý, không tuyên bố từng record được ánh xạ mã ISCO/ESCO.

Các gate Production ticket #7 vẫn chưa giải quyết. Dữ liệu preview là local, không phải lịch sử Production.

## Checkpoint Nhiệm vụ 3

Chỉ bắt đầu khi người dùng yêu cầu. Đọc HEAD task-2 và bốn JSON, liên kết truyện bằng ID ổn định thay vì vị trí mảng; giữ sáu truyện cũ và trạng thái chưa cập nhật. Chưa xây Nhiệm vụ 3, không tự phát hành. Hiện dừng để người dùng xem giao diện 8003 và duyệt.

---
## Lưu trữ kế hoạch ban đầu tại b41f45c (không phải trạng thái hiện tại)

# Nhiệm vụ 2 — checkpoint khởi đầu, CHƯA HOÀN THÀNH

Ngày 2026-10-23. Nhánh `feat/task-2-career-library`, worktree `D:/khkt/.claude/worktrees/task-2`, tạo từ **88639f8** (đủ Nhiệm vụ 1 và Navbar phương án 2). Checkout task-1 và checkout chính được giữ nguyên. Không push/merge/deploy hoặc kết nối Neon.

## Đã làm thực tế

- Đọc yêu cầu ở attachment b2d789d6-9247-4740-8eb2-1d2e718f9bfc/Pasted text.txt.
- Tạo hợp đồng Pydantic Career/Catalog đủ các trường yêu cầu; 12 nhóm ổn định. Giữ nguyên ID sáu nghề cũ để tương thích truyện.
- Chuẩn hóa tìm kiếm chữ thường/không dấu, kể cả đ; phát hiện trùng ID/tên và nhóm không hợp lệ.
- Năm test hợp đồng dữ liệu PASS. Đây là dữ liệu mẫu unit test, **không phải thư viện 200 nghề**, không phải kiểm thử Guest/UI/AI.
- Chưa nối module mới vào API hoặc frontend. Chưa sửa chức năng đang hoạt động.

## Việc còn lại bắt buộc

1. Biên soạn/kiểm tra đúng 200 nghề thực tế, đủ schema, nội dung riêng, không bịa lương/cấp phép. Bốn đợt 50 nghề. Hiện website vẫn có sáu nghề cũ; dữ liệu sản phẩm mới chưa tạo.
2. API thư viện/categories/detail và phân trang/tìm kiếm; giữ API dùng chung đang hoạt động. UI lĩnh vực trước, không đổ 200 card; modal tái sử dụng với hai CTA.
3. Lưu `career_discovery`/`career_exploration` cùng career_id trong metadata từng phiên tương tự khảo sát; validate career_id backend. Không đổi schema Production. Exploration sau khảo sát chỉ điền draft hỏi nghề để học sinh sửa trước gửi; discovery giữ khảo sát/phân tích từ Nhiệm vụ 1.
4. Thu hẹp ngữ cảnh AI theo nghề/tìm kiếm, **không gửi cả 200 nghề ở mọi lượt**. Không giả lập kết quả AI. Giữ xưng hô và hồi phục mode/nghề/survey khi mở lại.
5. Truyện mở theo ID, không fallback sang nghề khác nếu ID hợp lệ chưa có truyện; thông báo đang cập nhật. Không xây Nhiệm vụ 3.
6. Giữ Firebase Anonymous + token thật mỗi khách, quota 8 và rate limit cũ. Không dùng UID chung, không localStorage làm xác thực, không ép login trước quota. Kiểm thử cách ly guest/member, mode, survey, quota và account switching. Local guest cần PostgreSQL test riêng theo adapter hiện tại; không giải quyết bằng vô hiệu hóa guest.
7. Kiểm thử UI desktop/mobile, route, hai mode AI, danh mục đủ 200, modal/story mapping, bản khảo sát mới; ghi rõ fixture/provider thật. Không gọi lại full Super Board; tối đa hai vòng sửa/thử lại mỗi lỗi.
8. Chạy Preview LOCAL bằng database tách biệt; không lấy secrets/DB Production. Chưa có server Nhiệm vụ 2 mới. `localhost:8002` là server task-1 có AI demo và thiếu cấu hình Firebase, **không được báo là preview đầy đủ Nhiệm vụ 2**.
9. Commit phần hoàn thiện, danh sách file/test/ảnh, checkpoint Nhiệm vụ 3; không push/merge/Production deploy. Không tuyên bố toàn bộ Nhiệm vụ 2 hoàn tất trước khi các mục trên thực sự làm xong.

Yêu cầu đầy đủ: attachment gốc. Các giới hạn phát hành Production của ticket #7 vẫn chưa được giải quyết. Không mở lại hay sửa migration 003 trong nhiệm vụ này.

## QA hồi quy Nhiệm vụ 1 + 2 — 2026-10-24

Trạng thái mới nhất sau baseline `8f32e3b`: **NOT READY FOR VERCEL PREVIEW**. Giữ thiết kế đã duyệt, không bắt đầu Nhiệm vụ 3. Đã sửa hai lỗi High: whitelist đúng bốn JSON nghề cho runtime Vercel (data khác vẫn bị loại) và chống response/error modal cũ ghi đè nghề vừa chọn. Hai index chỉ tăng phiên bản JS; không đổi auth/quota/schema.

Kết quả riêng biệt: **172 PASS / 2 FAIL / 5 BLOCKED / 3 CHƯA KIỂM CHỨNG**, 182 đơn vị. Backend có 79 method kết quả cuối PASS qua batch 78/79 và retest module 4/4 sau sửa encoding stdin của harness; không phải một batch 79/79. Browser 93 assertion PASS tại 1440/768/390/360px, Firebase stub và AI demo trên fixture 8013, PostgreSQL local riêng. Kiểm real Firebase/DeepSeek cho hai mode mới bị chặn vì chưa có môi trường test riêng được phép; không suy từ QA ticket #7 cũ.

Hai FAIL là rủi ro High còn mở: `/api/advice` và `/api/career-stories/{career_id}/ask` gọi graph khi không Authorization, không quota/rate chung (tái hiện mock, không gọi AI thật). Cần quyết định bảo vệ hoặc tắt legacy AI trước Preview có provider thật. Chưa chứng nhận biên tập ngữ nghĩa toàn bộ 200 nghề, thiết bị vật lý/Safari hoặc Vercel runtime thật. Đã rà 24 mẫu/12 nhóm và exact duplicates, không phát hiện trùng chính xác.

Báo cáo local: `artifacts/super-board-report.md`, `artifacts/super-board-summary.json`; ảnh `artifacts/qa/home-{1440,768,390,360}.png` và `exploration-draft-360.png`. Artifacts không commit. Server xem thử 8003 giữ nguyên; không Neon, push, merge hoặc deploy. Chỉ commit bản sửa đã kiểm chứng trên `feat/task-2-career-library` theo quyền được cấp.

## Shared AI protection — cập nhật sau b8cef96, 2026-10-24

Đã sửa High legacy bằng bảo vệ chung chat/advice/storyask và rate cho voice: danh tính backend, server guest cookie hash/TTL/CSRF, PostgreSQL UID/IP/day, quota8 chung và row lease/fencing cho cả member; claim giữ lịch sử. Giữ UI/survey/modes/catalog/story. Migration004 nguồn thêm guest sessions và charge_quota; **chỉ chạy PG local**, chưa remote. Không bỏ qua gate003 UUID/orphan.

197 PASS / 0 FAIL / 5 BLOCKED / 3 chưa kiểm chứng: 94 backend method có outcome cuối PASS (batch90/90 + security15/15, overlap11; không single batch94), browser93+8 PASS, hai boundary cũ401/graph0 PASS. Config/proxy retest2+1 nằm trong94, không cộng trùng. Firebase/DeepSeek thật vẫn BLOCKED; chuyên gia dữ liệu, thiết bị/Safari và Vercel runtime chưa kiểm chứng. **NOT READY FOR VERCEL PREVIEW** tới khi migration target được duyệt, proxy/origin và tích hợp live được xác minh.

Server8003 đã restart an toàn từ PID16280 sang PID16800 với database local mới có001/002/004, AI demo, dotenv tắt; không xóa dữ liệu cũ/không chạm8000/8002. Xem docs/shared-ai-protection.md, artifacts/super-board-report.md và JSON. Được phép commit cùng nhánh; không push/merge/deploy, không Nhiệm vụ3.
