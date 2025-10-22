import streamlit as st

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("尚未登入或權限不足，請由主畫面登入後再瀏覽此頁。")
    st.stop()

import pandas as pd

st.set_page_config(page_title="🔍 保養履歷資料總覽", layout="wide")
st.title("🔍 保養履歷資料總覽")

if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

try:
    df = pd.read_csv("data/history_maintenance_log.csv")
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error(f"❌ 無法載入保養履歷資料庫：{e}")
    st.stop()

st.markdown("---")
st.markdown("📸 若需將資料另存為圖片，請使用下方工具：")

# 圖片儲存按鈕（可連結 export_image.py）
if st.button("🖼️ 將保養履歷匯出為圖片"):
    st.switch_page("pages/export_image.py")

