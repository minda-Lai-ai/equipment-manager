import streamlit as st
import sqlite3
import hashlib
import datetime

# --- 資料庫 && 表結構自動加 ---
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
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
init_db()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT password_hash, role FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row and row[0] == hash_password(password):
        return True, row[1]
    return False, None

def add_user(username, password, role="一般使用者"):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    password_hash = hash_password(password)
    try:
        c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
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

def log_user_action(username, action):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT INTO user_logs (username, action) VALUES (?, ?)", (username, action))
    conn.commit()
    conn.close()

add_user("admin", "123456", "管理員")

# --- 自動隱藏 Streamlit 頁面樹 & 英文選單 ---
st.set_page_config(page_title="設備管理主控面板", layout="wide", page_icon="🛢️")
st.markdown("""
<style>
section[data-testid="stSidebarNav"] {display: none;}
header .st-emotion-cache-1avcm0n {background: #fff !important;}
</style>
""", unsafe_allow_html=True)

# --- 登入頁面 ---
def login_page():
    st.markdown("""
    <h1 style='text-align:center; color:#005580'>🛢️ 設備管理主控面板</h1>
    <hr>
    """, unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("帳號")
        password = st.text_input("密碼", type="password")
        submit = st.form_submit_button("登入")
        if submit:
            valid, role = verify_user(username, password)
            if valid:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["role"] = role
                log_user_action(username, "登入")
                st.experimental_rerun()
            else:
                st.warning("帳號或密碼錯誤。")

def register_page():
    st.subheader("👤 新增使用者（限管理員）")
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
                log_user_action(st.session_state["username"], f"新增 {new_username} ({new_role})")
                st.success(f"成功新增使用者：{new_username}（{new_role}）")
            else:
                st.error("新增失敗。")

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
            log_user_action(st.session_state["username"], "個人密碼更改")
            st.success("密碼更新成功！下次請用新密碼登入。")
            st.session_state["authenticated"] = False
            st.experimental_rerun()

def logout_button():
    if st.sidebar.button("🚪 登出"):
        st.session_state.clear()
        st.experimental_rerun()

# -- 權限檢查入口 --
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    login_page()
    st.stop()

# --- 側邊欄專屬自訂分群导航 ---
st.sidebar.markdown("<h2 style='color:#005580'>🧭 功能導覽</h2>", unsafe_allow_html=True)
st.sidebar.markdown("#### 資料庫模組")
st.sidebar.page_link("main_dashboard.py", label="主控面板", icon="🏠")
st.sidebar.page_link("pages/equipment_system.py", label="設備請購維修系統", icon="📋")
st.sidebar.page_link("pages/equipment_detail.py", label="詳細資料", icon="🔍")
st.sidebar.page_link("pages/edit_data.py", label="編輯資料", icon="✏️")
st.sidebar.page_link("pages/delete_data.py", label="刪除資料", icon="🗑️")
st.sidebar.page_link("pages/new_equipment.py", label="新增設備", icon="🆕")
st.sidebar.page_link("pages/view_main_equipment.py", label="主設備總覽", icon="🔍")
st.sidebar.markdown("---")
st.sidebar.markdown("#### 保養/異常模組")
st.sidebar.page_link("pages/maintenance_log.py", label="檢修履歷", icon="🧾")
st.sidebar.page_link("pages/edit_log.py", label="編輯履歷", icon="✏️")
st.sidebar.page_link("pages/add_event.py", label="新增保養", icon="🆕")
st.sidebar.page_link("pages/report_abnormal.py", label="異常回報", icon="📸")
st.sidebar.page_link("pages/export_abnormal.py", label="匯出異常", icon="📤")
st.sidebar.page_link("pages/abnormal_overview.py", label="異常紀錄總覽", icon="📋")
st.sidebar.markdown("---")
st.sidebar.markdown("#### 資料匯入/查閱")
st.sidebar.page_link("pages/save_data.py", label="資料儲存", icon="💾")
st.sidebar.page_link("pages/view_data.py", label="資料庫內容", icon="🔍")
st.sidebar.page_link("pages/view_maintenance_log.py", label="保養履歷總覽", icon="🧾")
st.sidebar.markdown("---")
st.sidebar.markdown("#### 其他")
st.sidebar.page_link("pages/guide.py", label="使用者手冊", icon="📘")

# --- 管理員專屬：管理頁連結/註冊功能 ---
if st.session_state.get("role") == "管理員":
    st.sidebar.markdown("#### 系統管理")
    st.sidebar.page_link("pages/admin_manage.py", label="帳號管理", icon="🛡️")
    if st.sidebar.button("➕ 新增使用者"):
        register_page()
        st.stop()

st.sidebar.markdown("---")
st.sidebar.write(f"👤 {st.session_state['username']}　|　{st.session_state['role']}")
if st.sidebar.button("🛠 修改密碼"):
    change_password_page()
    st.stop()
logout_button()

# --- 主控畫面美化與提示 ---
st.markdown("""
<div style='background:#e0f0ff; border-radius:10px; padding:2em; margin-bottom:1em;'>
<h1 style='color:#004466; font-size:2em; text-align:center;'>🛢️ 設備管理主控面板</h1>
<p style='font-size:1.2em; text-align:center;'>請利用左側選單進入各模組頁面<br><span style='color:#1976d2'>每日管理、維護、記錄都在一頁完成</span></p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
col_db1, col_db2 = st.columns([1, 1])
with col_db1:
    st.button("進入設備請購維修系統", on_click=lambda: st.experimental_redirect("pages/equipment_system.py"), use_container_width=True)
with col_db2:
    st.button("進入設備檢修保養履歷", on_click=lambda: st.experimental_redirect("pages/maintenance_log.py"), use_container_width=True)

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.markdown("#### 常用快速操作")
    st.button("新增保養事件", on_click=lambda: st.experimental_redirect("pages/add_event.py"))
    st.button("新增設備", on_click=lambda: st.experimental_redirect("pages/new_equipment.py"))
    st.button("主設備資料總覽", on_click=lambda: st.experimental_redirect("pages/view_main_equipment.py"))
    st.button("保養履歷資料總覽", on_click=lambda: st.experimental_redirect("pages/view_maintenance_log.py"))
    st.button("設備異常回報系統", on_click=lambda: st.experimental_redirect("pages/report_abnormal.py"))
    st.button("匯出異常報告", on_click=lambda: st.experimental_redirect("pages/export_abnormal.py"))
with col2:
    st.markdown("#### 其他操作與查詢")
    st.button("瀏覽資料庫內容", on_click=lambda: st.experimental_redirect("pages/view_data.py"))
    st.button("設備詳細資料", on_click=lambda: st.experimental_redirect("pages/equipment_detail.py"))
    st.button("資料儲存模組", on_click=lambda: st.experimental_redirect("pages/save_data.py"))
    st.button("圖片儲存模組", on_click=lambda: st.experimental_redirect("pages/export_image.py"))
    st.button("刪除設備資料", on_click=lambda: st.experimental_redirect("pages/delete_data.py"))
    st.button("使用者手冊", on_click=lambda: st.experimental_redirect("pages/guide.py"))
    st.button("異常紀錄總覽", on_click=lambda: st.experimental_redirect("pages/abnormal_overview.py"))

st.markdown("---")
st.caption("海運組油氣處理課")

