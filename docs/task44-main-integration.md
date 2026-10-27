# Đồng bộ Task 4.4 vào main, không phát hành Production

## Phê duyệt và cổng triển khai

Chủ dự án đã cho phép cập nhật `TrooliGM/quocan4:main` và sau preflight đã phê duyệt rõ `git.deploymentEnabled.main=false` để chặn Gitauto-deploy riêngmain. Cờ này được đưa vào chính commit tích hợp trướcpush, vẫn giữ tới khi có quyết định thay đổi khác. Không thay ProductionBranch, projectintegration, domain, environment hoặc secrets; không dùngCLIdeployProduction.

ProjectVercelrootDirectory làrootrepo; cấu hìnhvercel.jsonởrootđượcgiữframeworkFastAPI. Không có wildcardtrue ghiđèrulemainfalse. Không có workflowGitHubActions trong hai câycode được tíchhợp. Mục tiêu là GitHub, không phải đưa code mới lênwebsite.

## Hai lịch sử được bảo toàn

- Main trướcđồngbộ: `346e9757dec7ebce43f74b815ccb138758cfa077`.
- NguồnTask44: `1cd665a64ac8ddcfb329c39355399f18866e940e` trênhotfix/task44-navigation-grounding; đây làe55c84f cộngbáocáopreflight, không đổiappcode.
- Đã xácminhcả `3f77005`, `f581e39`, `36a0490`, `e55c84f` đều nằm trong lịch sử nguồn. Nội dungbao gồm điều hướng đúng nghề, cùngtab/giữhội thoại, diagnostic/version/trace vàQA mới nhất.
- Hai nhánh khôngcóancestorchung. Tạo `integrate/task44-main-sync`/worktree `task44-main-sync` từoriginmain, không chỉnhcheckout chính hoặcnhánh đangdở.
- Đốichiếu:19filegiống,34fileđãcậpnhật, **khôngcófilechỉởmain**. Đã rà34đườngdẫncầnresolution;23blobcũ cótronglịchsửđúngpathcủanhánhnguồn, cácfilecấuhình/tàiliệu/auth/chat/testkhác đượcđốichiếudiff riêng.
- Mergehai-parent sửdụngunrelated-histories **saukiểmtra**, không dùngours/theirsstrategytoàncây hoặc épghiđèmain.34add/addconflictsđượcgiảiquyếttheoexplicitpathlistđãreview. Câyindexsauresolutiongiốnghệtsourcetrước khithêmguard/docs vàhaisửanhỏ dướiđây. Khôngcófilemain-onlybịxóa.
- Commitmerge cóparent1làmain346e975,parent2lànguồn1cd665a. Cậpnhậtmain bằngfast-forwardthường sẽgiữcảhai lịchsử; khôngforce/reset.

## Hai vấn đề phát hiện khi hồi quy bản tích hợp

1. `advisor/graph.py`: importNavigationMetadataErrornằm sauresponse.json/kiểmfinish_reason trongtry. NếuJSONhỏnghoặcbịcắtsớm, nhánhcatchthamchiếulocalchưađượcgán, gâyUnboundLocalError. Đưaclassimportlênmodule, giữ nguyênboundedretry/validation/errorHTTP. RegressioncũđãkiểmproviderJSONhỏng/cắtdở vàkhônglưulượthỏng; khôngthêmtestchỉsoimport.
2. `public/chat.html` làfallbackcòndùngcachekeycũ, khácrootchat.html. Đồngbộfallbacktừshellchính, khôngđổithiếtkế/logicchat. TestbundleVercel/khôngcópublicfolderđãPASSsaukhiđồngbộ.

Hai vấn đề này **không phải bằng chứng nguyên nhân HistoricalValidationError** trongphântíchkhảosát. Giữ kếtluận **Historical ValidationError – root cause undetermined**. Task4tổngthể vẫnchưahoànthành.

Ngoài guard, hai sửa trên vàtài liệu/README, backend/frontend được giữ từnguồnTask44 đãQA. Envexample và5filemigration hiệncó đượcđốichiếuGitblob/cleanfiltergiốnghệtnguồn; CRLFtrongworkingtreekhôngđượcnhầmthànhđổinộidung. Khôngđọchoặcsửa.env/secrets. KhôngthựcthimigrationtrênNeon.

## Kiểm thử và bảo mật

- Lầnđầuchạy115test có1FAILvà2ERRORởruntime (haisựviệctrên); khônggánlầnđóPASS.
- Sau sửa, chạylại51testthuộc4nhóm bịảnhhưởng:releaseRuntime/navigationGrounding/navigationActions/Task44profileJourney: **51PASS**.
-64testcòn lại đãPASS vàkhôngbịảnhhưởng, gồmphântích/schema/retryjobs,sharedprotection,Task42pipelinevàcareercontracts. Tổng **115testduynhất đượckiểmtheonhóm**, khôngphảituyênbốchạylại115bàimộtlầnsauchỉnh.
- Chrome localstatic: XSS/openredirect,same-tab,draft,0AIrequests,desktop/mobilePASS. ChromeFastAPI+PostgreSQLlocal: Chat→hồsơ→truyện/cảnh→Chat,3nghề,BackForward,giữID/survey/draft,tab1→1,khôngchat/create/analysisdođiềuhướngPASS. GoogleởfixturekhônglàpopupLIVE; kếtquảGoogleQAthậttrướcđóđượckếthừavìauthkhôngđổi.
- TấtcảDBfixturelàPostgreSQLlocalriêng; khôngnốighiNeon/Production. KhônggọiDeepSeekthật/tiêuquotaLIVEtrongđợtGitnày. GiữFirebase,Neon,Guest8câu,quyềnhồsơvàdữliệu.
- Quét220filetrackedvà748bloblịchsửmớiđượcđưavàomain: khôngpháthiệnkhóathật theo cácmẫuAPI/privatekey/JWT/GitHub/Google/databasecredential. Chỉ5URIgiảởtest_storage_release_config.pyđượcreviewlàplaceholder/test. Khôngcó.env,SQLite,artifacts,.vercel,serviceaccount/privatekeytrongcâycommit. Giátrịkhóakhôngđượcinra.
- Gitdiffcheck/stagedcheckPASS. Khôngđưaartifacts/bundle/credentials/screenshotsvàoGit.39testvalidationđãcókếtquảđượcgiữ,khôngnhậnmocklàLIVEhoặcsuyđãsửatriệtđểlỗilịch sử.

## Backup và các worktree đang dở

Localtag`backup/main-before-task44-20261027-346e975`vàbundleđầyđủlịchsửđãverifyPASSởworktreetask44-navigation-fix/artifacts. Khôngpushbackupbranch/taglàmphátsinhdeploykhác. Maincũcònnguyêntrongparent1củamerge.

17worktreebanđầuđãđượcrà;6worktreecòndirtyđượcgiữnguyên. Khônggomcodehome/story-shaređangdởhoặctàiliệuởworktreekhácvàobảnđãQA. Chỉtạothêmworktree18chointegration. Nhánhbackup-la-ban/fix-vercel/stagingvàdefaultbranchGitHubbackup-la-ban khôngđổi.

## Kiểm tra trước và sau push

Trướcpush: đốichiếuremote vẫn346e975, guardmainfalseởHEADđãcommit, mergeparents/ancestorđúng, worktreesạch, scansecretskhôngcófindingcầnreview. Khôngpushnhánhtíchhợphoặctag; chỉHEAD→refs/heads/main, khôngforce.

Checkpointnày **chưa ghi push làđãhoànthành**. BiênnhậnSHAGitHubvàProductiondeploymentđượcghi saukhipushthựctế. Productiontrướcpush:source`da6d14669a96e6a4c30b718d348ee3235a35f2cb`,deployment`dpl_9TdB69NsBqWmKssEUQbNhG92jsVS`,READY.

Rollbackmainnếucần: commitrevertbảotoànhistory,giữmainfalsetrongcấuhìnhrevert. Khôngreset/forcepush,khôngkhôiphụcschema/database/quota. Khôngtựbậtmainauto-deploykhihoàntáccode. Websitekhôngđượcđụngđếntừđợtđồngbộnày.

## Biên nhận push đã xác minh

Đãpushduynhất `HEAD:refs/heads/main`, fast-forwardthường, khôngforce, khôngpushnhánh/tagnào khác. MergecommittrênGitHub là **8c1d26c5497ba81268adcdc2e671e29d90978288**,parent1main346e975vàparent2source1cd665ađãđốichiếubằngGitHubAPI. ToànbộcáccheckpointTask44đều đượcgiữ tronglịchsửmain.

Đãđọclại `vercel.json` quaGitHubContentsAPI ởmain, xácnhậnrulemainfalse. GitHubmainSHAkhớpcommitvừapush;fetchoriginmainvàancestorcheckPASS. Khôngnhầmtrạngtháilocalvớiremote.

Hậu kiểm saupush: Productionaliasvẫndeployment **dpl_9TdB69NsBqWmKssEUQbNhG92jsVS**,source **da6d14669a96e6a4c30b718d348ee3235a35f2cb**,READY. QueryVercelkhôngcóProductiondeploymentmớitrongcửasổtừlúcpushđếnkiểmtra (khoảng75giâysaupush). KhôngdeployCLI,khôngpromote,khôngđổiDB/Firebase/secret/quota;mainGitđượcđồngbộnhưngwebsitedangchạykhôngđổi.

Scan cuối câycommit có221filetracked (thêm1báocáo),748blobnguồn; vẫnkhôngcófindingkhóathật. Cácbảnbáocáobổsungsaumergechỉđổitàiliệu,giữmainfalsevàkhôngcầnchạylạitestbackendđãPASS.

Commitbiênnhậnnàylàconsau của merge8c1d26c, khôngđổiappcode. SHAcuốicùngmainđượcđốichiếulạisaulầnpushbiênnhậnvàbáochongườidùng; khôngghiSHAowncommittrongchínhnộidungcommit.
