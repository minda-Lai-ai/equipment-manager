import streamlit as st

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("尚未登入或權限不足，請由主畫面登入後再瀏覽此頁。")
    st.stop()

import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="🔧 修改紀錄", layout="wide")
st.title("🔧 修改紀錄總覽")

log_path = "data/edit_log.csv"

# 載入紀錄
try:
    log_df = pd.read_csv(log_path)
except:
    log_df = pd.DataFrame(columns=["時間戳記", "設備請購維修編號", "欄位名稱", "原始值", "新值", "來源模組"])

# 刪除期限設定
st.markdown("### 🗓️ 自動清除過期紀錄")
days = st.number_input("輸入刪除期限（天）", min_value=1, value=90)
cutoff = datetime.now() - timedelta(days=days)

# 清除過期紀錄
log_df["時間戳記"] = pd.to_datetime(log_df["時間戳記"], errors="coerce")
log_df = log_df[log_df["時間戳記"] >= cutoff]

# 顯示紀錄
st.markdown("---")
st.subheader("📋 修改紀錄表格")

if log_df.empty:
    st.info("目前沒有修改紀錄")
else:
    for i, row in log_df.iterrows():
        with st.expander(f"🛠️ {row['設備請購維修編號']} | {row['欄位名稱']}"):
            st.markdown(f"**修改時間**：{row['時間戳記']}")
            st.markdown(f"**來源模組**：{row['來源模組']}")
            st.markdown(f"**原始值**：`{row['原始值']}`")
            st.markdown(f"**新值**：`{row['新值']}`")
            if st.button(f"🗑️ 刪除此紀錄", key=f"del_{i}"):
                log_df.drop(index=i, inplace=True)
                log_df.to_csv(log_path, index=False)
                st.success("✅ 已刪除該筆紀錄")
                st.experimental_rerun()

# 儲存更新後紀錄
log_df.to_csv(log_path, index=False)

