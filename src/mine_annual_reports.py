"""Download and mine the five banks' 2023-2025 annual reports."""
import argparse
import csv
import hashlib
import io
import json
import pathlib
import re
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "data" / "annual_reports"
YEARS = {"2023", "2024", "2025"}
BANKS = {"VCB": "VCB", "CTG": "VietinBank", "SHB": "SHB", "STB": "Sacombank", "NAB": "Nam A Bank"}
KEYWORDS = [
    "chuyển đổi số", "ngân hàng số", "giao dịch số", "kênh số", "khách hàng số",
    "dữ liệu lớn", "trí tuệ nhân tạo", "điện toán đám mây", "cloud", "big data",
    "artificial intelligence", "machine learning", "tự động hóa", "sinh trắc học",
    "open banking", "api", "an ninh mạng", "an toàn thông tin", "digital banking",
    "digital transformation", "ekyc", "tài chính số", "hệ sinh thái số",
]
HEADERS = {"User-Agent": "bank-dx-ranking/1.0 (annual report research)"}
REMOTE_ARCHIVES = {}
REMOTE_NAMES = {}


def normalized_key(value):
    return re.sub(r"[^a-z0-9]", "", value.lower())


def pick(row, aliases):
    values = {normalized_key(str(key)): value for key, value in row.items() if key}
    for alias in aliases:
        value = values.get(normalized_key(alias))
        if value not in (None, ""):
            return str(value).strip()
    return ""


def get_text(pdf_path):
    try:
        import pymupdf
    except ImportError:
        return None
    with pymupdf.open(pdf_path) as document:
        return "\n".join(page.get_text("text") for page in document)


def year_from(value):
    match = re.search(r"20\d{2}", str(value))
    if match:
        return match.group(0)
    match = re.search(r"(?:^|[_-])(\d{2})(?:N|CN)(?:[_.-]|$)", str(value), re.I)
    return f"20{match.group(1)}" if match else ""


def fetch_zenodo_reports():
    """Read Zenodo's small index, then locate only the target PDFs in its ZIP."""
    api = "https://zenodo.org/api/records/20949551"
    request = urllib.request.Request(api, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=60) as response:
        record = json.load(response)
    files = record.get("files", [])
    if isinstance(files, dict):
        files = [{"key": key, **value} for key, value in files.items()]
    index_file = next((item for item in files if item.get("key") == "file_index_full.csv"), None)
    archive_file = next((item for item in files if item.get("key") == "vn_bctn_2021_2025.zip"), None)
    if not index_file or not archive_file:
        raise RuntimeError("Zenodo record lacks file_index_full.csv or vn_bctn_2021_2025.zip.")
    def content_url(item):
        links = item.get("links") or {}
        key = item.get("key", "")
        return (
            links.get("content")
            or links.get("download")
            or item.get("download")
            or (f"https://zenodo.org/records/20949551/files/{key}?download=1" if key else None)
        )

    index_url = content_url(index_file)
    archive_url = content_url(archive_file)
    if not index_url or not archive_url:
        raise RuntimeError(
            "Zenodo metadata did not include downloadable URLs for the index and archive. "
            f"Index fields: {sorted(index_file)}; archive fields: {sorted(archive_file)}"
        )
    with urllib.request.urlopen(urllib.request.Request(index_url, headers=HEADERS), timeout=120) as response:
        index_bytes = response.read()

    index_rows = csv.DictReader(io.StringIO(index_bytes.decode("utf-8-sig")))
    selected = []
    for row in index_rows:
        filename = pick(row, ["filename", "file_name", "name"])
        ticker = pick(row, ["ticker", "symbol", "stock_code", "code"]).upper()
        if ticker not in BANKS:
            ticker = filename.split("_", 1)[0].upper()
        year = year_from(pick(row, ["year", "report_year", "fiscal_year"]) or filename)
        member = pick(row, ["path", "relative_path", "archive_path"])
        if not filename.lower().endswith(".pdf") or ticker not in BANKS or year not in YEARS:
            continue
        if not member:
            member = f"full_data/{ticker}/{filename}"
        selected.append((ticker, year, archive_url, {
            **row, "filename": filename, "zip_member": member, "source_url": archive_url,
        }))
    fallbacks = {
        ("STB", "2023"): "https://www.sacombank.com.vn/content/dam/sacombank/cf/nha-dau-tu/bao-cao-thuong-nien/bao-cao-thuong-nien-2023.pdf",
        ("SHB", "2023"): "https://www.shb.com.vn/BCTN2023/pdf/BCTN-SHB-2023.pdf",
    }
    present = {(ticker, year) for ticker, year, _, _ in selected}
    for (ticker, year), url in fallbacks.items():
        if (ticker, year) not in present:
            selected.append((ticker, year, url, {"filename": f"{ticker}_{year}_annual_report.pdf", "source_url": url}))
            print(f"{ticker} {year}: using official bank website fallback")
    size_gb = archive_file.get("size", 0) / (1024 ** 3)
    print(f"Zenodo index found {len(selected)} target reports; source ZIP is {size_gb:.1f} GB.")
    print("Downloading only matching PDF entries with HTTP byte ranges (not the whole ZIP).")
    return selected


def read_remote_member(archive_url, member):
    """Read a single ZIP member through HTTP Range; no full-file fallback."""
    try:
        from remotezip import RemoteZip
    except ImportError as exc:
        raise RuntimeError("Install the required package first: pip install remotezip") from exc
    archive = REMOTE_ARCHIVES.get(archive_url)
    if archive is None:
        archive = RemoteZip(archive_url)
        REMOTE_ARCHIVES[archive_url] = archive
        REMOTE_NAMES[archive_url] = archive.namelist()
    names = REMOTE_NAMES[archive_url]
    normalized = member.replace("\\", "/").lstrip("/").casefold()
    matches = [name for name in names if name.replace("\\", "/").lstrip("/").casefold() == normalized]
    if not matches:
        basename = normalized.rsplit("/", 1)[-1]
        matches = [name for name in names if name.casefold().rsplit("/", 1)[-1] == basename]
    if not matches:
        raise FileNotFoundError(f"Report was not found in the source ZIP: {member}")
    return archive.read(matches[0])


def load_csv_catalog(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    selected = []
    for row in rows:
        ticker = pick(row, ["ticker", "symbol", "stock_code", "code", "mã chứng khoán", "mã ck"]).upper()
        year = year_from(pick(row, ["year", "report_year", "fiscal_year", "năm"]))
        url = pick(row, ["url", "download_url", "file_url", "pdf_url", "link", "source_url"])
        if ticker in BANKS and year in YEARS and url.startswith(("https://", "http://")):
            selected.append((ticker, year, url, row))
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", nargs="?", help="Optional CSV with direct PDF URLs; omit for automatic Zenodo retrieval")
    parser.add_argument("--delay", type=float, default=0.5, help="pause between reports in seconds")
    args = parser.parse_args()
    if args.catalog:
        catalog_path = pathlib.Path(args.catalog).expanduser()
        if not catalog_path.is_absolute():
            catalog_path = pathlib.Path.cwd() / catalog_path
        if not catalog_path.is_file():
            raise SystemExit(f"Catalog not found: {catalog_path}\nRun without a catalog to retrieve reports from Zenodo:\n  python src/mine_annual_reports.py")
        selected = load_csv_catalog(catalog_path)
    else:
        try:
            selected = fetch_zenodo_reports()
        except Exception as exc:
            raise SystemExit(f"Could not retrieve the Zenodo catalog: {type(exc).__name__}: {exc}") from exc
    if not selected:
        raise SystemExit("No matching reports found for the five banks in 2023-2025.")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    manifest, seen = [], set()
    found = {(ticker, year) for ticker, year, _, _ in selected}
    for ticker, year, url, source in selected:
        if (ticker, year) in seen:
            continue
        seen.add((ticker, year))
        path = REPORT_DIR / f"{ticker}_{year}_annual_report.pdf"
        status, sha256, size = "downloaded", "", 0
        try:
            if path.exists():
                with path.open("rb") as existing:
                    valid_pdf = existing.read(5) == b"%PDF-"
                if not valid_pdf:
                    path.unlink()
            if not path.exists():
                if source.get("zip_member"):
                    payload = read_remote_member(url, source["zip_member"])
                else:
                    request = urllib.request.Request(url, headers=HEADERS)
                    with urllib.request.urlopen(request, timeout=60) as response:
                        payload = response.read()
                if not payload.startswith(b"%PDF"):
                    raise ValueError("Source entry is not a PDF")
                path.write_bytes(payload)
                time.sleep(max(0, args.delay))
            digest = hashlib.sha256()
            with path.open("rb") as pdf:
                for chunk in iter(lambda: pdf.read(1024 * 1024), b""):
                    digest.update(chunk)
            sha256, size = digest.hexdigest(), path.stat().st_size
        except Exception as exc:
            status = f"error: {type(exc).__name__}: {exc}"
            if path.exists() and path.stat().st_size == 0:
                path.unlink()
        text = get_text(path) if status == "downloaded" else None
        item = {
            "ticker": ticker, "bank": BANKS[ticker], "year": year,
            "url": source.get("source_url", url),
            "title": pick(source, ["title", "report_title", "name", "filename"]),
            "status": status, "file": path.relative_to(ROOT).as_posix() if status == "downloaded" else "",
            "bytes": size, "sha256": sha256,
            "text_status": "extracted" if text is not None else ("install pymupdf to extract" if status == "downloaded" else "not available"),
        }
        if text is not None:
            folded = text.casefold()
            item["keyword_counts"] = [
                {"term": term, "count": count}
                for term in KEYWORDS
                if (count := len(re.findall(re.escape(term.casefold()), folded)))
            ]
        manifest.append(item)
        print(f"{ticker} {year}: {status}")

    for ticker, bank in BANKS.items():
        for year in sorted(YEARS):
            if (ticker, year) not in found:
                manifest.append({"ticker": ticker, "bank": bank, "year": year, "url": "", "title": "", "status": "not found in source index", "file": "", "bytes": 0, "sha256": "", "text_status": "not available"})

    with (ROOT / "data" / "annual_reports_manifest.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        fields = ["ticker", "bank", "year", "url", "title", "status", "file", "bytes", "sha256", "text_status"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: item.get(key, "") for key in fields} for item in manifest)
    with (ROOT / "data" / "annual_report_keyword_counts.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        fields = ["ticker", "bank", "year", "file", "keyword", "count"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in manifest:
            for result in item.get("keyword_counts", []):
                writer.writerow({"ticker": item["ticker"], "bank": item["bank"], "year": item["year"], "file": item["file"], "keyword": result["term"], "count": result["count"]})
    for archive in REMOTE_ARCHIVES.values():
        archive.close()
    print(f"Manifest: data/annual_reports_manifest.csv ({len(manifest)} rows)")
    print("Keyword counts: data/annual_report_keyword_counts.csv")
    if "pymupdf" not in sys.modules:
        print("PDF text extraction unavailable. Install pymupdf to enable keyword counts.")


if __name__ == "__main__":
    main()
