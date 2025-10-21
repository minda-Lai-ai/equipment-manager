import streamlit as st
from firebase_init import get_firestore

st.set_page_config(page_title="🧪 Firebase 測試頁面", layout="centered")
st.title("🧪 Firebase 測試頁面")

# ✅ 初始化 Firestore
try:
    db = get_firestore()
    st.success("✅ Firestore 初始化成功")
except Exception as e:
    st.error(f"❌ Firestore 初始化失敗：{e}")
    st.stop()

# ✅ 顯示目前登入者（如有）
if "user" in st.session_state:
    user = st.session_state["user"]
    st.info(f"👤 登入者：{user['name']}（{user['email']}）")
else:
    st.warning("⚠️ 尚未登入")

# ✅ 嘗試讀取 users 集合
st.markdown("### 👥 Firestore 使用者列表")
try:
    users = db.collection("users").stream()
    for u in users:
        data = u.to_dict()
        st.write(f"- 📧 {u.id}｜👤 {data.get('name', '')}｜🧑‍💼 {data.get('role', '')}")
except Exception as e:
    st.error(f"❌ 無法讀取 users 集合：{e}")
