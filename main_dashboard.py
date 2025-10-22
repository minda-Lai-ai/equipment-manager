# main_dashboard.py - 設備管理主控面板 (移除登入，強化視覺與響應式設計)

import streamlit as st

# --- 1. 頁面配置 ---
# 使用 'wide' 佈局以最大化桌面空間
st.set_page_config(
    page_title="🧭 設備管理主控面板", 
    layout="wide",
    initial_sidebar_state="collapsed" # 預設收起側邊欄，釋放手機螢幕空間
)

# --- 2. 自定義 CSS 樣式 (關鍵：響應式設計與視覺優化) ---
# 使用 Streamlit 的自定義 CSS 技巧來優化 page_link 的外觀
st.markdown(
    """
    <style>
    /* 設定字體和主要佈局 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;500;700&display=swap');
    html, body, [class*="st-emotion-"] {
        font-family: 'Noto Sans TC', sans-serif;
    }

    /* 隱藏預設的 Streamlit 側邊欄開關 */
    [data-testid="stSidebarContent"] {
        padding: 0;
    }

    /* 主標題樣式 */
    h1 {
        font-weight: 700;
        color: #0E7490; /* 藍綠色強調 */
        border-bottom: 2px solid #E0F2F7;
        padding-bottom: 10px;
    }

    /* 模組標題樣式 */
    h2 {
        font-weight: 600;
        color: #0E7490;
        margin-top: 30px;
        margin-bottom: 15px;
    }

    /* 響應式卡片樣式：將 st.page_link 包裝成漂亮的卡片 */
    .stPageLink {
        /* 基礎卡片樣式 */
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease-in-out;
        background-color: #FFFFFF;
        
        /* 確保內容居中且圖標和文字清晰 */
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* 卡片懸停效果 */
    .stPageLink:hover {
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
        transform: translateY(-3px);
        border-color: #0E7490;
    }
    
    /* 調整 st.page_link 的圖標大小和顏色 */
    .stPageLink .st-emotion-table {
        font-size: 24px !important;
        color: #0E7490; /* 匹配主色調 */
        min-width: 30px; /* 確保圖標區域固定 */
        text-align: center;
    }

    /* 調整 st.page_link 的文字樣式 */
    .stPageLink p {
        font-size: 16px;
        font-weight: 500;
        margin: 0;
        color: #333333;
    }

    /* 針對手機屏幕的響應式調整 */
    @media (max-width: 768px) {
        /* 在手機上，讓頁面內容更緊湊 */
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        /* 在手機上，將卡片拉伸至全寬，且間距更小 */
        .stPageLink {
            width: 100%;
            margin-bottom: 10px;
            padding: 12px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 3. 頁面內容 ---

st.title("🧭 設備管理主控面板")
st.markdown("---")

st.markdown(
    """
    <p style="font-size: 18px; color: #555;">
    歡迎來到**海運組油氣處理課**設備管理系統。請點擊下列卡片進入各模組頁面。
    </p>
    """,
    unsafe_allow_html=True
)

# --- 核心系統與流程 (兩欄佈局，手機自動堆疊) ---
st.header("⚙️ 核心系統與流程")

# 桌面顯示兩欄，手機顯示一欄
col_db1, col_db2 = st.columns(2)
with col_db1:
    st.page_link("pages/equipment_system.py", 
                 label="設備請購維修系統", 
                 icon="📋", 
                 use_container_width=True)
with col_db2:
    st.page_link("pages/maintenance_log.py", 
                 label="設備檢修保養履歷", 
                 icon="🧾", 
                 use_container_width=True)


# --- 資料管理與操作 (三欄佈局，手機自動堆疊) ---
st.header("💾 資料管理與操作")

# 桌面顯示三欄，手機顯示一欄
col1, col2, col3 = st.columns(3)
with col1:
    st.page_link("pages/new_equipment.py", 
                 label="🆕 新增設備", 
                 icon="🆕", 
                 use_container_width=True)
    st.page_link("pages/view_main_equipment.py", 
                 label="🔍 主設備資料總覽", 
                 icon="🔍", 
                 use_container_width=True)
with col2:
    st.page_link("pages/edit_data.py", 
                 label="✏️ 編輯設備資料", 
                 icon="✏️", 
                 use_container_width=True)
    st.page_link("pages/delete_data.py", 
                 label="🗑️ 刪除設備資料", 
                 icon="🗑️", 
                 use_container_width=True)
with col3:
    st.page_link("pages/add_event.py", 
                 label="🆕 新增保養事件", 
                 icon="🛠️", # 使用新的圖標來區分新增設備
                 use_container_width=True)
    st.page_link("pages/view_maintenance_log.py", 
                 label="🔍 保養履歷總覽", 
                 icon="🔍", 
                 use_container_width=True)

# --- 報表與系統輔助 (兩欄佈局，手機自動堆疊) ---
st.header("📊 報表與系統輔助")

col4, col5 = st.columns(2)
with col4:
    st.page_link("pages/report_abnormal.py", 
                 label="📸 設備異常回報系統", 
                 icon="📸", 
                 use_container_width=True)
    st.page_link("pages/abnormal_overview.py", 
                 label="📋 異常紀錄總覽", 
                 icon="📋", 
                 use_container_width=True)
with col5:
    st.page_link("pages/export_abnormal.py", 
                 label="📤 匯出異常報告", 
                 icon="📤", 
                 use_container_width=True)
    st.page_link("pages/guide.py", 
                 label="📘 使用者手冊", 
                 icon="📘", 
                 use_container_width=True)

st.markdown("---")
st.caption("© 海運組油氣處理課 - 設備管理系統")
