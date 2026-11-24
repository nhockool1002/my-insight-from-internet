# my-insight-from-internet

Dashboard theo dõi giờ làm & thu nhập cá nhân từ Applause Tasks Management
(`my.applause.com/u/internal/tasks/time-entries`).

## Cấu trúc

- `index.html` — trang dashboard tĩnh (không cần build), đọc dữ liệu trực tiếp
  từ `data/time_entries.json` và `config/rates.json` lúc tải trang.
- `data/time_entries.json` — tập dữ liệu gốc, mỗi time entry lưu theo `id`
  (không trùng lặp). Đây là file được cập nhật mỗi lần lấy dữ liệu mới.
- `config/rates.json` — bảng đơn giá ($/giờ) theo dự án. Sửa file này và push
  lại khi mức lương thay đổi — dashboard đọc trực tiếp, không cần build lại.
- `scripts/merge_entries.py` — gộp một lượt tải mới (`data/raw_time_entries.json`)
  vào `data/time_entries.json` theo `id` (upsert), không cần tải lại từ đầu.

## Quy trình cập nhật dữ liệu

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

## Xem thử cục bộ

```bash
python3 -m http.server 8080
```

rồi mở `http://localhost:8080`.
