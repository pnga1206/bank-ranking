import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

import utils as U  # noqa: E402

U.hero("So sánh giữa các ngân hàng", "Chọn 2–5 ngân hàng để so sánh tổng điểm, chỉ tiêu và trụ cột")
U.banner(U.DISCLAIMER, "warn")

yr = U.yearly_df()
f1, f2 = st.columns([1.4, 1])
sel = f1.multiselect("Ngân hàng (2–5)", U.BANKS, default=U.BANKS, format_func=lambda b: U.BANK_FULL[b])
period = f2.radio("Kỳ xem", ["Trung bình 2023–2025", "2023", "2024", "2025"], horizontal=True)
if len(sel) < 2:
    st.info("Vui lòng chọn ít nhất 2 ngân hàng để so sánh.")
    st.stop()
years = [2023, 2024, 2025] if period.startswith("Trung bình") else [int(period)]

# ---- tổng điểm
tot = yr[yr["year"].isin(years) & yr["score"].notna()].groupby("bank").agg(score=("score", "mean"), cov=("coverage", "mean")).reindex(sel)
tot["rank"] = tot["score"].rank(ascending=False, method="min").astype(int)
cols = st.columns(len(sel))
for c, b in zip(cols, sel):
    with c:
        U.kpi(U.BANK_FULL[b], U.fmt(tot.loc[b, "score"]), f"Hạng {tot.loc[b, 'rank']} · {U.level_of(tot.loc[b, 'score'])} · phủ {tot.loc[b, 'cov']:.0%}",
              U.BANK_COLORS[b])
st.write("")

a, b = st.columns(2)
with a:
    st.markdown("#### Tổng điểm theo năm")
    fig = go.Figure()
    for bk in sel:
        s = yr[(yr["bank"] == bk)].sort_values("year")
        fig.add_trace(go.Bar(x=s["year"].astype(str), y=s["score"], name=bk, marker=dict(color=U.BANK_COLORS[bk]),
                             text=[U.fmt(x) for x in s["score"]], textposition="outside", cliponaxis=False))
    fig.update_layout(barmode="group")
    fig.update_yaxes(range=[0, 105], title="Điểm")
    st.plotly_chart(U.style_fig(fig, 400), width="stretch")
with b:
    st.markdown("#### Radar chồng — các chỉ tiêu")
    mm = U.metric_matrix(years)
    labels = [U.METRICS[m][1] for m in U.METRICS]
    fig = go.Figure()
    for bk in sel:
        v = list(mm.loc[bk].values)
        fig.add_trace(go.Scatterpolar(r=v + [v[0]], theta=labels + [labels[0]], name=bk, mode="lines+markers",
                                      line=dict(color=U.BANK_COLORS[bk], width=3), marker=dict(size=8), connectgaps=False))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 100], gridcolor=U.LINE, tickfont=dict(size=10)),
                                 angularaxis=dict(gridcolor=U.LINE), bgcolor="rgba(255,255,255,.6)"))
    st.plotly_chart(U.style_fig(fig, 400), width="stretch")

st.markdown("#### Heatmap: chỉ tiêu × ngân hàng")
view = st.radio("Mức tổng hợp", ["Theo chỉ tiêu", "Theo trụ cột DBI tham chiếu"], horizontal=True)
mat = (U.metric_matrix(years) if view == "Theo chỉ tiêu" else U.pillar_matrix(years)).loc[sel]
ylabels = [U.METRICS[m][1] for m in mat.columns] if view == "Theo chỉ tiêu" else list(mat.columns)
z = mat.T.values
text = [["Chưa có DL" if np.isnan(v) else f"{v:.0f}" for v in row] for row in z]
fig = go.Figure(go.Heatmap(z=z, x=[U.BANK_FULL[b] for b in mat.index], y=ylabels, zmin=0, zmax=100,
                           colorscale=[[0, "#F9D5DA"], [0.5, "#FFF1C9"], [1, "#CFE5F8"]], text=text, texttemplate="%{text}",
                           xgap=4, ygap=4, colorbar=dict(title="Điểm"), hoverongaps=False,
                           hovertemplate="%{x} · %{y}<br>Điểm: %{z:.1f}<extra></extra>"))
fig.update_yaxes(autorange="reversed")
fig.update_xaxes(side="top")
st.plotly_chart(U.style_fig(fig, 90 + 52 * len(ylabels), legend=False), width="stretch")
st.caption("Ô trống “Chưa có DL” nghĩa là không có bằng chứng công khai đủ dùng cho chỉ tiêu đó trong kỳ đã chọn — không được hiểu là 0 điểm.")

st.markdown("#### Bảng so sánh chi tiết")
tab = mat.copy().round(1)
tab.columns = ylabels
tab.insert(0, "Tổng điểm", tot["score"].round(1))
tab.insert(1, "Hạng", tot["rank"])
tab.index = [U.BANK_FULL[b] for b in tab.index]
st.dataframe(tab.sort_values("Hạng"), width="stretch")
