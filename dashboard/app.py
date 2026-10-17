"""Dashboard BXH chuyển đổi số 5 ngân hàng (tham khảo DBI). Chạy: streamlit run dashboard/app.py"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
import utils as U  # noqa: E402

st.set_page_config(page_title="BXH Chuyển đổi số Ngân hàng", page_icon="🏦", layout="wide",
                   initial_sidebar_state="expanded")
U.setup_app()

pages = [
    st.Page("pages/1_Tong_quan.py", title="Tổng quan", icon="🏆", default=True),
    st.Page("pages/2_Chi_tiet_ngan_hang.py", title="Chi tiết ngân hàng", icon="🏦"),
    st.Page("pages/3_So_sanh.py", title="So sánh", icon="⚖️"),
    st.Page("pages/4_Gap_Analysis.py", title="Gap Analysis", icon="🎯"),
    st.Page("pages/5_Bang_chung_va_do_nhay.py", title="Bằng chứng & độ nhạy", icon="🔎"),
]
nav = st.navigation(pages)

with st.sidebar:
    st.markdown("### 🌸 BXH Chuyển đổi số NH")
    st.caption("Khung tham khảo DBI · 5 ngân hàng · 2023–2025")
    st.markdown("---")
    st.caption("Kết quả là **đánh giá nghiên cứu từ bên ngoài** dựa trên dữ liệu công khai, "
               "không phải điểm DBI hay xếp hạng chính thức.")

nav.run()
U.footer()
