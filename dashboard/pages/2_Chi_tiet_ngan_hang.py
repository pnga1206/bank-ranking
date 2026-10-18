import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

import utils as U  # noqa: E402

U.hero("Chi tiết từng ngân hàng", "Điểm tổng thể, cấp độ, điểm theo trụ cột/chỉ tiêu và so sánh với trung bình nhóm")
U.banner(U.DISCLAIMER, "warn")

rk, yr, ml = U.ranking_df().set_index("bank"), U.yearly_df(), U.metrics_df()

f1, f2 = st.columns([1, 1])
bank = f1.selectbox("Chọn ngân hàng", U.BANKS, format_func=lambda b: U.BANK_FULL[b])
period = f2.radio("Kỳ xem", ["Trung bình 2023–2025", "2023", "2024", "2025"], horizontal=True)
years = [2023, 2024, 2025] if period.startswith("Trung bình") else [int(period)]

ys = yr[(yr["bank"] == bank) & (yr["year"].isin(years)) & yr["score"].notna()]
score = ys["score"].mean() if len(ys) else np.nan
cov = yr[(yr["bank"] == bank) & (yr["year"].isin(years))]["coverage"].mean()
grp = yr[yr["year"].isin(years) & yr["score"].notna()].groupby("bank")["score"].mean()
rank_here = int(grp.rank(ascending=False, method="min").get(bank, 0)) if bank in grp.index else None
color = U.BANK_COLORS[bank]

c1, c2, c3, c4 = st.columns(4)
with c1:
    U.kpi("Tổng điểm", U.fmt(score), f"Trung bình nhóm: {U.fmt(grp.mean())}", color)
with c2:
    U.kpi("Cấp độ (quy ước)", U.level_of(score), "Dải 20 điểm/mức", color)
with c3:
    U.kpi("Thứ hạng", f"#{rank_here}/5" if rank_here else "—", "Theo kỳ đang chọn", color)
with c4:
    U.kpi("Độ phủ dữ liệu", f"{cov * 100:.0f}%", "Tỷ trọng chỉ tiêu có dữ liệu", color)
st.write("")

mm = U.metric_matrix(years)
mine, grp_avg = mm.loc[bank], mm.mean(axis=0)
labels = [U.METRICS[m][1] for m in U.METRICS]

left, right = st.columns([1.1, 1])
with left:
    st.markdown("#### Radar chỉ tiêu so với trung bình nhóm")
    fig = go.Figure()
    cats = labels + [labels[0]]
    g = list(grp_avg.values) + [grp_avg.values[0]]
    fig.add_trace(go.Scatterpolar(r=g, theta=cats, name="TB nhóm", mode="lines+markers",
                                  line=dict(color="#B7B0D0", width=2, dash="dot"), marker=dict(size=6)))
    v = list(mine.values) + [mine.values[0]]
    complete = not np.isnan(mine.values).any()
    fig.add_trace(go.Scatterpolar(r=v, theta=cats, name=U.BANK_FULL[bank], mode="lines+markers",
                                  fill="toself" if complete else "none", fillcolor=color.replace("#", "#") + "55" if complete else None,
                                  line=dict(color=color, width=3), marker=dict(size=9), connectgaps=False))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 100], gridcolor=U.LINE, tickfont=dict(size=10)),
                                 angularaxis=dict(gridcolor=U.LINE), bgcolor="rgba(255,255,255,.6)"))
    st.plotly_chart(U.style_fig(fig, 430), width="stretch")
    miss = [U.METRICS[m][1] for m in U.METRICS if np.isnan(mine[m])]
    if miss:
        U.banner("Chưa có dữ liệu cho: <b>" + ", ".join(miss) + "</b>. Các chỉ tiêu này để trống trên radar (không gán 0) và không chứng tỏ năng lực thấp.", "note")

with right:
    st.markdown("#### Điểm theo trụ cột DBI tham chiếu")
    pm = U.pillar_matrix(years)
    pv = pm.loc[bank]
    fig = go.Figure()
    fig.add_trace(go.Bar(y=U.PILLARS, x=pm.mean(axis=0).reindex(U.PILLARS), orientation="h", name="TB nhóm",
                         marker=dict(color="#DAD5EA")))
    fig.add_trace(go.Bar(y=U.PILLARS, x=pv.reindex(U.PILLARS), orientation="h", name=U.BANK_FULL[bank],
                         marker=dict(color=color), text=[U.fmt(x) if not np.isnan(x) else "chưa có DL" for x in pv.reindex(U.PILLARS)],
                         textposition="outside", cliponaxis=False))
    fig.update_layout(barmode="group")
    fig.update_xaxes(range=[0, 110])
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(U.style_fig(fig, 430), width="stretch")

st.markdown("#### Điểm từng chỉ tiêu")
rows = []
mlb = ml[(ml["bank"] == bank) & (ml["year"].isin(years))]
for m, (full, short, pillar) in U.METRICS.items():
    g = mlb[mlb["metric"] == m]
    if g.empty:
        rows.append({"Chỉ tiêu": full, "Trụ cột": pillar, "Trọng số (%)": U.weights()[m], "Điểm (0–100)": None,
                     "Giá trị gốc": "—", "Đóng góp": None})
    else:
        unit = g["unit"].iloc[0] if "unit" in g and isinstance(g["unit"].iloc[0], str) else ""
        vals = "; ".join(f"{int(r.year)}: {r.value:g}" for r in g.sort_values("year").itertuples())
        rows.append({"Chỉ tiêu": full, "Trụ cột": pillar, "Trọng số (%)": U.weights()[m], "Điểm (0–100)": g["score"].mean(),
                     "Giá trị gốc": f"{vals} {unit}".strip(), "Đóng góp": g["contribution"].mean()})
tbl = pd.DataFrame(rows)
st.dataframe(tbl, hide_index=True, width="stretch", column_config={
    "Điểm (0–100)": st.column_config.ProgressColumn("Điểm (0–100)", min_value=0, max_value=100, format="%.1f"),
    "Đóng góp": st.column_config.NumberColumn("Đóng góp TB (điểm)", format="%.1f"),
    "Trọng số (%)": st.column_config.NumberColumn(format="%d"),
})
st.caption("“Đóng góp” là phần điểm chỉ tiêu đóng góp vào điểm năm (sau khi chuẩn hóa lại trọng số theo chỉ tiêu có dữ liệu); khi xem nhiều năm là giá trị trung bình.")

st.markdown("#### Diễn biến theo năm")
a, b = st.columns([1, 1])
with a:
    s = yr[yr["bank"] == bank].sort_values("year")
    fig = go.Figure(go.Bar(x=s["year"].astype(str), y=s["score"], marker=dict(color=color), text=[U.fmt(x) for x in s["score"]],
                           textposition="outside", cliponaxis=False,
                           customdata=s["coverage"], hovertemplate="%{x}: %{y:.1f}<br>Độ phủ %{customdata:.0%}<extra></extra>"))
    gm = yr.dropna(subset=["score"]).groupby("year")["score"].mean()
    fig.add_trace(go.Scatter(x=[str(y) for y in gm.index], y=gm.values, mode="lines+markers", name="TB nhóm",
                             line=dict(color="#9B7FE6", dash="dot")))
    fig.update_yaxes(range=[0, 105], title="Điểm")
    st.plotly_chart(U.style_fig(fig, 320, legend=False), width="stretch")
with b:
    s2 = s.copy()
    s2["Cấp độ"] = s2["score"].map(U.level_of)
    s2["Độ phủ"] = s2["coverage"]
    st.dataframe(s2[["year", "score", "Cấp độ", "Độ phủ"]].rename(columns={"year": "Năm", "score": "Điểm"}), hide_index=True,
                 width="stretch", column_config={
                     "Điểm": st.column_config.NumberColumn(format="%.1f"),
                     "Độ phủ": st.column_config.ProgressColumn(min_value=0, max_value=1, format="percent"),
                     "Năm": st.column_config.NumberColumn(format="%d")})
