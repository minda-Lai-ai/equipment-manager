import streamlit as st
from supabase import create_client
import pandas as pd

supabase = create_client(
    "https://todjfbmcaxecrqlkkvkd.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvZGpmYm1jYXhlY3JxbGtrdmtkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzMjk3NDgsImV4cCI6MjA3NjkwNTc0OH0.0uTJcrHwvnGM8YT1bPHzMyGkQHIJUZWXsVEwEPjp0sA"
)

# 權限檢查
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("尚未登入或登入已逾時，請回主畫面重新登入。")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.write(f"👤 使用者：{st.session_state['username']}")
st.sidebar.write(f"🧩 角色：{st.session_state['role']}")

st.set_page_config(page_title="瀏覽資料", layout="wide")
st.title("🔍 瀏覽資料庫內容")
if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")
st.markdown("---")

db_choice = st.radio("選擇資料庫", ["設備請購維修系統", "設備檢修保養履歷"])

if db_choice == "設備請購維修系統":
    result = supabase.table("main_equipment_system").select("*").execute()
    df = pd.DataFrame(result.data)
else:
    result = supabase.table("history_maintenance_log").select("*").execute()
    df = pd.DataFrame(result.data)

st.subheader(f"📘 顯示：{db_choice}")
st.dataframe(df, use_container_width=True)
