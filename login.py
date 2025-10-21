import streamlit as st
from firebase_init import get_firestore

st.set_page_config(page_title="🔐 使用者登入", layout="centered")
st.title("🔐 使用者登入")

db = get_firestore()

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
