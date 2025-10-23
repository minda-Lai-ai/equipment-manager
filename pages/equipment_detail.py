import streamlit as st
import pandas as pd
from io import BytesIO
from utils.status_utils import status_light, maintenance_light
import matplotlib.pyplot as plt
from matplotlib import font_manager

def equipment_info_image(row):
    # 設置中文字型（如：Microsoft JhengHei/微軟正黑體、SimHei等必須已安裝）
    font_path = "/usr/share/fonts/truetype/arphic/ukai.ttc"  # Linux (可換成適用路徑)
    if not font_manager.findSystemFonts(fontpaths=[font_path]):
        font_path = None  # 若找不到則不指定
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei','SimHei','Arial Unicode MS'] if not font_path else [font_path]
    plt.rcParams['axes.unicode_minus'] = False
    fig, ax = plt.subplots(figsize=(6, len(row.index) * 0.5 + 1))
    ax.axis('off')
    text = "\n".join([f"{col}: {row[col]}" for col in row.index])
    ax.text(0, 1, text, va='top', fontsize=12)
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf

# 權限檢查
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("尚未登入或登入已逾時，請回主畫面重新登入。")
    st.stop()

# 顯示登入者資訊
st.sidebar.markdown("---")
st.sidebar.write(f"👤 使用者：{st.session_state['username']}")
st.sidebar.write(f"🧩 角色：{st.session_state['role']}")

# 載入資料庫
df = pd.read_csv("data/main_equipment_system.csv")

st.set_page_config(page_title="設備詳細資料", layout="wide")
st.title("🔍 設備詳細資料")

# 返回主控面板
if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

st.markdown("---")

selected_id = st.session_state.get("selected_equipment_id", None)
if not selected_id:
    st.warning("⚠️ 尚未選取設備，請從設備請購維修系統進入")
    st.stop()

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

# 編輯設備（美化主頁按鈕）
# 編輯按鈕（正確跳分頁）
st.page_link("pages/edit_data.py", label="✏️ 編輯此設備 ✏️✏️", icon="✏️")

# 儲存為 CSV 檔供下載
csv_data_bom = '\ufeff' + row_df.to_csv(index=False)
st.download_button(
    "💾 下載設備CSV（相容Excel）",
    data=csv_data_bom.encode("utf-8"),
    file_name=f"{selected_id}_設備資料.csv",
    mime="text/csv"
)

# 儲存為 Excel 檔供下載
excel_buffer = BytesIO()
row_df.to_excel(excel_buffer, index=False)
st.download_button(
    "📊 下載此設備資料（Excel檔）",
    data=excel_buffer.getvalue(),
    file_name=f"{selected_id}_設備資料.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# 下載圖片（修正中文亂碼）

def equipment_info_image(row):
    fig, ax = plt.subplots(figsize=(6, len(row.index) * 0.5 + 1))
    ax.axis('off')
    text = "\n".join([f"{col}: {row[col]}" for col in row.index])
    ax.text(0, 1, text, va='top', fontsize=12)
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf

if st.button("🖼️ 生成設備圖片"):
# 下載圖片（修正中文亂碼）
    img_bytes = equipment_info_image(row)
    st.download_button(
        "🖼️ 下載設備資料圖片",
        data=img_bytes.getvalue(),
        file_name=f"{selected_id}_設備資料.png",
        mime="image/png"
    )

st.markdown("---")
