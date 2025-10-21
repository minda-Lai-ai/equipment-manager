import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

# ✅ 安全初始化 Firebase Admin SDK（只執行一次）
if not firebase_admin._apps:
    cred = credentials.Certificate(eval(st.secrets["firebase_adminsdk"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

email = st.text_input("Email")
password = st.text_input("密碼", type="password")

if st.button("登入"):
    user_ref = db.collection("users").document(email)
    user_doc = user_ref.get()

    if user_doc.exists and user_doc.to_dict()["password"] == password:
        user_data = user_doc.to_dict()
        st.session_state["user"] = {
            "email": email,
            "name": user_data.get("name", ""),
            "role": user_data.get("role", "user")
        }
        st.success("✅ 登入成功")
        st.switch_page("主控面板")  # 請確認標題是否正確
    else:
        st.error("❌ 登入失敗，請檢查帳號密碼")
