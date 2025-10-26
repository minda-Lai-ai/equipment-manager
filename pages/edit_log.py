import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime, timedelta

SUPABASE_URL = "https://todjfbmcaxecrqlkkvkd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvZGpmYm1jYXhlY3JxbGtrdmtkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzMjk3NDgsImV4cCI6MjA3NjkwNTc0OH0.0uTJcrHwvnGM8YT1bPHzMyGkQHIJUZWXsVEwEPjp0sA"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 權限檢查
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("尚未登入或登入已逾時，請回主畫面重新登入。")
    st.stop()
st.sidebar.markdown("---")
st.sidebar.write(f"👤 使用者：{st.session_state['username']}")
st.sidebar.write(f"🧩 角色：{st.session_state['role']}")

st.set_page_config(page_title="🔧 修改紀錄", layout="wide")
st.title("🔧 修改紀錄總覽")

# 載入雲端紀錄
result = supabase.table("edit_log").select("*").execute()
log_df = pd.DataFrame(result.data)

# 篩選刪除日期
st.markdown("### 🗓️ 自動清除過期紀錄")
days = st.number_input("輸入刪除期限（天）", min_value=1, value=90)
cutoff = datetime.now() - timedelta(days=days)

# 篩選過期
log_df["時間戳記"] = pd.to_datetime(log_df["時間戳記"], errors="coerce")
filtered_df = log_df[log_df["時間戳記"] >= cutoff]

# 顯示紀錄
st.markdown("---")
st.subheader("📋 修改紀錄表格")

if filtered_df.empty:
    st.info("目前沒有修改紀錄")
else:
    for i, row in filtered_df.iterrows():
        expander_title = f"🛠️ {row['設備請購維修編號']} | {row['欄位名稱']}"
        with st.expander(expander_title):
            st.markdown(f"**修改時間**：{row['時間戳記']}")
            st.markdown(f"**來源模組**：{row['來源模組']}")
            st.markdown(f"**原始值**：`{row['原始值']}`")
            st.markdown(f"**新值**：`{row['新值']}`")
            if st.button(f"🗑️ 刪除此紀錄", key=f"del_{row['id']}"):
                supabase.table("edit_log").delete().eq("id", row["id"]).execute()
                st.success("✅ 已刪除該筆紀錄")
                st.experimental_rerun()

# 自動批次清除所有過期
if st.button("🧹 批次刪除所有過期紀錄"):
    expired_ids = log_df[log_df["時間戳記"] < cutoff]["id"].tolist()
    for eid in expired_ids:
        supabase.table("edit_log").delete().eq("id", eid).execute()
    st.success(f"✅ 已批次刪除 {len(expired_ids)} 筆過期紀錄")
    st.experimental_rerun()
