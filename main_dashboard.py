import streamlit as st
import time
from firebase_init import get_firestore_client

st.set_page_config(
    page_title="🧭 設備管理主控面板", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS 美化 ---
st.markdown("""
<style>
/* 隱藏 Streamlit 預設的 main menu 和 footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* 主頁標題樣式 */
.main-title {
    font-size: 2.5em;
    font-weight: bold;
    color: #0d47a1; /* 深藍色 */
    margin-bottom: 0.5em;
}

/* 按鈕卡片容器樣式 */
.link-card-container {
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

/* 核心系統區塊 (深藍色背景) */
.core-system {
    background-color: #e3f2fd; /* 淺藍色背景 */
    border-left: 5px solid #1565c0; /* 左側深藍色標記 */
}

/* 資料管理區塊 (綠色背景) */
.data-management {
    background-color: #e8f5e9; /* 淺綠色背景 */
    border-left: 5px solid #2e7d32; /* 左側深綠色標記 */
}

/* 其他工具區塊 (灰色背景) */
.other-tools {
    background-color: #f5f5f5; /* 淺灰色背景 */
    border-left: 5px solid #424242; /* 左側灰色標記 */
}

/* 調整 st.page_link 的樣式，讓它填滿容器並美觀 */
/* 注意：這個樣式對 Streamlit 內建的 page_link 影響有限，主要影響容器 */
.stPageLink {
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)
# --- CSS 結束 ---

# 🔐 登入檢查 (如果沒有 'user' 狀態，則停止並導向登入頁面)
if "user" not in st.session_state:
    st.warning("⚠️ 請先登入才能使用系統")
    # ***修正路徑***：導向 pages/login.py
    st.page_link("pages/login.py", label="🔐 前往登入頁面", icon="🔑")
    st.stop()

# 呼叫快取過的函式
try:
    db = get_firestore_client()  
except Exception as e:
    st.error(f"❌ 無法連線到 Firestore。請檢查金鑰配置。錯誤: {e}")
    st.stop()

# 👤 顯示登入者資訊 (在側邊欄)
user = st.session_state["user"]
st.sidebar.success(f"👤 登入者：{user['name']}（{user['email']}）")

# 🚪 登出按鈕 (在側邊欄)
def logout():
    st.session_state.clear()
    # ***修正路徑***：登出後導向 pages/login.py
    st.switch_page("pages/login.py") 

if st.sidebar.button("🚪 登出", use_container_width=True):
    # 增加一個短暫的提示，讓使用者知道正在登出
    st.toast("正在登出...", icon='🚪')
    time.sleep(0.5)
    logout()

# --- 主控面板內容 ---
st.markdown('<h1 class="main-title">🧭 設備管理主控面板</h1>', unsafe_allow_html=True)
st.info("👋 歡迎回來！請透過下方模組進入系統功能。")

# 1. 核心系統模組 (Core System)
st.markdown("## ⚙️ 核心系統與主要流程", help="設備從請購、維修到履歷紀錄的主要功能。")
st.markdown('<div class="link-card-container core-system">', unsafe_allow_html=True)

col_core1, col_core2 = st.columns(2)

with col_core1:
    st.markdown('<p style="font-size:1.2em; font-weight:bold; color:#1565c0;">🛠️ 設備請購/維修系統</p>', unsafe_allow_html=True)
    st.page_link("pages/equipment_system.py", label="📋 設備請購維修單", icon="📋", use_container_width=True)

with col_core2:
    st.markdown('<p style="font-size:1.2em; font-weight:bold; color:#1565c0;">🧾 檢修與保養履歷</p>', unsafe_allow_html=True)
    st.page_link("pages/maintenance_log.py", label="🧾 設備檢修保養履歷", icon="🧾", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("---")


# 2. 資料管理模組 (Data Management)
st.markdown("## 📊 資料庫與紀錄管理", help="用來新增、編輯和總覽設備與保養數據的功能。")
st.markdown('<div class="link-card-container data-management">', unsafe_allow_html=True)

col_data1, col_data2, col_data3 = st.columns(3)

with col_data1:
    st.markdown('<p style="font-weight:bold; color:#2e7d32;">🆕 新增資料</p>', unsafe_allow_html=True)
    st.page_link("pages/new_equipment.py", label="🆕 新增設備", icon="🛠️", use_container_width=True)
    st.page_link("pages/add_event.py", label="🆕 新增保養事件", icon="📅", use_container_width=True)
    st.page_link("pages/save_data.py", label="💾 資料儲存模組", icon="💾", use_container_width=True) 

with col_data2:
    st.markdown('<p style="font-weight:bold; color:#2e7d32;">🔍 總覽與瀏覽</p>', unsafe_allow_html=True)
    st.page_link("pages/view_main_equipment.py", label="🔍 主設備資料總覽", icon="🏢", use_container_width=True)
    st.page_link("pages/view_maintenance_log.py", label="🔍 保養履歷資料總覽", icon="📜", use_container_width=True)
    st.page_link("pages/view_data.py", label="🔍 瀏覽資料庫內容", icon="📖", use_container_width=True)

with col_data3:
    st.markdown('<p style="font-weight:bold; color:#2e7d32;">✏️ 編輯與移除</p>', unsafe_allow_html=True)
    st.page_link("pages/edit_data.py", label="✏️ 編輯設備資料", icon="✏️", use_container_width=True)
    st.page_link("pages/equipment_detail.py", label="🔍 設備詳細資料", icon="🔎", use_container_width=True)
    st.page_link("pages/delete_data.py", label="🗑️ 刪除設備資料", icon="🗑️", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("---")


# 3. 異常與輔助工具模組 (Abnormal & Tools)
st.markdown("## 🚨 異常回報與輔助工具", help="用於緊急回報和系統輔助功能。")
st.markdown('<div class="link-card-container other-tools">', unsafe_allow_html=True)

col_tool1, col_tool2 = st.columns(2)

with col_tool1:
    st.markdown('<p style="font-weight:bold; color:#424242;">🚨 異常處理</p>', unsafe_allow_html=True)
    st.page_link("pages/report_abnormal.py", label="📸 設備異常回報系統", icon="🚨", use_container_width=True)
    st.page_link("pages/abnormal_overview.py", label="📋 異常紀錄總覽", icon="📑", use_container_width=True)

with col_tool2:
    st.markdown('<p style="font-weight:bold; color:#424242;">🔧 系統工具</p>', unsafe_allow_html=True)
    st.page_link("pages/export_abnormal.py", label="📤 匯出異常報告", icon="📥", use_container_width=True)
    st.page_link("pages/export_image.py", label="🖼️ 圖片儲存模組", icon="🖼️", use_container_width=True)
    st.page_link("pages/guide.py", label="📘 使用者手冊", icon="📖", use_container_width=True)


st.markdown('</div>', unsafe_allow_html=True)
st.caption("© 海運組油氣處理課 - 設備管理系統")
