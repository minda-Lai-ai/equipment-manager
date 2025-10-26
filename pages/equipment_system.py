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

st.set_page_config(page_title="📋 設備請購維修系統", layout="wide")
st.title("📋 設備請購維修系統")
if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")
st.markdown("---")

# 直接載入雲端設備資料
result = supabase.table("main_equipment_system").select("*").execute()
df = pd.DataFrame(result.data)

required_columns = ["主設備", "次設備", "設備", "設備請購維修編號", "設備狀況"]
missing = [col for col in required_columns if col not in df.columns]
if missing:
    st.error(f"❌ 資料庫缺少欄位：{', '.join(missing)}")
    st.stop()

# 四階選單
main_equipment_list = sorted(df["主設備"].dropna().unique())
selected_main = st.selectbox("選擇主設備", main_equipment_list)
filtered_df_1 = df[df["主設備"] == selected_main]

sub_equipment_list = sorted(filtered_df_1["次設備"].dropna().unique())
selected_sub = st.selectbox("選擇次設備", sub_equipment_list)
filtered_df_2 = filtered_df_1[filtered_df_1["次設備"] == selected_sub]

equipment_list = sorted(filtered_df_2["設備"].dropna().unique())
selected_equipment = st.selectbox("選擇設備", equipment_list)
filtered_df_3 = filtered_df_2[filtered_df_2["設備"] == selected_equipment]

id_list = sorted(filtered_df_3["設備請購維修編號"].dropna().unique())
selected_id = st.selectbox("選擇設備請購維修編號", id_list)

row = filtered_df_3[filtered_df_3["設備請購維修編號"] == selected_id]
if row.empty:
    st.warning("⚠️ 找不到該設備資料列，請確認資料庫內容")
    st.stop()

row = row.iloc[0]
st.subheader(f"🛠️ 設備：{row['設備']}（{selected_id}）")
st.markdown(f"**設備狀況**：{row['設備狀況']}  \n**備註**：{row.get('備註', '')}")

if st.button("🔍 查看詳細資料"):
    st.session_state["selected_equipment_id"] = selected_id
    st.switch_page("pages/equipment_detail.py")
