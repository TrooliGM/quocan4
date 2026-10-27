# Task 4.4 — điều tra ValidationError và theo dõi tái phát

**Historical ValidationError – root cause undetermined**

Không có đủ output/stack trace của lần lỗi lịch sử để xác định trường hoặc dữ liệu gây lỗi. Các ca tái hiện tổng hợp dưới đây kiểm chứng hành vi hiện tại, không chứng minh nguyên nhân của lần lỗi cũ. Không tuyên bố đã sửa lỗi lịch sử. Task 4 tổng thể chưa hoàn thành; không push, merge, migration hoặc deploy Production.

## Trạng thái kế thừa

Worktree `task44-navigation-fix`, nhánh `hotfix/task44-navigation-grounding`, nền `d6a95a1`/code `3df3897`. Giữ nguyên ba thay đổi tài liệu chưa commit từ lần xác nhận Google. Google popup thật đã PASS theo người dùng; không kiểm lại vì không thay code đăng nhập, frontend hay hành trình.

Đã rà luồng `analysis_jobs.execute` → `survey_analysis.generate_analysis` → đọc JSON → `Analysis.model_validate` → kiểm tra căn cứ → `finish`. Bản cũ đã có bounded repair, lease PostgreSQL và request_id ổn định. Không nới schema/validator. Một lần retry trước đây ghiValueError khác loại với ValidationError lịch sử; không gộp hai lỗi.

## Bổ sung trong đợt này

- Phiên bản schema `Analysis/v1` và trace ID UUIDv4 ngẫu nhiên do server tạo cho mỗi attempt thực sự. Hai provider call trong cùng bounded repair dùng một trace; retry chủ động của cùng request_id có trace mới. Cache không tạo trace hay attempt mới. Tác vụ lịch sử không có trace được giữ `trace_id=null`, không tự tạo bằng chứng hồi tố.
- ContextVar truyền trace qua async và được reset trong finally, không dùng UID, session_id, request_id, token hay hash nội dung làm trace. Client không được tự truyền trace vào API.
- Log validation chứa mã lỗi, loại lỗi, schema/version, vị trí trường, kiểu/độ dài dữ liệu và frame mã nguồn giới hạn. Key lạ bị thay bằng `<extra>`. Không có input/context/locals/exception message tùy ý hoặc giá trị thực tế, kể cả giá trị enum. Không ghi khảo sát, prompt, raw output, thông tin học sinh hay credentials.
- Các ValueError kiểm tra căn cứ cũng có vị trí trường cụ thể. Điều kiện từ chối không đổi. Trace và frame chỉ phục vụ log server; không đưa chúng vào prompt sửa output gửi provider.
- Lỗi trả response an toàn kèm trace/schema version; khảo sát và request_id được giữ. Kết quả không hợp lệ không được lưu thành đề xuất chính thức. Không thêm endpoint tìm người dùng hoặc đọc dữ liệu bằng trace.
- Không đổi UI, catalog, Google/Firebase, database/schema, quyền hồ sơ, giới hạn Guest hoặc ngân sách analysis.

## Kiểm thử thực chạy ở local

**39 test Python PASS, 0 SKIP**, PostgreSQL local riêng, model/Firebase fixture; không phải DeepSeek LIVE. Gồm11method ma trận mới,7testvalidation,17testjobs và4testanalysis hiện có.

| Nhóm dữ liệu | Kết quả hiện tại |
| --- | --- |
| Khảo sát đủ5câu và output có căn cứ | PASS, đọc/kiểm đúng schema và ID |
| Câu ngắn, chưa rõ/thiếu thông tin | PASS với đề xuất rỗng/làm rõ; không bắt tạo hồ sơ giả |
| Thông tin mâu thuẫn | PASS với kết quả chưa kết luận/làm rõ có kiểm soát |
| Thiếu câu khảo sát hoặc câu rỗng | API422, không thay khảo sát đang lưu |
| AI thiếu trường gốc hoặc thiếu evidence | Từ chối, mãmissing và vị trí trường an toàn |
| Sai kiểu summary/items/question_id | Từ chối string_type/list_type/int_type |
| JSONrootnull/list/string, enumlạ, keythừa | Từ chối model_type/literal_error/extra_forbidden |
| JSONhỏng, codefence hoặc văn bản ngoàiJSON | Từ chối analysis_json, tối đa2attemptprovider |
| Excerptgiả hoặc khác định dạng | Không tự chấp nhận; kiểm nguyên văn giữ nguyên |
| Retry/cache/concurrency | Giữ survey/request_id, không trùng kết quả; mộtlease; cache không gọi lạiAI |
| Lỗi trênGuest | Không tạo phiên, không tự ghi hồ sơ, không giảm8lượt chat |
| Trace và riêng tư | Mộttrace/hai call, trace khác giữa tác vụ/retry; không tràncontext; log không chứa marker riêng tư |
| Client giả trace/sai request_id | 422/409 trước provider; không tự cấp quyền hoặc tiêu ngân sách |

Đối chiếu JSON SchemaAnalysis với source3df3897: **giống hệt**, SHA256 `d2387c076478f234c4c8f43a0e3cbcf87fdff4e99047d86287d411823d7d08de`. Việc thêm monitoring không thay trường, Literal, giới hạn độ dài, extra=forbid hay quy tắc căn cứ.

Testschema có thể tạo PydanticValidationError thật từ dữ liệu giả như categorysai hoặc thiếu trường. Chỉ xác nhận chúng được phát hiện và xử lý an toàn, không gán cho dữ liệu lịch sử.

## Preview và hạn mức

Ở checkpoint trước build đợt này, ngân sách phân tích của Member QA trên staging vẫn6/6, còn khoảng13486giây trong cửa sổ ngày lúc kiểm bằng READONLY. Không reset, đổi tài khoản/IP hoặc tạo phiên để né hạn mức. Guest đã8/8; không gọi thêm chat để vượt quota. Kết quả Preview mới sẽ bổ sung sau build và kiểm tra API. Nếu không thể kiểm đường lỗi LIVE do429, phải ghiBLOCKED thay vì dùng mock làm bằng chứngLIVE.

## Khi lỗi xảy ra tiếp theo

1. Giữ survey/session hiện tại, không tạo cuộc trò chuyện khác để thử lại lỗi.
2. Ghi nhận trace_id và schema_version từ response phân tích của chính người dùng; không thu token, câu trả lời hoặc prompt. Trace không phải bằng chứng quyền truy cập.
3. Tìm log `survey_analysis_invalid`/`survey_analysis_failed` theo đúng trace. Đối chiếu error_code, loại lỗi, đường dẫn trường, version và attempt. Mã nguồn chỉ ghi framefile/function/line, khônglocals.
4. Nếu trace lànull thì đó có thể là job lưu trước monitoring; không tự suy hoặc sinh trace gốc. Chỉ attempt mới hợp lệ mới sinh trace.
5. Retry chủ động cùng request_id và trong hạn mức; thành công thì cache, thất bại thì giữ thông báo an toàn. Không tắt validator/rate limit, không tự chấp nhận hồ sơ.
6. Chỉ kết luận nguyên nhân tái phát khi có diagnostic tương ứng. Không hồi tố nó thành nguyên nhân chắc chắn của lỗi lịch sử.

## Bàn giao

File code: `advisor/survey_analysis.py`, `advisor/analysis_jobs.py`. Test: `tests/test_analysis_validation.py`, `tests/test_analysis_validation_matrix.py`. Tài liệu Google đã xác nhận được giữ và cập nhật cùng bộ nhớ/decisions. Artifacts/credentials không đưa vàoGit.

Rollback chỉ code/Preview về3df3897/deploymentDA5F6cd6, không xóa/restore database, khảo sát, lịch sử hoặc quota. Production vẫnda6d146/9TdB69Ns và không được phát hành trong nhiệm vụ này.
