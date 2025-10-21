import streamlit as st
import pandas as pd

# from auth_check import require_login
# require_login()

st.set_page_config(page_title="📋 設備請購維修系統", layout="wide")
st.title("📋 設備請購維修系統")

# 返回主控面板
if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

st.markdown("---")

# 載入資料庫
try:
    df = pd.read_csv("data/main_equipment_system.csv")
except Exception as e:
    st.error(f"❌ 無法載入設備資料庫：{e}")
    st.stop()

# 欄位檢查
required_columns = ["主設備", "次設備", "設備", "設備請購維修編號", "設備狀況"]
missing = [col for col in required_columns if col not in df.columns]
if missing:
    st.error(f"❌ 資料庫缺少欄位：{', '.join(missing)}")
    st.stop()

# 第一層：主設備
main_equipment_list = sorted(df["主設備"].dropna().unique())
selected_main = st.selectbox("選擇主設備", main_equipment_list)

# 第二層：次設備
filtered_df_1 = df[df["主設備"] == selected_main]
sub_equipment_list = sorted(filtered_df_1["次設備"].dropna().unique())
selected_sub = st.selectbox("選擇次設備", sub_equipment_list)

# 第三層：設備
filtered_df_2 = filtered_df_1[filtered_df_1["次設備"] == selected_sub]
equipment_list = sorted(filtered_df_2["設備"].dropna().unique())
selected_equipment = st.selectbox("選擇設備", equipment_list)

# 第四層：設備請購維修編號
filtered_df_3 = filtered_df_2[filtered_df_2["設備"] == selected_equipment]
id_list = sorted(filtered_df_3["設備請購維修編號"].dropna().unique())
selected_id = st.selectbox("選擇設備請購維修編號", id_list)

# 顯示摘要
row = filtered_df_3[filtered_df_3["設備請購維修編號"] == selected_id]
if row.empty:
    st.warning("⚠️ 找不到該設備資料列，請確認資料庫內容")
    st.stop()

row = row.iloc[0]
st.subheader(f"🛠️ 設備：{row['設備']}（{selected_id}）")
st.markdown(f"**設備狀況**：{row['設備狀況']}  \n**備註**：{row.get('備註', '')}")

# 詳細資料按鈕
if st.button("🔍 查看詳細資料"):
    st.session_state["selected_equipment_id"] = selected_id
    st.switch_page("pages/equipment_detail.py")


