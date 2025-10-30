import streamlit as st
import pandas as pd
from supabase import create_client

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

st.set_page_config(page_title="🆕 新增保養事件", layout="wide")
st.title("🆕 新增保養事件")
if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

# 雲端設備選單
main_result = supabase.table("history_maintenance_log").select("*").execute()
eq_df = pd.DataFrame(main_result.data)

# 主要下拉選單（不直接用四階，一次全選項）
main_options = sorted(eq_df["主設備"].dropna().unique().tolist())
main_sel = st.selectbox("主設備", main_options)
sub_df = eq_df[eq_df["主設備"] == main_sel]

sub_options = sorted(sub_df["次設備"].dropna().unique().tolist())
sub_sel = st.selectbox("次設備", sub_options)
eq2_df = sub_df[sub_df["次設備"] == sub_sel]

device_options = sorted(eq2_df["設備"].dropna().unique().tolist())
device_sel = st.selectbox("設備", device_options)
eq3_df = eq2_df[eq2_df["設備"] == device_sel]

eid_options = sorted(eq3_df["設備請購維修編號"].dropna().unique().tolist())
eid_sel = st.selectbox("設備請購維修編號", eid_options)

st.markdown("---")
st.subheader("✏️ 新增事件欄位")

with st.form("event_form"):
    編號 = st.text_input("編號")
    發生異常日期 = st.text_input("發生異常日期")  # 可改用 st.date_input
    事件項目 = st.text_input("事件項目")  # 新增欄位
    事件處理說明 = st.text_area("事件處理說明")
    備註 = st.text_area("備註")

    save = st.form_submit_button("💾 儲存")
    reset = st.form_submit_button("🔄 復原")

if reset:
    st.experimental_rerun()

if save:
    new_event = {
        "主設備": main_sel,
        "次設備": sub_sel,
        "設備": device_sel,
        "設備請購維修編號": eid_sel,
        "編號": 編號,
        "發生異常日期": 發生異常日期,
        "事件項目": 事件項目,
        "事件處理說明": 事件處理說明,
        "備註": 備註,
        "表單修改人": st.session_state['username']
    }
    # 必須確保 new_event key 跟 table schema完全一致
    # 如還有其他必填欄位請補上，欄位型態勿留空

    try:
        supabase.table("history_maintenance_log").insert([new_event]).execute()
        st.success(f"✅ 已新增事件：{事件類型} 編號：{編號}")
    except Exception as e:
        st.error(f"❌ 新增失敗，請檢查欄位/資料型態或RLS Policy，訊息：{e}")
