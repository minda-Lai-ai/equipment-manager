import streamlit as st
import sqlite3
import hashlib

# --- 資料庫初始化：自動建立 users.db 與 users 資料表 ---
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

# --- 密碼雜湊 ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- 帳密驗證 ---
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

# --- 新增使用者（只在不存在 admin 時執行） ---
def add_user(username, password, role="一般使用者"):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    password_hash = hash_password(password)
    try:
        c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                  (username, password_hash, role))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # 已存在就不重複新增
    conn.close()

# --- 初始化資料庫和預設 admin 帳號 ---
init_db()
add_user("admin", "123456", "管理員")

# --- 登入頁面 ---
def login_page():
    st.title("🔒 登入系統")
    username = st.text_input("帳號")
    password = st.text_input("密碼", type="password")
    if st.button("登入"):
        valid, role = verify_user(username, password)
        if valid:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.session_state["role"] = role
        else:
            st.error("帳號或密碼錯誤。")

# --- 登出邏輯 ---
def logout_button():
    if st.button("登出"):
        st.session_state["authenticated"] = False
        st.experimental_rerun()

# --- 權限檢查&內容顯示 ---
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    login_page()
    st.stop()

# --- 登入後顯示主控面板（可加入你的原頁面內容） ---
st.sidebar.write(f"👋 您好，{st.session_state['username']}（{st.session_state['role']}）")
logout_button()

# --- 原本主控面板頁面內容放在這裡 ---
st.set_page_config(page_title="設備管理主控面板", layout="wide")

st.title("🧭 設備管理主控面板")
st.markdown("請選擇下列功能進入各模組頁面。")
# ...（頁面內容依你的原檔案繼續寫）

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
