"""Dashboard Streamlit: BXH chuyển đổi số ngân hàng 2023–2025.

Chạy:  streamlit run src/app.py
Cho phép đổi trọng số, chọn năm, và bật/tắt các dòng số liệu bị đánh dấu "không tính điểm".
"""
import pathlib
import sys

import altair as alt
import pandas as pd
import streamlit as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from method import method  # noqa: E402
from scoring import BANKS, METRICS, YEARS, norm  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
LABEL = {m: v[2] for m, v in METRICS.items()}

st.set_page_config(page_title="BXH chuyển đổi số ngân hàng", page_icon="🏦", layout="wide")


@st.cache_data
def load():
    ev = pd.read_csv(ROOT / "data" / "evidence.csv", encoding="utf-8-sig")
    news = pd.read_csv(ROOT / "data" / "news_2026.csv", encoding="utf-8-sig")
    return ev, news


ev, news = load()

# ---------------- Sidebar ----------------
st.sidebar.header("Thiết lập")
years = st.sidebar.multiselect("Năm tính điểm", YEARS, default=YEARS)
include_flagged = st.sidebar.checkbox(
    "Tính cả số liệu bị đánh dấu 'không tính điểm'", value=False,
    help="Gồm VietinBank 2025 (14 triệu người dùng) và Sacombank 2025 (6,8 triệu): nghi khác định nghĩa.")
st.sidebar.subheader("Trọng số chỉ tiêu")
weights = {m: st.sidebar.slider(LABEL[m], 0, 50, v[1], 5) for m, v in METRICS.items()}
tie_gap = st.sidebar.slider("Gộp 'nhóm ngang nhau' nếu chênh ≤ (điểm)", 0.0, 6.0, 3.0, 0.5)
st.sidebar.caption("Tin 2026 không tính điểm. Đây không phải điểm DBI chính thức.")

if not years or sum(weights.values()) == 0:
    st.warning("Chọn ít nhất 1 năm và 1 trọng số khác 0.")
    st.stop()

# ---------------- Tính điểm ----------------
d = ev[ev["year"].isin(years)].copy()
if not include_flagged:
    d = d[d["scored"] == 1]
d["norm"] = [norm(m, v) for m, v in zip(d["metric"], d["value"])]
d["w"] = d["metric"].map(weights)
d = d[d["w"] > 0]

yearly = []
contrib_rows = []
for (b, y), g in d.groupby(["bank", "year"]):
    wsum = g["w"].sum()
    yearly.append({"bank": b, "year": int(y), "score": (g["w"] * g["norm"]).sum() / wsum,
                   "coverage": wsum / sum(weights.values())})
    for _, r in g.iterrows():
        contrib_rows.append({"bank": b, "year": int(y), "metric": LABEL[r["metric"]],
                             "contribution": r["w"] * r["norm"] / wsum})
yearly = pd.DataFrame(yearly)
contrib = pd.DataFrame(contrib_rows)

board = (yearly.groupby("bank").agg(score=("score", "mean"), coverage=("coverage", "mean")).reset_index()
         .sort_values("score", ascending=False).reset_index(drop=True))
board["Hạng"] = board.index + 1
grp, g_id, prev = [], 0, None
for s in board["score"]:
    if prev is not None and prev - s > tie_gap:
        g_id += 1
    grp.append("ABCDE"[g_id])
    prev = s
board["Nhóm"] = grp
board["Độ tin cậy"] = board["coverage"].map(lambda c: "Khá" if c >= 0.7 else "Trung bình" if c >= 0.5 else "Thấp")

# ---------------- Giao diện ----------------
st.title("Bảng xếp hạng chuyển đổi số ngân hàng 2023–2025")
st.caption("VCB · VietinBank · SHB · Sacombank · Nam A Bank — khung tham khảo DBI doanh nghiệp lớn. "
           "Cập nhật 15/10/2026; tin 2026 không tính điểm.")

top = board.iloc[0]
c1, c2, c3 = st.columns(3)
c1.metric("Dẫn đầu", top["bank"], f"{top['score']:.1f} điểm")
c2.metric("Số nhóm ngang nhau", board["Nhóm"].nunique())
low = board[board["Độ tin cậy"] == "Thấp"]["bank"].tolist()
c3.metric("Độ phủ dữ liệu thấp", ", ".join(low) if low else "Không có")
if low:
    st.warning(f"Độ phủ dữ liệu dưới 50% với {', '.join(low)}: thứ hạng của các bank này kém tin cậy hơn.")

t1, t2, t3, t4, t5, t6 = st.tabs(["Xếp hạng", "Điểm theo chỉ tiêu", "Theo năm", "Minh chứng", "Tin 2026", "Phương pháp"])

with t1:
    show = board[["Hạng", "bank", "score", "Nhóm", "coverage", "Độ tin cậy"]].rename(
        columns={"bank": "Ngân hàng", "score": "Điểm TB", "coverage": "Độ phủ dữ liệu"})
    st.dataframe(
        show, hide_index=True, use_container_width=True,
        column_config={
            "Điểm TB": st.column_config.ProgressColumn("Điểm TB", min_value=0, max_value=100, format="%.1f"),
            "Độ phủ dữ liệu": st.column_config.NumberColumn(format="percent"),
        })
    bars = alt.Chart(board).mark_bar().encode(
        x=alt.X("score:Q", title="Điểm (0–100)", scale=alt.Scale(domain=[0, 100])),
        y=alt.Y("bank:N", sort=list(board["bank"]), title=None),
        color=alt.Color("Nhóm:N", legend=alt.Legend(title="Nhóm")),
        tooltip=["bank", alt.Tooltip("score:Q", format=".1f"), "Nhóm"])
    st.altair_chart(bars, use_container_width=True)
    st.caption("Các bank cùng nhóm chênh nhau không quá ngưỡng ở thanh bên: coi như ngang nhau, không nên đọc thứ hạng cứng.")

with t2:
    avg = contrib.groupby(["bank", "metric"])["contribution"].sum().reset_index()
    nyears = yearly.groupby("bank")["year"].nunique()
    avg["contribution"] = avg.apply(lambda r: r["contribution"] / nyears[r["bank"]], axis=1)
    ch = alt.Chart(avg).mark_bar().encode(
        y=alt.Y("bank:N", sort=list(board["bank"]), title=None),
        x=alt.X("contribution:Q", title="Điểm đóng góp", stack="zero"),
        color=alt.Color("metric:N", title="Chỉ tiêu"),
        tooltip=["bank", "metric", alt.Tooltip("contribution:Q", format=".1f")])
    st.altair_chart(ch, use_container_width=True)
    st.caption("Thanh ngắn có thể do thiếu dữ liệu, không nhất thiết do làm kém.")

with t3:
    line = alt.Chart(yearly).mark_line(point=True).encode(
        x=alt.X("year:O", title="Năm"), y=alt.Y("score:Q", title="Điểm", scale=alt.Scale(domain=[40, 100])),
        color="bank:N", tooltip=["bank", "year", alt.Tooltip("score:Q", format=".1f"),
                                 alt.Tooltip("coverage:Q", format=".0%")])
    st.altair_chart(line, use_container_width=True)
    piv = d.pivot_table(index=["bank", "year"], columns="metric", values="value", aggfunc="first").rename(columns=LABEL)
    piv = piv.join(yearly.set_index(["bank", "year"])[["score", "coverage"]]).rename(
        columns={"score": "Điểm", "coverage": "Độ phủ"})
    st.dataframe(piv, use_container_width=True)
    st.caption("Ô trống = chưa tìm thấy số liệu công bố đáng tin cậy (không bị tính là 0).")

with t4:
    f1, f2, f3 = st.columns(3)
    fb = f1.multiselect("Ngân hàng", BANKS, default=BANKS)
    fy = f2.multiselect("Năm", YEARS, default=YEARS, key="ev_year")
    fm = f3.multiselect("Chỉ tiêu", list(LABEL), default=list(LABEL), format_func=LABEL.get)
    e = ev[ev["bank"].isin(fb) & ev["year"].isin(fy) & ev["metric"].isin(fm)].copy()
    e["metric"] = e["metric"].map(LABEL)
    e["scored"] = e["scored"].map({1: "có", 0: "KHÔNG"})
    e["kind"] = e["kind"].map({"reported": "số công bố", "rubric": "chấm theo thang"})
    st.dataframe(
        e[["bank", "year", "metric", "value", "unit", "note", "kind", "scored", "as_of", "source_title", "url"]],
        hide_index=True, use_container_width=True,
        column_config={"url": st.column_config.LinkColumn("Nguồn", display_text="mở"),
                       "note": st.column_config.TextColumn("Ghi chú", width="large")})
    st.download_button("Tải evidence.csv", (ROOT / "data" / "evidence.csv").read_bytes(), "evidence.csv", "text/csv")

with t5:
    st.info("Tin 2026 chỉ để tham khảo, không tính vào điểm.")
    for _, n in news.iterrows():
        st.markdown(f"**{n['bank']}** · {n['date']} — {n['headline']}  \n"
                    + (f"_{n['note']}_  \n" if isinstance(n["note"], str) and n["note"] else "")
                    + f"[Nguồn]({n['url']})")

with t6:
    st.markdown(method["dbi"], unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(method["rows"], columns=["Chỉ tiêu", "Trụ cột DBI tham chiếu", "Trọng số mặc định (%)", "Cách quy điểm 0–100"]),
                 hide_index=True, use_container_width=True)
    st.markdown("**Giới hạn quan trọng**")
    for lim in method["limits"]:
        st.markdown(f"- {lim}", unsafe_allow_html=True)
    st.markdown("**Nguồn khung DBI:** " + " · ".join(f"[{t}]({u})" for t, u in method["dbi_sources"]))

