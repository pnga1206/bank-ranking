# Bank DX Ranking: data and research pipeline

This repository contains a research dataset on digital transformation for five Vietnamese banks (VCB, VietinBank/CTG, SHB, Sacombank/STB, and Nam A Bank/NAB), covering 2023-2025. It is a group research ranking informed by DBI, not an official ranking issued by the State Bank of Vietnam.

## Repository structure

- `data/evidence.csv`: observations currently used as scoring inputs, with bank, year, metric, value, and current source.
- `data/evidence_source_matrix.csv`: original sources and annual-report excerpts suggested for review. `match_status` distinguishes exact numeric corroboration from topic-only context.
- `data/evidence_audit_summary.csv`: review status for each bank/year/metric. Excerpts with different definitions are not treated as corroboration.
- `data/news_2026.csv`: collected related news items.
- `data/scores.json`: research ranking generated from `evidence.csv` and the current scoring weights.
- `data/annual_reports/`: 15 annual report PDFs (five banks x three years), about 195 MB.
- `data/annual_reports_manifest.csv`: source, filename, download status, and SHA-256 for each report.
- `data/annual_report_keyword_counts.csv`: keyword counts in the reports.
- `data/annual_report_snippets.csv`: short page-linked excerpts for manual review. These are search aids, not self-validating evidence.
- `data/report_catalog.csv`: optional CSV template for direct PDF URLs when running the miner with a custom catalog.
- `src/mine_annual_reports.py`: reads the Zenodo index, downloads matching PDFs (not the entire ZIP), and creates the manifest and keyword counts.
- `src/extract_report_snippets.py`: extracts page contexts from downloaded PDFs.
- `src/scoring.py` and `src/method.py`: scoring and research-method definitions; no dashboard is included.

The PDFs are annual reports from the banks distributed in a Zenodo BCTN dataset. The local copies came from the Zenodo mirror, and the manifest links to that mirror. Use the SHA-256 values in the manifest to check file integrity.

## Install and run

Python 3.10 or later is required. From the repository root:

```powershell
python -m pip install -r requirements.txt
python src/mine_annual_reports.py
python src/extract_report_snippets.py
python src/scoring.py
```

The miner needs an internet connection to read the Zenodo index. It downloads only missing target PDFs. To use a custom catalog, run `python src/mine_annual_reports.py data/report_catalog.csv`. The checked-in template has blank URLs and must be filled before use this way.

## Research limitations

Before comparing transaction shares, digital users, or automation rates, confirm scope (retail or whole bank), denominator, measurement period, consolidation basis, and metric definition. Definitions may differ by bank and year. The audit currently shows that many criteria still lack independent corroboration; do not present the ranking as fully verified or official.
