import streamlit as st

from supabase import create_client
import pandas as pd

supabase = create_client("https://todjfbmcaxecrqlkkvkd.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvZGpmYm1jYXhlY3JxbGtrdmtkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzMjk3NDgsImV4cCI6MjA3NjkwNTc0OH0.0uTJcrHwvnGM8YT1bPHzMyGkQHIJUZWXsVEwEPjp0sA")
result = supabase.table("history_maintenance_log").select("*").execute()
df = pd.DataFrame(result.data)

# 權限檢查
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("尚未登入或登入已逾時，請回主畫面重新登入。")
    st.stop()

# 顯示登入者資訊於頁首或側邊欄
st.sidebar.markdown("---")
st.sidebar.write(f"👤 使用者：{st.session_state['username']}")
st.sidebar.write(f"🧩 角色：{st.session_state['role']}")


import pandas as pd

st.set_page_config(page_title="🔍 保養履歷資料總覽", layout="wide")
st.title("🔍 保養履歷資料總覽")

if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

try:
    df = pd.read_csv("data/history_maintenance_log.csv")
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error(f"❌ 無法載入保養履歷資料庫：{e}")
    st.stop()

st.markdown("---")
st.markdown("📸 若需將資料另存為圖片，請使用下方工具：")

# 圖片儲存按鈕（可連結 export_image.py）
if st.button("🖼️ 將保養履歷匯出為圖片"):
    st.switch_page("pages/export_image.py")

