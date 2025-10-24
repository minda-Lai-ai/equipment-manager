import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("尚未登入或登入已逾時，請回主畫面重新登入。")
    st.stop()

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

def status_light(status):
    color = {"on": "green", "off": "red", "none": "black"}.get(str(status).strip().lower(), "gray")
    return f'<span style="display:inline-block;width:16px;height:16px;border-radius:8px;background-color:{color};margin-right:6px;vertical-align:middle"></span>{status}'

def maintenance_light(next_time):
    # 若為空、nan、亂碼則黑燈，否則依規則給
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
    except Exception:
        color = "black"
    # 只顯示燈號無文字
    return f'<span style="display:inline-block;width:16px;height:16px;border-radius:8px;background-color:{color};vertical-align:middle"></span>'

# 產生顯示用 dataframe
df_disp = df.copy()
if "設備狀況" in df_disp.columns:
    df_disp["設備狀況"] = df_disp["設備狀況"].apply(status_light)
if "下次維修日期" in df_disp.columns:
    df_disp["維修保養提示"] = df_disp["下次維修日期"].apply(maintenance_light)

# 美化表格，不換行＋自動寬＋表頭藍底白字
st.markdown("""
<style>
    table {table-layout:auto !important;}
    th {
        white-space:nowrap !important;
        background: #2363a9 !important;
        color: #fff !important;
        font-size: 15px !important;
        text-align: center !important;
    }
    td {
        white-space:nowrap !important;
        font-size: 15px !important;
        vertical-align: middle !important;
        text-align: center !important;
    }
</style>
""", unsafe_allow_html=True)
st.write("（設備狀況、保養提示已加燈號，所有欄寬自適應最大內容）")
st.write(df_disp.to_html(escape=False, index=False), unsafe_allow_html=True)

st.markdown("---")
st.markdown("💾 若需另存資料，請選擇下載格式：")
csv_data = '\ufeff' + df.to_csv(index=False)
st.download_button(
    "下載 CSV",
    data=csv_data.encode("utf-8"),
    file_name="main_equipment_system.csv",
    mime="text/csv"
)
excel_buffer = BytesIO()
df.to_excel(excel_buffer, index=False, engine="openpyxl")
st.download_button(
    "下載 Excel",
    data=excel_buffer.getvalue(),
    file_name="main_equipment_system.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
