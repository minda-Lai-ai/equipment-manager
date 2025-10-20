import streamlit as st

st.set_page_config(page_title="首頁", layout="wide")

st.title("🏠 設備管理系統首頁")

st.markdown("系統正在導向主控面板...")

# 自動跳轉
st.switch_page("main_dashboard.py")

