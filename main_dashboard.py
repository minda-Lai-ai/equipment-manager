# main_dashboard.py - 使用 Streamlit Authenticator 的設備管理主控面板（最終、最穩健版本）

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# --- 1. 頁面配置 ---
st.set_page_config(page_title="🧭 設備管理主控面板", layout="wide")

# --- 2. 載入驗證配置 ---
try:
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    
    # 載入錯誤檢查
    required_keys = ['cookie', 'credentials']
    if not isinstance(config, dict) or not all(key in config for key in required_keys):
        st.error("⚠️ config.yaml 載入結構錯誤：缺少 'cookie' 或 'credentials' 區塊！")
        st.stop()
        
except FileNotFoundError:
    st.error("⚠️ 找不到 config.yaml 檔案，請檢查檔案是否在根目錄！")
    st.stop()
except Exception as e:
    st.error(f"⚠️ 載入 config.yaml 時發生錯誤：{e}")
    st.stop()

# --- *** 檢查版本資訊 (FOR DEBUG) *** ---
st.sidebar.caption(f"Streamlit 版本: {st.__version__}")
try:
    st.sidebar.caption(f"Authenticator 版本: {stauth.__version__}")
except AttributeError:
    st.sidebar.caption("Authenticator 版本: (未找到)")
# --- ********************************* ---

# --- 3. 初始化 Authenticator ---
cookie_config = config.get('cookie', {})

# *** 核心修正區域：驗證 Authenticator 的初始化參數 ***
# 確保所有參數都是有效值，如果缺失則給予合理的預設值或報錯
try:
    authenticator = stauth.Authenticate(
        config['credentials'],
        # 確保 'name' 和 'key' 存在且為字串
        cookie_config.get('name', 'default_cookie'),
        cookie_config.get('key', 'default_secret_key'),
        # 確保 'expiry_days' 存在且為數字
        cookie_config.get('expiry_days', 30)
    )
except Exception as e:
    st.error(f"⚠️ Authenticator 初始化失敗，請檢查 config.yaml 中的 credentials 或 cookie 欄位: {e}")
    st.stop()

# --- 4. 登入 UI（主頁面） ---
st.title("🔐 使用者登入")

# 接收返回值，這是最穩定的做法
name, authentication_status, username = authenticator.login('🔑 登入系統', location='main') 

# --- 5. 處理登入狀態 (依賴區域變數) ---

if authentication_status is False:
    st.error("❌ 用戶名或密碼錯誤")
    st.warning("⚠️ 請檢查用戶名和密碼後重試")
elif authentication_status is None:
    st.info("👆 請輸入用戶名和密碼，然後按「🔑 登入系統」")
elif authentication_status:
    # 成功登入
    st.sidebar.success(f"✅ 已登入：{name} ({username})")
    authenticator.logout('🚪 登出', 'sidebar', key='logout_button')

    # --- 6. 主控面板內容 ---
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] { border-right: 1px solid rgba(49, 51, 63, 0.2); }
        .big-font { font-size: 18px !important; font-weight: bold; }
        .stPageLink { border: 1px solid #ddd; border-radius: 8px; padding: 10px; margin-bottom: 10px; 
                     transition: all 0.2s; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.05); }
        .stPageLink:hover { box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.1); transform: translateY(-2px); }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("🧭 設備管理主控面板")
    st.markdown("歡迎來到設備管理系統。請選擇下列功能進入各模組頁面。")
    st.markdown("---")

    # 核心系統模組
    st.header("⚙️ 核心系統與流程")
    col_db1, col_db2 = st.columns(2)
    with col_db1:
        st.page_link("pages/equipment_system.py", label="設備請購維修系統", icon="📋", use_container_width=True)
    with col_db2:
        st.page_link("pages/maintenance_log.py", label="設備檢修保養履歷", icon="🧾", use_container_width=True)

    st.markdown("---")

    # 資料管理與操作
    st.header("💾 資料管理與操作")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.page_link("pages/new_equipment.py", label="🆕 新增設備", icon="🆕")
        st.page_link("pages/view_main_equipment.py", label="🔍 主設備資料總覽", icon="🔍")
    with col2:
        st.page_link("pages/edit_data.py", label="✏️ 編輯設備資料", icon="✏️")
        st.page_link("pages/delete_data.py", label="🗑️ 刪除設備資料", icon="🗑️")
    with col3:
        st.page_link("pages/add_event.py", label="🆕 新增保養事件", icon="🆕")
        st.page_link("pages/view_maintenance_log.py", label="🔍 保養履歷總覽", icon="🔍")

    st.markdown("---")

    # 報表與系統輔助
    st.header("📊 報表與系統輔助")
    col4, col5 = st.columns(2)
    with col4:
        st.page_link("pages/report_abnormal.py", label="📸 設備異常回報系統", icon="📸")
        st.page_link("pages/abnormal_overview.py", label="📋 異常紀錄總覽", icon="📋")
    with col5:
        st.page_link("pages/export_abnormal.py", label="📤 匯出異常報告", icon="📤")
        st.page_link("pages/guide.py", label="📘 使用者手冊", icon="📘")

    st.markdown("---")
    st.caption("海運組油氣處理課")

