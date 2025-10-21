import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# ✅ 初始化 Firebase（只執行一次）
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(eval(st.secrets["firebase_adminsdk"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.set_page_config(page_title="🔐 使用者登入", layout="centered")
st.title("🔐 使用者登入")

# 登入表單
email = st.text_input("Email")
password = st.text_input("密碼", type="password")

# 登入邏輯
if st.button("登入"):
    if not email or not password:
        st.error("❌ 請輸入 Email 和密碼")
        st.stop()

    user_ref = db.collection("users").document(email)
    user_doc = user_ref.get()

    if user_doc.exists:
        user_data = user_doc.to_dict()
        if user_data.get("password") == password:
            st.session_state["user"] = {
                "email": email,
                "name": user_data.get("name", ""),
                "role": user_data.get("role", "user")
            }
            st.success("✅ 登入成功")
            st.switch_page("main_dashboard.py")
        else:
            st.error("❌ 密碼錯誤")
    else:
        st.error("❌ 查無此帳號")
