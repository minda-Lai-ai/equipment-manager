import streamlit as st

# 權限檢查
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("尚未登入或登入已逾時，請回主畫面重新登入。")
    st.stop()

# 顯示登入者資訊於頁首或側邊欄
st.sidebar.markdown("---")
st.sidebar.write(f"👤 使用者：{st.session_state['username']}")
st.sidebar.write(f"🧩 角色：{st.session_state['role']}")

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

