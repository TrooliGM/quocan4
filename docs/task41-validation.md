# Task 4.1 — nghiệm thu Preview, 25/10/2026

Kết luận: **READY FOR QA PREVIEW**, chưa đủ nghiệm thu Search/Google popup trên Preview để phát hành rộng. Không thay đổi kết luận43PASS/10BLOCKED của đợt Task4 cũ bằng số liệu Task4.1.

## Phạm vi và điểm khôi phục

- Nhánh: `feat/task-4-1-advisor-intelligence`, nền `dba80a6` (runtime Production `957ffde` cùng tài liệu hotfix). Checkpoint: `b8b4179` → `56678c9` → `377a3d7` → `e2fc257` → `2d0a2ea` → `a2a2f76`.
- Candidate cuối: `a2a2f76fe3f68814174ebbe444a10398942edf90`, deployment `dpl_GCno2S2r4NQqqqZswEJVU4jNZej3`, **READY, Preview**, [mở bản thử](https://quocan4-7x3jqli76-khkt3.vercel.app).
- Production được đối chiếu bằng Vercel API, vẫn `957ffde390f70acbcd63045bc21bf7f3459b5ca6` / `dpl_BwthFvvNpNDscwEuKPC744bVe38z`. Không promote, merge, deploy hoặc ghi dữ liệu thử vào Production.
- Neon Preview: nhánh schema-only `task41-preview-schema-20261025` / `br-morning-tooth-aznv081q`, role riêng `task41_preview_app`, database `neondb`. Ban đầu cả 8 bảng đều 0 dòng; không sao chép dữ liệu học sinh. Schema006 được thừa hưởng qua schema clone; không chạy lại migration006 trên Neon.
- Thử nghiệm chỉ dùng tài khoản QA/dữ liệu tổng hợp. Artifacts thô nằm ngoài Git, phản hồi/credentials QA được mã hóa DPAPI trên máy. Tài liệu không chứa UID/email/token/connection string.

Preview có Vercel Deployment Protection: cần tài khoản Vercel có quyền project để xem. Chỉ các UID QA đã xác minh được backend mở Task4.1; khách và tài khoản khác tiếp tục nhánh ổn định. Đây chưa phải phát hành đại trà. Có thể ngừng dùng Preview; rollback Production không cần thực hiện vì Production không đổi.

## Nguyên nhân và thay đổi

Mã cũ phân tích khảo sát trong luồng chat, kèm lời gọi nén bộ nhớ thường xuyên; mở hồ sơ phải gửi một prompt kỹ thuật, dễ phát sinh thêm lượt chat. Context chứa nhiều dữ liệu nghề/đề xuất lặp và có chỉ thị gợi ý ba nhóm nghề khi người dùng đang hỏi cụ thể. Bộ phân loại xưng hô trước đây chủ yếu nhận câu có dấu. Không có Brave key nên câu cần số liệu mới không thể có nguồn thật.

Đã bổ sung xử lý intent/detail không cần LLM router, lịch sử tối đa40 message/12.000 ký tự, giữ role và tên nghề gợi ý; chọn tối đa6 tham chiếu nghề. Ngữ cảnh khảo sát có question/answer, hồ sơ confirmed có block độc lập ngay trước câu hỏi mới. Chỉ attach bản phân tích đã có, không chèn cả danh sách proposal mỗi lượt. Nén bộ nhớ mỗi6turn hoặc lịch sử dài; câu ngắn không nén thêm. Bộ nén nhận thêm recent_turns córole, tối đa6000ký tự, để giữ các chia sẻ giữa hai lần nén, không chỉ lượt cuối. Quy tắc mới giữ chủ đề/career_id/mode, yêu cầu xưng hô mới nhất kể cả thiếu dấu và phân biệt yêu cầu được tư vấn với mong muốn rèn kỹ năng.

Giữ model `deepseek-flash` đã xác minh qua cấu hình/runtime thật, không thay bằng tên model chưa được cấp quyền, không tăng temperature. Budget đầu ra điều chỉnh theo intent (800–3500 token), analysis giữ3000. Cơ chế retry đầu ra hỏng và giới hạn9000 token đã có từ trước vẫn còn; không bảo đảm mỗi request chỉ một provider call khi xảy ra lỗi hoặc đến lượt nén. Thống kê LIVE bên dưới là các request không gặp retry.

## Khảo sát → bản đề xuất → xác nhận

Sau5câu, frontend tự POST tác vụ phân tích riêng; không gửi technicalprompt/main chat. PostgreSQL lưu pending/processing/completed/failed trong metadata messages hiện hữu. Hash câu trả lời, survey_id, attempt fencing và lease90s chống gọi trùng; completed dùng lại, failed chỉ retry rõ ràng. Khóa usage→session cùng thứ tự luồng quota/claim, không giữ transaction trong lúc chờ model. Kết quả và chat mới được merge dưới row lock; worker cũ không ghi đè kết quả mới.

Ngân sách riêng mặc định UID6attempt/ngày,2/phút, IP30/ngày, cấu hình qua `ANALYSIS_USER_PER_DAY`, `ANALYSIS_USER_PER_MINUTE`, `ANALYSIS_IP_PER_DAY`; timeout qua `ANALYSIS_TIMEOUT_SECONDS` mặc định25s. Đây là cửa sổ tính từ đầu lượt, không phải reset theo 0giờ. Retry có giữ lượt mới vẫn tính vào budget analysis; cache/invalid/concurrent cùngjob không tính thêm. **Analysis không trừ quota chat Guest8.** Không gọi provider khi thiếu key. Budget PostgreSQL dùng chung giữa instance; không tin XFF khi chưa cấu hình proxy tin cậy.

Survey answers, analysis draft/proposals và confirmed profile tách về mặt dữ liệu; chưa xác nhận không ghi profile_items. Accept/edit/reject từng mục, căn cứ nguyên văn theo câu, mức chắc chắn định tính, draft RAM theo owner/version; logout xóa draft. Chỉ confirmed profile opt-in được cá nhân hóa xuyên chat. UI không còn nút “phân tích qua AI Chat tính một lượt”; có tiến trình, retry lỗi và thông báo lưu thất bại giữ lựa chọn. Bubbles/rich text/Copy/header logo giữ nguyên; desktop/mobile không tràn.

## Kiểm thử đã chạy thực tế

| Nhóm | Kết quả và giới hạn |
|---|---|
| Python trọng tâm | **56 test unique PASS, 0 FAIL còn lại, 0 SKIP**: context8, Search5, jobs14, policy4, personalization8, validator4, runtime/provider13. Tổng hợp các lượt; chỉ chạy lại ca bị ảnh hưởng, không chạy full Super Board. |
| Browser local | **6 nhóm PASS**, PostgreSQL local/Firebase+LLM fixture: autoanalysis, consent/edit/reject/cache, lỗi lưu giữ draft, mobile/Copy/Guestquota, retry lỗi, Google fixture giữ exploration/career/step/draft. Không gọi fixture là Google LIVE. |
| UI thật trên Preview377a3d7 | Firebase SDK email/password thật + DeepSeek thật:5câu→1analysis/0chat;0confirmed trước click→1 sau accept; mở lại không gọi thêm model; desktop1440/mobile390 PASS. Code UI không thay sau checkpoint này nên kế thừa kết quả. |
| Nén bộ nhớ thật trên candidate cuối | Tiếp tục đúng phiên QA tổng hợp đã có2turn, gửi thêm4turn ngắn; lượt6 có2provider calls (main+nén), summary giữ thíchvẽ/biếtchútmáytính/chưabiếtlậptrình/chưachọnnghề/xưngtôibạn, câu trả lời không gán giỏi lập trình, không tự lưu confirmed profile: **PASS LIVE**. Đây là1mẫu kiểm ngữ cảnh dài, không bảo đảm mọi lịch sử dài đều nhớ đầy đủ. |
| Gates candidate cuối | Vercel READY/Preview, config live, đúng staging role/schema chỉ đọc, Firebase token thật, auth sai401, clientuid422, khác owner404 ở GET/analysis, cachedanalysis0provider, guest Secure/HttpOnly/SameSite strict/hostcookie và Origin403, guest mới còn8, legacy AI token sai401, private paths404 và assets không chứa secrets: **PASS LIVE**. |
| Bảo toàn phạm vi | 200nghề/12nhóm vẫn đúng API; không sửa data careers/Truyện nghề/stable graph/Firebase auth/Neon migration. Không chạy lại toàn bộ nội dung nghề hay8câu AI thật trên Preview; kế thừa kiểm thử stable trước đó và kiểm Guestquota ở local. |
| Build/JS/Git | Vercel build thật READY; `node --check`, `git diff --check`, manifest100file không env/artifacts/docs/tests/secrets PASS. Git auto-deploy tắt riêng nhánhTask4.1 để không sinh bản thử thiếu binding; không đổi Production Branch/routes/rewrites. |
| Google popup Preview | **BLOCKED**, chưa thao tác Google thật trên hostname cuối. Miền đã thêm bằng Firebase API, bảo toàn toàn bộ miền cũ; Firebase token thật/SDK password và Google fixture không thay thế phép thử popup. |
| Brave Search LIVE | **BLOCKED**, thiếu cấu hình/key được cấp phép. Adapter thật, timeout/cache/budget/SSRF/citation đã có và unit PASS; không gọi đó là nghiệm thu LIVE. |

Hai test runtime cũ ban đầu FAIL vì fixture giả định nén mọi lượt/không có messages; đã điều chỉnh fixture đúng lượt6, giữ phép kiểm provider nén lỗi vẫn không mất chat. Có một lỗi harness đường dẫn import và token QA hết hạn lúc chạy eval; đã sửa/refresh và chỉ chạy tiếp phần chưa thực thi, không tính là lỗi model hoặc PASS dịch vụ.

Driver periodicLIVE ban đầu dùng nhầm key response sessions thay vì items và giả định title bằng câu đầu; đã dừng trước AIcall, sửa cách xác minh phiên bằng đúng nội dung2tin QA, không chọn mò hoặc sửa phiên khác. Sau đó4turn thực thi thành công. Không giấu các lần harness chưa chạy được thành PASS sản phẩm.

## 16 tình huống DeepSeek thật và rubric

Fixture tại `tests/fixtures/task41-eval.json`, driver `scripts/evaluate_task41.py`. Rubric10mục: trọng tâm/tự nhiên/dễ hiểu/độ sâu/không bịa/căn cứ/hỏi đúng lúc/quyền quyết định/riêng tư/không gán nhãn. Không tự đánh giá bằng HTTP200. Có32phản hồi thực thi thành công cho16cặp; sau rà soát chỉ thử lại mẫu12, thêm mẫu17 thiếu dấu, rồi thử lại riêng mẫu9 do sửa đúng lỗi phát hiện. Không sử dụng dữ liệu học sinh.

Baseline runtime957ffde triển khai Preview riêng `dpl_A8p8YMWRh4qCKzTLfFhPnPhu5AfQ`, cùng schema-only staging/model/QA; candidate đầu377a3d7, thử lại12/17 trêne2fc257 và9 trên2d0a2ea. Phản hồi baseline nhiều mẫu đã đúng; không kết luận tất cả câu mới tốt hơn hoặc có năng lực tương đương ChatGPT.

| # | Tình huống | Đối chiếu nội dung trước/sau và kết quả |
|---|---|---|
|1|Thích Tin học, lo Toán|Không ép bỏ CNTT, phân biệt sở thích/kỹ năng rèn được, có trải nghiệm nhỏ; **PASS** mẫu sau.|
|2|Chưa rõ nghề|Gợi trải nghiệm và hỏi mục tiêu, không kết luận nghề phù hợp; **PASS**.|
|3|Bác sĩ/điều dưỡng|Hai bản đều phân biệt vai trò, bản sau tổ chức rõ khó khăn/cách thử; **PASS phạm vi tổng quan**, chưa kiểm chứng quy định hành nghề hiện hành bằng nguồn.|
|4|Một ngày Kiểm sát viên|Giữ nghề cụ thể, nghiên cứu chứng cứ/hồ sơ/công tố/kiểm sát tư pháp, không nhầm người quyết định hình phạt, ngày làm việc có biến thiên; **PASS tổng quan**, không chứng nhận tư vấn pháp luật.|
|5|Thủy lợi2020|Sau không bịa số liệu/URL, sources rỗng và unavailable; fallback trung thực PASS, **BLOCKED yêu cầu số liệu có nguồn thật**.|
|6|Tuyển sinh mới|Không suy thông tin hiện hành từ kiến thức nền, **BLOCKED nguồn mới**, báo thiếu nguồn đúng.|
|7|Đổi xưng hô|Hai bản đều theo lựa chọn mới; sau giữ lời giải ngắn không chào lại, **PASS**. Thử thêm17thiếu dấu/đổi giữa chat PASS trêne2fc257.|
|8|“Nghề đó” nối tiếp|Giữ lập trình trong exploration, trả thứ tự kỹ năng và bước thử, không hỏi lại tên nghề; **PASS**.|
|9|ProfileON|Đọc sở thích công nghệ đã xác nhận; bản377 có suy diễn yêu cầu “được giải thích” thành kỹ năng muốn rèn. Đã sửa quy tắc phân biệt, thử lại trên2d0a2ea dùng profile và bài tập dưới dạng gợi ý, không gán mong muốn rèn giải thích; **PASS sau sửa**.|
|10|ProfileOFF|Không query/load block profile riêng và không suy sở thích từ tài khoản; **PASS**, có Server-Timing và hồi quy2owner.|
|11|Khảo sát rõ|Tóm tắt tổng hợp, quote đúng5câu, selfreportedstrength và proposal tách biệt; **PASS** bản mới. Không cần chatprompt/tự lưu như luồng cũ.|
|12|Khảo sát mơ hồ|Bản377 summary thận trọng nhưng xếp thiếu tự tin vào strengths: **FAIL lúc đầu**. Validator chặn + prompt sửa; thử lạie2fc257 chỉ uncertainties/clarify, không gọi giao tiếp kém, tối đa3câu hỏi: **PASS sau sửa**.|
|13|Chỉ2câu|Hai bản đều đúng2câu về tester, không ép3nghề; **PASS**.|
|14|So sánh sâu|Sau có hoạt động, đánh đổi và6tuần thử đồ họa/UIUX; **PASS** yêu cầu tổ chức/độ sâu, chưa là tổng quan thị trường có nguồn.|
|15|Bầu trời xanh|Giải thích hiện tượng, không ép tư vấn nghề, **PASS**.|
|16|Search lỗi/thiếu|Không giả nguồn hoặc số liệu mới; **BLOCKED Search thật**, fallback trung thực PASS.|

Kết quả rubric: **13 PASS / 3 BLOCKED / 0 FAIL còn lại** sau hai bản sửa có kiểm thử lại đúng mẫu9/12. Ba ca cần nguồn trực tuyến thật vẫn BLOCKED; không coi fallback là đạt yêu cầu nguồn. Mẫu17 là bổ sung, không cộng trùng vào16ca chuẩn. Bộ mẫu này không chứng minh mọi phản hồi sẽ đúng hoặc chatbot tương đương ChatGPT.

## Hiệu năng và chi phí đo được

16request chat ở mỗi bản (loại hai luồng analysis11/12 để so sánh cùng loại request): trung vị nhận đủ response **9,17s→4,27s**, khoảng3,85–15,08s trước/1,56–13,31s sau. Mẫu13 hai câu7,43s→1,56s; mẫu14 sâu15,08s→13,31s. Đây là mẫu nhỏ, chạy tuần tự trước/sau và mạng có biến thiên; không phải benchmark ngẫu nhiên hay SLA.

16request sau có `llm_calls=1`/request, tổng input85.090/output8.494token do provider trả usage. Baseline chưa có bộ đếm usage này nên không có con số token/chi phí tiền trước tương ứng; không coi field thiếu là0calls. Chưa quy đổi thành chi phí vì không đối chiếu hóa đơn/đơn giá tài khoản. Luồng5câu UI thật chỉ1analysis call, mainchat0; nguồn cũ có các lời gọi phân tích+nén bên trong chat theo code. Retry và nén định kỳ vẫn có thể phát sinh thêm call đã giới hạn.

## Cấu hình và việc còn lại trước phát hành

- Preview dùng binding DeepSeek/Firebase đã được project cấp sẵn cho cảProduction+Preview; không sao chép/decrypt secret Production, nhưng **không phải hai tài khoản provider/Firebase project độc lập**. DATABASE_URL override chỉ staging mới; Search cố ý để thiếu cấu hình thật. Không ghi giá trị secret vào tài liệu/frontend/Git.
- Muốn nghiệm thu Search: cấu hình **Preview** `SEARCH_PROVIDER=brave`, `SEARCH_API_KEY` qua giao diện bảo mật Vercel, cấp key được phép; redeploy Preview rồi chỉ chạy lại5/6/16 và kiểm source/chi phí. Không gửi key qua chat.
- Cần người dùng thử popup Google trên hostname Preview cuối bằng tài khoản QA đã được allowlist, kiểm đúng mode/career/step/draft. Không mở canary cho học sinh trước khi nghiệm thu.
- Mọi phát hành Production cần người dùng duyệt Preview và phê duyệt riêng. Không migration mới; giữ gate và schema hiện hữu. Nếu sau này triển khai lỗi, rollback deployment ứng dụng về957ffde, không DROP/reset quota/restore đè database.

Chứng cứ trên máy: `artifacts/task41-browser.json`, `task41-live-browser.json`, `task41-final-gates.json`, `task41-firebase-domain-final.json`, `task41-preview-db.json`, ảnh `task41-live-profile-1440.png`/`390.png`; raw eval mã hóaDPAPI chỉ dùng QA. Các artifact này không commit.

## File và trạng thái Git

- Backend: `advisor/analysis_jobs.py`, `conversation_context.py`, `conversation_policy.py`, `graph.py`, `memory-prompt.txt`, `survey_analysis.py`, `confirmed_profile.py`, `routes.py`, `search_provider.py`, `performance.py`, `store.py`, cùng `deepseek_client.py`.
- Frontend: `chat.html`, `public/chat.html`, `public/assets/advisor-entry.js`, `chat.js`, `chat.css`, `profile-panel.js`. Không sửa thư viện/Truyện nghề.
- Kiểm thử/QA: `tests/test_task41_context.py`, `test_task41_analysis_jobs.py`, `test_advisor30_policy.py`, `test_task4_personalization.py`, `test_release_runtime.py`, `browser_task41.py`, `fixtures/task41-eval.json`, `scripts/evaluate_task41.py`.
- Cấu hình/tài liệu: `.env.example`, `vercel.json` (chỉ chặn auto-build nhánh QA), checkpoint/báo cáo/bộ nhớ/quyết định dự án. Không migration mới.
- Remote đã có377a3d7 từ checkpoint trước; các checkpoint cuối được commit local và deploy bằng CLI, **chưa push thêm**. Không coi quyền tạo Preview/commit là quyền merge hoặc phát hành Production. Worktree sẽ được kiểm sạch sau commit tài liệu cuối; root checkout và worktree khác được giữ nguyên.
