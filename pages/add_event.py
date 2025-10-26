import streamlit as st
import pandas as pd
from supabase import create_client
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

st.set_page_config(page_title="🆕 新增保養事件", layout="wide")
st.title("🆕 新增保養事件")

if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

# 從 Supabase 讀設備
result = supabase.table("main_equipment_system").select("*").execute()
main_df = pd.DataFrame(result.data)

result = four_level_selector(main_df)
filtered_df = result["filtered_df"]

if filtered_df.empty:
    st.warning("⚠️ 找不到符合條件的設備")
    st.stop()

row = filtered_df.iloc[0]
original = {
    "主設備": row["主設備"],
    "次設備": row["次設備"],
    "設備": row["設備"],
    "設備請購維修編號": row["設備請購維修編號"],
    "事件日期": "",
    "事件類型": "",
    "事件描述": "",
    "備註": ""
}

if "event_buffer" not in st.session_state:
    st.session_state.event_buffer = original.copy()

st.markdown("---")
st.subheader("✏️ 新增事件欄位")

with st.form("event_form"):
    for col in original:
        st.session_state.event_buffer[col] = st.text_input(f"{col}", value=st.session_state.event_buffer[col])
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        back = st.form_submit_button("🔙 上一步")
    with col2:
        reset = st.form_submit_button("🔄 復原")
    with col3:
        compare = st.form_submit_button("⏭️ 下一步")
    with col4:
        save = st.form_submit_button("💾 儲存")

if reset:
    st.session_state.event_buffer = original.copy()
    st.info("🔄 已復原為初始欄位")

if compare:
    st.markdown("---")
    st.subheader("🧮 新增事件內容比較")
    for col in original:
        old = original[col]
        new = st.session_state.event_buffer[col]
        if old != new:
            st.markdown(f"🔸 **{col}**：`{old}` → `🆕 {new}`")
        else:
            st.markdown(f"▫️ {col}：`{old}`（未變更）")

if save:
    supabase.table("history_maintenance_log").insert([st.session_state.event_buffer]).execute()
    st.success(f"✅ 已新增事件：{st.session_state.event_buffer['事件類型']}（{st.session_state.event_buffer['設備請購維修編號']}）")

