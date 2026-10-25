# Task 4.3 — Hành động trong hệ sinh thái La Bàn

Checkpoint nền b2d55e0 (Production runtime bd906df). Worktree riêng task-4-3 / feat/task-4-3-ecosystem-actions; không sửa checkout chính đang dirty hoặc Production.

## Thiết kế

Cùng completion DeepSeek hiện tại có thể trả lời Markdown như cũ hoặc gọi hàm kết thúc present_laban_actions với answer tự viết, ý định, trích lời học sinh làm căn cứ và tối đa4 đề xuất kind/career_id. Không thêm một lượt phân loại LLM, không thực thi công cụ tùy ý. Danh mục rút gọn ID/tên của đủ200 nghề (8.651 ký tự) và tham chiếu các nhóm nút trước được cung cấp để model hiểu ngữ nghĩa/viết tắt/thứ tự; không hardcode câu trả lời hoặc router hiểu ý chỉ dựa từ khóa. Nghề chưa rõ cần hỏi lại; không chuyển mọi lời nhắn thành hướng nghiệp.

Backend đối chiếu ID/name và truyện có thật, tự dựng nhãn và URL theo ba kind: career_profile, career_story (gồm một ngày làm việc), career_exploration. ID null chỉ được mở thư viện nghề/truyện. Không có trường URL trong proposal. Backend chặn key thừa, ID không tồn tại, URL giả, nhãn/đường dẫn không canonical và căn cứ chỉ có trong web/lời AI. Việc này không cấp quyền hồ sơ, không tự xác nhận nghề suy luận.

Metadata navigation_actions đi cùng câu trả lời trong JSON messages hiện có, bảo toàn qua save PostgreSQL atomic, chế độ tạm/lâu dài, nén ngữ cảnh và retry; tin nhắn cũ mặc định danh sách rỗng. Hai API tương thích cũng trả metadata khi lưu/retry. Không migration.

Frontend dùng DOM textContent và kiểm lại hình dạng URL theo kind/ID, nút xanh/kem nhỏ cùng hệ Premium, focus rõ và vùng nhấn tối thiểu46/48px. Nút là anchor mở tab mới noopener/noreferrer, lưu draft tại tab chat trước khi mở, không POST AI hoặc tự chuyển trang. Hội thoại và khảo sát trong tab cũ giữ nguyên. Helper login-return giữ thêm tham số career cho modal hồ sơ; vẫn loại URL ngoài/return_to tùy ý. Cache version HTML/chat.js/chat.css được đổi cho đúng bản mới.

## Kiểm thử đã chạy

- 15 test PASS: unit builder/metadata/security, PG local thật lưu/read/retry cho Guest/Member/QA, tạm/lâu dài, owner404, cùng completion một lần; cộng regression pipeline Task4.2.
- Local Chrome fixture PASS: XSS/open redirect, tab cũ và draft, target mới đúng route, không POST, helper auth-return và viewport1440/390. Fixture này không phải xác minh Google popup hoặc khả năng hiểu tiếng Việt của model LIVE. Lỗi mở tab đầu tiên do fixture không cấp userGesture đã sửa trong harness, không sửa sản phẩm.
- Đang chạy nhóm regression bảo vệ/quota/Search. Chưa có Preview hoặc LIVE Task4.3 tại checkpoint này; không đánh dấu đã hoàn tất.

## Phạm vi phát hành

Chỉ Preview dùng staging riêng và cấu hình Firebase/DeepSeek được cấp phép hiện có. Không dùng database Production để thử tính năng, không reset quota, không chạy migration, không push/deploy Production. Guest staging trước đó đã hết quota; chỉ thử LIVE nếu có hạn mức hợp lệ, không tạo/đổi định danh để lách. Google popup mới cần thao tác người dùng, báo BLOCKED nếu chưa xác minh. Chi tiết kết quả thực tế sẽ bổ sung sau Preview.

Bổ sung checkpoint: nhóm regression bảo vệ/Search 46/46 PASS, tổng61 phương thức Python PASS. Các log storage/timeout là tình huống mock dự kiến, không lỗi dịch vụ thật.

## Preview đầu và lỗi phát hiện qua LIVE

Preview b2a5adf / dpl_B3hGcrwKwyrukJFADRuNDTGLb9aB READY (staging riêng). 10 phản hồi model thật: mở thư viện viết tắt không dấu, hồ sơ Chuyên viên phân tích nghiệp vụ, truyện Kỹ sư hàng không, AI Nhân viên buồng phòng; tham chiếu Nhà sử học và nghề thứ hai đều đúng ID. Gợi ý từ vẽ mặt bằng/thiết kế nhà đưa Kiến trúc sư, Thiết kế nội thất và trải nghiệm an toàn, hỏi chọn nghề trước, không mặc định nút ở lượt đó. Toán ngoài chủ đề không có nút; metadata giữ qua GET lịch sử/retry.

Thêm3 ca LIVE: source OWASP thực chứa lệnh prompt injection được xử lý như dữ liệu, có nguồn và không có navigation_actions; chọn rõ Kiến trúc sư mở đúng truyện. Nhưng câu “nghề đó” sau hai lựa chọn còn ưu tiên Kiến trúc sư trước: FAIL yêu cầu làm rõ tham chiếu mơ hồ. Không đánh dấu toàn bộ LIVE là PASS.

Bản sửa: hàng rào tham chiếu hẹp dựa vào tên/ID thật vừa xuất hiện (không nghề hardcode), cung cấp reference.status=ambiguous cho model và bỏ hành động chọn nghề khi chưa rõ. Nếu model vẫn chọn, hỏi làm rõ bằng danh sách tên thật; không thêm lượt LLM. Ý định/nội dung hội thoại vẫn do DeepSeek xử lý, đây chỉ là kiểm tra tính nhất quán của tham chiếu. Unit mới với hai nghề ngẫu nhiên PASS; nhóm navigation11/11 PASS sau sửa, tổng62 phương thức đã kiểm. Cần kiểm lại đúng ca này trên Preview mới, không làm lại các ca đã PASS.

Guest staging được xác minh chỉ đọc:8/8, ngân sách cấp phiên/IP10/10 còn khoảng49.733 giây tại lần kiểm tra. Không dùng Guest Production hoặc tạo định danh/staging khác để lách. Guest LIVE Task4.3 vẫn BLOCKED; role Guest được kiểm trong PostgreSQL local có mock model. Người dùng trả lời chưa kiểm tra được Google popup, giữ BLOCKED mục này. Chrome Member đã mở đúng thư viện/hồ sơ thật, reload nút và draft, desktop/mobile PASS; QA đang kiểm tra trang đích và khảo sát đúng nghề.

## Hoàn thiện sau kiểm tra

Preview ceef90d / dpl_8CamYvNpyftiMbMLnKVrg3XuzTHt đã kiểm lại3 lượt DeepSeek LIVE: nêu2 nghề, “nghề đó” hỏi làm rõ/không phát nút chọn thay, rồi “nghề thứ hai” mở đúng truyện Kỹ sư điện tử. Guard đạt đúng ca đã FAIL trước. Các luồng cũ không làm lại toàn bộ.

Chrome thực trên Preview đầu đã mở đúng thư viện Truyện nghề, modal Chuyên viên phân tích nghiệp vụ, truyện Kỹ sư hàng không và AI Nhân viên buồng phòng. AI đích hiện khảo sát5 bước, đúng career_context và chỉ có lời chào, chưa gửi câu hỏi AI. Đổi trang/newtab giữ draft/tab cũ; metadata hiện sau reload, desktop/mobile PASS. Hai lỗi harness (selector dialog và so sánh URL trước khi ứng dụng đổi sang conversation) đã sửa trong script QA, không sửa sản phẩm để làm test PASS.

Rà soát liên kết Markdown: DOMPurify ngăn script, nhưng href tương đối/protocol-relative cũ có thể đi vòng lớp nút điều hướng. Bổ sung kiểm tra chỉ giữ citation URL trong sources đã kiểm, mọi link Markdown tự tạo khác thành văn bản; nút điều hướng nội bộ vẫn qua metadata riêng. Chrome fixture với //evil.test, /?career=unknown và một citation HTTPS được kiểm: chỉ citation thật còn là link, navigation/draft/newtab không đổi. Tăng version asset tránh cache. Cần build Preview cuối và kiểm giao diện/citation thực tế.

## Bàn giao cuối — 26/10/2026 (Asia/Bangkok)

- Nhánh feat/task-4-3-ecosystem-actions, worktree D:/khkt/.claude/worktrees/task-4-3. Runtime code cuối **04a67da7a8dc5c65d18a7b227f7eb8de491c7a68**. Preview **dpl_DahG7koM2gkszvbciy7C7XfkQqLc**, READY, target Preview: https://quocan4-dod5r4joj-khkt3.vercel.app/ai-career-advisor . Deployment Protection giữ nguyên, có thể yêu cầu đăng nhập Vercel.
- Dùng đúng staging br-morning-tooth-aznv081q đã có, không sao chép dữ liệu Production. DeepSeek deepseek-flash và DDGS thật, không demo. Hai nhóm Member/QA dùng cùng function/pipeline; dữ liệu hồ sơ nhạy cảm giữ QA-only như trước, không gắn quyền navigation vào allowlist đó.
- **62 phương thức Python local PASS**, 0 FAIL còn lại trong các nhóm đã chạy: navigation11, pipeline Task4.2 năm phương thức, shared protection15, score13, search-context18. Tình huống Firebase/provider trong unit là mock; PostgreSQL là cluster local thật. Không chạy Super Board toàn diện.
- **16 phản hồi chat DeepSeek LIVE** ở các candidate: 10 ca đầu +3 ca bổ sung +3 lượt kiểm lại guard. Bao gồm yêu cầu viết tắt/không dấu, mở hồ sơ/truyện/AI của các nghề lấy ngẫu nhiên (Chuyên viên phân tích nghiệp vụ, Kỹ sư hàng không, Nhân viên buồng phòng, Nhà sử học), tham chiếu/thứ tự, gợi ý từ vẽ và Toán, chuyển chủ đề; mẫu source OWASP thật có lệnh injection không sinh hành động trái ý. Có một lỗi chọn thay khi mơ hồ ở candidate đầu, đã sửa và nghiệm thu riêng trên ceef90d; không gọi đó là PASS trước khi sửa. Không tuyên bố chống mọi kiểu injection hoặc mọi cách diễn đạt.
- Gợi ý từ sở thích: model giải thích Kiến trúc sư/Thiết kế nội thất và hoạt động an toàn, hỏi học sinh muốn chọn nghề nào. Không ép mọi câu đó phải có nút. Khi chọn rõ, mở đúng truyện; với tham chiếu chưa rõ thì hỏi một câu, không tự lựa chọn.
- Lịch sử/retry metadata đã kiểm qua API staging; giữ đúng dữ liệu đã lưu, không gọi lại model khi replay. JSON messages dùng schema cũ, không thêm bảng/cột hoặc migration.
- **Chrome thật SDK email/password**: Member mở thư viện và modal nghề thật, QA mở truyện cụ thể và AI career_exploration đúng career_id. AI đích chỉ có greeting và khảo sát chưa hoàn tất (chưa gọi chat AI); tab cũ giữ draft. Nút còn sau reload. Viewport1440/390 PASS. Candidate cuối kiểm lại Member và citation OWASP qua DOM; các destination QA đã PASS được kế thừa vì frontend action schema/routes không đổi. Không dùng xác thực mock trong phép thử này. Ảnh local: artifacts/task43-member-1440.png, task43-member-390.png, task43-qa-1440.png, task43-qa-390.png (không commit).
- Local Chrome fixture: XSS từ label hiển thị dạng text, href không canonical/protocol-relative bị chặn; Markdown chỉ giữ citation đã có trong nguồn; login-return giữ career/mode/career_id/conversation nội bộ và bỏ return_to ngoài allowlist; click mở tab mới, không POST API trong fixture. Hành vi Google popup thật không được suy ra từ fixture.
- Bảo mật Preview cuối: token sai401; khác chủ session404; client tự gửi navigation_actions422; Origin khác403; Guest hết quota429; đường dẫn dotenv/backend/artifacts404. Thư viện200 nghề/12 nhóm, header/bubble và cả Search4.2 được bảo toàn. Không in/lưu secret trong tài liệu hoặc commit.
- Chỉ thêm hostname các Preview trong đợt vào Firebase authorized domains, giữ tất cả miền cũ, không đổi project/key hoặc logic đăng nhập.

### BLOCKED, chưa đủ nghiệm thu toàn bộ

1. **Guest navigation LIVE**: Guest staging QA cũ đã8/8, ngân sách cấp phiên/IP/ngày10/10. Không reset, đổi IP/định danh/DB, hoặc mang Guest Production sang staging để vượt giới hạn. Local PostgreSQL kiểm cả Guest/Member/QA PASS nhưng không gọi đó là Guest LIVE.
2. **Google popup mới**: người dùng trả lời chưa kiểm tra được. SDK password, draft/newtab và helper return-path PASS không thay thế bước popup Google thật. Cần thử trên Preview khi có thể: đăng nhập Google, mở hồ sơ nghề từ nút, quay lại chat và tải lại lịch sử; không gửi mật khẩu/token.

**Preview sẵn sàng để người dùng duyệt; chưa nghiệm thu LIVE toàn bộ và KHÔNG phát hành Production.** Production vẫn dpl_CoeNba7iFQNA7412ibdQbCUqqfwP / bd906df (Task4.2 cho mọi role), đã xác minh lại bằng GET control plane. Không merge, push nhánh Task4.3 hoặc deploy Production. Các thay đổi cũ ở D:/khkt và worktree Task4.2 được giữ nguyên.

### File thay đổi

- Backend: advisor/navigation.py (schema/registry/validation/context), advisor/graph.py (cùng completion + metadata), advisor/prompt.txt, advisor/postgres_store.py và advisor/legacy_ai.py (lưu/retry metadata).
- Frontend: public/assets/navigation-actions.js, public/assets/chat.js, public/assets/chat.css, public/assets/chat-journey.js; chat.html và public/assets/advisor-entry.js đổi version asset. Không sửa career_library.py, story_library.py hoặc dữ liệu200 nghề/Truyện nghề.
- Kiểm thử: tests/test_navigation_actions.py, tests/browser_navigation.py.
- Báo cáo/bộ nhớ: tài liệu này, docs/project-memory.md, docs/decisions.md.

Các checkpoint sau runtime nếu có chỉ cập nhật báo cáo, không đồng nghĩa Preview build lại code. Khi tiếp tục, kế thừa các PASS trên và chỉ chạy lại phần bị ảnh hưởng hoặc còn BLOCKED.
