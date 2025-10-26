import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

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

st.set_page_config(page_title="資料儲存", layout="wide")
st.title("💾 資料儲存與備份")
if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")
st.markdown("---")

# 雲端 table 匯出
main_result = supabase.table("main_equipment_system").select("*").execute()
main_df = pd.DataFrame(main_result.data)
log_result = supabase.table("history_maintenance_log").select("*").execute()
log_df = pd.DataFrame(log_result.data)

date_tag = datetime.now().strftime("%Y%m%d")
main_filename = f"main_equipment_system_{date_tag}.csv"
log_filename = f"history_maintenance_log_{date_tag}.csv"

csv_main = '\ufeff' + main_df.to_csv(index=False)
csv_log = '\ufeff' + log_df.to_csv(index=False)

st.success("✅ 雲端資料已成功匯出(備份檔可下載)")
st.download_button("📁 下載主設備資料備份", data=csv_main.encode("utf-8"), file_name=main_filename, mime="text/csv")
st.download_button("📁 下載保養履歷資料備份", data=csv_log.encode("utf-8"), file_name=log_filename, mime="text/csv")
