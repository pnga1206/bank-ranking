# Xếp hạng chuyển đổi số ngân hàng

Dashboard Streamlit cho 5 ngân hàng (VCB, VietinBank, SHB, Sacombank, Nam A Bank), dữ liệu điểm giai đoạn 2023–2025.

## Chạy dashboard

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m streamlit run src/app.py
```

Mở URL Streamlit in ra terminal, thường là `http://localhost:8501`.

## Dữ liệu dashboard dùng

- `data/evidence.csv`: quan sát điểm theo ngân hàng/năm/tiêu chí, ghi nguồn trong `url`; `scored=1` được tính, `scored=0` bị loại mặc định.
- `data/news_2026.csv`: tin 2026 để tham khảo, không tính điểm. Đây là CSV tĩnh, chưa tự cập nhật.
- `src/scoring.py`: danh sách tiêu chí, trọng số, chuẩn hóa điểm.
- `src/method.py`: diễn giải phương pháp và nguồn tham khảo DBI.

## Giới hạn dữ liệu

Đây là BXH nghiên cứu của nhóm dựa trên nguồn công khai, không phải BXH hay điểm DBI do NHNN ban hành. Độ phủ giữa các ngân hàng khác nhau; định nghĩa các số liệu công bố chưa chắc đồng nhất. `evidence.csv` hiện có một URL cho mỗi dòng, chưa đảm bảo 2–3 minh chứng độc lập cho từng tiêu chí. Tin tức cần được rà và cập nhật thủ công.

Xem [HANDOFF_CODER2.md](HANDOFF_CODER2.md) để biết cách dùng dữ liệu và yêu cầu dashboard tiếp theo.
