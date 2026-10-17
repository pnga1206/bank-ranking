import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

import utils as U  # noqa: E402

U.hero("Gap Analysis — khoảng cách đến cấp độ mục tiêu",
       "Xác định chỉ tiêu/ngân hàng có khoảng cách lớn để làm cơ sở cho hàm ý và lộ trình (Chương 5–6)")
U.banner(U.DISCLAIMER, "warn")

yr, w = U.yearly_df(), U.weights()
f1, f2, f3 = st.columns([1.1, 1.2, 1.2])
period = f1.radio("Kỳ xem", ["Năm 2025", "Trung bình 2023–2025"], horizontal=False)
years = [2025] if period == "Năm 2025" else [2023, 2024, 2025]
level_pick = f2.selectbox("Cấp độ mục tiêu", ["Mức 3 (40 điểm)", "Mức 4 (60 điểm)", "Mức 5 (80 điểm)", "Tùy chỉnh"], index=2)
preset = {"Mức 3 (40 điểm)": 40, "Mức 4 (60 điểm)": 60, "Mức 5 (80 điểm)": 80}
target = preset.get(level_pick) or f3.slider("Điểm mục tiêu", 40, 100, 80, 5)
if level_pick != "Tùy chỉnh":
    f3.metric("Điểm mục tiêu", f"{target}")

# ---- gap tổng thể từng ngân hàng
cur = yr[yr["year"].isin(years) & yr["score"].notna()].groupby("bank")["score"].mean().reindex(U.BANKS)
gap = (target - cur).clip(lower=0)

st.markdown("#### Khoảng cách tổng điểm tới mục tiêu")
fig = go.Figure()
fig.add_trace(go.Bar(y=U.BANKS, x=[target] * 5, orientation="h", marker=dict(color="#EFEAFB"), name=f"Mục tiêu ({target})", hoverinfo="skip"))
fig.add_trace(go.Bar(y=U.BANKS, x=cur.values, orientation="h", width=0.35, name="Điểm hiện tại",
                     marker=dict(color=[U.BANK_COLORS[b] for b in U.BANKS]),
                     text=[f"{v:.1f}" for v in cur.values], textposition="inside"))
fig.add_vline(x=target, line_color="#9B7FE6", line_width=3)
for b, g_ in gap.items():
    fig.add_annotation(x=target + 1, y=b, text=("Đạt mục tiêu" if g_ == 0 else f"Còn thiếu {g_:.1f}"), showarrow=False,
                       xanchor="left", font=dict(size=12, color=U.MUTED))
fig.update_layout(barmode="overlay")
fig.update_xaxes(range=[0, max(105, target + 25)], title="Điểm")
fig.update_yaxes(autorange="reversed")
st.plotly_chart(U.style_fig(fig, 340), width="stretch")

# ---- gap theo chỉ tiêu
mm = U.metric_matrix(years)
gm = (target - mm).clip(lower=0)


def zone(g):
    if np.isnan(g):
        return "Chưa có dữ liệu"
    return "Đỏ" if g >= 40 else "Cam" if g >= 20 else "Xanh"


st.markdown("#### Bản đồ khoảng cách: chỉ tiêu × ngân hàng")
z = gm.T.values
text = [["Chưa có DL" if np.isnan(v) else f"{v:.0f}" for v in row] for row in z]
fig = go.Figure(go.Heatmap(z=z, x=U.BANKS, y=[U.METRICS[m][1] for m in mm.columns], zmin=0, zmax=60, text=text, texttemplate="%{text}",
                           colorscale=[[0, "#D5F0E3"], [0.33, "#FFF1C9"], [0.66, "#FBD9B8"], [1, "#F5B5BF"]], xgap=4, ygap=4,
                           hoverongaps=False, colorbar=dict(title="Gap"), hovertemplate="%{x} · %{y}<br>Thiếu %{z:.1f} điểm<extra></extra>"))
fig.update_yaxes(autorange="reversed")
fig.update_xaxes(side="top")
st.plotly_chart(U.style_fig(fig, 380, legend=False), width="stretch")
st.caption("Vùng **đỏ**: thiếu ≥ 40 điểm · **cam**: 20–40 · **xanh**: < 20. Ô “Chưa có DL” là khoảng trống dữ liệu công khai, chưa thể kết luận là điểm yếu.")

# ---- bảng ưu tiên
st.markdown("#### Bảng ưu tiên đầu tư theo chỉ tiêu")
rows = []
for m in mm.columns:
    avail = mm[m].dropna()
    g_avg = gm[m].dropna().mean() if len(avail) else np.nan
    rows.append({"Chỉ tiêu": U.METRICS[m][0], "Trụ cột": U.METRICS[m][2], "Trọng số (%)": w[m],
                 "Điểm TB nhóm": avail.mean() if len(avail) else np.nan, "Gap TB": g_avg,
                 "Chỉ số ưu tiên": (g_avg * w[m] / 100) if not np.isnan(g_avg) else np.nan,
                 "Số NH có dữ liệu": f"{len(avail)}/5", "Vùng": zone(g_avg)})
pr = pd.DataFrame(rows).sort_values("Chỉ số ưu tiên", ascending=False).reset_index(drop=True)
pr.insert(0, "Ưu tiên", range(1, len(pr) + 1))
st.dataframe(pr, hide_index=True, width="stretch", column_config={
    "Điểm TB nhóm": st.column_config.NumberColumn(format="%.1f"),
    "Gap TB": st.column_config.NumberColumn(format="%.1f"),
    "Chỉ số ưu tiên": st.column_config.ProgressColumn("Chỉ số ưu tiên", min_value=0, max_value=max(1.0, float(pr["Chỉ số ưu tiên"].max() or 1)), format="%.1f"),
    "Trọng số (%)": st.column_config.NumberColumn(format="%d")})
st.caption("Chỉ số ưu tiên = Gap trung bình × trọng số chỉ tiêu ÷ 100: kết hợp (1) điểm thấp, (2) khoảng cách tới mục tiêu và (3) mức ảnh hưởng (trọng số) — ba căn cứ ưu tiên ở mục 6.1.")

st.markdown("#### Ưu tiên theo từng ngân hàng")
bank = st.selectbox("Chọn ngân hàng", U.BANKS, format_func=lambda b: U.BANK_FULL[b])
rows = []
for m in mm.columns:
    s, g_ = mm.loc[bank, m], gm.loc[bank, m]
    rows.append({"Chỉ tiêu": U.METRICS[m][0], "Điểm hiện tại": s, "Gap tới mục tiêu": g_, "Trọng số (%)": w[m],
                 "Chỉ số ưu tiên": (g_ * w[m] / 100) if not np.isnan(g_) else np.nan,
                 "Vùng": zone(g_) if not np.isnan(g_) else "Chưa có dữ liệu công khai"})
bt = pd.DataFrame(rows).sort_values("Chỉ số ưu tiên", ascending=False, na_position="last")
st.dataframe(bt, hide_index=True, width="stretch", column_config={
    "Điểm hiện tại": st.column_config.NumberColumn(format="%.1f"), "Gap tới mục tiêu": st.column_config.NumberColumn(format="%.1f"),
    "Chỉ số ưu tiên": st.column_config.NumberColumn(format="%.1f")})
