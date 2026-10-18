import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

import utils as U  # noqa: E402

U.hero("Tổng quan xếp hạng chuyển đổi số ngân hàng",
       "Vietcombank · VietinBank · SHB · Sacombank · Nam A Bank — giai đoạn 2023–2025, tham khảo khung DBI doanh nghiệp lớn")
U.banner(U.DISCLAIMER, "warn")

rk, yr = U.ranking_df(), U.yearly_df()

mode = st.radio("Cách xếp hạng", ["Điểm trung bình 2023–2025", "Điểm năm 2025"], horizontal=True)
col, rcol = ("overall", "rank") if mode.startswith("Điểm trung bình") else ("s2025", "rank_2025")
df = rk.sort_values(rcol).reset_index(drop=True)

# ---- KPI
leader = df.iloc[0]
c1, c2, c3 = st.columns(3)
with c1:
    U.kpi("Dẫn đầu", U.BANK_FULL[leader["bank"]], f"{leader[col]:.1f} điểm · {U.level_of(leader[col])}", "#6FA8DC")
with c2:
    U.kpi("Điểm trung bình nhóm", f"{df[col].mean():.1f}", f"Khoảng cách top–cuối: {df[col].max() - df[col].min():.1f} điểm", "#A98BEA")
with c3:
    U.kpi("Độ phủ dữ liệu TB", f"{rk['coverage'].mean() * 100:.0f}%", "Tỷ trọng chỉ tiêu có dữ liệu (TB các năm)", "#76CBA8")

st.write("")
left, right = st.columns([1.15, 1])

with left:
    st.markdown("#### Xếp hạng 5 ngân hàng")
    d = df.sort_values(col)
    fig = go.Figure(go.Bar(
        x=d[col], y=d["bank"], orientation="h", marker=dict(color=[U.BANK_COLORS[b] for b in d["bank"]],
                                                           line=dict(color="#fff", width=1.5)),
        text=[f"{v:.1f}" for v in d[col]], textposition="outside", cliponaxis=False,
        customdata=d[["coverage", rcol]].values,
        hovertemplate="<b>%{y}</b><br>Điểm: %{x:.1f}<br>Hạng: %{customdata[1]}<br>Độ phủ: %{customdata[0]:.0%}<extra></extra>"))
    avg = df[col].mean()
    fig.add_vline(x=avg, line_dash="dash", line_color="#9B7FE6",
                  annotation_text=f"TB nhóm {avg:.1f}", annotation_position="top")
    fig.update_xaxes(range=[0, 105], title="Điểm (0–100)")
    st.plotly_chart(U.style_fig(fig, 360, legend=False), width="stretch")

with right:
    st.markdown("#### Bảng xếp hạng")
    medal = {1: "#F9E2A8", 2: "#E3E6EE", 3: "#F5D2B5"}
    for _, r in df.iterrows():
        n = int(r[rcol])
        cov = r["coverage"]
        st.markdown(
            f'<div class="rank-row"><div class="rank-no" style="background:{medal.get(n, "#EFEAFB")}">{n}</div>'
            f'<div><div class="rank-name">{U.BANK_FULL[r["bank"]]} {U.level_badge(r[col])}</div>'
            f'<div class="rank-meta">Độ phủ dữ liệu {cov:.0%}</div>'
            f'<div class="bar-bg"><div class="bar-fg" style="width:{cov * 100:.0f}%"></div></div></div>'
            f'<div class="rank-score">{r[col]:.1f}</div></div>', unsafe_allow_html=True)
    st.caption("Cấp độ 1–5 là quy ước hiển thị theo dải điểm (mỗi mức 20 điểm), không phải cấp độ DBI chính thức.")

st.markdown("#### Diễn biến điểm theo năm")
t1, t2 = st.columns([1.3, 1])
with t1:
    fig = go.Figure()
    for b in U.BANKS:
        s = yr[yr["bank"] == b].sort_values("year")
        fig.add_trace(go.Scatter(
            x=s["year"], y=s["score"], mode="lines+markers", name=b, line=dict(color=U.BANK_COLORS[b], width=3),
            marker=dict(size=10, line=dict(color="#fff", width=2)), customdata=s["coverage"],
            hovertemplate="<b>" + b + "</b><br>%{x}: %{y:.1f} điểm<br>Độ phủ: %{customdata:.0%}<extra></extra>"))
    fig.update_xaxes(dtick=1, title="Năm")
    fig.update_yaxes(title="Điểm", range=[40, 95])
    st.plotly_chart(U.style_fig(fig, 340), width="stretch")
with t2:
    pv = yr.pivot(index="bank", columns="year", values="coverage").reindex(U.BANKS)
    fig = go.Figure(go.Heatmap(
        z=pv.values, x=[str(c) for c in pv.columns], y=pv.index, zmin=0, zmax=1,
        colorscale=[[0, "#FADADD"], [0.5, "#FFF1C9"], [1, "#CDEBDD"]], text=[[f"{v:.0%}" for v in r] for r in pv.values],
        texttemplate="%{text}", showscale=False, xgap=3, ygap=3,
        hovertemplate="%{y} · %{x}<br>Độ phủ: %{z:.0%}<extra></extra>"))
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(title=dict(text="Độ phủ dữ liệu theo năm", font=dict(size=14)))
    st.plotly_chart(U.style_fig(fig, 340, legend=False), width="stretch")
st.caption("Điểm năm chỉ tính trên các chỉ tiêu có dữ liệu (trọng số được chuẩn hóa lại); độ phủ thấp nghĩa là điểm dựa trên ít chỉ tiêu hơn, cần đọc thận trọng.")

# ---- tin tức 2026
news = U.load_csv("news_2026.csv")
if not news.empty:
    st.markdown("#### Cập nhật 2026")
    U.banner("Tin tức 2026 chỉ để cập nhật bối cảnh, <b>không tham gia chấm điểm</b>. Một số mục là mục tiêu công bố, chưa phải kết quả.", "info")
    sel = st.multiselect("Lọc theo ngân hàng", U.BANKS, default=U.BANKS, key="news_f")
    n = news[news["bank"].isin(sel)].copy()
    n["date"] = n["date"].astype(str)
    n = n.sort_values("date", ascending=False)
    cols = st.columns(2)
    for i, (_, r) in enumerate(n.iterrows()):
        note = f'<div class="n">⚠ {r["note"]}</div>' if isinstance(r["note"], str) and r["note"] else ""
        with cols[i % 2]:
            st.markdown(f'<div class="news"><div class="d">{r["date"]} · {U.badge(r["bank"], U.BANK_COLORS.get(r["bank"], "#EEE"))}</div>'
                        f'<a href="{r["url"]}" target="_blank">{r["headline"]}</a>{note}</div>', unsafe_allow_html=True)

with st.expander("Phương pháp chấm điểm (tóm tắt)"):
    w = U.weights()
    mt = pd.DataFrame([{"Chỉ tiêu": U.METRICS[m][0], "Trụ cột DBI tham chiếu": U.METRICS[m][2], "Trọng số (%)": w[m]} for m in U.METRICS])
    st.dataframe(mt, hide_index=True, width="stretch")
    st.markdown("""
- Mỗi chỉ tiêu được quy về thang 0–100; điểm năm là trung bình có trọng số của **các chỉ tiêu có dữ liệu** (trọng số chuẩn hóa lại), kèm **độ phủ dữ liệu**.
- Điểm tổng thể là trung bình các năm có điểm. Dữ liệu thiếu **không** bị gán 0 ở phương án cơ sở; phương án thận trọng (thiếu = 0) được kiểm tra ở trang *Bằng chứng & độ nhạy*.
- Mốc sản phẩm, chiến lược và giải thưởng có yếu tố mã hóa thủ công theo rubric.
""")
