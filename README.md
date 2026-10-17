# Bank DX Ranking: dữ liệu và pipeline nghiên cứu

Repo lưu dữ liệu nghiên cứu chuyển đổi số của 5 ngân hàng Việt Nam (VCB, VietinBank/CTG, SHB, Sacombank/STB và Nam A Bank/NAB), giai đoạn 2023–2025. Đây là BXH nghiên cứu của nhóm tham khảo DBI, không phải BXH chính thức do Ngân hàng Nhà nước công bố.

## Cấu trúc repo

- `data/evidence.csv`: các quan sát đang dùng để chấm điểm, gồm ngân hàng, năm, tiêu chí, giá trị và nguồn hiện có.
- `data/scores.json`: điểm nghiên cứu tổng hợp từ `evidence.csv` theo trọng số hiện tại.
- `data/evidence_source_matrix.csv`: nguồn gốc và trích đoạn BCTN để đối chiếu. Cột `match_status` phân biệt nguồn khớp số liệu với trích đoạn chỉ liên quan chủ đề.
- `data/evidence_audit_summary.csv`: trạng thái rà soát theo ngân hàng/năm/tiêu chí; cho biết tiêu chí còn thiếu nguồn đối chiếu.
- `data/news_2026.csv`: các tin tức liên quan đã thu thập.
- `data/annual_reports/`: 15 file PDF BCTN (5 ngân hàng × 3 năm), tổng dung lượng khoảng 195 MB.
- `data/annual_reports_manifest.csv`: nguồn, tên file, trạng thái tải và mã SHA-256 của từng báo cáo.
- `data/annual_report_keyword_counts.csv`: số lần xuất hiện từ khóa trong từng báo cáo.
- `data/annual_report_snippets.csv`: trích đoạn ngắn kèm số trang để hỗ trợ rà soát thủ công; trích đoạn không tự xác nhận tính đúng đắn của điểm.
- `data/report_catalog.csv`: mẫu CSV tùy chọn để cung cấp URL PDF trực tiếp khi chạy công cụ tải với catalog riêng.
- `src/mine_annual_reports.py`: lấy mục lục Zenodo, tải các PDF khớp ngân hàng/năm và tạo manifest cùng thống kê từ khóa. Công cụ tải các báo cáo mục tiêu, không tải toàn bộ ZIP.
- `src/extract_report_snippets.py`: trích ngữ cảnh theo trang từ các PDF đã tải.
- `src/scoring.py`, `src/method.py`: mã tính điểm và mô tả phương pháp nghiên cứu.
- `dashboard/`: dashboard Streamlit 5 trang (`app.py`, `utils.py`, `pages/`), chỉ đọc dữ liệu trong `data/`.
- `.streamlit/config.toml`: theme pastel sáng của dashboard.
- `docs/USER_GUIDE.md`: hướng dẫn sử dụng dashboard.
- `requirements.txt`: thư viện Python cần cài.

Các PDF là BCTN của ngân hàng được phân phối trong bộ dữ liệu BCTN trên Zenodo. Bản trong repo được lấy từ bản lưu trữ Zenodo; đường dẫn trong manifest trỏ tới nguồn này. Có thể dùng mã SHA-256 trong manifest để kiểm tra tính toàn vẹn của file.

## Cài đặt và chạy

Yêu cầu Python 3.10 trở lên. Mở terminal tại thư mục gốc repo và chạy:

```powershell
python -m pip install -r requirements.txt
python src/mine_annual_reports.py
python src/extract_report_snippets.py
python src/scoring.py
```

Lệnh tải báo cáo cần kết nối Internet để đọc mục lục Zenodo. Công cụ chỉ tải các PDF mục tiêu còn thiếu. Để dùng catalog riêng, chạy `python src/mine_annual_reports.py data/report_catalog.csv`. File mẫu trong repo đang để trống URL; cần điền URL PDF trước khi chạy theo cách này.

## Lưu ý khi dùng dữ liệu

Trước khi so sánh tỷ lệ giao dịch số, người dùng số hoặc tỷ lệ tự động hóa, cần kiểm tra phạm vi (bán lẻ hay toàn ngân hàng), mẫu số, kỳ đo, phạm vi hợp nhất và định nghĩa chỉ tiêu. Các ngân hàng hoặc các năm có thể dùng định nghĩa khác nhau.

Audit hiện ghi nhận nhiều tiêu chí chưa có đủ nguồn độc lập đối chiếu. Không nên trình bày BXH như kết quả đã được kiểm chứng đầy đủ hoặc như BXH chính thức của Ngân hàng Nhà nước. Khi làm dashboard, nên hiển thị nguồn, trạng thái kiểm chứng và độ phủ dữ liệu cùng với điểm số.


## Dashboard

```powershell
python -m pip install -r requirements.txt
streamlit run dashboard/app.py
```

Chạy lệnh tại thư mục gốc repo (để Streamlit đọc `.streamlit/config.toml`). Dashboard mở tại http://localhost:8501.

| Trang | Nội dung |
|---|---|
| Tổng quan | Xếp hạng 5 ngân hàng, KPI, diễn biến theo năm, độ phủ dữ liệu, tin cập nhật 2026 |
| Chi tiết ngân hàng | Tổng điểm, cấp độ, radar chỉ tiêu, điểm theo trụ cột, bảng chỉ tiêu |
| So sánh | 2–5 ngân hàng: radar chồng, heatmap chỉ tiêu/trụ cột × ngân hàng |
| Gap Analysis | Khoảng cách tới cấp độ mục tiêu, vùng đỏ–cam, bảng ưu tiên đầu tư |
| Bằng chứng & độ nhạy | Bộ lọc bằng chứng, trạng thái audit, minh chứng/trích đoạn BCTN, 6 phương án độ nhạy |

Dashboard không hard-code điểm: mọi bảng/biểu đồ được tính từ `data/scores.json`, `data/evidence.csv`, `data/evidence_audit_summary.csv`, `data/evidence_source_matrix.csv`, `data/news_2026.csv` và các file BCTN trích xuất. Sau khi sửa `evidence.csv`, chạy lại `python src/scoring.py` rồi tải lại trang để cập nhật.

### Deploy (tùy chọn)

Đẩy repo lên GitHub, vào Streamlit Community Cloud, chọn repo và đặt *Main file path* là `dashboard/app.py`. Thư mục `data/annual_reports/` (~195 MB) không cần cho dashboard; có thể bỏ khỏi bản deploy để cài đặt nhanh hơn.

### Lưu ý khi trình bày

Dashboard luôn hiển thị cảnh báo: đây là BXH nghiên cứu của nhóm tham khảo DBI, không phải BXH chính thức của NHNN; nhiều tiêu chí chưa đủ nguồn độc lập. Cấp độ 1–5 trên dashboard là quy ước hiển thị theo dải 20 điểm, không phải cấp độ DBI chính thức.
