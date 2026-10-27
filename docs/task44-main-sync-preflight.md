# Đồng bộ Task 4.4 lên main — dừng tại cổng Vercel

Ngày kiểm tra:27/10/2026. Repository đúng `TrooliGM/quocan4`. Người dùng cho phép cập nhậtGitHubmain nhưng yêu cầu **dừng nếu pushmain có nguy cơ tự thay đổi Production**. Đây là lý do dừng, không phải một yêu cầu xác nhận suy ra từ skill.

## Kết luận

**BLOCKED trước tích hợp/push.** ProjectVercel `quocan4` đang nối GitHubTrooliGM/quocan4 và có:

- ProductionBranch:`main`.
- `gitProviderOptions.createDeployments="enabled"`.
- `autoAssignCustomDomains=true`.
- Không có ignored-build command được cấu hình.
- `vercel.json` của candidate không có rule chặnmain, nên main vẫn được bật theo mặc định.

Do đó pushmain có thể tự tạo Productiondeployment và tự gán domain, dù không dùngCLIdeploy. Không thử bằng cáchpush để xác minh. Không tự đổiVercel settings, ProductionBranch, domain hoặcvercel.json để vượt cổng này.

Nguồn chính thức: [Git production branch](https://vercel.com/docs/git#production-branch), [git.deploymentEnabled](https://vercel.com/docs/project-configuration/git-configuration#gitdeploymentenabled), [auto-promotion](https://vercel.com/docs/deployments/promoting-a-deployment).

## Phiên bản và lịch sử Git

- Candidate đã kiểm:`e55c84f771face442fc5d55ddcdd412887e93b6f`, nhánh `hotfix/task44-navigation-grounding`, worktreetask44-navigation-fix sạch tại lúc kiểm.
- Cả4mốc `3f77005`, `f581e39`, `36a0490`, `e55c84f` đều làancestor của candidate.
- Candidate chứa bản kiểm định nút đúng ngữ cảnh, same-tab/journey củaTask44, schema_version/trace và báo cáoQA mới nhất. SourcecodeđượcPreviewkiểm ở36a0490; e55c84f chỉ bổ sung báo cáo.
- `origin/main` đãfetch/đối chiếuGitHub:`346e9757dec7ebce43f74b815ccb138758cfa077`.
- `git merge-base origin/main e55c84f` trả không cóancestor chung. Không chạymergeunrelated, cherry-pick hàng loạt, reset hoặcforcepush; chưa tạo commit tích hợp.
- Không có localbranchmain đang được sửa. Không tự đụng `backup-la-ban`, `fix/vercel-ai-postgres` hoặcstaging.

## Sao lưu trước tích hợp

Đã tạo **local annotated tag** `backup/main-before-task44-20261027-346e975`, dereference đúngcommit346e975 ở trên. Không push tag.

Đã tạo và xác minh bundle đầy đủ lịch sử của tag:

`D:/khkt/.claude/worktrees/task44-navigation-fix/artifacts/main-before-task44-20261027-346e975.bundle`

`git bundle verify` PASS, bundle nằm trongartifacts bịignore, không upload/commit. Bản sao này bảo toàn lịch sửmain trước mọi tích hợp; GitHubmain vẫn nguyên trạng. Không backup/restore database vì nhiệm vụ này không đụng database.

## Kiểm tra17worktree

Có6worktree còn thay đổi từ trước, tất cả được giữ nguyên:

| Worktree | Thay đổi được phát hiện |
| --- | --- |
| CheckoutchínhD:/khkt |9filetrackedthay đổi,15mụcuntracked; không stage/ghiđè |
| ai-chat-21 |3filetài liệucheckpoint/memory/decisions |
| chat-perf |3filetài liệucheckpoint/memory/decisions |
| issue-1-build |4filetruyệnghềHTML/CSS/JS và1testuntracked |
| issue-6-homepage |2fileindex và2assetpremiumuntracked |
| release-task12 |3filetài liệureadiness/memory/decisions |

11worktree còn lại sạch, gồm ứngviênTask44. Không tự gom mã trangchủ/truyệnghề đangdở ởworktreecũ vào bảnTask44đãQA. Việc candidate sạch không có nghĩa các thay đổi cũ ngoài candidate đã được tích hợp; chúng được bảo toàn riêng.

## Kiểm thử và trạng thái website

- Không có code hoặc kết quảmerge mới trong lần này; **chưa chạy regression cho main đã tích hợp**, vì đã dừng trước bước đó.
- Kế thừa39testPythonPASS0SKIP và Preview36a0490kiểmcache/requestguard/privacyPASS từ đợt đã báo cáo; không giả vờ đó là kiểm thửmain mới.
- GooglepopupPASS theo người dùng, khôngkiểm lại. **Historical ValidationError – root cause undetermined** giữ nguyên; Task4tổngthể chưahoànthành.
- Productionvẫn source `da6d14669a96e6a4c30b718d348ee3235a35f2cb`, deployment `dpl_9TdB69NsBqWmKssEUQbNhG92jsVS`,READY; bản đang phục vụ được phát hànhCLI từfeat/task-4-4-continuous-journey, không phải originmain346e975. Điều đó không tắt auto-deploy của các pushmain tương lai.
- Khôngpush/merge/PR/deploy, khôngđổi environment/Firebase/Neon/schema/quota, không chạy migration.

## Phương án cần phê duyệt để tiếp tục

Đề xuất tối thiểu: chặnGitauto-deploy **riêngmain** bằng `git.deploymentEnabled.main=false` trong cấu hình của nhánh tích hợp trước bất kỳpushmain nào. Hiện **chưa áp dụng**. Đây là thay đổi chính sách phát hành cần người dùng duyệt; nó sẽ tiếp tục chặn các pushmain sau này cho đến khi được đổi lại. Không tự tắt/bật projectintegration hoặcchuyểnProductionBranch.

Sau khi được duyệt và xác minh cổng deploy đã an toàn:

1. Tạo worktree/nhánh tích hợp từoriginmain346e975, kiểm lại remote không trôi vàbackup còn đúng.
2. Đối chiếu câyfile hai phía, đặc biệtfilechỉcóởmain, cấu hìnhGitHub/Vercel và migrations. Giải quyết từngxungđột trước khi tạo mergehai-parent để bảo toàn cảhai lịch sử. Không ép ghiđèmain hoặc coi `--allow-unrelated-histories` là cách tự giải quyết xungđột.
3. Chạy regression liên quan trên **kết quả tích hợp thực tế**, scansecrets/filedữliệu vàreviewdiff. Giữ nguyênmigrationđãcó dưới dạngsource, khôngthực thi SQL.
4. Chỉcập nhậtmain bằngfast-forward/PRphùhợp với quyềnrepo, khôngforce; đốichiếuSHAGitHub và Productionalias saupush.

Hiện chưa có thay đổimain đểrollback. Nếu sau này cầnrevertbản tíchhợp thì dùngcommitrevert bảo toàn lịch sử và **giữ cơchế chặnauto-deploy** trongcommitrevert; không phục hồi nguyênvercel.jsoncũ làm vô tình bậtdeploy. Không tựrollbackwebsite/database trong nhiệm vụ chỉđồngbộGitHub.
