import streamlit as st
import hashlib
from typing import Tuple, Optional
from supabase import create_client, Client

# --- 1. 頁面與風格配置 (設定中文字體與全屏寬度) ---
st.set_page_config(
    page_title="🧭 設備管理主控面板", 
    layout="wide",
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

    /* 隱藏 Streamlit 自動生成的頁面導航 */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* 主標題樣式 */
    h1 {
        font-weight: 700;
        color: #0E7490;
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

    /* 響應式卡片樣式 */
    .stPageLink {
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease-in-out;
        background-color: #F8F9FA;
        display: flex;
        align-items: center;
        gap: 15px;
    }

    .stPageLink:hover {
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
        transform: translateY(-5px);
        border-color: #0E7490;
        background-color: #E6F7FF;
    }
    
    .stPageLink .st-emotion-table {
        font-size: 28px !important;
        color: #0E7490;
        min-width: 40px;
        text-align: center;
    }

    .stPageLink p {
        font-size: 18px;
        font-weight: 500;
        margin: 0;
        color: #333333;
    }
    
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

# --- Supabase 初始化 ---
@st.cache_resource
def init_supabase() -> Client:
    """初始化 Supabase 連線（使用快取避免重複連線）"""
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_supabase()

# --- 認證函數 (改用 Supabase) ---
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username: str, password: str) -> Tuple[bool, Optional[str]]:
    """驗證使用者帳號密碼"""
    try:
        result = supabase.table("users").select("*").eq("username", username).execute()
        if result.data:
            user = result.data[0]
            if user["password_hash"] == hash_password(password):
                return True, user["role"]
    except Exception as e:
        st.error(f"驗證錯誤：{e}")
    return False, None

def add_user(username: str, password: str, role: str = "一般使用者") -> bool:
    """新增使用者"""
    try:
        password_hash = hash_password(password)
        supabase.table("users").insert({
            "username": username,
            "password_hash": password_hash,
            "role": role
        }).execute()
        return True
    except Exception as e:
        st.error(f"新增使用者失敗：{e}")
        return False

def user_exists(username: str) -> bool:
    """檢查使用者是否存在"""
    try:
        result = supabase.table("users").select("username").eq("username", username).execute()
        return len(result.data) > 0
    except:
        return False

def log_user_action(username: str, action: str):
    """記錄使用者操作"""
    try:
        from datetime import datetime
        supabase.table("user_logs").insert({
            "username": username,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }).execute()
    except Exception as e:
        st.error(f"記錄操作失敗：{e}")

# --- 登入頁面 ---
def login_page():
    st.title("🔒 登入系統")
    
    with st.form("login_form"):
        username = st.text_input("帳號")
        password = st.text_input("密碼", type="password")
        submitted = st.form_submit_button("登入")
        
        if submitted:
            valid, role = verify_user(username, password)
            if valid:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["role"] = role
                log_user_action(username, "登入")
                st.rerun()
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
                    log_user_action(st.session_state["username"], f"新增使用者 {new_username}")
                    st.success(f"✅ 成功新增使用者：{new_username}（{new_role}）")
                else:
                    st.error("新增失敗。")

# --- 登出 ---
def logout():
    if st.session_state.get("authenticated"):
        log_user_action(st.session_state["username"], "登出")
    st.session_state.clear()
    st.rerun()

# --- 修改密碼 ---
def change_password_page():
    st.subheader("🔑 修改密碼")
    with st.form("change_pw_form"):
        old_pw = st.text_input("舊密碼", type="password")
        new_pw = st.text_input("新密碼", type="password")
        confirm_pw = st.text_input("確認新密碼", type="password")
        submitted = st.form_submit_button("更新密碼")

        if submitted:
            try:
                result = supabase.table("users").select("password_hash").eq("username", st.session_state["username"]).execute()
                if not result.data:
                    st.error("❌ 帳號不存在。")
                elif hash_password(old_pw) != result.data[0]["password_hash"]:
                    st.error("❌ 舊密碼不正確。")
                elif new_pw != confirm_pw:
                    st.warning("⚠️ 兩次新密碼不一致。")
                else:
                    supabase.table("users").update({
                        "password_hash": hash_password(new_pw)
                    }).eq("username", st.session_state["username"]).execute()
                    log_user_action(st.session_state["username"], "修改密碼")
                    st.success("✅ 密碼更新成功！")
                    st.info("下次登入請使用新密碼。")
                    logout()
            except Exception as e:
                st.error(f"密碼更新失敗：{e}")

# --- 權限檢查與登入流程 ---
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    login_page()
    st.stop()

# =========================================================
# 側邊欄：登入者資訊與管理功能
# =========================================================
st.sidebar.markdown(f"#### 👤 登入資訊")
st.sidebar.markdown(f"**帳號:** `{st.session_state['username']}`")
st.sidebar.markdown(f"**角色:** `{st.session_state['role']}`")
st.sidebar.markdown("---")

if "page" not in st.session_state:
    st.session_state["page"] = "dashboard"

st.sidebar.markdown("#### ⚙️ 帳號管理與設定")
if st.session_state["role"] == "管理員":
    if st.sidebar.button("➕ 管理使用者帳號", key="btn_register"):
        st.session_state["page"] = "register"
        st.rerun()
    st.sidebar.page_link("pages/admin_manage.py", label="🛡️ 帳號管理中心", icon="🛡️")

if st.sidebar.button("🛠 修改密碼", key="btn_change_pw"):
    st.session_state["page"] = "change_pw"
    st.rerun()
    
st.sidebar.button("🚪 登出", on_click=logout, key="btn_logout")
st.sidebar.markdown("---")

if st.sidebar.button("🏠 主控面板", key="btn_dashboard"):
    st.session_state["page"] = "dashboard"
    st.rerun()
st.sidebar.markdown("---")

# 功能連結 expander
with st.sidebar.expander("📖 所有功能連結 (顯示更多)"):
    st.markdown("##### 🧭 功能導覽")
    
    st.markdown("---")
    st.markdown("##### 設備資料與管理")
    st.page_link("pages/equipment_system.py", label="設備請購維修系統")
    st.page_link("pages/equipment_detail.py", label="設備詳細資料")
    st.page_link("pages/edit_data.py", label="編輯設備資料")
    st.page_link("pages/delete_data.py", label="刪除設備資料")
    st.page_link("pages/new_equipment.py", label="新增設備")
    st.page_link("pages/view_main_equipment.py", label="主設備資料總覽")
    
    st.markdown("---")
    st.markdown("##### 保養履歷")
    st.page_link("pages/maintenance_log.py", label="設備檢修保養履歷")
    st.page_link("pages/edit_log.py", label="編輯履歷資料")
    st.page_link("pages/add_event.py", label="新增保養事件")
    
    st.markdown("---")
    st.markdown("##### 異常與報告")
    st.page_link("pages/report_abnormal.py", label="設備異常回報", icon="📸")
    st.page_link("pages/export_abnormal.py", label="匯出異常報告", icon="📤")
    st.page_link("pages/abnormal_overview.py", label="異常紀錄總覽", icon="📋")
    
    st.markdown("---")
    st.markdown("##### 資料庫輔助")
    st.page_link("pages/save_data.py", label="資料儲存模組")
    st.page_link("pages/view_data.py", label="瀏覽資料庫內容")
    st.page_link("pages/view_main_equipment.py", label="主設備總覽")
    st.page_link("pages/view_maintenance_log.py", label="保養履歷總覽")
    
    st.markdown("---")
    st.page_link("pages/guide.py", label="使用者手冊")

st.sidebar.markdown("---")

# ==============================
# 主畫面內容路由
# ==============================
current_page = st.session_state.get("page", "dashboard")

if current_page == "register" and st.session_state["role"] == "管理員":
    register_page()
    st.caption("👈 點擊左側 '主控面板' 按鈕返回主畫面")
elif current_page == "change_pw":
    change_password_page()
    st.caption("👈 點擊左側 '主控面板' 按鈕返回主畫面")
else:
    st.title("🧭 設備管理主控面板")
    st.markdown("歡迎來到 **海運組油氣處理課** 設備管理系統。請點擊下方卡片進入各模組頁面。")
    st.markdown("---")

    st.header("⚙️ 核心系統與流程")
    col_db1, col_db2 = st.columns(2)
    with col_db1:
        st.page_link("pages/equipment_system.py", label="設備請購維修系統", use_container_width=True)
    with col_db2:
        st.page_link("pages/maintenance_log.py", label="設備檢修保養履歷", use_container_width=True)

    st.markdown("---")

    st.header("💾 資料管理與操作")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("新增與總覽")
        st.page_link("pages/new_equipment.py", label="新增設備", icon="🆕", use_container_width=True)
        st.page_link("pages/add_event.py", label="新增保養事件", icon="🛠️", use_container_width=True)
        st.page_link("pages/view_main_equipment.py", label="主設備資料總覽", icon="🔍", use_container_width=True)
        st.page_link("pages/view_maintenance_log.py", label="保養履歷總覽", icon="📜", use_container_width=True)

    with col2:
        st.subheader("編輯與管理")
        st.page_link("pages/edit_data.py", label="編輯設備資料", icon="✏️", use_container_width=True)
        st.page_link("pages/edit_log.py", label="編輯履歷資料", icon="🖊️", use_container_width=True)
        st.page_link("pages/delete_data.py", label="刪除設備資料", icon="🗑️", use_container_width=True)
        st.page_link("pages/view_data.py", label="瀏覽資料庫內容", icon="🖥️", use_container_width=True)

    with col3:
        st.subheader("報表與輔助")
        st.page_link("pages/report_abnormal.py", label="設備異常回報", icon="📸", use_container_width=True)
        st.page_link("pages/abnormal_overview.py", label="異常紀錄總覽", icon="📋", use_container_width=True)
        st.page_link("pages/export_abnormal.py", label="匯出異常報告", icon="📤", use_container_width=True)
        st.page_link("pages/guide.py", label="使用者手冊", icon="📘", use_container_width=True)

    st.markdown("---")
    st.caption("© 海運組油氣處理課 - 設備管理系統")
