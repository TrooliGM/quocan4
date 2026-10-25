# Task4.2 — Production canary cho chủ dự án

Người dùng đã cho phép push featurebranch và phát hành Production canary, không mở Search đại trà. Baselinea40bde6/runtime4aae6f8 có DDGS và Previewđãkiểm; không dùng mã cũ thayTask4.2.

## Checkpoint trước phát hành

- Worktree `.claude/worktrees/task-4-1`, nhánh `feat/task-4-1-advisor-intelligence`, lúc bắt đầu sạch tại a40bde6.
- Repository `TrooliGM/quocan4`; projectVercel `quocan4` / prj_ZYNrx6mJp1SUWEX7vGO8c98G7489, teamkhkt3. ProductionBranch cấu hình main nhưng domain đang phục vụ deployCLI từfeaturebranch, source dee7785e04607a92ace450225c63266b6d605159.
- Rollback: **dpl_EhYXDvrYDNJznoBThVVHZ5Pu7ZDg**, URL quocan4-lld4cqszx-khkt3.vercel.app, READY. Candidate có ancestry từ đúng sourceProduction. Không merge, đổiProductionBranch hoặcforcepush.
- PreviewTask4.2 **dpl_AHoqbo8kkjoo7TifbprKxkd6xJ7o**, READY,4aae6f8; không promote nó vì DATABASE_URLstaging.
- NeonProduction được xác minh bằngconnection startupreadonly, đúngbranchproduction/neondb; schema_check.ready=true, haiIDTEXT/cột004 và bảngprofile006hiệnhữu. KhôngSQLghi/migration. Schema không cần thay để thêmSearch.
- MetadataProduction có bindingDATABASE_URL/DeepSeek/Firebase/model/demo hiện hành. Profilefeature hiệnfalse cho tài khoảnQA và thường. Không thay secret hoặc quyền profile để mởSearch.

## Cô lập tính năng

`SEARCH_QA_ONLY=true`; serverxác minh Firebase rồi so UID với `SEARCH_TEST_UIDS` riêng. Nếu biến riêng không khai báo có thể dùng allowlistADVISOR_TEST_UIDS; khai báo rỗng/UIDthiếu/provideranonymous/custom đều failclosed. Production mặc định restricted ngay cả khi quên biến. `ADVISOR_CONTROLLED_ROLLOUT=false` không thể tự mởSearch. Cờ riêng tránh mở quyềnprofileđangfalse trênProduction.

Quyền được đặt bởi dependencyserver cho cảchat/advice/story, không lấyrole/UID/flagtừclient; LangGraph khai báo kênhflag và wrappercompatibility đặt đè từidentity. Gate trướcqueryexpansion/cache/provider; nonQA vẫnTask4.1/DeepSeek thật, khônglegacy, khôngmởSearch. Việc hiển thịnguồn đãlưuởtin cũ không có nghĩa mới thực hiệnSearch.

Chỉ override ba biến cho **deployment mới**: SEARCH_PROVIDER=ddgs,SEARCH_QA_ONLY=true,SEARCH_TEST_UIDS (cácUIDQAđãxácminh, khôngghiGit). Không bind DBstaging, khôngđổiFirebase/DeepSeek/DATABASE_URL/role/rate/quota, không sửa authorizeddomains. Profilecanary vàsurvey/consent giữ cấu hình hiệnhành.

BuildProduction bằng `deploy --prod --skip-domain`, kế thừa envProduction hiện có. Chỉsau kiểmcandidate/canary mới promote deploymentProduction mới này vào domain; khôngpromotePreview. Trước thao tác phảikiểm alias vẫncheckpointđãghi, projectIDđúng, sourceđúng vàworktreeclean. Nếu alias thay đổi ngoài phiên, dừng để ràsoát.

## Kiểm thử trước phát hành

54method local PASS/0FAIL/0SKIP, có3casecanarymới: defaultclosed, khôngđọcprovider/cache khi thiếuquyền, 3role×3API cùngTask4.1 nhưng chỉQA cóSearch; headergiảkhôngcấpphép, bodyflaggiả422, controlledfalsekhôngmởSearch. Provider/identitymock, PostgreSQLlocal thật; khôngđánhdấuLIVEtừtestlocal. Sau tách allowlist riêng,2case bịảnhhưởng retestPASS. Dependencyddgs9.16.1 và pipcheckPASS.

Đã bổ sung ràngbuộc không đoán đối tượng/loại tỷ lệ từsnippetbịcắt vìQA trước cómộtparentheticalthiếucăncứ; cầnđọc câu trảlời thật sau phát hành, không coi policy làbằngchứng mọi suy diễn đãhết. DDGSđãcóLIVEPreview nhưngkhông bảo đảm luônkhảdụng.

## Nghiệm thu và rollback

Kiểm trực tiếp trênlabanhuongnghiep.vercel.app bằng FirebaseQA đượcphép và dữliệuthử riêng:5câu người dùng yêu cầu, URL/snippet/latency/providerstatus/cache, đồngthờikiểm membervàGuestkhôngSearch/khônglegacy, token/owner/Origin/quota và2compatAPI. Googlepopup, GuestSearchLIVE vàinjectionLIVEcònthiếu ởPreview khôngtựđổi thànhPASS; canary choowner khônglàpháthànhđạitrà.

Nếu lỗi nghiêmtrọng, chạy CLI `vercel rollback dpl_EhYXDvrYDNJznoBThVVHZ5Pu7ZDg --scope khkt3 --yes` rồi xácminhlạidomain/runtime. Khôngrollback/resetdatabase/quota, không xóađữliệuthử hoặcngười dùng. Trướcpháthànhgiữđượccảdeploymentnguồn vàtagGitlocal; kếtquảthựctế sẽbổsungsaukiểm, hiệnchưa báo ProductionPASS.
