import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# 初始化 Firebase（只執行一次）
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-adminsdk.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

st.set_page_config(page_title="使用者管理", layout="wide")
st.title("👤 使用者管理")

# 🔐 檢查登入與權限
if "user_email" not in st.session_state or st.session_state["user_role"] != "admin":
    st.warning("僅限管理者使用此頁面")
    st.stop()

# ➕ 新增使用者
st.subheader("➕ 新增使用者")
new_email = st.text_input("使用者 Email")
new_role = st.selectbox("角色", ["user", "admin"])
if st.button("新增使用者"):
    if new_email:
        db.collection("users").add({
            "email": new_email,
            "role": new_role
        })
        st.success(f"已新增使用者：{new_email}（{new_role}）")
        st.experimental_rerun()

# 📋 使用者清單
st.subheader("📋 使用者清單")
users = db.collection("users").stream()
for doc in users:
    data = doc.to_dict()
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        st.write(data["email"])
    with col2:
        new_role = st.selectbox("角色", ["user", "admin"], index=["user", "admin"].index(data["role"]), key=doc.id)
    with col3:
        if st.button("🗑️ 刪除", key="del_" + doc.id):
            db.collection("users").document(doc.id).delete()
            st.success("使用者已刪除")
            st.experimental_rerun()
        elif st.button("💾 更新", key="upd_" + doc.id):
            db.collection("users").document(doc.id).update({"role": new_role})
            st.success("角色已更新")
            st.experimental_rerun()

