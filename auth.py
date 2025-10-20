import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# 初始化 Firebase Admin
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-adminsdk.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# 登入表單（簡易版）
email = st.text_input("請輸入 Email")
password = st.text_input("請輸入密碼", type="password")
login_button = st.button("登入")

# 登入邏輯（僅示範，實際應使用 Firebase Authentication SDK）
if login_button and email and password:
    # 查詢 Firestore 中的使用者資料
    docs = db.collection("users").where("email", "==", email).get()
    if docs:
        user_data = docs[0].to_dict()
        if user_data.get("password") == password:  # ⚠️ 僅示範，請改用 Firebase Auth 驗證
            st.session_state["user_email"] = email
            st.session_state["user_role"] = user_data.get("role", "user")
            st.success(f"歡迎 {email}（{st.session_state['user_role']}）")
        else:
            st.error("密碼錯誤")
    else:
        st.error("找不到使用者")
