import streamlit as st

# 權限檢查
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("尚未登入或登入已逾時，請回主畫面重新登入。")
    st.stop()

# 顯示登入者資訊於頁首或側邊欄
st.sidebar.markdown("---")
st.sidebar.write(f"👤 使用者：{st.session_state['username']}")
st.sidebar.write(f"🧩 角色：{st.session_state['role']}")

import pandas as pd
from modules.four_level_selector import four_level_selector
from datetime import datetime

st.set_page_config(page_title="🗑️ 刪除設備資料", layout="wide")
st.title("🗑️ 刪除設備資料")

if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

main_path = "data/main_equipment_system.csv"
log_path = "data/history_maintenance_log.csv"
main_df = pd.read_csv(main_path)
log_df = pd.read_csv(log_path)

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
    # 備份
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    main_df.to_csv(f"data/main_equipment_before_delete_{timestamp}.csv", index=False)
    log_df.to_csv(f"data/maintenance_log_before_delete_{timestamp}.csv", index=False)

    # 刪除
    main_df = main_df[main_df["設備請購維修編號"] != eid]
    log_df = log_df[log_df["設備請購維修編號"] != eid]

    main_df.to_csv(main_path, index=False)
    log_df.to_csv(log_path, index=False)

    st.success(f"✅ 已刪除設備與履歷：{eid}")
