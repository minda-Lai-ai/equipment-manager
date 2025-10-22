import streamlit as st
import sqlite3
import hashlib

# --- 資料庫與認證函數 ---
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

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

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

def add_user(username, password, role="一般使用者"):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    password_hash = hash_password(password)
    try:
        c.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def user_exists(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

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
            st.experimental_rerun()   # 登入立即刷新，只需按一次
        else:
            st.error("帳號或密碼錯誤。")
 
# --- 管理員新增帳號頁面 ---
def register_page():
    st.header("👤 新增使用者（限管理員）")
    new_username = st.text_input("新帳號")
    new_password = st.text_input("新密碼", type="password")
    new_role = st.selectbox("角色", ["一般使用者", "管理員"])
    if st.button("新增使用者"):
        if user_exists(new_username):
            st.warning("此帳號已存在！")
        elif not new_username or not new_password:
            st.warning("請填寫帳號與密碼。")
        else:
            ok = add_user(new_username, new_password, new_role)
            if ok:
                st.success(f"成功新增使用者：{new_username}（{new_role}）")
            else:
                st.error("新增失敗。")

# --- 登出 ---
def logout_button():
    if st.sidebar.button("登出"):
        st.session_state.clear()
        st.experimental_rerun()

# --- 修改密碼 ---
def change_password_page():
    st.subheader("🔑 修改密碼")
    old_pw = st.text_input("舊密碼", type="password")
    new_pw = st.text_input("新密碼", type="password")
    confirm_pw = st.text_input("確認新密碼", type="password")

    if st.button("更新密碼"):
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT password_hash FROM users WHERE username = ?", (st.session_state["username"],))
        row = c.fetchone()
        if not row:
            st.error("帳號不存在。")
        elif hash_password(old_pw) != row[0]:
            st.error("舊密碼不正確。")
        elif new_pw != confirm_pw:
            st.warning("兩次新密碼不一致。")
        else:
            c.execute("UPDATE users SET password_hash=? WHERE username=?",
                      (hash_password(new_pw), st.session_state["username"]))
            conn.commit()
            conn.close()
            st.success("密碼更新成功！")
            st.info("下次登入請使用新密碼。")
            st.session_state["authenticated"] = False
            st.experimental_rerun()

# --- 權限檢查 ---
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    login_page()
    st.stop()

# --- 側邊欄登入者訊息 ---
st.sidebar.markdown("---")
st.sidebar.write(f"👤 使用者：{st.session_state['username']}")
st.sidebar.write(f"🧩 角色：{st.session_state['role']}")
logout_button()
st.sidebar.markdown("---")

# --- 僅管理員能進入新增使用者頁 ---
if st.session_state["role"] == "管理員":
    if st.sidebar.checkbox("📋 管理使用者帳號"):
        register_page()
        st.stop()

# ==============================
# 側邊欄頁面導覽連結（移到最上方）
# ==============================
st.sidebar.title("🧭 功能導覽")

# 分組 1
st.sidebar.page_link("main_dashboard.py", label="Main Dashboard", icon="🏠")
st.sidebar.markdown("---")

# 分組 2
st.sidebar.page_link("pages/equipment_system.py", label="設備請購維修系統", icon="📋")
st.sidebar.page_link("pages/equipment_detail.py", label="設備詳細資料", icon="🔍")
st.sidebar.page_link("pages/edit_data.py", label="編輯設備資料", icon="✏️")
st.sidebar.page_link("pages/delete_data.py", label="刪除設備資料", icon="🗑️")
st.sidebar.page_link("pages/new_equipment.py", label="新增設備", icon="🆕")
st.sidebar.page_link("pages/view_main_equipment.py", label="主設備資料總覽", icon="🔍")
st.sidebar.markdown("---")

# 分組 3
st.sidebar.page_link("pages/maintenance_log.py", label="設備檢修保養履歷", icon="🧾")
st.sidebar.page_link("pages/edit_log.py", label="編輯履歷資料", icon="✏️")
st.sidebar.page_link("pages/add_event.py", label="新增保養事件", icon="🆕")
st.sidebar.markdown("---")

# 分組 4
st.sidebar.page_link("pages/report_abnormal.py", label="設備異常回報", icon="📸")
st.sidebar.page_link("pages/export_abnormal.py", label="匯出異常報告", icon="📤")
st.sidebar.page_link("pages/abnormal_overview.py", label="異常紀錄總覽", icon="📋")
st.sidebar.markdown("---")

# 分組 5
st.sidebar.page_link("pages/save_data.py", label="資料儲存模組", icon="💾")
st.sidebar.page_link("pages/view_data.py", label="瀏覽資料庫內容", icon="🔍")
st.sidebar.page_link("pages/view_main_equipment.py", label="主設備總覽", icon="🔍")
st.sidebar.page_link("pages/view_maintenance_log.py", label="保養履歷總覽", icon="🧾")
st.sidebar.markdown("---")

# 分組 6
st.sidebar.page_link("pages/guide.py", label="使用者手冊", icon="📘")

# ==============================
# 側邊欄下方：使用者資訊與管理功能
# ==============================
st.sidebar.markdown("---")
st.sidebar.write(f"👤 使用者：{st.session_state['username']}")
st.sidebar.write(f"🧩 角色：{st.session_state['role']}")

if st.session_state["role"] == "管理員":
    if st.sidebar.button("➕ 新增使用者帳號"):
        register_page()
        st.stop()

if st.sidebar.button("🚪 登出"):
    st.session_state.clear()
    st.experimental_rerun()

if st.sidebar.button("🛠 修改密碼"):
    change_password_page()
    st.stop()

# ==============================
# 主畫面內容
# ==============================
st.set_page_config(page_title="設備管理主控面板", layout="wide")
st.title("🧭 設備管理主控面板")
st.markdown("請選擇側邊功能連結進入各模組頁面。")

# ...把你的原分頁連結按鈕、模組內容放在這裡

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

col1, col2 = st.columns(2)

with col1:
    if st.session_state.get("authenticated", False):
        st.page_link("pages/add_event.py", label="新增保養事件", icon="🆕")
        st.page_link("pages/new_equipment.py", label="新增設備", icon="🆕")
        st.page_link("pages/view_main_equipment.py", label="主設備資料總覽", icon="🔍")
        st.page_link("pages/view_maintenance_log.py", label="保養履歷資料總覽", icon="🔍")
        st.page_link("pages/report_abnormal.py", label="設備異常回報系統", icon="📸")
        st.page_link("pages/export_abnormal.py", label="匯出異常報告", icon="📤")
    else:
        st.warning("請先登入才能使用功能頁面。")

with col2:
    if st.session_state.get("authenticated", False):
        st.page_link("pages/view_data.py", label="瀏覽資料庫內容", icon="🔍")
        st.page_link("pages/equipment_detail.py", label="設備詳細資料", icon="🔍")
        st.page_link("pages/save_data.py", label="資料儲存模組", icon="💾")
        st.page_link("pages/export_image.py", label="圖片儲存模組", icon="🖼️")
        st.page_link("pages/delete_data.py", label="刪除設備資料", icon="🗑️")
        st.page_link("pages/guide.py", label="使用者手冊", icon="📘")
        st.page_link("pages/abnormal_overview.py", label="異常紀錄總覽", icon="📋")
    else:
        st.warning("請先登入才能使用功能頁面。")

st.markdown("---")
st.caption("海運組油氣處理課")
