# BXH chuyển đổi số ngân hàng 2023–2025

Ngân hàng: VCB, VietinBank, SHB, Sacombank, Nam A Bank. Khung tham khảo: DBI doanh nghiệp lớn.

## Chạy (VS Code, Python 3.9+)

```bash
python src/seed_evidence.py     # data/evidence.csv + data/news_2026.csv
python src/scoring.py           # output/scores.json
python src/build_dashboard.py   # output/dashboard.html  <- mở file này
# tuỳ chọn, cần internet: pip install requests && python src/scrape.py
```

## Cấu trúc
- `data/evidence.csv` – mỗi dòng 1 số liệu + link nguồn + từ khóa kiểm chứng
- `data/news_2026.csv` – tin 2026, không tính điểm
- `src/scoring.py` – trọng số, quy điểm, xếp hạng, độ phủ dữ liệu
- `output/dashboard.html` – dashboard (file đơn)

## Lưu ý
Không phải điểm DBI chính thức; xem mục “Phương pháp và giới hạn” trong dashboard.
