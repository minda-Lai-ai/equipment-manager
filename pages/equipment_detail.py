import streamlit as st
import pandas as pd
from utils.status_utils import status_light, maintenance_light

# 載入資料庫
df = pd.read_csv("data/main_equipment_system.csv")

st.set_page_config(page_title="設備詳細資料", layout="wide")
st.title("🔍 設備詳細資料")

# 返回主控面板
if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

st.markdown("---")

# 取得選定設備編號
selected_id = st.session_state.get("selected_equipment_id", None)

if not selected_id:
    st.warning("⚠️ 尚未選取設備，請從設備請購維修系統進入")
    st.stop()

# 查詢設備資料
row_df = df[df["設備請購維修編號"] == selected_id]

if row_df.empty:
    st.error("找不到該設備資料")
    st.stop()

row = row_df.iloc[0]
st.subheader(f"🛠️ 設備：{row['設備']}（{selected_id}）")

# 顯示所有欄位（唯讀）
for col in row.index:
    if col == "設備狀況":
        st.markdown(f"**{col}**：{row[col]} {status_light(row[col])}")
    elif "下次維修保養" in col:
        st.markdown(f"**{col}**：{row[col]} {maintenance_light(row[col])}")
    else:
        st.markdown(f"**{col}**：{row[col]}")

st.markdown("---")

# 編輯按鈕
if st.button("✏️ 編輯此設備"):
    st.switch_page("edit_data.py")

# 儲存按鈕（重新儲存並備份）
if st.button("💾 儲存此設備資料"):
    df.to_csv("data/main_equipment_system.csv", index=False)
    backup_name = f"data/main_equipment_system_{pd.Timestamp.now().strftime('%Y%m%d')}.csv"
    df.to_csv(backup_name, index=False)
    st.success("✅ 資料已儲存並備份")

# 圖片儲存按鈕
if st.button("🖼️ 存成圖片"):
    st.session_state["equipment_snapshot"] = row.to_dict()
    st.switch_page("export_image.py")

