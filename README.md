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
- `src/scoring.py`, `src/method.py`: mã tính điểm và mô tả phương pháp nghiên cứu; repo không chứa dashboard.
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
