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
from datetime import datetime

st.set_page_config(page_title="資料儲存", layout="wide")
st.title("💾 資料儲存與備份")

# 返回主控面板
if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

st.markdown("---")

# 載入資料庫
main_df = pd.read_csv("data/main_equipment_system.csv")
log_df = pd.read_csv("data/history_maintenance_log.csv")

# 建立備份檔名
date_tag = datetime.now().strftime("%Y%m%d")
main_filename = f"data/main_equipment_system_{date_tag}.csv"
log_filename = f"data/history_maintenance_log_{date_tag}.csv"

# 儲存備份
main_df.to_csv(main_filename, index=False)
log_df.to_csv(log_filename, index=False)

st.success("✅ 資料已成功備份")
st.markdown(f"- 📁 `{main_filename}`")
st.markdown(f"- 📁 `{log_filename}`")

