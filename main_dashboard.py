import streamlit as st
import sqlite3
import hashlib

# --- 1. 頁面與風格配置 (設定中文字體與全屏寬度) ---
st.set_page_config(
    page_title="🧭 設備管理主控面板", 
    layout="wide",
    # 預設折疊側邊欄，釋放手機螢幕空間
    initial_sidebar_state="auto" 
)

# --- 自定義 CSS 樣式 (視覺美化與響應式卡片) ---
st.markdown(
    """
    <style>
    /* 導入優雅的中文字體 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;500;700&display=swap');
    html, body, [class*="st-emotion-"] {
        font-family: 'Noto Sans TC', sans-serif;
    }

    /* 隱藏 Streamlit 自動生成的頁面連結 (解決英文/多餘連結問題) */
    [data-testid="stSidebarNav"] li:nth-child(n+2) {
        display: none;
    }
    
    /* 主標題樣式 */
    h1 {
        font-weight: 700;
        color: #0E7490; /* 藍綠色強調 */
        border-bottom: 3px solid #E0F2F7;
        padding-bottom: 10px;
        margin-bottom: 20px !important;
    }

    /* 模組標題樣式 */
    h2 {
        font-weight: 600;
        color: #0E7490;
        margin-top: 30px;
        margin-bottom: 15px;
        font-size: 1.5rem;
    }

    /* 響應式卡片樣式 (應用於 st.page_link 容器) */
    .stPageLink {
        /* 基礎卡片樣式 */
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08); /* 稍微強烈的陰影 */
        transition: all 0.3s ease-in-out;
        background-color: #F8F9FA; /* 淺灰色背景 */
        
        display: flex;
        align-items: center;
        gap: 15px;
    }

    /* 卡片懸停效果 */
    .stPageLink:hover {
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
        transform: translateY(-5px); /* 提升效果 */
        border-color: #0E7490;
        background-color: #E6F7FF; /* 淺藍色懸停背景 */
    }
    
    /* 調整 st.page_link 的圖標大小和顏色 */
    .stPageLink .st-emotion-table {
        font-size: 28px !important;
        color: #0E7490;
        min-width: 40px;
        text-align: center;
    }

    /* 調整 st.page_link 的文字樣式 */
    .stPageLink p {
        font-size: 18px;
        font-weight: 500;
        margin: 0;
        color: #333333;
    }
    
    /* 手機優化：確保內容在小螢幕上不會擠壓 */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        .stPageLink {
            padding: 15px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


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

# 初始化資料庫並確保 admin 存在
init_db()
if not user_exists("admin"):
    add_user("admin", "123456", "管理員")

# --- 登入頁面 ---
def login_page():
    st.title("🔒 登入系統")
    username = st.text_input("帳號")
    password = st.text_input("密碼", type="password")
    
    # 修正登入機制：使用表單確保按鈕只運行一次且狀態更新後立即重跑
    with st.form("login_form"):
        submitted = st.form_submit_button("登入")
        if submitted:
            valid, role = verify_user(username, password)
            if valid:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["role"] = role
                # 登入成功後，立即刷新，解決雙擊問題
                st.experimental_rerun()
            else:
                st.error("❌ 帳號或密碼錯誤。")

# --- 管理員新增帳號頁面 ---
def register_page():
    st.header("👤 新增使用者（限管理員）")
    with st.form("register_form"):
        new_username = st.text_input("新帳號")
        new_password = st.text_input("新密碼", type="password")
        new_role = st.selectbox("角色", ["一般使用者", "管理員"])
        submitted = st.form_submit_button("新增使用者")
        
        if submitted:
            if user_exists(new_username):
                st.warning("此帳號已存在！")
            elif not new_username or not new_password:
                st.warning("請填寫帳號與密碼。")
            else:
                ok = add_user(new_username, new_password, new_role)
                if ok:
                    st.success(f"✅ 成功新增使用者：{new_username}（{new_role}）")
                else:
                    st.error("新增失敗。")

# --- 登出 ---
def logout():
    st.session_state.clear()
    st.experimental_rerun()

# --- 修改密碼 ---
def change_password_page():
    st.subheader("🔑 修改密碼")
    with st.form("change_pw_form"):
        old_pw = st.text_input("舊密碼", type="password")
        new_pw = st.text_input("新密碼", type="password")
        confirm_pw = st.text_input("確認新密碼", type="password")
        submitted = st.form_submit_button("更新密碼")

        if submitted:
            conn = sqlite3.connect("users.db")
            c = conn.cursor()
            c.execute("SELECT password_hash FROM users WHERE username = ?", (st.session_state["username"],))
            row = c.fetchone()
            
            if not row:
                st.error("❌ 帳號不存在。")
            elif hash_password(old_pw) != row[0]:
                st.error("❌ 舊密碼不正確。")
            elif new_pw != confirm_pw:
                st.warning("⚠️ 兩次新密碼不一致。")
            else:
                c.execute("UPDATE users SET password_hash=? WHERE username=?",
                        (hash_password(new_pw), st.session_state["username"]))
                conn.commit()
                conn.close()
                st.success("✅ 密碼更新成功！")
                st.info("下次登入請使用新密碼。")
                
                # 登出並強制使用者使用新密碼重新登入
                logout() 

# --- 權限檢查與登入流程 ---
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    # 檢查是否有切換到管理頁面的旗標，並確保登出後回到登入頁
    if st.session_state.get("page") == "register" or st.session_state.get("page") == "change_pw":
        st.session_state["page"] = "login"
    login_page()
    st.stop() # 停止執行後續的主控面板內容

# --- 側邊欄：登入者資訊與功能按鈕 (極度簡化) ---
st.sidebar.markdown(f"#### 歡迎回來！")
st.sidebar.markdown(f"**👤 帳號:** `{st.session_state['username']}`")
st.sidebar.markdown(f"**🧩 角色:** `{st.session_state['role']}`")
st.sidebar.markdown("---")

# 管理功能按鈕 (僅限管理員)
if st.session_state["role"] == "管理員":
    if st.sidebar.button("➕ 管理使用者帳號", key="btn_register"):
        st.session_state["page"] = "register"
        st.experimental_rerun()
    st.sidebar.markdown("---")

# 其他使用者功能
if st.sidebar.button("🛠 修改密碼", key="btn_change_pw"):
    st.session_state["page"] = "change_pw"
    st.experimental_rerun()
    
st.sidebar.button("🚪 登出", on_click=logout, key="btn_logout")

# --- 主控面板內容路由 (根據側邊欄按鈕切換頁面) ---
current_page = st.session_state.get("page", "dashboard")

if current_page == "register" and st.session_state["role"] == "管理員":
    register_page()
elif current_page == "change_pw":
    change_password_page()
else:
    # --- 頁面標題 ---
    st.title("🧭 設備管理主控面板")
    st.markdown("歡迎來到 **海運組油氣處理課** 設備管理系統。請點擊下方卡片進入各模組頁面。")
    st.markdown("---")

    # --- 核心系統與流程 (兩欄佈局，手機自動堆疊) ---
    st.header("⚙️ 核心系統與流程")
    col_db1, col_db2 = st.columns(2)
    with col_db1:
        st.page_link("pages/equipment_system.py", label="設備請購維修系統", icon="📋", use_container_width=True)
    with col_db2:
        st.page_link("pages/maintenance_log.py", label="設備檢修保養履歷", icon="🧾", use_container_width=True)

    st.markdown("---")

    # --- 資料管理與操作 (三欄佈局，手機自動堆疊) ---
    st.header("💾 資料管理與操作")

    col1, col2, col3 = st.columns(3)
    
    # 連結分組：新增與總覽
    with col1:
        st.subheader("新增與總覽")
        st.page_link("pages/new_equipment.py", label="🆕 新增設備", icon="🆕", use_container_width=True)
        st.page_link("pages/add_event.py", label="🛠️ 新增保養事件", icon="🛠️", use_container_width=True)
        st.page_link("pages/view_main_equipment.py", label="🔍 主設備資料總覽", icon="🔍", use_container_width=True)
        st.page_link("pages/view_maintenance_log.py", label="📜 保養履歷總覽", icon="📜", use_container_width=True)

    # 連結分組：編輯與刪除
    with col2:
        st.subheader("編輯與管理")
        st.page_link("pages/edit_data.py", label="✏️ 編輯設備資料", icon="✏️", use_container_width=True)
        st.page_link("pages/edit_log.py", label="🖊️ 編輯履歷資料", icon="🖊️", use_container_width=True)
        st.page_link("pages/delete_data.py", label="🗑️ 刪除設備資料", icon="🗑️", use_container_width=True)
        st.page_link("pages/view_data.py", label="🖥️ 瀏覽資料庫內容", icon="🖥️", use_container_width=True)


    # 連結分組：報表與輔助
    with col3:
        st.subheader("報表與輔助")
        st.page_link("pages/report_abnormal.py", label="📸 設備異常回報", icon="📸", use_container_width=True)
        st.page_link("pages/abnormal_overview.py", label="📋 異常紀錄總覽", icon="📋", use_container_width=True)
        st.page_link("pages/export_abnormal.py", label="📤 匯出異常報告", icon="📤", use_container_width=True)
        st.page_link("pages/guide.py", label="📘 使用者手冊", icon="📘", use_container_width=True)

    st.markdown("---")
    st.caption("© 海運組油氣處理課 - 設備管理系統")
