# main_dashboard.py

import streamlit as st
import time
from firebase_init import get_firestore_client
import firebase_admin

# 頁面配置
st.set_page_config(page_title="🧭 設備管理主控面板", layout="wide")

# ----------------------------------------
# 注入美化 CSS (讓按鈕和頁面更好看)
# ----------------------------------------
st.markdown("""
<style>
/* Streamlit 主標題樣式 */
.st-emotion-cache-1j02r3h h1 {
    color: #1f77b4; /* 藍色 */
    font-weight: 700;
}

/* 讓 Streamlit 按鈕看起來像卡片 */
.st-emotion-cache-1f87530 a, .st-emotion-cache-1f87530 button {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 15px 10px;
    border-radius: 12px;
    box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease-in-out;
    background-color: #ffffff; /* 淺色背景 */
    color: #333333 !important;
    font-weight: 600;
    font-size: 16px;
    height: 100%; /* 確保容器內高度一致 */
}

/* Hover 效果 */
.st-emotion-cache-1f87530 a:hover, .st-emotion-cache-1f87530 button:hover {
    box-shadow: 5px 5px 15px rgba(0, 0, 0, 0.2);
    transform: translateY(-2px);
    border-color: #1f77b4;
    background-color: #e6f0ff; /* 淺藍色背景 */
}

/* 讓頁面內容更居中 */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* 核心模組（大按鈕）的特殊樣式 */
.core-module .st-emotion-cache-1f87530 a, .core-module .st-emotion-cache-1f87530 button {
    background-color: #d1e7f9; /* 更深的藍色調 */
    color: #1f77b4 !important;
    padding: 25px 15px;
    font-size: 18px;
    font-weight: 700;
}

.core-module .st-emotion-cache-1f87530 a:hover, .core-module .st-emotion-cache-1f87530 button:hover {
    background-color: #a0cff0;
}

/* 調整 sidebar success 訊息的樣式 */
.st-emotion-cache-6qob1r .st-emotion-cache-1ky9w80 {
    font-size: 16px;
    font-weight: 600;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)


# ----------------------------------------
# 🔐 登入檢查與 Firebase 初始化
# ----------------------------------------

# 檢查登入狀態
if "user" not in st.session_state:
    st.warning("⚠️ 請先登入才能使用系統")
    # 注意：假設 login.py 檔案在 pages/ 資料夾內
    st.page_link("pages/login.py", label="🔐 前往登入頁面", icon="🔑")
    st.stop()

# 獲取 Firestore 客戶端 (使用快取，包含錯誤診斷)
try:
    db = get_firestore_client()
except firebase_admin.exceptions.AppError:
    # 錯誤訊息會在 firebase_init.py 中顯示，這裡只需停止運行
    st.stop()
except Exception:
    # 如果 firebase_init.py 停止了但狀態沒更新
    st.stop()

# 👤 顯示登入者資訊
user = st.session_state["user"]
st.sidebar.success(f"👤 登入者：{user['name']} ({user['email']})")
st.sidebar.caption(f"權限：{user['role']}")

# 🚪 登出按鈕
if st.sidebar.button("🚪 登出", use_container_width=True):
    st.session_state.clear()
    st.success("🚪 您已登出。")
    time.sleep(0.5)
    # 導向登入頁面
    st.switch_page("pages/login.py")


# ----------------------------------------
# 🧭 主控面板內容
# ----------------------------------------

st.title("🧭 設備管理主控面板")
st.markdown("### 歡迎回來，請選擇功能模組。")
st.markdown("---")

# --------------------
# 區塊一：核心系統 (使用美化CSS中的 core-module 類別)
# --------------------
st.markdown("### 🔷 核心系統模組", unsafe_allow_html=True)
st.markdown('<div class="core-module">', unsafe_allow_html=True)
col_core1, col_core2 = st.columns(2)
with col_core1:
    st.page_link("pages/equipment_system.py", label="設備請購維修系統", icon="📋", use_container_width=True)
with col_core2:
    st.page_link("pages/maintenance_log.py", label="設備檢修保養履歷", icon="🧾", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# --------------------
# 區塊二：資料管理與檢視
# --------------------
st.markdown("### 🔹 資料管理與檢視", unsafe_allow_html=True)
col_data1, col_data2, col_data3 = st.columns(3)

with col_data1:
    st.page_link("pages/new_equipment.py", label="新增設備資料", icon="🆕", use_container_width=True)
    st.page_link("pages/add_event.py", label="新增保養事件", icon="📅", use_container_width=True)

with col_data2:
    st.page_link("pages/view_main_equipment.py", label="主設備資料總覽", icon="🔍", use_container_width=True)
    st.page_link("pages/view_maintenance_log.py", label="保養履歷資料總覽", icon="📑", use_container_width=True)

with col_data3:
    st.page_link("pages/edit_data.py", label="編輯設備資料", icon="✏️", use_container_width=True)
    st.page_link("pages/delete_data.py", label="刪除設備資料", icon="🗑️", use_container_width=True)

st.markdown("---")

# --------------------
# 區塊三：異常回報與報告
# --------------------
st.markdown("### ⚙️ 異常回報與報告", unsafe_allow_html=True)
col_report1, col_report2, col_report3 = st.columns(3)

with col_report1:
    st.page_link("pages/report_abnormal.py", label="設備異常回報系統", icon="📸", use_container_width=True)

with col_report2:
    st.page_link("pages/abnormal_overview.py", label="異常紀錄總覽", icon="📋", use_container_width=True)

with col_report3:
    st.page_link("pages/export_abnormal.py", label="匯出異常報告", icon="📤", use_container_width=True)

st.markdown("---")
st.caption("© 海運組油氣處理課 - 設備管理系統")
