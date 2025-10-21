import streamlit as st
import pandas as pd
from firebase_init import get_firestore
db = get_firestore()

st.set_page_config(page_title="🔍 主設備資料總覽", layout="wide")
st.title("🔍 主設備資料總覽")

if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

try:
    df = pd.read_csv("data/main_equipment_system.csv")
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error(f"❌ 無法載入主設備資料庫：{e}")
    st.stop()

st.markdown("---")
st.markdown("📸 若需將資料另存為圖片，請使用下方工具：")

# 圖片儲存按鈕（可連結 export_image.py）
if st.button("🖼️ 將主設備資料匯出為圖片"):
    st.switch_page("pages/export_image.py")

