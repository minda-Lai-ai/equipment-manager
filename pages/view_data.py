import streamlit as st
import pandas as pd

st.set_page_config(page_title="瀏覽資料", layout="wide")
st.title("🔍 瀏覽資料庫內容")

# 返回主控面板
if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

st.markdown("---")

# 選擇資料庫
db_choice = st.radio("選擇資料庫", ["設備請購維修系統", "設備檢修保養履歷"])

if db_choice == "設備請購維修系統":
    df = pd.read_csv("data/main_equipment_system.csv")
else:
    df = pd.read_csv("data/history_maintenance_log.csv")

st.subheader(f"📘 顯示：{db_choice}")
st.dataframe(df, use_container_width=True)

