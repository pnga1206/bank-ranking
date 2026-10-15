"""Extract short, page-linked keyword contexts for manual evidence review."""
import csv
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEYWORDS = [
    "chuyển đổi số", "ngân hàng số", "giao dịch số", "kênh số", "khách hàng số",
    "dữ liệu lớn", "trí tuệ nhân tạo", "điện toán đám mây", "cloud", "big data",
    "artificial intelligence", "machine learning", "tự động hóa", "sinh trắc học",
    "open banking", "api", "an ninh mạng", "an toàn thông tin", "digital banking",
    "digital transformation", "ekyc", "tài chính số", "hệ sinh thái số",
]
MAX_PER_TERM_REPORT = 3
CONTEXT_CHARS = 240


def main():
    try:
        import pymupdf
    except ImportError as exc:
        raise SystemExit("Cài PyMuPDF trước: python -m pip install pymupdf") from exc

    with (ROOT / "data" / "annual_reports_manifest.csv").open(encoding="utf-8-sig", newline="") as handle:
        reports = list(csv.DictReader(handle))
    output = ROOT / "data" / "annual_report_snippets.csv"
    fields = ["ticker", "bank", "year", "page", "keyword", "context", "file", "source_url"]
    total = 0
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for report in reports:
            if report.get("status") != "downloaded" or not report.get("file"):
                continue
            pdf_path = ROOT / report["file"]
            if not pdf_path.is_file():
                continue
            counts = {term: 0 for term in KEYWORDS}
            with pymupdf.open(pdf_path) as document:
                for page_number, page in enumerate(document, start=1):
                    text = re.sub(r"\s+", " ", page.get_text("text"))
                    folded = text.casefold()
                    for term in KEYWORDS:
                        if counts[term] >= MAX_PER_TERM_REPORT:
                            continue
                        start = 0
                        while counts[term] < MAX_PER_TERM_REPORT:
                            position = folded.find(term.casefold(), start)
                            if position < 0:
                                break
                            left = max(0, position - CONTEXT_CHARS // 2)
                            right = min(len(text), position + len(term) + CONTEXT_CHARS // 2)
                            context = text[left:right].strip()
                            if left:
                                context = "…" + context
                            if right < len(text):
                                context += "…"
                            writer.writerow({
                                "ticker": report["ticker"], "bank": report["bank"],
                                "year": report["year"], "page": page_number,
                                "keyword": term, "context": context,
                                "file": report["file"], "source_url": report.get("url", ""),
                            })
                            counts[term] += 1
                            total += 1
                            start = position + len(term)
            print(f"{report['ticker']} {report['year']}: snippets extracted")
    print(f"Wrote {total} review snippets: {output}")


if __name__ == "__main__":
    main()
