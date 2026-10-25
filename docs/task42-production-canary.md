# Task 4.2 — Production canary DDGS Search

Ngày nghiệm thu: 25/10/2026. Người dùng đã cho phép push feature branch và phát hành canary trên tên miền chính thức, chỉ cho tài khoản QA được phép.

**Deployment và bảo vệ canary đã kiểm tra thành công trên Production. Nghiệm thu chất lượng AI Search còn PARTIAL; không mở đại trà.**

## Phiên bản và khôi phục

- Website: https://labanhuongnghiep.vercel.app/ai-career-advisor.
- Project: quocan4 / prj_ZYNrx6mJp1SUWEX7vGO8c98G7489, team khkt3, repository TrooliGM/quocan4.
- Branch: feat/task-4-1-advisor-intelligence. Bắt đầu từ a40bde6, kế thừa runtime Task 4.2 4aae6f8.
- Source/runtime Production: **1b1b64080a00a389d8b93a0fb8f35d0e7bf91dd8**.
- Deployment: **dpl_EJvYVHp8yYb4Ync29JPu91WXWa6c**, target=production, READY; alias và SHA đã đối chiếu bằng Vercel API.
- Production Branch cấu hình vẫn là main. Phát hành bằng CLI từ feature branch; không merge, đổi Production Branch hoặc force push.
- Rollback: **dpl_EhYXDvrYDNJznoBThVVHZ5Pu7ZDg**, source dee7785e04607a92ace450225c63266b6d605159, URL quocan4-lld4cqszx-khkt3.vercel.app.
- Tag Git local: backup/task42-before-ddgs-canary-20261025, trỏ đúng dee7785. Không push tag hoặc nhánh khác.
- Checkpoint tài liệu sau source không thay đổi runtime, không cần redeploy chỉ vì cập nhật báo cáo.

## Cấu hình và cô lập

SEARCH_PROVIDER=ddgs; SEARCH_QA_ONLY=true; SEARCH_TEST_UIDS chứa hai UID đã xác minh: tài khoản Google của chủ dự án và tài khoản QA tự động. Không ghi UID/email/credential vào Git. Đối chứng thành viên không nằm trong allowlist Search.

Cờ Search độc lập quyền Hồ sơ. Nếu SEARCH_TEST_UIDS không khai báo, code có thể dùng ADVISOR_TEST_UIDS; khai báo rỗng thì không cấp quyền. Production mặc định đóng cho non-QA, kể cả khi ADVISOR_CONTROLLED_ROLLOUT=false. Anonymous/custom provider không được hưởng quyền chỉ vì có UID giống QA. Role, UID và cờ do client gửi không được tin tưởng.

Dependency backend xác minh Firebase rồi đặt cờ server vào state của cả ba API: /api/ai/chat, /api/advice và /api/career-stories/{career_id}/ask. Gate chạy trước query expansion, cache và provider. Guest/member vẫn dùng cùng pipeline Task 4.1 và DeepSeek thật, không chuyển về legacy. Tin nhắn cũ có nguồn vẫn giữ nguyên; hiển thị nguồn cũ không chứng minh vừa gọi Search mới.

Chỉ ba biến Search được override cho deployment này. Không đổi secret hoặc binding DATABASE_URL, DeepSeek, Firebase, model, demo, proxy, rate limit, quota hay quyền Hồ sơ. Profile_enabled vẫn false cho QA/member như trước. Không sửa Firebase authorized domains. Không sửa HTML/CSS/JS, thư viện 200 nghề hoặc Truyện nghề.

Build bằng deploy --prod --skip-domain, kế thừa environment Production. Không promote Preview Task 4.2 dpl_AHoqbo8kkjoo7TifbprKxkd6xJ7o vì Preview đó dùng staging. Chỉ sau các gate và kiểm thử thật trên candidate mới promote deployment Production mới vào domain.

Fresh build tương lai phải kiểm tra và cấp đúng ba biến Search. Không tự đưa chúng vào project env cho mọi phiên bản vì source cũ có thể chưa có gate. Với source hiện tại, thiếu UID/flag sẽ fail closed. Metadata env của deployment không liệt kê đầy đủ override CLI; hành vi runtime đã được kiểm thay vì suy đoán từ danh sách tên biến.

## Kiểm tra trước phát hành

- Git sạch tại a40bde6, ancestry từ đúng source Production dee7785 được xác minh. Push đúng feature branch, kiểm lại bằng ls-remote; không main/merge/force push.
- 54 method local PASS, 0 FAIL, 0 SKIP. Có kiểm tra default closed, tách quyền Search/profile, thiếu quyền không chạm provider/cache, ba role × ba API, header giả không cấp quyền và body flag giả trả 422. PostgreSQL local thật, Firebase/DDGS/DeepSeek mock; không gọi các bài này là LIVE. Chỉ chạy lại các bài bị ảnh hưởng sau thay đổi nhỏ.
- ddgs==9.16.1 trong hai manifest, pip check PASS. Manifest deploy 100 file, không dotenv/artifacts/credentials/database local.
- Neon production/neondb được xác minh qua kết nối startup read-only. Schema check ready=true, không thiếu bảng/cột hoặc sai kiểu; bảng profile hiện hữu. Không chạy migration 001–006 hoặc SQL thay đổi schema.
- API candidate đọc được phiên QA có sẵn trong chính Neon Production: bằng chứng binding runtime thực, không lấy kết quả staging thay cho Production.
- Candidate giữ config model/live/profile/analysis và Firebase Web config như domain chính. QA /advice lấy nguồn Internet thật; member vẫn trả lời Task 4.1 nhưng không Search. Guest thật có Search=false, quota=8.
- Bổ sung policy không đoán đối tượng của “tỷ lệ này” khi snippet thiếu văn cảnh. Chỉ đánh giá sửa lỗi bằng câu trả lời thật, không coi prompt là bảo đảm tuyệt đối.

## Năm câu trên domain chính thức

| Câu hỏi | Bằng chứng | Kết luận |
| --- | --- | --- |
| Tìm thông tin ngành Công an Việt Nam năm 2020 | Search mới, 4 nguồn, request 9,34s; Search 3958ms. Có nguồn Công an Hải Phòng, học viện Bộ Công an và VietnamNet. | PASS trong phạm vi snippet: phân biệt kỳ thống kê/dự thảo; không đoán tỷ lệ không rõ đối tượng, không bịa con số bị cắt. |
| Xu hướng ngành AI Việt Nam năm 2026 | Lần đầu unavailable/0 nguồn, 6,18s. QA gọi API Truyện nghề cùng query sau đó lấy 4 nguồn thật. Một lần retry chat dùng bộ nguồn cache này, Search 0,1ms, request 7,43s. | Có nguồn thật sau retry, nhưng retry là CACHE, không phải lần gọi Internet mới. Giữ nguyên bằng chứng lỗi ban đầu. Phân biệt nguồn doanh nghiệp với nguồn nhà nước. |
| Tra cứu thông tin tuyển sinh đại học mới nhất | Lần đầu unavailable, 6,38s. Đúng một retry Search mới có 4 nguồn, request 7,65s; Search 3576,6ms. Có cổng Bộ GDĐT và trang tổng hợp. | Nguồn PASS; chưa xác minh lịch/chỉ tiêu cụ thể. PARTIAL: model nói dùng cache dù timing/timestamp chứng minh Search mới. Không dùng lời model làm bằng chứng cache. |
| Tìm nguồn chính thức về ngành công nghệ thông tin | 4 nguồn, request 4,68s; cache 0,1ms từ pretest trên candidate. Có URL Chính phủ/luật CNTT, Wikipedia được phân biệt là bách khoa mở. | Nguồn PASS, diễn đạt PARTIAL: còn kéo ngữ cảnh tuyển sinh từ câu trước vào câu chỉ hỏi nguồn CNTT. |
| Giải thích lập trình là gì, chỉ hai câu | not_needed, 0 nguồn, 1,62s. | PASS: trả lời hai câu, không gọi Search. |

Không xóa hai lần unavailable khỏi báo cáo, không retry vô hạn hoặc sửa giới hạn để làm test xanh. Đã đọc câu trả lời và đối chiếu snippet/title/URL/retrieved_at. Không coi HTTP 200 là bằng chứng Search hoặc xem retrieved_at là ngày xuất bản. Chỉ xác minh snippet và link, không giả nhận đã đọc toàn trang hoặc chứng nhận mọi nội dung chuyên môn.

## Kiểm tra bảo toàn và phần chưa xác minh

- Hội thoại QA lưu/đọc lại được; gửi lại cùng request_id giữ nguồn và không gọi AI lại. Cross-owner 404, invalid token 401 dù có Guest cookie, Origin khác 403. Header X-Role/X-User-Id giả không cấp Search cho Guest/member.
- Hai API compatibility hoạt động với Task 4.1: QA Truyện nghề có 4 nguồn thật trên domain chính; Guest/member advice không Search. Retry giữ sources/search_status.
- Guest Production thử đúng một câu: used_questions=1, limit=8, remaining=7; retry không tính thêm. Không reset quota hoặc xóa dữ liệu. Đây là Guest CHAT Task 4.1 LIVE, không phải Guest SEARCH LIVE.
- Firebase ID token và Chrome SDK email/password thật PASS. Chrome desktop 1440/mobile 390 trên main thấy header mới, footer nguồn HTTPS/noopener và lời giải thích snippet, không tràn ngang. Ảnh: artifacts/task42-production-search-1440.png và task42-production-search-390.png.
- API vẫn có 200 nghề/12 nhóm. Diff HTML/CSS/JS/data so với Production cũ bằng không.
- Google popup đang chờ chủ dự án xác nhận theo câu hỏi đã gửi. Không dùng password SDK thay bằng chứng Google popup. Guest Search chưa mở; injection LIVE chưa kiểm. Không tự đánh dấu các mục này PASS.
- DDGS có lúc unavailable. Còn lỗi diễn đạt về cache và ngữ cảnh ở bảng trên; không mở Search đại trà trước khi xử lý/nghiệm thu thêm. Mẫu QA nhỏ không phải SLA hoặc kiểm thử mọi tổ hợp role/mode/lịch sử.

## Rollback

Không phát hiện lỗi bảo mật, mất dữ liệu hoặc hỏng toàn ứng dụng cần rollback ngay; vấn đề Search đang được giới hạn cho QA. Nếu phát hiện lỗi nghiêm trọng, chạy:

```sh
vercel rollback dpl_EhYXDvrYDNJznoBThVVHZ5Pu7ZDg --scope khkt3 --yes
```

Sau đó kiểm alias, source, health và chat trên domain chính. Không restore đè, reset quota hoặc reverse migration. Bản rollback đã có schema tương thích các tin nhắn/nguồn hiện tại.

Artifact báo cáo: task42-production-preflight.json, task42-prod-readonly-schema.json, task42-candidate-gates.json, task42-production-promote.json, task42-production-live-summary.json, task42-production-browser.json, task42-production-final-audit.json. Raw QA/cookie/credential mã hóa DPAPI trong artifacts, không commit.
