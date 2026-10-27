# Task4.1 — cùng pipeline hội thoại cho mọi người

## Quyết định mới thay thế giới hạn trí tuệ QA

Người dùng yêu cầu Guest/member/QA cùng engine Task4.1, kể cả phiên đã có và cả hai mode. Giới hạn QA chỉ còn áp dụng tính năng dữ liệu chưa phát hành, không dùng để quay lại AI cũ. Chỉ Preview và chuẩn bị phát hành; không được tự deploy Production hoặc chạy migration/reset quota.

Đã xác minh worktree sạch ở `e624285`, nhánh `feat/task-4-1-advisor-intelligence`. Production trước thao tác là957ffde; điểm quay lại Preview trước sửa: `e933f98` / `dpl_GPWPYMsLL3F7MwYsDaFsYzmBihDZ`, URL `https://quocan4-bp6m6anvt-khkt3.vercel.app`. Chưa thay Production.

## Mã thực tế đã sửa

- `/api/ai/chat` gọi duy nhất graph Task4.1, bỏ chọn stable_graph theo allowlist. `task4_enabled=true`, `chat_pipeline=task41`, automatic analysis cho mọi phiên xác thực hợp lệ. Model/tham số/prompt không chia theo vai trò.
- `/api/advice` và `/api/career-stories/{career_id}/ask` dùng lại các node answer của Task4.1 (context, history, retrieval, analysis draft, generation, validation). Giữ wrapper xác thực/quota/idempotency/atomic save; tên module legacy_ai là compatibility protocol, không còn mô hình/prompt cũ. Giữ bối cảnh/safety cảnh truyện. Hai API này vẫn là hợp đồng hỏi đơn lẻ theo request_id, không tự ghép lịch sử từ các request khác của cùng người.
- Server-Timing `ai_pipeline=task41` được đặt tại node tạo câu trả lời thật, cùng số provider calls/token; response mới có pipeline. Retry đã lưu trả `saved_response`, không gọi lại AI hoặc gắn nhãn kết quả cũ như vừa tạo mới.
- Nén/hồ sơ hội thoại chỉ dữ liệu của phiên hiện tại. Confirmed profile context có cờ quyền server riêng và OFF mặc định; Guest không đọc profile bank dù metadata cũ đã opt-in. Member/QA có quyền dữ liệu mới đọc confirmed của chính mình; không tin UID/role client.
- Analysis draft owner-scoped mở cho cả3vai trò sau5câu, ngân sách PG riêng6/ngày2/phút/IP30/ngày, không trừ Guest8; chỉ cache cùng survey hash. Confirm/edit/delete private profile còn QA-only theo cờ dữ liệu hiện hành. UI hiển thị draft cho mọi người, khóa thao tác chưa có quyền và giải thích rõ, không biến thành AI legacy.
- UI mới không còn phụ thuộc QA trong candidate. Compatibility loader cho HTML cũ tải UI hiện hành, lỗi thì báo lỗi rõ, không import stable-chat.js. Cache version `task41-unified-1`. Production hiện hữu chưa thay đổi vì chưa triển khai candidate.
- Đổi chủ đề rõ ràng không kéo thêm survey/career refs không liên quan. Không hardcode câu trả lời; dùng chung DeepSeek/prompt/tool cho mọi vai trò. Brave chưa có key được phép, không giả nguồn.

## Kiểm thử trước Preview

Các test liên quan đã chạy bằng PostgreSQL local và provider/Firebase fixture; không dùng kết quả này thay LIVE. Đã kiểm chung engine của3vai trò/3endpoint, chat cũ/mới, cả2mode, temporary/durable, quota8/câu9, retry miễn phí, lỗi không fallback, owner isolation và analysis không tự confirm/không trừ chat. Hồi quy shared protection/token/IP/rate/lease, personalization ON/OFF và analysis jobs đã kiểm các phần bị ảnh hưởng.

Hai lỗi harness phát hiện và xử lý: test lease seed INSERT trùng rowusage0 nay do pendinganalysis tạo; sửa fixture local thành seed UPDATE có kiểm rowcount, không sửa dữ liệu thật. Header Server-Timing trước chỉ có ở /api/ai; bổ sung cho2API compatibility để nghiệm thu đường gọi thật. Những ca FAIL/ERROR đã chạy lại đạt. Không chạy toàn bộ Super Board.

Đang chờ build Preview và so sánh DeepSeek LIVE cùng6câu cho3vai trò, kiểm UI autoanalysis và kiểm quota/rate/phân quyền thật. Chưa kết luận PASS LIVE/READY trước khi có kết quả.

## Kết quả vòng LIVE đầu — f22a6c9

Preview f22a6c9 READY, không Production. Chrome thật3persona cùng hoàn thành5câu: mỗi người tự1analysis DeepSeek/0chat, xem được đề xuất có căn cứ; Guest/member không gọi profile bank và nút lưu private khóa, QA chỉ thêm1mục sauAccept. Dùng lại đúng Guest tổng hợp cũ còn7lượt, không reset/tạo lại để vượt quota.

Đã thực thi18turn LIVE, cùng6câu choGuest/member/QA: thíchvẽ→bítchútmáytính/viếttắt→đổixưnghô/nghềthứ2→nghềđó→đổichủđềbầutrờixanh→kếhoạch2tuần. Có Server-Timing tại node generate task41 cho cả3, không chỉ config/headerUI. Đã đọc mẫu: cả3nối sở thích, đọc đúng nghềthứ2, trả câu ngoài nghề và quaylại2tuần đúng. QA một lượt3còn tựxưng“mình” ở câu hỏi cuối sau yêu cầutôi–bạn; ghi nhận1PARTIAL vềxưnghô, bổ sungquytắc áp dụng toàncục, chờ thửlại riêngQA không chạy lại18turn.

Hậu kiểm LIVE: tiếp tục phiênGuest cũquaTask41, tổngGuestđủ8thìcâu9bịchặn429 ở cả2APIcompatibility; retrycũmiễnphí. Member gọi2APIcompatibility thật dùngengineTask41. OwnercrossGET/analysis404, tokenfake401, uidbody422,Origin403. Rateanalysis thật3request đồngthời(3survey khác) ra200/200/429 dùXFF/XRealIPkhác; budgetPGperUIDchung, khôngreset. CaseGraph/profile/unit đãđạt, tổnglocalđãchạy57methodunique kểcả4policytests, khôngfullSuperBoard.

## Candidate cuối và trạng thái thật

- Nhánh `feat/task-4-1-advisor-intelligence`, runtime **`dee7785e04607a92ace450225c63266b6d605159`**, đã push.
- Deployment **`dpl_Gooca1fySbMiFkmzANji1bGY2w1x`**, **READY / Preview**, [mở AI Chat thống nhất](https://quocan4-ju5z22f0t-khkt3.vercel.app/ai-career-advisor).
- Production kiểm lại qua Vercel API vẫn **957ffde / dpl_BwthFvvNpNDscwEuKPC744bVe38z**. Candidate là hậu duệ Production hiện hành; không merge main hay đổi Production Branch.
- Cùng Neon staging schema-only/role riêng như trước, chỉ kiểm schema/role và dữ liệu QA bằng kết nối readonly hoặc API ứng dụng. Vẫn8bảng; không migration, reset hoặc sửa dữ liệu Production.

| Kiểm tra | Kết quả thực tế |
|---|---|
| Pipeline chung Guest/member/QA | **PASS LIVE**:18turn cùng6câu, response `pipeline=task41` và dấu tại node generate; model cùng deepseek-flash. Không có nhánh lựa chọn AI legacy theo UID. |
| Chất lượng6câu | Đã đọc cả3nhóm: ngữ cảnh/viết tắt/nghềthứhai/chuyểnchủđề/kếhoạch đạt trong mẫu. Ban đầu17PASS/1PARTIAL về đại từ QA. Sửa quy tắc chung, thử riêngQA trên candidate cuối: trả họa sĩ minh họa, hỏi tiếp bằng “bạn”, không quay lại “mình/anh/chị/em”. **Focused retest PASS**; không tuyên bố đã chạy lại18turn ở commit cuối. |
| Cả2mode và lịch sử | Unit kiểm discovery/exploration, temporary/durable, lượt sau của phiên đã có PASS. LIVE Guest tiếp tục cuộc trò chuyện có trước deployment qua engine mới; LIVE member ngoàiQA hỏi Kiểm sát viên ở exploration giữ nguyên mode/career_id và trả đúng nghề, không gợi nghề khác. Không tuyên bố đã chạy LIVE mọi tổ hợp role×mode×storage. |
| 2API compatibility | Member gọi LIVE cả advice/story, cùng node/prompt/tool Task4.1, có pipeline marker. Unit9tổ hợp3role×3endpoint PASS. API hỏi đơn lẻ không tự ghép toàn bộ các request khác thành cuộc trò chuyện. |
| Autoanalysis3persona | **PASS Chrome LIVE**: mỗi nhóm5câu→1provider analysis/0mainchat; đề xuất cócăn cứ. QA không tăngprofile trướcAccept, tăngđúng1sauAccept. Guest/member códraft nhưng quyền đọc/lưu bankprivate vẫnkhóa. |
| Quota Guest | **PASS LIVE**: giữ nguyên Guest cũ đã dùng1, gửi7câu mới (6câu chung+1ởphiêncũ) đạt8tổng; câu9 ở cả2APIkhác bị429; duplicatekhôngtrừ. Candidatecuối vẫn0remaining, không reset. |
| Rate/concurrency/proxy headers | **PASS LIVE trong phạm vi test**:3analysis khác của cùng member đồngthời ra200/200/429, đổiXFF/XRealIPkhôngbỏquaUIDbudget. KiểmPGreadonly sau đó có0bucket theo6IPgiả đã gửi, tức các header đó không thành IPidentity ở Preview này. UnitPGkiểmquota/concurrency/lease/IPtrust/tokenshared. Không coi đó là loadtest sốlượnglớn hoặc chứng minh mọi chuỗi proxy Production đã được audit. |
| Token/owner/private data | **PASS LIVE**401invalidtoken,404crossowner vàprivatewrites chưađượcphép,422uidgiả,403Originkhác. Guest/memberkhôngtựsinhprofile_items: readonlystagingcount0. Confirmedcontext mặc địnhOFF vàchặnGuestdùsessionoptincũ. |
| Candidate cuối | Config/chat_pipeline/analysis cho cả3, cachedanalysis0providercho cả3, HTMLunified vàstagingrole/schemaPASS. ThửxưnghôQA+memberexplorationLIVEtrên đúngdee7785; phầnUI/corekhácgiữ nguyên f22a6c9 nênkếthừatestđãPASS. |
| Local regression | **57method unique PASS cuối,0FAIL cònlại,0SKIP** qua các lượt trọngtâm, khôngfullSuperBoard. GồmpublicUI5, profile2, protection15, unified6, analysisjobs14, personalization8, topicchange1, provider2, policy4. Không cộng lại những ca chạy lại. |
| Brave Search | **BLOCKED LIVE**:chưa cókeyđượcphép; coretool dùngchung mọirole, khôngQA-gate, không bịa nguồn. |
| Google popup trên hostname cuối | **Chưa kiểm lại**; domainđãthêmgiữmiềncũ, FirebaseSDKpassword/IDtoken thật3nhómđược kiểm. Auth/journey không viếtlại; không gắnPASS cho popup chưa thao tác. |

Fixture6câu/cáctiêuchí nằm ở `tests/fixtures/task41-unified-live.json`, khớp18record thật; không dùngHTTP200 thay chấm nội dung. Bộ mẫu nhỏ kiểm kỹ năng hội thoại, không chứng nhận mọi kiến thức khoa học/pháp luật của model đều đúng hoặc trí tuệ ngang ChatGPT. Câu trả lời có thể khác nhau tự nhiên giữa lượt gọi; cùng engine không có nghĩa giống từng chữ.

Ảnh UI/analysis cả3nhóm desktop1440/mobile390 đã chụp và xem trên f22a6c9, UI không đổi trong dee7785: `artifacts/task41-unified-{guest|member|qa}-{profile|chat}-{1440|390}.png`. Kết quả: `task41-unified-browser.json`, `task41-unified-live-gates.json`, `task41-unified-final.json`. Raw18turn/retest/exploration mã hóaDPAPI, không commit credentials/UID hoặc nội dung học sinh.

## Chuẩn bị Production, chưa cấp phép phát hành

Đủ bằng chứng để duyệt **Preview pipeline thống nhất**; chưa tự phát hành hoặc tuyên bố mọi kiểm tra Production đã hoàn tất.

1. Người dùng duyệt URL/runtime trên. Chỉ sau phê duyệt mới kiểm lại alias/commit Production, các binding Production và kết nối/schema readonly ngay trước release; không coi kết nối staging là kiểm DATABASE_URL Production.
2. **Build Production mới từ commit được duyệt với environment Production hiện hành**. Không promote nguyên deployment Preview vì nó được bind DATABASE_URL staging; không dùng helper Preview hoặc sao chép secrets để làm release.
3. Giữ Firebase/DeepSeek/DATABASE_URL Production, data canary `ADVISOR_CONTROLLED_ROLLOUT=true` và allowlist chỉ kiểm soát profile, không chọn chất lượng AI. Không chạy lại migration. Chưa cần đổi main/Production Branch để phát hành bằng quy trình đã được duyệt; nếu muốn tích hợp Git phải đối chiếu lịch sử riêng.
4. Khi được cấp Search key: cấu hình `SEARCH_PROVIDER=brave`, `SEARCH_API_KEY` ở môi trường phù hợp và bỏ override Search rỗng trong helper Preview, nghiệm thu link/citation/privacy/chi phí trước bật. Không yêu cầu gửi secret qua chat. Thiếu Search không chuyển model hoặc quay về legacy.
5. Kiểm lại Google popup/khảo sát-return, profile quyền hiện hành, Guestquota vàrate/proxy phù hợp môi trường Production. Không lấy lý dođổiAI để tắt bảo mật hoặc mởbankprivate choall.
6. Nếu phát hành được phê duyệt và gặp lỗi nghiêm trọng: rollback ứng dụng về **dpl_BwthFvvNpNDscwEuKPC744bVe38z** đã ghi nhận; không reverse schema/reset quota/restore đè dữ liệu. Đây là rollback phiên bản có công bố, không fallback legacy âm thầm trong runtime mới. Preview có thể quay lại URLcheckpoint e933f98 đã lưu, dữ liệu staging vẫn giữ nguyên.

Những thay đổi mới có quyền dữ liệu đã được nghiệm thu theo từng nhóm mới được mở dần; học sinh không bị ép dùng model/pipeline cũ vì chưa được cấp quyền profile. Chờ người dùng phê duyệt Production riêng.

Các file runtime thay đổi chính: `advisor/routes.py`, `graph.py`, `conversation_context.py`, `conversation_policy.py`, `profile_context.py`, `legacy_ai.py`, `performance.py`, `rollout.py`, `ai.py`, `story_ai.py`, `app.py`, hai bảnchatHTML và các modulechat/profile/entry. `.env.example` bỏ cờ UI phânvai trò cũ, mô tả lại canary chỉquyền dữ liệu. Không thay dữ liệu200nghề/Truyệnnghề, schema/migration, Firebase auth hoặc secret. Test/fixture/báo cáo được commit; artifacts và credentials mãhóa không commit.
