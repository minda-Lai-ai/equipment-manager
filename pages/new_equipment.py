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

st.set_page_config(page_title="🆕 新增設備", layout="wide")
st.title("🆕 新增設備資料")
if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

# 直接從 Supabase 取欄位（取一筆即可抓表頭）
result = supabase.table("main_equipment_system").select("*").limit(1).execute()
if result.data and len(result.data) > 0:
    columns = list(result.data[0].keys())
else:
    # 如果資料庫空無內容，請確認資料表已建立所有所需欄位
    columns = [
        "主設備", "次設備", "設備狀況", "維修提示", "設備", "設備編號", "設備請購維修編號",
        "設備類型", "設備規格", "設備廠商", "最近維修保養_日期", "下次維修保養_日期",
        "維修保養週期_月", "設備負責人", "維修廠商", "廠內維修單位", "維修單位聯絡人_分機",
        "是否有備品", "請購履歷", "備品狀況", "備品位置", "備品數量", "表單修改人", "備註"
    ]

if "new_buffer" not in st.session_state:
    st.session_state.new_buffer = {col: "" for col in columns}

st.markdown("---")
st.subheader("✏️ 輸入新設備欄位")

#MINDA
def clean_buffer(buffer):
    import re
    for k, v in buffer.items():
        # 空字串自動轉 None
        if str(v).strip() == "":
            buffer[k] = None
        # 自動辨識日期
        elif "日期" in k and v:
            try:
                buffer[k] = pd.to_datetime(v).strftime("%Y-%m-%d")
            except:
                buffer[k] = None
        # 自動辨識數量、週期、數字
        elif any(w in k for w in ["數量", "週期"]):
            try:
                buffer[k] = int(v)
            except:
                buffer[k] = None
    return buffer

if save:
    new_data = clean_buffer(st.session_state.new_buffer.copy())
    try:
        supabase.table("main_equipment_system").insert([new_data]).execute()
        st.success(f"✅ 已新增設備：{new_data.get('設備')}（{new_data.get('設備請購維修編號')}）")
        st.session_state.new_buffer = {col: "" for col in columns}
    except Exception as ex:
        st.error(f"❌ 新增失敗，請檢查必填欄位、型態或RLS Policy。訊息：{ex}")
        st.write(new_data)
#MINDA



with st.form("new_form"):
    for col in columns:
        st.session_state.new_buffer[col] = st.text_input(f"{col}", value=st.session_state.new_buffer[col])
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        back = st.form_submit_button("🔙 上一步")
    with col2:
        reset = st.form_submit_button("🔄 清空欄位")
    with col3:
        compare = st.form_submit_button("⏭️ 預覽輸入")
    with col4:
        save = st.form_submit_button("💾 儲存")

if reset:
    st.session_state.new_buffer = {col: "" for col in columns}
    st.info("🔄 已清空欄位")

if compare:
    st.markdown("---")
    st.subheader("🧮 新設備內容預覽")
    for col in columns:
        val = st.session_state.new_buffer[col]
        if val:
            st.markdown(f"🔸 **{col}**：`{val}`")
        else:
            st.markdown(f"▫️ {col}：`（空白）`")

if save:
    # 直接新增至 Supabase table
    supabase.table("main_equipment_system").insert([st.session_state.new_buffer]).execute()
    st.success(f"✅ 已新增設備：{st.session_state.new_buffer.get('設備')}（{st.session_state.new_buffer.get('設備請購維修編號')}）")
    st.session_state.new_buffer = {col: "" for col in columns}

