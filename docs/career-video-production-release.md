# Phát hành video nghề nghiệp — 29/10/2026

Người dùng trực tiếp cho phép commit, push nhánh tính năng, tích hợp main và triển khai Production từ checkpoint video 200 nghề; thay phạm vi chỉ Preview trước đó. Cho phép hoãn sửa ghi chú tiếng Việt và rà nội dung bổ sung. Không thay đổi cấu hình Production, quota, dữ liệu hoặc migration.

- Nguồn: worktree `career-video-pilot`, nhánh `feat/career-video-pilot`, base `1a1a4c48a6221c7850496038064c066b91aea701`, trùng `origin/main` trước tích hợp.
- Catalog: 200 nghề có video riêng, 200 truyện tương tác; một video Chef pending cũ không công khai. Không tuyên bố 200/200 phát thành công trên Production.
- Production trước phát hành: commit `43a8337f694c6931fcf26805a9349841ddabf93c`, deployment READY `dpl_7cdWzerGqdzD3c4Ucjvfb8GaJbfE`, URL deployment `quocan4-nkqnpwx0d-khkt3.vercel.app`.
- Project Vercel `khkt3/quocan4`, Production Branch `main`; `git.deploymentEnabled.main=false` giữ nguyên. Phát hành thủ công bằng Production candidate `--prod --skip-domain`, kiểm tra rồi promote.
- Không dùng các helper override Preview để triển khai Production. Không sao chép DATABASE_URL staging hoặc tắt AI/Firebase/database; clean checkout dùng environment Production hiện có.
- Sao lưu mã/bằng chứng trước phát hành: `artifacts/checkpoints/career-videos-200-20261029/` ở worktree gốc; không commit artifacts hoặc secrets.

## Phần được hoãn theo yêu cầu người dùng

Một số ghi chú phụ đề/phạm vi rà của 7 nguồn pilot và mô tả Ngân quỹ/Phát triển nông thôn có lỗi dấu `?`. Các URL/ID không bị thay đổi vì lỗi này. Giữ bản hiện có để phát hành; sửa văn bản sau. Mức rà nội dung chỉ là mẫu hình/phụ đề/mô tả, chưa nghe trọn toàn bộ video.

Hậu kiểm cần ghi riêng: phát nhúng từng video trên domain chính, desktop/mobile đầy đủ, Google popup và hội thoại AI LIVE. Không dùng build READY hay kết quả pilot để tự đánh dấu các mục này PASS.

## Quy trình rollback

Nếu xác minh lỗi nghiêm trọng sau promote, dùng Vercel rollback về deployment `dpl_7cdWzerGqdzD3c4Ucjvfb8GaJbfE` của cùng project; không reset database/quota và không force-push main. Git có thể phục hồi bằng revert commit phát hành trong lần xử lý tiếp theo nếu cần.

Kết quả triển khai thực tế sẽ được lưu riêng sau khi candidate READY và kiểm tra domain.
