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

Rollback Preview: mở lại deployment Task4.1 `dpl_Gooca1fySbMiFkmzANji1bGY2w1x`, hoặc deploy source cũ với staging riêng. Không reset dữ liệu/quota. GET alias Production thực tế ngày25/10 cho thấy `dee7785` / `dpl_EhYXDvrYDNJznoBThVVHZ5Pu7ZDg`, khác checkpoint957ffde trong báo cáo cũ. Task4.2 chỉ đọc alias, không thực hiện thay đổi Production, không suy đoán người/thời điểm thay đổi từ checkpoint cũ. Khi phát hành phải xác minh lại checkpoint hiện hành và được phê duyệt riêng, build mới với envProduction, không promote deployment đang dùng database staging. DDGS scraping có thể bị chặn từ datacenter; nếu LIVE thất bại phải báo BLOCKED, không tuyên bố mọi ca Search hoàn tất hoặc dùng nguồn giả.

## Bàn giao Preview thực tế —25/10/2026

- Nhánh giữ nguyên `feat/task-4-1-advisor-intelligence`; baseline163e61c. Runtime cuối **4aae6f8ac618d5bdb2a6afeb90f98b584bf40122**. Không push GitHub; source local được Vercel CLI build trực tiếp. Commit tài liệu sau runtime không thay code đã deploy.
- URL: **https://quocan4-b4ajdo1cc-khkt3.vercel.app/ai-career-advisor**.
- Deployment: **dpl_AHoqbo8kkjoo7TifbprKxkd6xJ7o**, READY, target=null (Preview). DDGS9.16.1 + DeepSeek thật deepseek-flash, không demo. Build và runtime Linux thực sự gọi thư viện được, không chỉ cài/import local. Giữ Deployment Protection; nếu Vercel yêu cầu quyền thì đăng nhập tài khoản Vercel được cấp phép.
- Binding staging riêng như mô tả; không chạy006 hoặc migration khác, không sao chép secret/dữ liệu Production, không reset quota. Chỉ override SEARCH_PROVIDER=ddgs cho deployment; project env/.env không thay đổi. Hostname Preview được thêm vào Firebase authorized domains theo quyền đã có, giữ tất cả domain cũ. Google popup trên hostname cuối chưa kiểm; SDK email/password/ID token thật đã kiểm.

### Bằng chứng và kết quả

| Hạng mục | Kết quả thực tế |
| --- | --- |
| Unit/integration local | **51 method unique PASS**,0FAIL còn lại,0SKIP. 16 mới +35 hồi quy. PostgreSQL local thật, DDGS/DeepSeek mock; không gọi đây là LIVE. Sau thay đổi grounding/cache chạy lại đúng8method rồi2method bị ảnh hưởng, không cộng trùng. pip check PASS. |
| A — Công an2020 | Member vàQA có nguồn thật, phân biệt dự thảo với thông tin đã ban hành, không biến thành bảng điểm chuẩn hiện nay. Phạm vi tìm được chủ yếu tuyển sinh, không phải lịch sử đầy đủ ngành Công an. Đối chiếu thủ công bài Học viện trên domain bocongan.gov.vn: nội dung dự thảo/năm2020 khớp; không xem đây là kết luận quy định hiện hành. |
| B — CNTT2026 | Member/QA có nguồn FPT/whitepaper và nguồn khác; trả lời dựa snippet, không tuyên bố đọc toàn trang. Không đánh đồng dự báo toàn cầu với số liệu Việt Nam. |
| C — Tuyển sinh mới | Member có nguồn thật gồm cổng BộGDĐT và trường. Một lầnQA unavailable, ghi nhận thật, không xóa lần lỗi hoặc coiHTTP200 làSearchPASS. Lấy đượcHEAD không chứng minh tảiđượcfullGET; mở kiểm tra cổng Bộ bằng công cụweb gặp403. |
| D — Trò chuyện thường | Hai vai trò trả lời lập trình, status=not_needed,0nguồn; Search node~0,1ms, không gọi provider. |
| E — Lỗi/timeout | Unit blocked/timeout/empty PASS, local query lịch sử timeout7s. Vercel có3lượt unavailable qua các đợt; trả lời thông báo đúng thiếu nguồn, không bịa kết quả. |
| F — Các vai trò | Local PG/API test cảGuest/member/QA và3route dùng cùng Search, khôngQA-gated. LIVE member/QA PASS có nguồn. **Guest LIVE BLOCKED**: phiên QA Guest cũ đã dùng8/8; cấp phiên mới bị429, kiểm PGreadonly thấy budget cấp phiênIP/ngày10/10. Không reset, đổi header giả, sửa giới hạn hoặc tạo FirebaseAnonymous để lách. Config Guest trên runtime cuối vẫntask41/quota8, không quaylegacy. |
| G — Riêng tư | Provider spy local xác nhận không nhận survey/profile/định danh; LIVE query có thông tin giả nhậnprivacy_blocked/0nguồn, model cuối nói đúng backend không gửi truy vấn vì riêng tư. Không dùng dữ liệu học sinh thật. |
| H — Injection | Local kiểm snippet độc hại ở khối dữ liệu, systemguard và URLallowlist PASS; DOM nguồn dùng textContent/HTTPS. **Chưa có thử nghiệm trang độc hại với LLM LIVE**, không chứng nhận miễn nhiễm tuyệt đối. |
| Hai API compatibility | `/api/advice`, `/api/career-stories/{career_id}/ask` có lượtLIVE Search thành công trên29a7f8d,4nguồn mỗiroute, pipeline marker thật. Trước đó có unavailable và được giữ trong báo cáo. Retry trả đúngsources/search_status, khôngAI lại; kiểm local vàLIVE. Không thay code routing/quota ở4aae6f8. |
| Bảo mật runtime cuối | Invalidtoken401 cả3role; Guest/member đọc hội thoạiQA404; Origin khác403; privatepaths404; profile data chỉQA; quota Guest cũ vẫn8đãdùng/0còn, khôngreset. Giữ kiểm PG concurrency/proxy/rate đãPASS;429 cấp Guest quan sát thật. Chưa coi đây là audit mọi chuỗi proxy Production. |
| Giao diện | Chrome ẩn danh thật+FirebaseSDK, khôngnetwork/authmock: header mới/nguồnởcuốitin/HTTPS+noopener/thông báo snippet/khôngtràn ở1440 và390 PASS trên runtime cuối. Ảnh artifacts/task42-search-1440.png và task42-search-390.png. Không sửa UI hoặc dữ liệu nghề; API vẫn200nghề/12nhóm. |

Đã thực hiện **18yêu cầu trả lời DeepSeek thật** qua các deployment Preview, không cộng request retrycached. Trong14lượt cần tra cứu,11lượt có nguồn (có1lượt từ cache),3unavailable;2lượt thường khôngSearch và2lượt privacy_blocked. Đây là mẫu QA nhỏ, không phảiSLA hoặc tỉ lệ thành công dài hạn. Một số lượt có thêm nén ngữ cảnh theo logic cũ; số yêu cầu trả lời không đồng nghĩa tổng sốLLMcall.

LIVE đầu trên5b2ff83:3câu tra cứu mỗirole có5/6thànhcông,1unavailable. Thời gian request có nguồn5,15–7,35s; phần Search1,997–3,217s. Câu thường1,42–1,81s. Sau đó phát hiện một reply hỏi lặp dùng lại nhận định cũ không nằm trong snippet hiện tại: **đã sửa29a7f8d**, đặt ràng buộc nguồn sát câu hỏi, xem lịch sử chỉ là ngữ cảnh. Rerunfocused cho thấy AI rút lại các nhận định cũ không được snippet mới hỗ trợ. Một câuadvice còn tự diễn giải ngoặc về “tỷ lệ” trong snippet chưa nói rõ đối tượng: ghi **PARTIAL về độ chính xác diễn đạt**, cần rà chuyên môn/siết thêm nếu dùng tư vấn quy định, không che bằngstatusok.

4aae6f8 sửa cách diễn đạt khi cached=true, không tuyên bố vừa Search mới. **Hai lượt LIVE cuối có4nguồn mỗi lượt**: request5,86s/5,12s; Search1599,9ms→0,4ms; retrieved_at giữ nguyên và AI nói rõ lượt hai dùng bộ nhớ đệm. Đã đọc cả câu trả lời và snippet tương ứng, không chỉ kiểmHTTP200. Bản cuối kế thừa test51PASS và cácLIVEnêu rõsource ởtrên, không tuyên bố đã chạy lại toàn bộ ma trận trên4aae6f8.

Ví dụ câu trả lời thật của29a7f8d: “AI chuyển từ thử nghiệm sang vận hành quy mô lớn”, kèm https://fptcloud.com/white-paper/10-xu-huong-cong-nghe-tai-viet-nam-2026/. Có lưu câu trả lời đầy đủ và bộ nguồn mã hóa trong artifacts; không commit rawcredentials/UID. Upstream có thể thay snippet giữa các truy vấn; không xem retrieved_at là published_at, không tự dựng ngày xuất bản.

Artifact báo cáo: task42-live-summary.json, task42-manual-review.json, task42-final-runtime.json, task42-security-final.json, task42-browser.json, task42-production-observed.json. Raw syntheticQA và cookies/identities mã hóaDPAPI, khôngGit. Các kiểm thử phạm vi cũ chưa thay đổi (khảo sát tự động/consent/history/Guestquota concurrency) kế thừa checkpointTask4.1 và cáclocalregression đã nêu; không giả định đã nghiệm thu lại mọi luồngLIVE.

### Điều kiện trước Production

**Có Preview Search thật để xem; NOT READY FOR PRODUCTION / chưa hoàn tất nghiệm thu đầy đủ Task4.2.** Không đánh dấu GuestLIVE hayH adversarialLIVE làPASS. Cần dùng phiên Guest thử hợp lệ cònquota khi cửa sổ hạn mức cấp phiên cho phép, không láchgiới hạn; kiểm thêm độ bềnDDGS từdatacenter và diễn đạt khi snippetpháplý thiếuchi tiết, hoàn tấtGooglepopup hostname mới và đánhgiá adversarial phù hợp. Nếu cần nâng hạn mứcQA phải có phê duyệt cấu hình riêng, không tự sửa.

Không sử dụng rawPreview này làmProduction vì DATABASE_URL làstaging. Phải được người dùng duyệt riêng, kiểm lạiProdalias/env/schema readonly và chuẩn bịrollbackcheckpoint hiện hành. Không tựmerge/push/Production/migration.
