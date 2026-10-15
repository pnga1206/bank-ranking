"""Kiểm chứng lại từng số liệu trong data/evidence.csv trên trang nguồn.

Với mỗi dòng: tải URL, tìm chuỗi `keyword`, ghi kết quả vào output/verification.csv.
Chạy trên máy cá nhân (cần internet):  python src/scrape.py
Lưu ý: PDF được bỏ qua phần kiểm chứng tự động (đánh dấu 'pdf-manual').
"""
import csv
import pathlib
import re
import time

import requests  # pip install requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
HEADERS = {"User-Agent": "Mozilla/5.0 (research; bank-dx-ranking)"}


def fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", r.text))


def main():
    rows = list(csv.DictReader(open(ROOT / "data" / "evidence.csv", encoding="utf-8-sig")))
    cache, out = {}, []
    for r in rows:
        url = r["url"]
        if url.lower().endswith(".pdf"):
            status = "pdf-manual"
        else:
            try:
                if url not in cache:
                    cache[url] = fetch(url)
                    time.sleep(1)
                status = "found" if r["keyword"] in cache[url] else "keyword-not-found"
            except Exception as e:  # noqa: BLE001
                status = f"error: {type(e).__name__}"
        out.append({**r, "verify": status})
        print(status, r["bank"], r["year"], r["metric"])
    (ROOT / "output").mkdir(exist_ok=True)
    with open(ROOT / "output" / "verification.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)


if __name__ == "__main__":
    main()
