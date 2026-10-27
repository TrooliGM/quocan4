# Task 4 — mở tính năng QA cho Guest và Member (ứng viên, chưa phát hành)

Ngày 27/10/2026. Nhánh: `feature/task4-public-guest-member-unlock-20261027`; base `main` tại `3b2f704`.

## Phạm vi

- Bỏ kiểm soát theo `ADVISOR_TEST_UIDS`/`ADVISOR_CONTROLLED_ROLLOUT` đối với những chức năng được phát hành công khai. Chỉ chấp nhận identity do backend xác thực: server-issued Guest, Firebase Google hoặc email/password.
- Cho Guest và Member truy cập Hồ sơ đã xác nhận, bật/tắt sử dụng Hồ sơ trong AI, và thao tác sửa/xóa mục **của chính mình** khi `ADVISOR_PROFILE_ENABLED=true` và migration 006 có sẵn.
- Guest: mục hồ sơ được xác nhận **tự hết hạn sau 2 giờ**, không thể đặt `retain=true` hoặc lưu cuộc trò chuyện lâu dài khi chưa đăng nhập; quota AI Guest **8 câu** vẫn giữ.
- Member: giữ hội thoại lâu dài bằng yêu cầu chủ động; không tự lưu suy luận AI thành mục hồ sơ.
- Tìm kiếm DDGS/Brave mở cho Guest và Member được xác thực, bỏ allowlist tìm kiếm `SEARCH_TEST_UIDS` / `SEARCH_QA_ONLY`. `SEARCH_PUBLIC_ENABLED=false` là kill-switch toàn bộ tìm kiếm khi sự cố, không phải QA-only. `SEARCH_PROVIDER` vẫn phải được thiết lập; giới hạn, xử lý nguồn và bảo vệ thông tin cá nhân không thay đổi.
- Khảo sát 5 câu và phân tích tự động đã dùng chung Guest/Member/QA; không sửa quota phân tích, API model hoặc dữ liệu người dùng.

## Điều kiện phát hành

1. Kiểm tra migration 006 đã được áp dụng; kiểm tra **chỉ trạng thái bật/tắt**, không đọc hay tiết lộ giá trị secret. `ADVISOR_PROFILE_ENABLED=true` là điều kiện cần. Nếu chưa bật, **không** tự động bật/bỏ migration trên Production.
2. Chạy thử nghiệm tập trung: `tests/test_task4_rollout.py`, `tests/test_task41_public_ui.py`, `tests/test_task44_profile_journey.py`, `tests/test_task42_search.py`, `tests/test_advisor30_profile.py`, `tests/test_task4_personalization.py`, `tests/test_guest_postgres.py`.
3. Preview: Guest bắt đầu mới, khảo sát, phân tích, xác nhận một mục, bật dùng profile, sửa/xóa mục trong 2 giờ; Member thao tác tương tự và lưu hội thoại; tài khoản B không xem/sửa hồ sơ A; Guest chưa đăng nhập không lưu lâu dài; Guest hết quota vẫn chặn chat. Search bật khi cấu hình hợp lệ; test tắt `SEARCH_PUBLIC_ENABLED=false`.
4. Kiểm tra phiên Guest chuyển sang Member không phá TTL/đồng ý lưu; không sao chép tự động mục tạm thành mục vĩnh viễn.
5. Chưa phát hành Production, chưa thay đổi env, chưa tự chạy migration. Yêu cầu xác nhận triển khai, rollback và báo cáo PASS/BLOCKED trên Preview.

**Trạng thái:** code nhánh và kiểm thử được cập nhật; các test chưa được chạy trong môi trường kết nối GitHub hiện tại. Không tuyên bố LIVE PASS.
