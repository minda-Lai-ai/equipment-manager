import streamlit as st
from supabase import create_client
import pandas as pd
from modules.four_level_selector import four_level_selector
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

st.set_page_config(page_title="🗑️ 刪除設備資料", layout="wide")
st.title("🗑️ 刪除設備資料")
if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

# 透過 supabase 取設備 (四階選單)
main_result = supabase.table("main_equipment_system").select("*").execute()
main_df = pd.DataFrame(main_result.data)
result = four_level_selector(main_df)
filtered_df = result["filtered_df"]

if filtered_df.empty:
    st.warning("⚠️ 找不到符合條件的設備")
    st.stop()

row = filtered_df.iloc[0]
eid = row["設備請購維修編號"]

st.markdown("---")
st.subheader("🧮 即將刪除的設備資料")
for col in row.index:
    st.markdown(f"🔸 **{col}**：{row[col]}")

if st.button("🗑️ 確認刪除"):
    # 雲端備份 (選擇性) 可寫 export 但這裡僅作說明，如需再補流程
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # 刪除主表
    supabase.table("main_equipment_system").delete().eq("設備請購維修編號", eid).execute()
    # 刪除所有該筆設備履歷
    supabase.table("history_maintenance_log").delete().eq("設備請購維修編號", eid).execute()
    st.success(f"✅ 已刪除設備與履歷：{eid}")
