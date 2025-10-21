import streamlit as st

def require_login():
    if "user" not in st.session_state:
        st.warning("⚠️ 請先登入才能使用系統")
        st.page_link("pages/login.py", label="🔐 前往登入頁面", icon="🔑")
        st.stop()
