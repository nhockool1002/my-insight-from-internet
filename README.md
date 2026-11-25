# my-insight-from-internet

Dashboard theo dõi giờ làm & thu nhập cá nhân, gộp 2 nguồn:

- **Applause** Tasks Management (`my.applause.com/u/internal/tasks/time-entries`)
- **uTest** Payments (`platform.utest.com/account/payments`)

Trang có 2 tab (Applause / uTest), mỗi tab có bộ lọc thời gian, KPI, heatmap
cường độ theo ngày, thu nhập theo dự án/công ty, biểu đồ theo tháng — độc lập
với nhau.

## Cấu trúc

- `index.html` — trang dashboard tĩnh (không cần build), đọc dữ liệu trực tiếp
  từ các file JSON bên dưới lúc tải trang.
- `data/time_entries.json` — dữ liệu Applause, mỗi time entry lưu theo `id`
  (không trùng lặp).
- `config/rates.json` — bảng đơn giá ($/giờ) theo dự án Applause (Applause
  không có sẵn trường tiền). Sửa file này và push lại khi mức lương thay đổi.
- `data/utest_payments.json` — dữ liệu uTest, mỗi dòng là một khoản thanh toán
  (test case result / bug / TTL payment / hourly payment / bonus...) lưu theo
  `id` tổng hợp (`paymentId-entityTypeId-entityId`), có sẵn trường `amount` và
  `url` trỏ thẳng tới Bug/Test Case liên quan trên uTest.
- `scripts/merge_entries.py` — gộp một lượt tải mới Applause
  (`data/raw_time_entries.json`) vào `data/time_entries.json` theo `id`.
- `scripts/merge_utest_payments.py` — gộp một lượt tải mới uTest
  (`data/raw_utest_payments.json`) vào `data/utest_payments.json` theo `id`.

## Quy trình cập nhật dữ liệu Applause

Dữ liệu chỉ có thể lấy được khi đã đăng nhập `my.applause.com`, nên việc cập
nhật được thực hiện thủ công qua phiên chat với Claude:

1. Người dùng vào lại session chat này, yêu cầu "lấy dữ liệu mới nhất".
2. Claude mở trình duyệt, gọi API nội bộ
   `GET /api/time-entries?...&page=1&size=2000&sort=id,DESC` (đã đăng nhập sẵn),
   tải JSON kết quả.
3. Chạy `python3 scripts/merge_entries.py data/raw_time_entries.json data/time_entries.json`
   để gộp (các dòng đã **Invoiced** không đổi nữa, các dòng khác sẽ được ghi đè
   theo trạng thái mới nhất).
4. Commit & push `data/time_entries.json` lên GitHub.

## Quy trình cập nhật dữ liệu uTest

Tương tự, cần đăng nhập `platform.utest.com`:

1. Claude gọi `GET /api/profile/payments/` để lấy danh sách các đợt thanh toán
   (mỗi đợt là một `paymentId`).
2. Với mỗi `paymentId` **chưa có trong dữ liệu cục bộ**, gọi
   `GET /api/profile/payments/{paymentId}` để lấy chi tiết từng dòng thanh
   toán (test case result, bug, TTL/hourly payment...) — các đợt đã lưu rồi
   thì bỏ qua vì chi tiết thanh toán không đổi sau khi đã phát hành.
3. Với mỗi dòng, dựng `url`:
   - `paidEntityTypeId === 1` (Bug): `/testcycles/{testCycleId}/issues/{paidEntityId}`
   - `paidEntityTypeId === 9` (Test Case Result): `/testcycles/{testCycleId}/testcases/{testCaseId}`
     (testCaseId lấy từ `paidEntityDescription`, regex `Test Case #(\d+)`; nếu
     không khớp được — thường là các khoản rất cũ, mô tả không theo mẫu số —
     thì rơi về link cấp cycle)
   - Loại khác (TTL/Hourly Payment, Bonus...): `/testcycles/{testCycleId}/`
4. Chạy `python3 scripts/merge_utest_payments.py data/raw_utest_payments.json data/utest_payments.json`.
5. Commit & push `data/utest_payments.json` lên GitHub.

## Xem thử cục bộ

```bash
python3 -m http.server 8080
```

rồi mở `http://localhost:8080`.
