import streamlit as st
import pandas as pd
from datetime import datetime
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
    # 空值、NaN、非日期統一黑色
    try:
        if pd.isna(next_time) or not str(next_time).strip():
            raise ValueError
        next_date = pd.to_datetime(str(next_time), errors='coerce')
        if pd.isna(next_date):
            raise ValueError
        today = datetime.today()
        delta = (next_date - today).days
        if delta < 0:
            color = "red"
        elif delta <= 31:
            color = "yellow"
        else:
            color = "green"
        return f'<span style="display:inline-block;width:16px;height:16px;border-radius:8px;background-color:{color};margin-right:8px;vertical-align:middle"></span>{next_time}'
    except Exception:
        return '<span style="display:inline-block;width:16px;height:16px;border-radius:8px;background-color:black;margin-right:8px;vertical-align:middle"></span>無資料'

# ---------- 製作顯示用 DataFrame ----------
df_disp = df.copy()
if "設備狀況" in df_disp.columns:
    df_disp["設備狀況"] = df_disp["設備狀況"].apply(status_light)
# 假設「下次維修日期」欄名如下，請確認列名正確
if "下次維修日期" in df_disp.columns:
    df_disp["維修保養提示"] = df_disp["下次維修日期"].apply(maintenance_light)

# ---------- 顯示於頁面，不換行、最寬自適應 ----------
st.markdown("""
<style>
    table {
        table-layout: auto !important;
    }
    td {
        white-space: nowrap !important;
        font-size: 15px !important;
        vertical-align: middle !important;
    }
    th {
        white-space: nowrap !important;
        background: #e0f0ff !important;
        font-size: 15px !important;
    }
</style>
""", unsafe_allow_html=True)
st.write("（部分欄位已加燈號；欄寬自隨最大資料自適應）")
st.write(df_disp.to_html(escape=False, index=False), unsafe_allow_html=True)

# ---------- 匯出 ----------
st.markdown("---")
st.markdown("💾 若需另存資料，請選擇下載格式：")

# CSV 匯出
csv_data = '\ufeff' + df.to_csv(index=False)
st.download_button(
    "下載 CSV",
    data=csv_data.encode("utf-8"),
    file_name="main_equipment_system.csv",
    mime="text/csv"
)
# Excel 匯出
excel_buffer = BytesIO()
df.to_excel(excel_buffer, index=False, engine="openpyxl")
st.download_button(
    "下載 Excel",
    data=excel_buffer.getvalue(),
    file_name="main_equipment_system.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
