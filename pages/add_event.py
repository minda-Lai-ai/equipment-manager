import streamlit as st
import pandas as pd
from supabase import create_client

supabase = create_client(
    "https://todjfbmcaxecrqlkkvkd.supabase.co",
    "你的 supabase key"
)

# 權限檢查略...

st.set_page_config(page_title="🆕 新增保養事件", layout="wide")
st.title("🆕 新增保養事件")
if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

main_result = supabase.table("history_maintenance_log").select("*").execute()
eq_df = pd.DataFrame(main_result.data)

# 主要下拉選單
main_options = sorted(eq_df["主設備"].dropna().unique().tolist())
main_sel = st.selectbox("主設備（下拉選）", main_options + [""], index=len(main_options))
main_custom = st.text_input("主設備（可自行輸入）", value="")
主設備 = main_custom.strip() if main_custom.strip() else main_sel

sub_options = sorted(eq_df[eq_df["主設備"] == main_sel]["次設備"].dropna().unique().tolist())
sub_sel = st.selectbox("次設備（下拉選）", sub_options + [""], index=len(sub_options))
sub_custom = st.text_input("次設備（可自行輸入）", value="")
次設備 = sub_custom.strip() if sub_custom.strip() else sub_sel

device_options = sorted(eq_df[eq_df["次設備"] == sub_sel]["設備"].dropna().unique().tolist())
device_sel = st.selectbox("設備（下拉選）", device_options + [""], index=len(device_options))
device_custom = st.text_input("設備（可自行輸入）", value="")
設備 = device_custom.strip() if device_custom.strip() else device_sel

eid_options = sorted(eq_df[eq_df["設備"] == device_sel]["設備請購維修編號"].dropna().unique().tolist())
eid_sel = st.selectbox("設備請購維修編號（下拉選）", eid_options + [""], index=len(eid_options))
eid_custom = st.text_input("設備請購維修編號（可自行輸入）", value="")
設備請購維修編號 = eid_custom.strip() if eid_custom.strip() else eid_sel

st.markdown("---")
st.subheader("✏️ 新增事件欄位")

with st.form("event_form"):
    編號 = st.text_input("編號")
    發生異常日期 = st.text_input("發生異常日期")
    事件項目 = st.text_input("事件項目")
    事件處理說明 = st.text_area("事件處理說明")
    備註 = st.text_area("備註")

    save = st.form_submit_button("💾 儲存")
    reset = st.form_submit_button("🔄 復原")

if reset:
    st.experimental_rerun()

if save:
    new_event = {
        "主設備": 主設備,
        "次設備": 次設備,
        "設備": 設備,
        "設備請購維修編號": 設備請購維修編號,
        "編號": 編號,
        "發生異常日期": 發生異常日期,
        "事件項目": 事件項目,
        "事件處理說明": 事件處理說明,
        "備註": 備註,
        "表單修改人": st.session_state['username']
    }
    try:
        supabase.table("history_maintenance_log").insert([new_event]).execute()
        st.success(f"✅ 已新增事件：{編號} 編號：{編號}")
    except Exception as e:
        st.error(f"❌ 新增失敗，請檢查欄位/資料型態或RLS Policy，訊息：{e}")

