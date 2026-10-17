"""Tiện ích dùng chung cho dashboard BXH chuyển đổi số ngân hàng.

Nguyên tắc: dashboard CHỈ ĐỌC dữ liệu trong thư mục data/ (scores.json, evidence*.csv, news_2026.csv ...)
và tự tính mọi bảng/biểu đồ; không hard-code điểm. Khi chạy lại src/scoring.py hoặc sửa evidence.csv,
dashboard tự cập nhật.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# ----------------------------------------------------------------------------- cấu hình hiển thị
BANKS = ["VCB", "VietinBank", "SHB", "Sacombank", "Nam A Bank"]
BANK_FULL = {
    "VCB": "Vietcombank", "VietinBank": "VietinBank", "SHB": "SHB",
    "Sacombank": "Sacombank", "Nam A Bank": "Nam A Bank",
}
BANK_COLORS = {
    "VCB": "#6FA8DC", "VietinBank": "#EE8FB0", "SHB": "#F2B66D",
    "Sacombank": "#76CBA8", "Nam A Bank": "#A98BEA",
}
INK, MUTED, LINE = "#3B3558", "#7A7597", "#E6E0F5"
FONT = "Be Vietnam Pro, Segoe UI, Roboto, sans-serif"

# metric: (nhãn đầy đủ, nhãn ngắn, trụ cột DBI tham chiếu)
METRICS = {
    "tx_share": ("Tỷ trọng giao dịch qua kênh số", "Giao dịch số", "Khách hàng"),
    "users_m": ("Người dùng số hoạt động (triệu)", "Người dùng số", "Khách hàng"),
    "ops_pct": ("Nghiệp vụ trọng yếu hoàn toàn trên kênh số", "Nghiệp vụ số", "Vận hành"),
    "milestones": ("Mốc sản phẩm/nền tảng số trong năm", "Mốc công nghệ", "Công nghệ"),
    "strategy": ("Chiến lược CĐS chính thức & mức định lượng", "Chiến lược CĐS", "Chiến lược"),
    "recognition": ("Giải thưởng CĐS độc lập", "Ghi nhận bên thứ ba", "Ghi nhận bên thứ ba"),
}
PILLARS = ["Khách hàng", "Vận hành", "Công nghệ", "Chiến lược", "Ghi nhận bên thứ ba"]

# Quy ước hiển thị cấp độ 1–5 theo dải điểm 0–100 (không phải cấp độ DBI chính thức)
LEVELS = [
    (0, 20, "Mức 1", "#F9D5DA"), (20, 40, "Mức 2", "#FBE3CF"), (40, 60, "Mức 3", "#FFF1C9"),
    (60, 80, "Mức 4", "#D6EFE2"), (80, 100.01, "Mức 5", "#CFE5F8"),
]

AUDIT_LABEL = {
    "needs_second_independent_source": "Cần thêm nguồn độc lập đối chiếu",
    "one_numeric_report_corroboration_only; needs_third_source": "Có 1 trích đoạn BCTN khớp số; cần thêm nguồn",
}
MATCH_LABEL = {
    "score input; definition requires review": "Nguồn đầu vào của điểm; cần rà soát định nghĩa",
    "supports_topic_only; does_not_verify_score": "Chỉ liên quan chủ đề; không xác minh được điểm",
    "corroborates_numeric_value": "Khớp số liệu",
}
KIND_LABEL = {"reported": "Số liệu công bố", "rubric": "Chấm theo rubric"}
ROLE_LABEL = {
    "original_score_source": "Nguồn dùng chấm điểm",
    "annual_report_candidate_excerpt": "Trích đoạn BCTN (đối chiếu)",
}

SCENARIOS = {
    "base": "Cơ sở: bỏ chỉ tiêu thiếu khỏi mẫu số, TB các năm",
    "y2025": "Chỉ xét năm 2025",
    "cov50": "Chỉ xét các năm có độ phủ ≥ 50%",
    "equal": "Trọng số bằng nhau giữa các chỉ tiêu",
    "reported": "Chỉ dùng số liệu công bố (bỏ rubric)",
    "zero": "Thiếu dữ liệu = 0 điểm (quy tắc thận trọng)",
}


def level_of(score: float | None) -> str:
    if score is None or pd.isna(score):
        return "—"
    for lo, hi, name, _ in LEVELS:
        if lo <= score < hi:
            return name
    return LEVELS[-1][2]


def level_color(score: float | None) -> str:
    if score is None or pd.isna(score):
        return "#EEEAF7"
    for lo, hi, _, color in LEVELS:
        if lo <= score < hi:
            return color
    return LEVELS[-1][3]


# ----------------------------------------------------------------------------- đọc dữ liệu
def _mtime(name: str) -> float:
    p = DATA / name
    return p.stat().st_mtime if p.exists() else 0.0


@st.cache_data(show_spinner=False)
def _read_json(name: str, mtime: float) -> dict:
    with open(DATA / name, encoding="utf-8-sig") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def _read_csv(name: str, mtime: float) -> pd.DataFrame:
    # Text snippets contain quoted Vietnamese report excerpts; use pandas' Python
    # parser for this small file to avoid C-parser allocation failures on Windows.
    engine = "python" if name == "annual_report_snippets.csv" else "c"
    return pd.read_csv(DATA / name, encoding="utf-8-sig", engine=engine)


def load_scores() -> dict:
    return _read_json("scores.json", _mtime("scores.json"))


def load_csv(name: str) -> pd.DataFrame:
    if not (DATA / name).exists():
        return pd.DataFrame()
    return _read_csv(name, _mtime(name))


def weights() -> dict:
    return load_scores()["weights"]


def ranking_df() -> pd.DataFrame:
    rows = []
    for b, d in load_scores()["banks"].items():
        yrs = [v["score"] for v in d["yearly"].values() if v["score"] is not None]
        rows.append({
            "bank": b, "overall": d["overall"], "s2025": d["s2025"], "coverage": d["coverage"],
            "rank": d["rank"], "rank_2025": d["rank_2025"], "n_years": len(yrs),
        })
    return pd.DataFrame(rows)


def yearly_df() -> pd.DataFrame:
    rows = []
    for b, d in load_scores()["banks"].items():
        for y, v in d["yearly"].items():
            rows.append({"bank": b, "year": int(y), "score": v["score"], "coverage": v["coverage"]})
    return pd.DataFrame(rows)


def metrics_df() -> pd.DataFrame:
    """Dạng dài: bank, year, metric, value, score, contribution, weight, kind, pillar."""
    sc = load_scores()
    w = sc["weights"]
    rows = []
    for b, d in sc["banks"].items():
        for y, v in d["yearly"].items():
            for m, x in v["metrics"].items():
                rows.append({"bank": b, "year": int(y), "metric": m, "value": x["value"],
                             "score": x["score"], "contribution": x["contribution"], "weight": w[m]})
    df = pd.DataFrame(rows)
    ev = load_csv("evidence.csv")
    if not ev.empty:
        ev = ev[ev["scored"] == 1][["bank", "year", "metric", "kind", "unit"]]
        df = df.merge(ev, on=["bank", "year", "metric"], how="left")
    df["pillar"] = df["metric"].map(lambda m: METRICS[m][2])
    return df


def metric_matrix(years: list[int] | None = None) -> pd.DataFrame:
    """Ma trận ngân hàng × chỉ tiêu: điểm TB (0–100) các năm có dữ liệu; NaN = chưa có dữ liệu."""
    ml = metrics_df()
    if years:
        ml = ml[ml["year"].isin(years)]
    pv = ml.pivot_table(index="bank", columns="metric", values="score", aggfunc="mean")
    return pv.reindex(index=BANKS, columns=list(METRICS))


def pillar_matrix(years: list[int] | None = None) -> pd.DataFrame:
    """Điểm theo trụ cột: trung bình có trọng số các chỉ tiêu có dữ liệu trong trụ cột."""
    ml = metrics_df()
    if years:
        ml = ml[ml["year"].isin(years)]
    out = {}
    for (b, y, p), g in ml.groupby(["bank", "year", "pillar"]):
        out[(b, y, p)] = np.average(g["score"], weights=g["weight"])
    s = pd.Series(out, name="score").rename_axis(["bank", "year", "pillar"]).reset_index()
    pv = s.pivot_table(index="bank", columns="pillar", values="score", aggfunc="mean")
    return pv.reindex(index=BANKS, columns=PILLARS)


def audit_df() -> pd.DataFrame:
    a = load_csv("evidence_audit_summary.csv")
    if not a.empty:
        a["audit_vi"] = a["audit_status"].map(AUDIT_LABEL).fillna(a["audit_status"])
    return a


def evidence_table() -> pd.DataFrame:
    ev = load_csv("evidence.csv").copy()
    au = audit_df()
    if not au.empty:
        ev = ev.merge(au[["bank", "year", "metric", "audit_status", "audit_vi", "report_excerpt_count",
                          "numeric_corroboration_count", "topic_only_excerpt_count"]],
                      on=["bank", "year", "metric"], how="left")
    sc = metrics_df()[["bank", "year", "metric", "score", "weight"]]
    ev = ev.merge(sc, on=["bank", "year", "metric"], how="left")
    ev["metric_label"] = ev["metric"].map(lambda m: METRICS[m][1])
    ev["pillar"] = ev["metric"].map(lambda m: METRICS[m][2])
    ev["kind_vi"] = ev["kind"].map(KIND_LABEL).fillna(ev["kind"])
    ev["in_score"] = ev["scored"].map({1: "Có", 0: "Không"})
    ev["flag"] = np.where(ev["audit_status"].notna(), "⚠ Chưa đủ nguồn độc lập", "")
    ev.loc[ev["scored"] == 0, "flag"] = "Không tính điểm (khác định nghĩa)"
    return ev


# ----------------------------------------------------------------------------- phân tích độ nhạy
def scenario_scores() -> pd.DataFrame:
    """Điểm tổng thể của 5 ngân hàng theo từng phương án xử lý thiếu dữ liệu / cách tính."""
    ml, yr, w = metrics_df(), yearly_df(), weights()
    res = {}
    base = yr.dropna(subset=["score"]).groupby("bank")["score"].mean()
    res["base"] = base
    res["y2025"] = yr[yr["year"] == 2025].set_index("bank")["score"]
    res["cov50"] = yr[(yr["coverage"] >= 0.5) & yr["score"].notna()].groupby("bank")["score"].mean()
    eq = ml.groupby(["bank", "year"])["score"].mean().groupby("bank").mean()
    res["equal"] = eq
    rep = ml[ml["kind"] == "reported"]
    rep_year = rep.groupby(["bank", "year"]).apply(lambda g: np.average(g["score"], weights=g["weight"]),
                                                   include_groups=False)
    res["reported"] = rep_year.groupby("bank").mean()
    tot_w = float(sum(w.values()))
    zero_year = ml.groupby(["bank", "year"]).apply(lambda g: (g["score"] * g["weight"]).sum() / tot_w,
                                                   include_groups=False)
    # năm không có chỉ tiêu nào vẫn tính là 0 điểm
    full = pd.MultiIndex.from_product([BANKS, [2023, 2024, 2025]], names=["bank", "year"])
    zero_year = zero_year.reindex(full).fillna(0.0)
    res["zero"] = zero_year.groupby("bank").mean()
    df = pd.DataFrame(res).reindex(BANKS)
    return df.round(1)


def scenario_ranks(scores: pd.DataFrame) -> pd.DataFrame:
    return scores.rank(ascending=False, method="min")


# ----------------------------------------------------------------------------- giao diện
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stMarkdown, .stDataFrame { font-family: 'Be Vietnam Pro', 'Segoe UI', sans-serif; }
.stApp { background: linear-gradient(160deg, #F8F6FF 0%, #F3F8FF 55%, #FFF7F5 100%); }
.block-container { padding-top: 2.2rem; max-width: 1250px; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #EFE9FD 0%, #E7F1FC 100%); border-right: 1px solid #E2DBF4; }
h1, h2, h3, h4 { color: #3B3558; letter-spacing: -0.01em; }
.hero { background: linear-gradient(120deg, #E9E0FB 0%, #DCEBFB 55%, #FBE4EC 100%); border-radius: 22px;
  padding: 26px 30px; margin-bottom: 16px; border: 1px solid #E2DBF4; box-shadow: 0 6px 22px rgba(155,127,230,.12); }
.hero h1 { margin: 0 0 4px 0; font-size: 1.75rem; }
.hero p { margin: 0; color: #5C5780; font-size: .97rem; }
.banner { border-radius: 14px; padding: 12px 16px; margin: 6px 0 16px 0; font-size: .9rem; line-height: 1.5; }
.banner.warn { background: #FFF4DE; border: 1px solid #F6DDA8; color: #6B5320; }
.banner.info { background: #E8F1FD; border: 1px solid #C9DDF5; color: #34507A; }
.banner.note { background: #F1ECFC; border: 1px solid #DDD3F4; color: #4D4377; }
.kpi { background: #fff; border-radius: 18px; padding: 16px 18px; border: 1px solid #EDE8F8; border-left: 6px solid var(--accent);
  box-shadow: 0 4px 16px rgba(120,100,180,.08); height: 100%; }
.kpi-label { color: #7A7597; font-size: .8rem; font-weight: 500; text-transform: uppercase; letter-spacing: .04em; }
.kpi-value { color: #3B3558; font-size: 1.7rem; font-weight: 700; margin: 4px 0 2px 0; line-height: 1.2; }
.kpi-sub { color: #8B86A6; font-size: .82rem; }
.card { background: #fff; border-radius: 18px; padding: 16px 18px; border: 1px solid #EDE8F8; box-shadow: 0 4px 16px rgba(120,100,180,.07); margin-bottom: 10px; }
.rank-row { display: flex; align-items: center; gap: 14px; padding: 12px 14px; background: #fff; border-radius: 16px;
  border: 1px solid #EDE8F8; margin-bottom: 8px; box-shadow: 0 3px 12px rgba(120,100,180,.06); }
.rank-no { width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-weight: 700; color: #3B3558; flex: none; }
.rank-name { font-weight: 600; color: #3B3558; }
.rank-meta { color: #8B86A6; font-size: .8rem; }
.rank-score { margin-left: auto; text-align: right; font-weight: 700; font-size: 1.25rem; color: #3B3558; }
.badge { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: .75rem; font-weight: 600; color: #3B3558; }
.bar-bg { background: #EFEAFB; border-radius: 999px; height: 7px; width: 120px; margin-top: 5px; }
.bar-fg { height: 7px; border-radius: 999px; background: linear-gradient(90deg, #B9A5F0, #8FC1F0); }
.news { background: #fff; border-radius: 14px; padding: 12px 14px; border: 1px solid #EDE8F8; margin-bottom: 8px; }
.news a { color: #5B6FD1; text-decoration: none; font-weight: 600; }
.news .d { color: #8B86A6; font-size: .78rem; }
.news .n { color: #8A6A1F; font-size: .8rem; }
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] { background: #F1ECFC; border-radius: 12px 12px 0 0; padding: 8px 16px; }
.stTabs [aria-selected="true"] { background: #fff; color: #5B45B0; font-weight: 600; }
footer { visibility: hidden; }
.footer-note { color: #9892B3; font-size: .78rem; text-align: center; margin-top: 28px; }
</style>
"""


def setup_app():
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str):
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def banner(text: str, kind: str = "warn"):
    st.markdown(f'<div class="banner {kind}">{text}</div>', unsafe_allow_html=True)


DISCLAIMER = ("<b>Lưu ý phương pháp:</b> đây là bảng xếp hạng nghiên cứu của nhóm, tham khảo khung DBI doanh nghiệp lớn, "
              "dựa trên dữ liệu công khai — <b>không phải xếp hạng chính thức của Ngân hàng Nhà nước</b>. "
              "Nhiều chỉ tiêu hiện <b>chưa đủ nguồn độc lập để đối chiếu</b>, vì vậy điểm số chưa được xem là đã kiểm chứng đầy đủ.")


def kpi(label: str, value: str, sub: str = "", accent: str = "#A98BEA"):
    st.markdown(f'<div class="kpi" style="--accent:{accent}"><div class="kpi-label">{label}</div>'
                f'<div class="kpi-value">{value}</div><div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)


def badge(text: str, color: str) -> str:
    return f'<span class="badge" style="background:{color}">{text}</span>'


def level_badge(score) -> str:
    return badge(level_of(score), level_color(score))


def style_fig(fig: go.Figure, height: int = 380, legend: bool = True) -> go.Figure:
    fig.update_layout(
        height=height, template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,.65)",
        font=dict(family=FONT, color=INK, size=13), margin=dict(l=10, r=10, t=40, b=10), showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hoverlabel=dict(font_family=FONT),
    )
    fig.update_xaxes(gridcolor=LINE, zeroline=False)
    fig.update_yaxes(gridcolor=LINE, zeroline=False)
    return fig


def fmt(x, nd: int = 1, suffix: str = "") -> str:
    return "—" if x is None or pd.isna(x) else f"{x:.{nd}f}{suffix}"


def footer():
    st.markdown('<div class="footer-note">BXH nghiên cứu của nhóm tham khảo DBI · Dữ liệu: BCTN 2023–2025 và nguồn công khai · '
                'Tin 2026 chỉ dùng để cập nhật, không tham gia chấm điểm</div>', unsafe_allow_html=True)
