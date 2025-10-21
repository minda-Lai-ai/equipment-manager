# main_dashboard.py - 設備管理系統主控面板
import streamlit as st
import time
from firebase_init import get_firestore_client 

# 設定頁面配置
st.set_page_config(page_title="🧭 設備管理主控面板", layout="wide")

# --------------------
# 注入美化 CSS 樣式
# --------------------
st.markdown("""
<style>
/* 隱藏 Streamlit 預設標籤和頁腳 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* 主標題樣式 */
h1 {
    color: #007BFF; /* 藍色主題 */
    border-bottom: 3px solid #007BFF;
    padding-bottom: 10px;
}

/* 按鈕樣式 (使用 Streamlit 的 page_link 模擬卡片按鈕) */
.stPageLink {
    text-decoration: none !important;
    color: inherit !important;
}

.card-button {
    background-color: #F8F9FA; /* 淺灰色背景 */
    border: 1px solid #DEE2E6; /* 邊框 */
    border-radius: 12px;
    padding: 15px 20px;
    margin-bottom: 10px;
    transition: all 0.2s ease-in-out;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    text-align: left;
}

.card-button:hover {
    background-color: #E9ECEF; /* 略深 */
    box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
}

.card-title {
    font-size: 1.15em;
    font-weight: bold;
    color: #343A40;
    margin-top: 5px;
}

.card-icon {
    font-size: 1.5em;
    margin-right: 10px;
}

/* 核心模組按鈕 (加大) */
.core-module .card-button {
    background-color: #D6EAF8; /* 淺藍色背景 */
    border-left: 5px solid #007BFF;
    padding: 25px 30px;
}
.core-module .card-button:hover {
    background-color: #BEE3F8;
}
</style>
""", unsafe_allow_html=True)

# --------------------
# 🔐 登入檢查
# --------------------
if "user" not in st.session_state:
    st.warning("⚠️ 請先登入才能使用系統")
    # 修正路徑：假設 login.py 在 pages/ 中
    st.page_link("pages/login.py", label="🔐 前往登入頁面", icon="🔑", help="點擊此處登入系統")
    st.stop()

# --------------------
# 初始化 Firestore
# --------------------
# 使用 st.cache_resource 確保穩定初始化
db = get_firestore_client() 

# --------------------
# 👤 顯示登入者資訊 & 🚪 登出按鈕
# --------------------
user = st.session_state["user"]
st.sidebar.success(f"👤 登入者：{user['name']}（{user['email']}）")

if st.sidebar.button("🚪 登出", use_container_width=True):
    st.session_state.clear()
    st.success("已登出，正在導向登入頁面...")
    time.sleep(0.5)
    # 修正登出導向：導向 pages/login.py
    st.switch_page("pages/login.py") 


# --------------------
# 🧭 主控面板內容
# --------------------
st.title("🧭 設備管理主控面板")
st.markdown("---")

# 1. 核心系統模組
st.header("⚙️ 核心系統與流程")
st.markdown('<div class="core-module">', unsafe_allow_html=True)
col_core1, col_core2 = st.columns(2)

with col_core1:
    # 設備請購維修系統 (使用 CSS 樣式)
    st.markdown(
        f'<div class="card-button">📋 <span class="card-title">設備請購維修系統</span></div>',
        unsafe_allow_html=True
    )
    st.page_link("pages/equipment_system.py", label="設備請購維修系統", icon="📋", help="進入請購與維修的作業流程", use_container_width=True)

with col_core2:
    # 設備檢修保養履歷 (使用 CSS 樣式)
    st.markdown(
        f'<div class="card-button">🧾 <span class="card-title">設備檢修保養履歷</span></div>',
        unsafe_allow_html=True
    )
    st.page_link("pages/maintenance_log.py", label="設備檢修保養履歷", icon="🧾", help="查看所有設備的保養紀錄", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# 2. 資料庫管理模組
st.header("🗄️ 資料庫管理與維護")
col1, col2 = st.columns(2)

with col1:
    st.subheader("新增與編輯")
    st.page_link("pages/new_equipment.py", label="🆕 新增設備資料", icon="➕", help="將新設備加入資料庫")
    st.page_link("pages/add_event.py", label="🆕 新增保養事件", icon="📅", help="記錄設備保養或檢修事件")
    st.page_link("pages/edit_data.py", label="✏️ 編輯設備資料", icon="📝", help="修改現有設備的資訊")
    
with col2:
    st.subheader("瀏覽與查詢")
    st.page_link("pages/view_main_equipment.py", label="🔍 主設備資料總覽", icon="🏢", help="瀏覽所有設備的基本資訊")
    st.page_link("pages/view_maintenance_log.py", label="🔍 保養履歷資料總覽", icon="⏳", help="查看所有保養紀錄")
    st.page_link("pages/equipment_detail.py", label="🔍 設備詳細資料", icon="ℹ️", help="查詢特定設備的詳細資訊")

st.markdown("---")

# 3. 報表與工具模組
st.header("🛠️ 報表與系統工具")
col3, col4 = st.columns(2)

with col3:
    st.page_link("pages/report_abnormal.py", label="📸 設備異常回報系統", icon="🚨", help="快速回報設備異常狀況")
    st.page_link("pages/abnormal_overview.py", label="📋 異常紀錄總覽", icon="📈", help="查看和管理所有異常紀錄")
    st.page_link("pages/export_abnormal.py", label="📤 匯出異常報告", icon="📁", help="匯出異常紀錄報表")


with col4:
    st.page_link("pages/save_data.py", label="💾 資料儲存模組", icon="☁️", help="手動備份或儲存數據")
    st.page_link("pages/export_image.py", label="🖼️ 圖片儲存模組", icon="🖼️", help="管理與查看上傳的圖片資產")
    st.page_link("pages/delete_data.py", label="🗑️ 刪除設備資料", icon="❌", help="永久刪除設備紀錄")
    st.page_link("pages/guide.py", label="📘 使用者手冊", icon="❓", help="系統操作指南")


st.markdown("---")
st.caption("© 海運組油氣處理課 - 設備管理系統")
