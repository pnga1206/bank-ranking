"""Chấm điểm chuyển đổi số ngân hàng 2023–2025 (khung tham khảo DBI doanh nghiệp lớn).

Điểm mỗi chỉ tiêu quy về 0–100, điểm năm = trung bình có trọng số các chỉ tiêu CÓ dữ liệu
(trọng số được chuẩn hoá lại), đồng thời báo độ phủ dữ liệu (coverage).
Tin 2026 KHÔNG đi vào file này.
"""
import csv
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
YEARS = [2023, 2024, 2025]
BANKS = ["VCB", "VietinBank", "SHB", "Sacombank", "Nam A Bank"]

# metric: (trụ cột DBI tham chiếu, trọng số, nhãn)
METRICS = {
    "tx_share":    ("Khách hàng", 30, "Tỷ trọng giao dịch qua kênh số"),
    "users_m":     ("Khách hàng", 25, "Người dùng số hoạt động (triệu)"),
    "ops_pct":     ("Vận hành", 15, "Nghiệp vụ trọng yếu hoàn toàn trên kênh số"),
    "milestones":  ("Công nghệ", 15, "Mốc sản phẩm/nền tảng số trong năm"),
    "strategy":    ("Chiến lược", 10, "Chiến lược CĐS chính thức & mức định lượng"),
    "recognition": ("Ghi nhận bên thứ ba", 5, "Giải thưởng CĐS độc lập"),
}


def norm(metric, v):
    if metric == "tx_share":      # 80% = mục tiêu NHNN (QĐ 810) -> 0 điểm; 100% -> 100
        return max(0.0, min(100.0, (v - 80) / 20 * 100))
    if metric == "users_m":       # chuẩn 18 triệu (mức cao nhất quan sát được)
        return min(v / 18, 1) * 100
    if metric == "ops_pct":
        return min(v, 100.0)
    if metric in ("milestones", "recognition"):  # tối đa 3 mốc/giải
        return min(v, 3) / 3 * 100
    if metric == "strategy":
        return float(v)
    raise ValueError(metric)


def load():
    with open(ROOT / "data" / "evidence.csv", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def year_score(rows):
    """rows: các dòng của 1 bank-năm (đã lọc scored=1)."""
    got = {r["metric"]: float(r["value"]) for r in rows if r["scored"] == "1"}
    wsum = sum(METRICS[m][1] for m in got)
    out = {"metrics": {}, "score": None, "coverage": round(wsum / 100, 2)}
    if not got:
        return out
    total = 0.0
    for m, v in got.items():
        s = norm(m, v)
        contrib = METRICS[m][1] * s / wsum
        total += contrib
        out["metrics"][m] = {"value": v, "score": round(s, 1), "contribution": round(contrib, 2)}
    out["score"] = round(total, 1)
    return out


def rank(values):
    order = sorted(values, key=lambda kv: -kv[1])
    return {k: i + 1 for i, (k, _) in enumerate(order)}


def main():
    rows = load()
    result = {"weights": {m: v[1] for m, v in METRICS.items()}, "banks": {}}
    for b in BANKS:
        yearly = {}
        for y in YEARS:
            sel = [r for r in rows if r["bank"] == b and int(r["year"]) == y]
            yearly[y] = year_score(sel)
        have = [yearly[y]["score"] for y in YEARS if yearly[y]["score"] is not None]
        cov = [yearly[y]["coverage"] for y in YEARS]
        result["banks"][b] = {
            "yearly": yearly,
            "overall": round(sum(have) / len(have), 1),
            "coverage": round(sum(cov) / len(cov), 2),
            "s2025": yearly[2025]["score"],
        }
    r_all = rank([(b, d["overall"]) for b, d in result["banks"].items()])
    r_25 = rank([(b, d["s2025"]) for b, d in result["banks"].items()])
    for b, d in result["banks"].items():
        d["rank"] = r_all[b]
        d["rank_2025"] = r_25[b]
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "scores.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    for b in sorted(result["banks"], key=lambda x: result["banks"][x]["rank"]):
        d = result["banks"][b]
        ys = " | ".join(f"{y}: {d['yearly'][y]['score']} (cov {d['yearly'][y]['coverage']})" for y in YEARS)
        print(f"#{d['rank']} {b:11s} overall {d['overall']:5.1f} cov {d['coverage']:.2f} rank2025 #{d['rank_2025']}  {ys}")


if __name__ == "__main__":
    main()
