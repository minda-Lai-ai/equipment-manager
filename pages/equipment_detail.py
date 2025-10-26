import streamlit as st
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib import font_manager
from supabase import create_client

# 連線 Supabase
supabase = create_client(
    "https://todjfbmcaxecrqlkkvkd.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvZGpmYm1jYXhlY3JxbGtrdmtkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzMjk3NDgsImV4cCI6MjA3NjkwNTc0OH0.0uTJcrHwvnGM8YT1bPHzMyGkQHIJUZWXsVEwEPjp0sA"
)

def status_light(status):
    color = {"on": "green", "off": "red", "none": "black"}.get(str(status).strip().lower(), "gray")
    return f'<span style="display:inline-block;width:16px;height:16px;border-radius:8px;background-color:{color};margin-right:6px;vertical-align:middle"></span>{status}'

def maintenance_light(next_time):
    try:
        if pd.isna(next_time) or not str(next_time).strip():
            color = "black"
        else:
            next_date = pd.to_datetime(str(next_time), errors='coerce')
            if pd.isna(next_date):
                color = "black"
            else:
                today = pd.Timestamp.today()
                delta = (next_date - today).days
                if delta < 0:
                    color = "red"
                elif delta <= 31:
                    color = "yellow"
                else:
                    color = "green"
    except Exception:
        color = "black"
    return f'<span style="display:inline-block;width:16px;height:16px;border-radius:8px;background-color:{color};vertical-align:middle"></span>'

def equipment_info_image(row):
    # 建議你用雲端環境支持的中文字型，這裡取系統已裝字型
    font_path = "/usr/share/fonts/truetype/arphic/ukai.ttc"
    try:
        plt.rcParams['font.sans-serif'] = [font_path]
    except:
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei','SimHei','Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
    fig, ax = plt.subplots(figsize=(6, len(row.index)*0.5+1))
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

st.sidebar.markdown("---")
st.sidebar.write(f"👤 使用者：{st.session_state['username']}")
st.sidebar.write(f"🧩 角色：{st.session_state['role']}")

st.set_page_config(page_title="設備詳細資料", layout="wide")
st.title("🔍 設備詳細資料")
if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

selected_id = st.session_state.get("selected_equipment_id", None)
if not selected_id:
    st.warning("⚠️ 尚未選取設備，請從設備請購維修系統進入")
    st.stop()

# 從 Supabase 查詢設備，完全不抓本地 CSV
result = supabase.table("main_equipment_system").select("*").eq("設備請購維修編號", selected_id).execute()
df = pd.DataFrame(result.data)
if df.empty:
    st.error("找不到該設備資料")
    st.stop()

row = df.iloc[0]
st.subheader(f"🛠️ 設備：{row['設備']}（{selected_id}）")

for col in df.columns:
    if col == "設備狀況":
        st.markdown(f"**{col}**：{row[col]} {status_light(row[col])}", unsafe_allow_html=True)
    elif "下次維修保養" in col or "下次維修日期" in col:
        st.markdown(f"**{col}**：{row[col]} {maintenance_light(row[col])}", unsafe_allow_html=True)
    else:
        st.markdown(f"**{col}**：{row[col]}")

st.markdown("---")

st.page_link("pages/edit_data.py", label="✏️ 編輯此設備 ✏️", icon="✏️")

csv_data_bom = '\ufeff' + df.to_csv(index=False)
st.download_button(
    "💾 下載設備CSV（相容Excel）",
    data=csv_data_bom.encode("utf-8"),
    file_name=f"{selected_id}_設備資料.csv",
    mime="text/csv"
)
excel_buffer = BytesIO()
df.to_excel(excel_buffer, index=False)
st.download_button(
    "📊 下載此設備資料（Excel檔）",
    data=excel_buffer.getvalue(),
    file_name=f"{selected_id}_設備資料.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

if st.button("🖼️ 生成設備圖片"):
    img_bytes = equipment_info_image(row)
    st.download_button(
        "🖼️ 下載設備資料圖片",
        data=img_bytes.getvalue(),
        file_name=f"{selected_id}_設備資料.png",
        mime="image/png"
    )

st.markdown("---")
