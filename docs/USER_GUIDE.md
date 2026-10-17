# Hướng dẫn sử dụng dashboard BXH chuyển đổi số ngân hàng

## 1. Khởi chạy
1. Cài Python 3.10+ và chạy `python -m pip install -r requirements.txt` tại thư mục gốc repo.
2. Chạy `streamlit run dashboard/app.py`, mở http://localhost:8501.
3. Thanh bên trái dùng để chuyển giữa 5 trang.

## 2. Cách đọc điểm
- Mỗi chỉ tiêu được quy về thang 0–100; điểm năm là trung bình có trọng số của **chỉ tiêu có dữ liệu** (trọng số chuẩn hóa lại).
- **Độ phủ dữ liệu** là tỷ trọng chỉ tiêu có dữ liệu. Độ phủ thấp nghĩa là điểm dựa trên ít chỉ tiêu, cần đọc thận trọng.
- **Cấp độ 1–5** là quy ước hiển thị theo dải 20 điểm (0–20, 20–40, …), không phải cấp độ DBI chính thức.
- Ô **“Chưa có DL”** nghĩa là chưa có bằng chứng công khai đủ dùng; không phải 0 điểm và không chứng tỏ năng lực thấp.
- Đây là BXH nghiên cứu của nhóm, không phải xếp hạng chính thức của NHNN.

## 3. Từng trang
**Tổng quan.** Chọn xếp hạng theo *trung bình 2023–2025* hoặc *năm 2025*. Xem KPI, bảng hạng, biểu đồ diễn biến, độ phủ và mục *Cập nhật 2026* (tin tức không tham gia chấm điểm).

**Chi tiết ngân hàng.** Chọn 1 ngân hàng và kỳ xem. Xem tổng điểm, cấp độ, hạng, radar so với trung bình nhóm, điểm theo trụ cột và bảng từng chỉ tiêu kèm trạng thái bằng chứng.

**So sánh.** Chọn 2–5 ngân hàng. Xem tổng điểm theo năm, radar chồng, heatmap theo chỉ tiêu hoặc trụ cột.

**Gap Analysis.** Chọn kỳ và cấp độ mục tiêu (Mức 3/4/5 hoặc tùy chỉnh). Xem khoảng cách tổng điểm, bản đồ gap (đỏ ≥ 40, cam 20–40, xanh < 20) và bảng ưu tiên. *Chỉ số ưu tiên = gap trung bình × trọng số ÷ 100.*

**Bằng chứng & độ nhạy.**
- *Bằng chứng*: lọc theo ngân hàng, năm, trụ cột, tiêu chí, loại và mức điểm; mở liên kết nguồn; xem trạng thái kiểm chứng và trích đoạn BCTN theo từng quan sát; tải CSV.
- *Độ nhạy xếp hạng*: so sánh 6 phương án (cơ sở, chỉ năm 2025, năm độ phủ ≥ 50%, trọng số bằng nhau, chỉ số liệu công bố, thiếu = 0).
- *Trích đoạn BCTN*: tần suất từ khóa và trích đoạn theo trang để rà soát thủ công.

## 4. Cập nhật dữ liệu
Sửa `data/evidence.csv` → chạy `python src/scoring.py` → tải lại trang (hoặc nhấn `R`). Dashboard không cần sửa code.

## 5. Xử lý sự cố
- *Lỗi thiếu thư viện*: chạy lại `pip install -r requirements.txt`.
- *Không thấy theme pastel*: chạy lệnh tại thư mục gốc repo để nhận `.streamlit/config.toml`.
- *Số liệu không đổi sau khi sửa*: chưa chạy lại `src/scoring.py`.
