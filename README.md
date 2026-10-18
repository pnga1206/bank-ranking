# Xếp hạng chuyển đổi số ngân hàng

Bộ dữ liệu và dashboard nghiên cứu so sánh 5 ngân hàng Việt Nam: Vietcombank (VCB), VietinBank (CTG), SHB, Sacombank (STB) và Nam A Bank (NAB), trong giai đoạn 2023–2025.

> **Lưu ý:** Đây là BXH nghiên cứu của nhóm, tham khảo khung DBI cho doanh nghiệp lớn. Đây không phải BXH chính thức của Ngân hàng Nhà nước. Điểm số được tính từ thông tin công khai; định nghĩa chỉ tiêu và độ phủ dữ liệu giữa ngân hàng/năm có thể khác nhau. Hãy xem điểm cùng nguồn, trạng thái kiểm chứng và độ phủ.

## Dự án làm gì?

1. Thu thập báo cáo thường niên (BCTN) của 5 ngân hàng trong 3 năm 2023–2025.
2. Trích từ khóa và đoạn văn theo số trang để hỗ trợ tìm bằng chứng trong BCTN.
3. Chấm điểm theo 6 tiêu chí có trọng số.
4. Hiển thị thứ hạng, so sánh, khoảng cách mục tiêu, nguồn minh chứng và tin tức trên dashboard Streamlit.

Luồng dữ liệu chính:

```text
BCTN + evidence.csv ──> src/scoring.py ──> data/scores.json ──> dashboard Streamlit
                                    └────> các bảng/biểu đồ đọc CSV trong data/
```

## Chạy dashboard trên Windows

Bạn chỉ cần làm các bước sau. Không cần mở hoặc sửa mã nguồn để xem dashboard.

### Bước 1: Cài Python

Cài Python 3.10 trở lên từ [python.org](https://www.python.org/downloads/). Khi cài, chọn **Add Python to PATH** nếu trình cài đặt có tùy chọn này.

Mở PowerShell hoặc Windows Terminal tại thư mục dự án (thư mục có `README.md`). Cách nhanh: mở thư mục dự án trong File Explorer, bấm vào thanh địa chỉ, gõ `powershell`, rồi nhấn Enter.

Kiểm tra Python:

```powershell
py --version
```

Nếu máy không nhận lệnh `py`, thử `python --version`. Nếu cả hai lệnh đều không chạy, hãy cài Python rồi mở lại Terminal.

### Bước 2: Cài thư viện

Sao chép và chạy lần lượt các lệnh sau tại thư mục gốc dự án:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Nếu máy không có lệnh `py`, thay `py` ở lệnh đầu bằng `python`. Có thể mất vài phút ở lần cài đầu tiên.

### Bước 3: Mở dashboard

```powershell
.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

Dashboard thường tự mở trong trình duyệt. Nếu không, mở địa chỉ hiện trong Terminal, thường là <http://localhost:8501>.

Để tắt dashboard, quay lại cửa sổ Terminal và nhấn **Ctrl+C**.

### Chạy lại vào những lần sau

Không cần tạo môi trường hoặc cài thư viện lại. Mở Terminal tại thư mục dự án và chạy:

```powershell
.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

## Dashboard có những trang nào?

| Trang | Nội dung |
|---|---|
| **Tổng quan** | BXH theo điểm trung bình 2023–2025 hoặc riêng năm 2025, KPI, diễn biến điểm, độ phủ dữ liệu và tin tức 2026. |
| **Chi tiết ngân hàng** | Điểm, cấp độ hiển thị, thứ hạng, radar, điểm theo trụ cột và chi tiết từng tiêu chí của một ngân hàng. |
| **So sánh** | So sánh từ 2 đến 5 ngân hàng bằng biểu đồ điểm, radar và heatmap. |
| **Gap Analysis** | Khoảng cách tới mức mục tiêu và bảng gợi ý tiêu chí nên ưu tiên xem xét. Đây là phân tích tham khảo, không phải khuyến nghị đầu tư. |
| **Bằng chứng & độ nhạy** | Lọc quan sát và nguồn, xem trạng thái audit/trích đoạn BCTN, tải CSV và so sánh BXH theo các kịch bản khác nhau. |

Cấp độ 1–5 trên dashboard chỉ là quy ước hiển thị theo các dải điểm 20 điểm; đây không phải cấp độ DBI chính thức.

## Cấu trúc dự án

```text
bank-ranking/
├── dashboard/
│   ├── app.py                   # Điểm vào của dashboard Streamlit
│   ├── utils.py                 # Đọc dữ liệu và hàm dùng chung
│   └── pages/                   # 5 trang dashboard
├── data/
│   ├── evidence.csv             # Dữ liệu đầu vào chấm điểm và nguồn hiện dùng
│   ├── scores.json              # Điểm và BXH được tạo từ evidence.csv
│   ├── evidence_source_matrix.csv # Nguồn/trích đoạn theo ngân hàng-năm-tiêu chí
│   ├── evidence_audit_summary.csv  # Tình trạng kiểm tra nguồn
│   ├── news_2026.csv            # Tin tức liên quan
│   ├── annual_reports/          # 15 PDF BCTN, khoảng 195 MB
│   ├── annual_reports_manifest.csv
│   ├── annual_report_keyword_counts.csv
│   ├── annual_report_snippets.csv
│   └── report_catalog.csv       # Mẫu catalog URL PDF tùy chọn
├── src/
│   ├── scoring.py               # Tính điểm và tạo data/scores.json
│   ├── method.py                # Trọng số, tiêu chí và giới hạn phương pháp
│   ├── mine_annual_reports.py   # Tải BCTN mục tiêu từ nguồn Zenodo
│   └── extract_report_snippets.py # Trích đoạn PDF theo trang/từ khóa
├── docs/
│   └── USER_GUIDE.md            # Hướng dẫn sử dụng dashboard chi tiết
├── .streamlit/config.toml       # Giao diện/theme Streamlit
├── requirements.txt             # Thư viện cần cài
└── README.md
```

## Các tệp dữ liệu dashboard sử dụng

Dashboard đọc dữ liệu trong `data/`; không nhập điểm trực tiếp trong mã giao diện.

- `scores.json`: điểm theo ngân hàng/năm, điểm tổng hợp, thứ hạng và độ phủ.
- `evidence.csv`: từng quan sát đầu vào, giá trị, ghi chú và URL nguồn. Các dòng có `scored=1` được tính điểm.
- `evidence_audit_summary.csv`: trạng thái đối chiếu nguồn theo từng ngân hàng/năm/tiêu chí.
- `evidence_source_matrix.csv`: thông tin nguồn và trích đoạn hỗ trợ kiểm tra từng điểm.
- `news_2026.csv`: tin tức hiển thị ở trang Tổng quan; tin tức không tham gia chấm điểm.
- `annual_report_snippets.csv` và `annual_report_keyword_counts.csv`: dữ liệu hiển thị phần rà soát BCTN.

Các PDF trong `data/annual_reports/` dùng khi cần tra cứu báo cáo gốc hoặc chạy lại bước trích đoạn. Dashboard hiện đọc các CSV trích xuất, không cần mở PDF khi khởi động.

## Cập nhật điểm và dữ liệu

### Chấm lại sau khi cập nhật bằng chứng

1. Cập nhật dòng phù hợp trong `data/evidence.csv`; kiểm tra ngân hàng, năm, tiêu chí, đơn vị, định nghĩa, ngày và URL nguồn.
2. Chỉ đặt `scored=1` khi quan sát được dùng làm đầu vào điểm. Không điền 0 để thay cho dữ liệu chưa tìm được.
3. Tại thư mục gốc dự án, chạy:

```powershell
.\.venv\Scripts\python.exe src/scoring.py
```

Lệnh này cập nhật `data/scores.json`. Tải lại trang Streamlit để xem dữ liệu mới. Dashboard tự đọc lại các tệp CSV/JSON khi chạy lại.

### Cập nhật tin tức

Thêm hoặc sửa bản ghi trong `data/news_2026.csv`, giữ nguyên các cột hiện có và điền URL nguồn. Tin tức là phần cập nhật riêng, không làm thay đổi điểm.

### Tải lại hoặc trích xuất BCTN

Các PDF 2023–2025 đã có sẵn trong repo. Chỉ chạy các lệnh sau nếu cần lấy lại báo cáo hoặc tạo lại dữ liệu khai phá:

```powershell
.\.venv\Scripts\python.exe src/mine_annual_reports.py
.\.venv\Scripts\python.exe src/extract_report_snippets.py
```

Lệnh tải cần Internet để đọc mục lục Zenodo và chỉ lấy PDF mục tiêu, không tải toàn bộ file ZIP lớn. Sau khi trích đoạn xong, kiểm tra lại `annual_report_snippets.csv` và `annual_report_keyword_counts.csv`. Tần suất từ khóa hoặc một trích đoạn liên quan chủ đề tự nó không xác nhận một con số.

## Cách tính điểm và cách đọc kết quả

| Tiêu chí | Trọng số |
|---|---:|
| Tỷ trọng giao dịch qua kênh số | 30% |
| Người dùng số hoạt động | 25% |
| Nghiệp vụ trọng yếu hoàn toàn trên kênh số | 15% |
| Mốc sản phẩm/nền tảng số trong năm | 15% |
| Chiến lược chuyển đổi số | 10% |
| Ghi nhận/giải thưởng độc lập | 5% |

Điểm tiêu chí được quy về thang 0–100. Điểm năm là trung bình có trọng số của các tiêu chí có dữ liệu; trọng số được chuẩn hóa lại khi thiếu tiêu chí. **Độ phủ** cho biết tỷ lệ trọng số có dữ liệu. Điểm tổng hợp là trung bình các năm có điểm.

Một số thang chuẩn hóa có tính quy ước nghiên cứu: tỷ lệ giao dịch số quy từ mốc 80% đến 100%; người dùng số chuẩn hóa theo mốc 18 triệu; số mốc và giải thưởng tối đa tính 3; điểm chiến lược theo rubric. Xem `src/scoring.py` và `src/method.py` nếu cần công thức/rubric đầy đủ.

## Lưu ý về nguồn và diễn giải

- Chỉ so sánh các tỷ lệ khi đã kiểm tra định nghĩa, mẫu số, phạm vi (bán lẻ/toàn ngân hàng), kỳ đo và số liệu hợp nhất.
- Một ngân hàng có thể công bố số giao dịch qua kênh số và số nghiệp vụ có thể hoàn tất trên kênh số; đây là hai chỉ tiêu khác nhau.
- Người dùng hoạt động không đồng nghĩa với lượt tải ứng dụng hoặc tổng số khách hàng đăng ký.
- Trích đoạn BCTN chỉ là đầu mối kiểm tra. Hãy mở nguồn gốc và xác minh câu chữ/số trang trước khi trích dẫn.
- Audit hiện cho thấy nhiều ô điểm chưa có đủ nguồn độc lập xác nhận. Độ phủ thấp cũng làm điểm nhạy hơn khi thay đổi tiêu chí.
- Không có dữ liệu không đồng nghĩa với điểm 0 hoặc năng lực thấp. Dashboard có thể trình bày cả hạng theo các kịch bản độ nhạy; cần ghi rõ kịch bản khi trích kết quả.
- BCTN được lưu trong repo lấy từ bộ dữ liệu trên Zenodo; manifest ghi nguồn tải và mã SHA-256 để kiểm tra tệp.

## Xử lý lỗi thường gặp

| Tình huống | Cách xử lý |
|---|---|
| `py` hoặc `python` không được nhận diện | Cài Python 3.10+, chọn thêm Python vào PATH khi cài đặt, rồi mở lại Terminal. |
| `No module named streamlit` hoặc thiếu thư viện | Chạy lại lệnh cài `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` tại thư mục dự án. |
| Không tìm thấy CSV/JSON | Kiểm tra Terminal đang ở thư mục chứa `README.md`; dashboard cần chạy từ mã `dashboard/app.py` trong repo này. |
| Dashboard không mở tự động | Mở thủ công `http://localhost:8501`; địa chỉ đầy đủ cũng được in trong Terminal. |
| Cổng 8501 đang bận | Chạy `.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py --server.port 8502` rồi mở `http://localhost:8502`. |
| Điểm chưa đổi sau khi sửa evidence | Chạy lại `src/scoring.py`, sau đó tải lại trang dashboard. |
| Giao diện không dùng theme dự kiến | Khởi động lệnh từ thư mục gốc repo để Streamlit nhận `.streamlit/config.toml`. |

## Hướng dẫn thêm

Xem [docs/USER_GUIDE.md](docs/USER_GUIDE.md) để biết cách đọc từng trang dashboard và các bộ lọc chi tiết.
