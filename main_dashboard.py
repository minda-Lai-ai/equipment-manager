import streamlit as st
from firebase_init import get_firestore

st.set_page_config(page_title="🧭 設備管理主控面板", layout="wide")

# 🔐 登入檢查
if "user" not in st.session_state:
    st.warning("⚠️ 請先登入才能使用系統")
    st.page_link("pages/login.py", label="🔐 前往登入頁面", icon="🔑")
    st.stop()

db = get_firestore()  # ✅ 正確取得 Firestore 實例

# 👤 顯示登入者資訊
user = st.session_state["user"]
st.sidebar.success(f"👤 登入者：{user['name']}（{user['email']}）")

APP_NAME = "equipment_manager_app"

def get_firestore():
    try:
        app = firebase_admin.get_app(APP_NAME)
    except ValueError:
        cred = credentials.Certificate(eval(st.secrets["firebase_adminsdk"]))
        app = firebase_admin.initialize_app(cred, name=APP_NAME)
    return firestore.client(app)

# 🚪 登出按鈕
if st.sidebar.button("🚪 登出"):
    st.session_state.clear()
    st.page_link("pages/firebase_test.py", label="🧪 Firebase 測試頁面", icon="🧬")
    st.switch_page("pages/login.py")  # 或改成 st.page_link(...) 也可以

# 🧭 主控面板內容
st.title("🧭 設備管理主控面板")
st.markdown("請選擇下列功能進入各模組頁面。")
st.markdown("---")

# 🔷 資料庫模組（最大按鈕）
col_db1, col_db2 = st.columns([1, 1])
with col_db1:
    st.page_link("pages/equipment_system.py", label="設備請購維修系統", icon="📋", use_container_width=True)
with col_db2:
    st.page_link("pages/maintenance_log.py", label="設備檢修保養履歷", icon="🧾", use_container_width=True)

st.markdown("---")

# 🔹 其他模組（小按鈕）
col1, col2 = st.columns(2)

with col1:
    st.page_link("pages/edit_data.py", label="編輯設備資料", icon="✏️")
    st.page_link("pages/add_event.py", label="新增保養事件", icon="🆕")
    st.page_link("pages/new_equipment.py", label="新增設備", icon="🆕")
    st.page_link("pages/view_main_equipment.py", label="主設備資料總覽", icon="🔍")
    st.page_link("pages/view_maintenance_log.py", label="保養履歷資料總覽", icon="🔍")
    st.page_link("pages/report_abnormal.py", label="設備異常回報系統", icon="📸")
    st.page_link("pages/export_abnormal.py", label="匯出異常報告", icon="📤")


with col2:
    st.page_link("pages/view_data.py", label="瀏覽資料庫內容", icon="🔍")
    st.page_link("pages/equipment_detail.py", label="設備詳細資料", icon="🔍")
    st.page_link("pages/save_data.py", label="資料儲存模組", icon="💾")
    st.page_link("pages/export_image.py", label="圖片儲存模組", icon="🖼️")
    st.page_link("pages/delete_data.py", label="刪除設備資料", icon="🗑️")
    st.page_link("pages/guide.py", label="使用者手冊", icon="📘")
    st.page_link("pages/abnormal_overview.py", label="異常紀錄總覽", icon="📋")

st.markdown("---")
st.caption("海運組油氣處理課")
