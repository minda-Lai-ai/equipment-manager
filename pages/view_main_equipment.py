import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

# 權限檢查
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("尚未登入或登入已逾時，請回主畫面重新登入。")
    st.stop()

# 顯示登入者資訊於頁首或側邊欄
st.sidebar.markdown("---")
st.sidebar.write(f"👤 使用者：{st.session_state['username']}")
st.sidebar.write(f"🧩 角色：{st.session_state['role']}")

st.set_page_config(page_title="🔍 主設備資料總覽", layout="wide")
st.title("🔍 主設備資料總覽")
if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

try:
    df = pd.read_csv("data/main_equipment_system.csv")
except Exception as e:
    st.error(f"❌ 無法載入主設備資料庫：{e}")
    st.stop()

# ---------- 狀態燈號&保養提示功能 ----------
def status_light(status):
    color = {"on": "green", "off": "red", "none": "black"}.get(str(status).strip().lower(), "gray")
    text = str(status)
    return f'<span style="display:inline-block;width:16px;height:16px;border-radius:8px;background-color:{color};margin-right:8px;vertical-align:middle"></span>{text}'

def maintenance_light(next_time):
    if isinstance(next_time, float) and pd.isna(next_time):   # 若為nan
        return '<span style="background:#bbb;width:16px;height:16px;border-radius:8px;display:inline-block;"></span> 無資料'
    try:
        next_date = pd.to_datetime(str(next_time), errors='coerce')
        if pd.isna(next_date):
            raise ValueError
        today = datetime.today()
        delta = (next_date - today).days
        if delta < 0:
            # 已逾期
            color = "red"
        elif delta <= 31:
            # 一個月內(31天)
            color = "yellow"
        else:
            color = "green"
        return f'<span style="display:inline-block;width:16px;height:16px;border-radius:8px;background-color:{color};margin-right:8px;vertical-align:middle"></span>{next_time}'
    except Exception as e:
        return '<span style="background:#bbb;width:16px;height:16px;border-radius:8px;display:inline-block;"></span> 無法解析'

# ---------- 製作顯示用 DataFrame ----------
df_disp = df.copy()
if "設備狀況" in df_disp.columns:
    df_disp["設備狀況"] = df_disp["設備狀況"].apply(status_light)
# 假設「下次維修日期」欄名如下，請確認列名正確
if "下次維修日期" in df_disp.columns:
    df_disp["維修保養提示"] = df_disp["下次維修日期"].apply(maintenance_light)

# ---------- 顯示於頁面 ----------
st.markdown('<style>td {vertical-align: middle;}</style>', unsafe_allow_html=True)
st.write("（部分欄位已加燈號）")
st.write(df_disp.to_html(escape=False, index=False), unsafe_allow_html=True)

st.markdown("---")
st.markdown("💾 若需另存資料，請選擇下載格式：")

# ---------- 下載 CSV ----------
csv_data = '\ufeff' + df.to_csv(index=False)    # BOM 避免 Excel 亂碼
st.download_button(
    "下載 CSV",
    data=csv_data.encode("utf-8"),
    file_name="main_equipment_system.csv",
    mime="text/csv"
)

# ---------- 下載 Excel ----------
excel_buffer = BytesIO()
df.to_excel(excel_buffer, index=False, engine="openpyxl")
st.download_button(
    "下載 Excel",
    data=excel_buffer.getvalue(),
    file_name="main_equipment_system.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.markdown("---")
st.markdown("📸 若需將資料另存為圖片，請使用下方工具：")
# 圖片儲存（轉到圖片分頁）
if st.button("🖼️ 將主設備資料匯出為圖片"):
    st.switch_page("pages/export_image.py")
