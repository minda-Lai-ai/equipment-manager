import streamlit as st

# 簡易登入使用者資料，可改從外部檔案或資料庫載入
USER_CREDENTIALS = {
    "admin": {"password": "123456", "role": "管理員"},
    "user1": {"password": "abc123", "role": "一般使用者"}
}

# 登入頁面函數
def login_page():
    st.title("🔒 登入系統")
    username = st.text_input("帳號")
    password = st.text_input("密碼", type="password")
    login_button = st.button("登入")

    if login_button:
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username]["password"] == password:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.session_state["role"] = USER_CREDENTIALS[username]["role"]
            st.success("登入成功！正在導向主控面板...")
            st.experimental_rerun()
        else:
            st.error("帳號或密碼錯誤，請重新輸入。")

# 登出功能
def logout_button():
    if st.button("登出"):
        st.session_state["authenticated"] = False
        st.experimental_rerun()

# 如果沒有登入，顯示登入頁面
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    login_page()
    st.stop()

# 如果登入成功，顯示你的原主控面板
st.sidebar.write(f"您好，{st.session_state['username']}（{st.session_state['role']}）")
logout_button()

st.set_page_config(page_title="設備管理主控面板", layout="wide")
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
