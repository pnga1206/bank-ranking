import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

import utils as U  # noqa: E402

U.hero("Bằng chứng & phân tích độ nhạy", "Tra cứu nguồn, trạng thái kiểm chứng và kiểm tra độ ổn định của thứ hạng")
U.banner(U.DISCLAIMER, "warn")

t_ev, t_sens, t_rep = st.tabs(["🔎 Bằng chứng", "📊 Độ nhạy xếp hạng", "📄 Trích đoạn BCTN"])

# =========================================================================== bằng chứng
with t_ev:
    ev = U.evidence_table()
    au = U.audit_df()
    n_need = int(ev["audit_status"].notna().sum())
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        U.kpi("Quan sát trong dữ liệu", str(len(ev)), f"{int((ev['scored'] == 1).sum())} dùng chấm điểm", "#A98BEA")
    with c2:
        U.kpi("Cần thêm nguồn đối chiếu", f"{n_need}", "Theo audit hiện tại", "#F2B66D")
    with c3:
        corro = int((au["numeric_corroboration_count"] > 0).sum()) if not au.empty else 0
        U.kpi("Có BCTN khớp số liệu", str(corro), "Số quan sát được đối chiếu số", "#76CBA8")
    with c4:
        U.kpi("Không tính điểm", str(int((ev["scored"] == 0).sum())), "Khác định nghĩa so với kỳ khác", "#EE8FB0")
    st.write("")

    f = st.columns(5)
    banks = f[0].multiselect("Ngân hàng", U.BANKS, default=U.BANKS)
    years = f[1].multiselect("Năm", [2023, 2024, 2025], default=[2023, 2024, 2025])
    pillars = f[2].multiselect("Trụ cột", U.PILLARS, default=U.PILLARS)
    metrics = f[3].multiselect("Tiêu chí", list(U.METRICS), default=list(U.METRICS), format_func=lambda m: U.METRICS[m][1])
    kinds = f[4].multiselect("Loại", list(U.KIND_LABEL), default=list(U.KIND_LABEL), format_func=lambda k: U.KIND_LABEL[k])
    g1, g2 = st.columns([1.2, 1])
    lo, hi = g1.slider("Mức điểm tiêu chí (0–100)", 0, 100, (0, 100))
    only_flag = g2.checkbox("Chỉ hiện quan sát có cờ cảnh báo (chưa đủ nguồn / không tính điểm)", value=False)

    d = ev[ev["bank"].isin(banks) & ev["year"].isin(years) & ev["pillar"].isin(pillars) & ev["metric"].isin(metrics) & ev["kind"].isin(kinds)]
    d = d[(d["score"].isna()) | ((d["score"] >= lo) & (d["score"] <= hi))]
    if only_flag:
        d = d[d["flag"] != ""]
    show = d[["bank", "year", "pillar", "metric_label", "value", "unit", "score", "kind_vi", "in_score", "flag", "note", "source_title", "url"]].copy()
    show.columns = ["Ngân hàng", "Năm", "Trụ cột", "Tiêu chí", "Giá trị", "Đơn vị", "Điểm (0–100)", "Loại", "Tính điểm", "Cờ", "Bằng chứng / ghi chú", "Nguồn", "Liên kết"]
    st.markdown(f"**{len(show)}** quan sát phù hợp bộ lọc")
    st.dataframe(show, hide_index=True, width="stretch", height=420, column_config={
        "Liên kết": st.column_config.LinkColumn("Liên kết", display_text="Mở nguồn"),
        "Điểm (0–100)": st.column_config.NumberColumn(format="%.1f"),
        "Giá trị": st.column_config.NumberColumn(format="%g"),
        "Năm": st.column_config.NumberColumn(format="%d"),
        "Bằng chứng / ghi chú": st.column_config.TextColumn(width="large"),
    })
    st.download_button("⬇ Tải bảng đang lọc (CSV)", show.to_csv(index=False).encode("utf-8-sig"), "bang_chung_loc.csv", "text/csv")

    st.markdown("##### Trạng thái kiểm chứng theo tiêu chí")
    if not au.empty:
        a = au.copy()
        a["Tiêu chí"] = a["metric"].map(lambda m: U.METRICS[m][1])
        sm = a.groupby("Tiêu chí").agg(**{"Số quan sát": ("metric", "size"),
                                          "Cần thêm nguồn": ("audit_status", lambda s: int(s.notna().sum())),
                                          "BCTN khớp số": ("numeric_corroboration_count", lambda s: int((s > 0).sum())),
                                          "BCTN chỉ liên quan chủ đề": ("topic_only_excerpt_count", lambda s: int((s > 0).sum()))}).reset_index()
        st.dataframe(sm, hide_index=True, width="stretch")
        st.caption("“BCTN chỉ liên quan chủ đề” là trích đoạn báo cáo thường niên cùng chủ đề nhưng không xác minh được con số/điểm.")

    st.markdown("##### Minh chứng chi tiết (nguồn gốc & trích đoạn)")
    sm_df = U.load_csv("evidence_source_matrix.csv")
    if not sm_df.empty:
        k1, k2, k3 = st.columns(3)
        b_ = k1.selectbox("Ngân hàng", U.BANKS, key="mb")
        y_ = k2.selectbox("Năm", [2023, 2024, 2025], index=2, key="my")
        m_ = k3.selectbox("Tiêu chí", list(U.METRICS), format_func=lambda m: U.METRICS[m][1], key="mm")
        sel = sm_df[(sm_df["bank"] == b_) & (sm_df["year"] == y_) & (sm_df["metric"] == m_)]
        if sel.empty:
            st.info("Chưa có dữ liệu minh chứng cho tổ hợp này (không có bằng chứng công khai trong bộ dữ liệu).")
        for _, r in sel.sort_values("source_no").iterrows():
            ok = r["match_status"] == "corroborates_numeric_value"
            page = f" · trang {int(r['page'])}" if pd.notna(r.get("page")) else ""
            with st.expander(f"Nguồn {int(r['source_no'])}: {U.ROLE_LABEL.get(r['source_role'], r['source_role'])}{page}"):
                st.markdown(f"**{r['source_title']}**")
                st.markdown(U.badge(U.MATCH_LABEL.get(r["match_status"], r["match_status"]), "#CDEBDD" if ok else "#FFF1C9"), unsafe_allow_html=True)
                st.markdown(f"> {r['excerpt']}")
                if isinstance(r["url"], str):
                    st.markdown(f"[Mở nguồn]({r['url']})")
                if isinstance(r.get("local_file"), str):
                    st.caption(f"File cục bộ: `{r['local_file']}`")
                st.caption(str(r["independence"]))

# =========================================================================== độ nhạy
with t_sens:
    U.banner("Kiểm tra xem thứ hạng có ổn định khi đổi cách xử lý dữ liệu thiếu và cách tổng hợp. Phương án cơ sở loại chỉ tiêu thiếu khỏi mẫu số; "
             "phương án thận trọng chấm chỉ tiêu thiếu = 0 (theo quy tắc “mức thấp nhất khi không có bằng chứng”).", "info")
    sc = U.scenario_scores()
    rk = U.scenario_ranks(sc)
    names = U.SCENARIOS
    chosen = st.multiselect("Phương án hiển thị", list(names), default=list(names), format_func=lambda k: names[k])
    if not chosen:
        st.stop()

    base_rank = rk["base"]
    st.markdown("##### Thứ hạng theo từng phương án")
    rt = rk[chosen].astype(int).copy()
    rt.columns = [names[c] for c in chosen]
    rt["Dịch chuyển tối đa so với cơ sở"] = [int(max(abs(rk.loc[b, c] - base_rank[b]) for c in chosen)) for b in rt.index]
    st.dataframe(rt.loc[sc["base"].sort_values(ascending=False).index], width="stretch")

    a, b = st.columns([1.25, 1])
    with a:
        fig = go.Figure()
        for bk in U.BANKS:
            fig.add_trace(go.Scatter(x=[names[c].split(":")[0] for c in chosen], y=[rk.loc[bk, c] for c in chosen], mode="lines+markers", name=bk,
                                     line=dict(color=U.BANK_COLORS[bk], width=3), marker=dict(size=12, line=dict(color="#fff", width=2)),
                                     hovertemplate=bk + "<br>%{x}<br>Hạng %{y:.0f}<extra></extra>"))
        fig.update_yaxes(autorange="reversed", dtick=1, title="Hạng", range=[5.4, 0.6])
        fig.update_layout(title=dict(text="Biểu đồ thay đổi thứ hạng", font=dict(size=14)))
        st.plotly_chart(U.style_fig(fig, 400), width="stretch")
    with b:
        z = sc[chosen]
        fig = go.Figure(go.Heatmap(z=z.values, x=[names[c].split(":")[0] for c in chosen], y=z.index, colorscale=[[0, "#F9D5DA"], [0.5, "#FFF1C9"], [1, "#CFE5F8"]],
                                   text=[[f"{v:.1f}" for v in r] for r in z.values], texttemplate="%{text}", xgap=3, ygap=3, showscale=False))
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(title=dict(text="Điểm tổng thể theo phương án", font=dict(size=14)))
        st.plotly_chart(U.style_fig(fig, 400, legend=False), width="stretch")

    st.markdown("##### Mức độ thay đổi của kết quả")
    spear = {names[c]: rk["base"].corr(rk[c], method="spearman") for c in chosen if c != "base"}
    top_same = {names[c]: ("Có" if rk[c].idxmin() == rk["base"].idxmin() else f"Không — {rk[c].idxmin()}") for c in chosen if c != "base"}
    out = pd.DataFrame({"Tương quan hạng Spearman (vs cơ sở)": spear, "Giữ nguyên ngân hàng đứng đầu": top_same})
    st.dataframe(out, width="stretch", column_config={"Tương quan hạng Spearman (vs cơ sở)": st.column_config.NumberColumn(format="%.2f")})
    spread = (rk[chosen].max(axis=1) - rk[chosen].min(axis=1)).astype(int)
    stable = [U.BANK_FULL[b] for b in spread.index if spread[b] <= 1]
    unstable = [f"{U.BANK_FULL[b]} (biên độ {spread[b]} hạng)" for b in spread.index if spread[b] > 1]
    st.markdown(f"**Nhận xét tự động:** {', '.join(stable) if stable else 'không có ngân hàng nào'} giữ thứ hạng ổn định (dao động ≤ 1 hạng) giữa các phương án"
                + (f"; **nhạy với cách xử lý dữ liệu:** {', '.join(unstable)}." if unstable else "."))
    st.caption("Ngân hàng có độ phủ thấp (đặc biệt Nam A Bank, Sacombank) thường nhạy nhất với phương án “thiếu = 0”. Kết quả độ nhạy phản ánh khoảng trống dữ liệu công khai, không phải khác biệt năng lực thực tế.")
    st.download_button("⬇ Tải bảng độ nhạy (CSV)", pd.concat([sc.add_prefix("diem_"), rk.add_prefix("hang_")], axis=1).to_csv().encode("utf-8-sig"), "do_nhay.csv", "text/csv")

# =========================================================================== trích đoạn BCTN
with t_rep:
    sn = U.load_csv("annual_report_snippets.csv")
    kw = U.load_csv("annual_report_keyword_counts.csv")
    if kw.empty or sn.empty:
        st.info("Chưa có dữ liệu khai phá BCTN.")
    else:
        st.markdown("##### Tần suất từ khóa trong BCTN")
        kws = sorted(kw["keyword"].unique())
        kk = st.selectbox("Từ khóa", kws, index=kws.index("chuyển đổi số") if "chuyển đổi số" in kws else 0)
        pv = kw[kw["keyword"] == kk].pivot_table(index="bank", columns="year", values="count", aggfunc="sum").reindex(U.BANKS)
        fig = go.Figure()
        for y in pv.columns:
            fig.add_trace(go.Bar(x=pv.index, y=pv[y], name=str(y)))
        fig.update_layout(barmode="group", colorway=["#CBB9F2", "#9CC7F0", "#F4B6C8"])
        st.plotly_chart(U.style_fig(fig, 320), width="stretch")
        st.caption("Tần suất từ khóa chỉ hỗ trợ rà soát bằng chứng, không tự chứng minh mức độ chuyển đổi số.")
        st.markdown("##### Trích đoạn theo trang (phục vụ rà soát thủ công)")
        c = st.columns(3)
        bb = c[0].selectbox("Ngân hàng", U.BANKS, key="sb")
        yy = c[1].selectbox("Năm", [2023, 2024, 2025], index=2, key="sy")
        kw2 = c[2].selectbox("Từ khóa", ["(tất cả)"] + kws, key="sk")
        s = sn[(sn["bank"] == bb) & (sn["year"] == yy)]
        if kw2 != "(tất cả)":
            s = s[s["keyword"] == kw2]
        st.dataframe(s[["keyword", "page", "context"]].rename(columns={"keyword": "Từ khóa", "page": "Trang", "context": "Trích đoạn"}),
                     hide_index=True, width="stretch", height=380,
                     column_config={"Trích đoạn": st.column_config.TextColumn(width="large")})
