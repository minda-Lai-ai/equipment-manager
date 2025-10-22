import streamlit as st
import pandas as pd
from modules.four_level_selector import four_level_selector

st.set_page_config(page_title="🧾 設備檢修保養履歷", layout="wide")
st.title("🧾 設備檢修保養履歷")

if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

# 載入資料庫
main_df = pd.read_csv("data/main_equipment_system.csv")
log_path = "data/history_maintenance_log.csv"
log_df = pd.read_csv(log_path)

# 四階選單
result = four_level_selector(main_df)
filtered_df = result["filtered_df"]

if filtered_df.empty:
    st.warning("⚠️ 找不到符合條件的設備")
    st.stop()

eid = result["selected_id"]
if eid == "無":
    st.warning("⚠️ 請選擇設備請購維修編號")
    st.stop()

# 篩選履歷
device_log = log_df[log_df["設備請購維修編號"] == eid]
st.markdown("---")
st.subheader(f"📋 設備履歷：{eid}")
st.dataframe(device_log, use_container_width=True)

# 選擇事件（依資料列 index）
event_indices = device_log.index.tolist()
selected_index = st.selectbox("選擇事件資料列編號", event_indices)

# 原始資料
original_row = device_log.loc[selected_index]
if "log_buffer" not in st.session_state:
    st.session_state.log_buffer = original_row.to_dict()
    st.session_state.log_original = original_row.to_dict()
    st.session_state.edit_mode = False

st.markdown("---")
st.subheader("🔍 事件詳細資料")

if not st.session_state.edit_mode:
    for col in st.session_state.log_buffer:
        st.markdown(f"**{col}**：{st.session_state.log_buffer[col]}")
else:
    for col in st.session_state.log_buffer:
        st.session_state.log_buffer[col] = st.text_input(f"{col}", value=st.session_state.log_buffer[col])

# 操作按鈕
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
        for col in st.session_state.log_buffer:
            log_df.at[selected_index, col] = st.session_state.log_buffer[col]
        log_df.to_csv(log_path, index=False)
        st.success(f"✅ 已儲存事件修改（資料列 {selected_index}）")
        st.session_state.edit_mode = False


