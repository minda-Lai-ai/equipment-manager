import streamlit as st
import sqlite3
import hashlib

# 建立或連接 SQLite 資料庫
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# 密碼哈希函數（避免明碼存密碼）
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 檢查使用者登入
def verify_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT password_hash, role FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        stored_hash, role = row
        if stored_hash == hash_password(password):
            return True, role
    return False, None

# 新增使用者（可事後以 Streamlit 管理者頁面或外部腳本新增）
def add_user(username, password, role="一般使用者"):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    password_hash = hash_password(password)
    try:
        c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                  (username, password_hash, role))
        conn.commit()
    except sqlite3.IntegrityError:
        st.warning("該帳號已存在！")
    conn.close()

# 初始化資料庫
init_db()

# 初始帳號（預設存在管理者帳號）
add_user("admin", "123456", "管理員")

# 登入頁面
def login_page():
    st.title("🔒 登入系統")

    username = st.text_input("帳號")
    password = st.text_input("密碼", type="password")
    login_button = st.button("登入")

    if login_button:
        valid, role = verify_user(username, password)
        if valid:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.session_state["role"] = role
            st.success("登入成功！正在導向主控面板...")
            st.experimental_rerun()
        else:
            st.error("帳號或密碼錯誤。")

# 登出功能
def logout_button():
    if st.button("登出"):
        st.session_state["authenticated"] = False
        st.experimental_rerun()

# 登入檢查
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    login_page()
    st.stop()

# 登入成功後顯示使用者身分
st.sidebar.write(f"👋 您好，{st.session_state['username']}（{st.session_state['role']}）")
logout_button()

st.set_page_config(page_title="設備管理主控面板", layout="wide")

st.title("🧭 設備管理主控面板")
st.markdown("請選擇下列功能進入各模組頁面。")
# ... 你的頁面連結區塊

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
