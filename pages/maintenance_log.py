import streamlit as st
from supabase import create_client
import pandas as pd
from modules.four_level_selector import four_level_selector

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

st.set_page_config(page_title="🧾 設備檢修保養履歷", layout="wide")
st.title("🧾 設備檢修保養履歷")
if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

# 四階選單來自雲端設備表
main_result = supabase.table("main_equipment_system").select("*").execute()
main_df = pd.DataFrame(main_result.data)
result = four_level_selector(main_df)
filtered_df = result["filtered_df"]

if filtered_df.empty:
    st.warning("⚠️ 找不到符合條件的設備")
    st.stop()
eid = result["selected_id"]
if eid == "無":
    st.warning("⚠️ 請選擇設備請購維修編號")
    st.stop()

# 從 Supabase 篩選取出該設備履歷
log_result = supabase.table("history_maintenance_log").select("*").eq("設備請購維修編號", eid).execute()
device_log = pd.DataFrame(log_result.data)
st.markdown("---")
st.subheader(f"📋 設備履歷：{eid}")
st.dataframe(device_log, use_container_width=True)

# 選擇事件
event_indices = device_log.index.tolist()
if not event_indices:
    st.warning("⚠️ 此設備尚無履歷紀錄")
    st.stop()
selected_index = st.selectbox("選擇事件資料列編號", event_indices)
selected_row = device_log.loc[selected_index]

if "log_buffer" not in st.session_state or st.session_state.get("eid") != eid or st.session_state.get("rowidx") != selected_index:
    st.session_state.log_buffer = selected_row.to_dict()
    st.session_state.log_original = selected_row.to_dict()
    st.session_state.edit_mode = False
    st.session_state.eid = eid
    st.session_state.rowidx = selected_index

st.markdown("---")
st.subheader("🔍 事件詳細資料")
if not st.session_state.edit_mode:
    for col in st.session_state.log_buffer:
        st.markdown(f"**{col}**：{st.session_state.log_buffer[col]}")
else:
    for col in st.session_state.log_buffer:
        st.session_state.log_buffer[col] = st.text_input(f"{col}", value=st.session_state.log_buffer[col])

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("✏️ 編輯整筆資料"):
        st.session_state.edit_mode = True
with col2:
    if st.button("🔄 復原"):
        st.session_state.log_buffer = st.session_state.log_original.copy()
        st.session_state.edit_mode = False
        st.info("🔄 已復原為原始資料")
with col3:
    if st.button("💾 儲存修改"):
        # 根據本筆資料唯一 id（假設有 id 欄位）直接寫回 Supabase
        record_id = selected_row["id"]  # 你的 table 必須有 id 主鍵
        supabase.table("history_maintenance_log").update(st.session_state.log_buffer).eq("id", record_id).execute()
        st.success(f"✅ 已儲存事件修改（資料列 {selected_index}）")
        st.session_state.edit_mode = False
