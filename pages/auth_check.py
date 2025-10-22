import streamlit as st

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("尚未登入或權限不足，請由主畫面登入後再瀏覽此頁。")
    st.stop()

def require_login():
    if "user" not in st.session_state:
        st.warning("⚠️ 請先登入才能使用系統")
        st.page_link("pages/login.py", label="🔐 前往登入頁面", icon="🔑")
        st.stop()
