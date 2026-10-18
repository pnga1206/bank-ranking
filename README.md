# Xếp hạng chuyển đổi số ngân hàng

## 1. Tổng quan

Dự án nghiên cứu và so sánh mức độ chuyển đổi số của 5 ngân hàng Việt Nam: Vietcombank (VCB), VietinBank (CTG), SHB, Sacombank (STB) và Nam A Bank (NAB), trong giai đoạn 2023–2025. Nhóm tham khảo khung DBI cho doanh nghiệp lớn, sử dụng dữ liệu công khai để xây dựng bộ tiêu chí, chấm điểm và trình bày kết quả trên dashboard.

Dashboard hỗ trợ xem BXH, theo dõi điểm theo năm, so sánh ngân hàng, xem khoảng cách tới mục tiêu, và tra cứu nguồn minh chứng.

> **Phạm vi:** Đây là BXH nghiên cứu của nhóm, không phải BXH chính thức của Ngân hàng Nhà nước. Điểm số phụ thuộc vào dữ liệu và phương pháp do nhóm xây dựng; cần đọc cùng độ phủ và trạng thái kiểm chứng nguồn.

## 2. Dữ liệu

Dữ liệu gồm báo cáo thường niên, thông tin công khai về hoạt động số, các quan sát được dùng để chấm điểm và tin tức liên quan. Repo có 15 PDF báo cáo thường niên (5 ngân hàng × 3 năm), cùng các bảng trích đoạn và manifest ghi lại tệp/nguồn.

Các tệp chính trong `data/`:

- `evidence.csv`: giá trị đầu vào cho từng ngân hàng, năm và tiêu chí; có URL và ghi chú nguồn. Dòng có `scored=1` được đưa vào tính điểm.
- `scores.json`: điểm tổng hợp, điểm theo năm, thứ hạng và độ phủ; được tạo từ `evidence.csv`.
- `evidence_source_matrix.csv` và `evidence_audit_summary.csv`: nguồn đối chiếu, trích đoạn và tình trạng rà soát.
- `annual_reports/`, `annual_reports_manifest.csv`: PDF báo cáo thường niên và thông tin nguồn/tệp.
- `annual_report_snippets.csv`, `annual_report_keyword_counts.csv`: trích đoạn theo trang và thống kê từ khóa để hỗ trợ rà soát thủ công.
- `news_2026.csv`: tin tức liên quan; tin không tham gia tính điểm.

## 3. Phương pháp

Điểm được tổng hợp từ sáu tiêu chí:

| Tiêu chí | Trọng số |
|---|---:|
| Tỷ trọng giao dịch qua kênh số | 30% |
| Người dùng số hoạt động | 25% |
| Nghiệp vụ trọng yếu hoàn toàn trên kênh số | 15% |
| Mốc sản phẩm/nền tảng số trong năm | 15% |
| Chiến lược chuyển đổi số | 10% |
| Ghi nhận hoặc giải thưởng từ bên thứ ba | 5% |

Mỗi tiêu chí được quy về thang 0–100. Điểm năm là trung bình có trọng số của các tiêu chí có dữ liệu; trọng số được chuẩn hóa lại khi thiếu tiêu chí. Điểm tổng hợp là trung bình các năm có điểm. **Độ phủ** thể hiện tỷ lệ trọng số có dữ liệu, giúp người xem biết điểm dựa trên bao nhiêu tiêu chí.

Một số mốc chuẩn hóa là quy ước nghiên cứu: tỷ lệ giao dịch số theo khoảng 80–100%, người dùng số theo mốc 18 triệu, số mốc/giải thưởng tối đa tính 3; điểm chiến lược được chấm theo rubric. Xem `src/scoring.py` và `src/method.py` để biết công thức chi tiết.

Các ngân hàng có thể công bố số liệu theo phạm vi, mẫu số, kỳ đo và định nghĩa khác nhau. Trích đoạn báo cáo chỉ là đầu mối tìm kiếm, không tự xác nhận con số. Audit hiện còn ghi nhận tiêu chí thiếu nguồn độc lập; không nên coi BXH là kết luận chính thức về năng lực thực tế.

## 4. Cấu trúc dự án

```text
bank-ranking/
├── dashboard/       # Ứng dụng Streamlit và các trang dashboard
├── data/            # Dữ liệu, báo cáo PDF, điểm và minh chứng
├── src/             # Tính điểm, tải báo cáo, trích đoạn PDF
├── docs/            # Hướng dẫn sử dụng dashboard
├── .streamlit/      # Cấu hình giao diện Streamlit
├── requirements.txt # Thư viện Python cần cài
└── README.md
```

## 5. Kết quả hiện tại

Theo `data/scores.json` hiện có, BXH điểm trung bình giai đoạn 2023–2025 như sau:

| Hạng | Ngân hàng | Điểm TB | Độ phủ TB | Hạng năm 2025 | Điểm năm 2025 |
|---:|---|---:|---:|---:|---:|
| 1 | Vietcombank (VCB) | 75,5 | 75% | 1 | 86,4 |
| 2 | Sacombank | 65,4 | 63% | 3 | 71,3 |
| 3 | VietinBank | 62,7 | 75% | 2 | 75,3 |
| 4 | SHB | 61,4 | 63% | 5 | 62,9 |
| 5 | Nam A Bank | 59,4 | 43% | 4 | 64,3 |

Đây là kết quả của bộ dữ liệu và trọng số hiện tại, không phải thứ hạng chính thức. Độ phủ giữa các ngân hàng chưa đồng đều; nên mở dashboard để xem nguồn, tình trạng audit và các kịch bản độ nhạy trước khi diễn giải hoặc trích dẫn kết quả. Chạy lại chương trình tính điểm sẽ cập nhật `scores.json` và có thể làm thay đổi bảng trên.

## 6. Hướng dẫn tái lập

Cần cài Python 3.10 trở lên. Mở PowerShell/Terminal tại thư mục gốc dự án (thư mục có `README.md`), rồi cài thư viện:

```powershell
python -m pip install -r requirements.txt
```

### Tính lại BXH

Sau khi cập nhật `data/evidence.csv`, chạy:

```powershell
python src/scoring.py
```

Kết quả mới được ghi vào `data/scores.json`.

### Chạy dashboard

```powershell
python -m streamlit run dashboard/app.py
```

Mở địa chỉ được in trong Terminal, thường là <http://localhost:8501>. Dừng dashboard bằng **Ctrl+C**.

### Tải lại và trích xuất báo cáo thường niên (tùy chọn)

Các PDF hiện đã nằm trong repo; không cần chạy bước này để xem dashboard. Khi muốn tải/cập nhật báo cáo, cần có Internet:

```powershell
python src/mine_annual_reports.py
python src/extract_report_snippets.py
```

Công cụ tải báo cáo mục tiêu từ mục lục Zenodo, không tải toàn bộ ZIP. Sau khi trích xuất, kiểm tra lại các CSV và xác minh nội dung từ nguồn gốc trước khi dùng làm minh chứng hoặc thay đổi điểm.

Nếu lệnh `python` không chạy, cài Python 3.10 trở lên, chọn thêm Python vào PATH khi cài đặt, rồi mở lại Terminal. Nếu báo thiếu thư viện, chạy lại lệnh cài đặt ở đầu mục này.
