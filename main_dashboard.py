import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

st.set_page_config(page_title="🧭 設備管理主控面板", layout="wide")

# --- 1. CONFIG & AUTHENTICATOR SETUP ---
try:
    # 嘗試載入 config.yaml
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("❌ 找不到 'config.yaml' 文件。請確認已將 config.yaml 放置在專案根目錄。")
    st.stop() # 停止執行以防錯誤

# 實例化 Authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['cookie_name'],
    config['cookie']['cookie_secret'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

# --- 2. AUTHENTICATION ---
# 在側邊欄顯示登入表單
name, authentication_status, username = authenticator.login('Login', 'sidebar')

# 2a. 處理驗證狀態
if authentication_status is False:
    st.sidebar.error("使用者名稱/密碼錯誤")
    st.warning("⚠️ 請先登入才能使用系統")
    st.stop() # 停止顯示主頁內容

elif authentication_status is None:
    st.warning("⚠️ 請先登入才能使用系統")
    st.stop() # 停止顯示主頁內容

elif authentication_status is True:
    # --- 使用者已成功登入 (authentication_status == True) ---

    # 3. 側邊欄：顯示使用者資訊和登出按鈕
    st.sidebar.success(f"👤 歡迎, {name}!")
    authenticator.logout('🚪 登出', 'sidebar')
    
    # 4. 頁面自訂樣式 (美化 CSS)
    st.markdown("""
        <style>
        /* 隱藏預設 Streamlit 頁面鏈接的箭頭 */
        a[data-testid="stPageLink"] > div > svg {
            display: none !important;
        }
        /* 主控面板標題 */
        h1 {
            color: #007BFF;
            font-weight: 700;
        }
        /* 模組按鈕容器 */
        div.stButton > button {
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-radius: 12px;
            font-size: 18px;
            height: 80px;
            text-align: left;
            padding-left: 20px;
            width: 100%;
        }
        /* 核心模組按鈕樣式 */
        .core-button-container div.stButton > button {
            background-color: #007BFF; /* 藍色背景 */
            color: white;
            font-size: 20px;
            font-weight: bold;
        }
        /* 核心模組 hover 效果 */
        .core-button-container div.stButton > button:hover {
            background-color: #0056b3;
            transform: translateY(-2px);
            box-shadow: 0 6px 10px rgba(0, 0, 0, 0.2);
        }
        /* 其他模組按鈕樣式 */
        .other-button-container div.stButton > button {
            background-color: #f0f2f6; /* 淺灰色背景 */
            color: #333;
            font-size: 16px;
        }
        /* 其他模組 hover 效果 */
        .other-button-container div.stButton > button:hover {
            background-color: #e2e4e8;
            transform: translateY(-1px);
        }
        </style>
        """, unsafe_allow_html=True)


    # 5. 主控面板內容
    st.title("🧭 設備管理主控面板")
    st.markdown("---")

    # 🔷 核心系統模組（最大按鈕）
    st.header("核心系統模組")
    st.markdown("處理日常核心業務流程。")
    st.markdown('<div class="core-button-container">', unsafe_allow_html=True)
    col_db1, col_db2 = st.columns([1, 1])
    with col_db1:
        st.page_link("pages/equipment_system.py", label="📋 設備請購維修系統", icon=" ", use_container_width=True)
    with col_db2:
        st.page_link("pages/maintenance_log.py", label="🧾 設備檢修保養履歷", icon=" ", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # 🔹 資料管理與報表模組
    st.header("資料管理與報表")
    st.markdown('<div class="other-button-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.page_link("pages/new_equipment.py", label="🆕 新增設備", icon=" ")
        st.page_link("pages/add_event.py", label="🆕 新增保養事件", icon=" ")
        st.page_link("pages/edit_data.py", label="✏️ 編輯設備資料", icon=" ")
        st.page_link("pages/report_abnormal.py", label="📸 設備異常回報系統", icon=" ")
        st.page_link("pages/export_abnormal.py", label="📤 匯出異常報告", icon=" ")


    with col2:
        st.page_link("pages/view_main_equipment.py", label="🔍 主設備資料總覽", icon=" ")
        st.page_link("pages/view_maintenance_log.py", label="🔍 保養履歷資料總覽", icon=" ")
        st.page_link("pages/abnormal_overview.py", label="📋 異常紀錄總覽", icon=" ")
        st.page_link("pages/delete_data.py", label="🗑️ 刪除設備資料", icon=" ")
        st.page_link("pages/guide.py", label="📘 使用者手冊", icon=" ")
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("海運組油氣處理課")
