import streamlit as st
import pandas as pd
from supabase import create_client

supabase = create_client(
    "https://todjfbmcaxecrqlkkvkd.supabase.co",
    "aaa"
)

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

# 取表頭（避開id/created_at）
result = supabase.table("main_equipment_system").select("*").limit(1).execute()
if result.data and len(result.data) > 0:
    columns = list(result.data[0].keys())
else:
    columns = [
        "主設備", "次設備", "設備狀況", "維修提示", "設備", "設備編號", "設備請購維修編號",
        "設備類型", "設備規格", "設備廠商", "最近維修保養_日期", "下次維修保養_日期",
        "維修保養週期_月", "設備負責人", "維修廠商", "廠內維修單位", "維修單位聯絡人_分機",
        "是否有備品", "請購履歷", "備品狀況", "備品位置", "備品數量", "表單修改人", "備註"
    ]

for drop_col in ["id", "created_at"]:
    if drop_col in columns:
        columns.remove(drop_col)

if "new_buffer" not in st.session_state:
    st.session_state.new_buffer = {col: "" for col in columns}

# 動態取得主設備/次設備/設備選單
try:
    df = pd.DataFrame(supabase.table("main_equipment_system").select("主設備,次設備,設備").execute().data)
    main_options = sorted(set(df["主設備"].dropna().unique())) if "主設備" in df else []
    sub_options = sorted(set(df["次設備"].dropna().unique())) if "次設備" in df else []
    eq_options = sorted(set(df["設備"].dropna().unique())) if "設備" in df else []
except Exception:
    main_options, sub_options, eq_options = [], [], []

st.markdown("---")
st.subheader("✏️ 輸入新設備欄位")

with st.form("new_form"):
    # 主設備
    main_sel = st.selectbox("主設備（下拉選）", main_options + [""], index=len(main_options))
    main_custom = st.text_input("主設備（可自行輸入）", value=st.session_state.new_buffer.get("主設備", ""))
    st.session_state.new_buffer["主設備"] = main_custom.strip() if main_custom.strip() else main_sel

    # 次設備
    sub_sel = st.selectbox("次設備（下拉選）", sub_options + [""], index=len(sub_options))
    sub_custom = st.text_input("次設備（可自行輸入）", value=st.session_state.new_buffer.get("次設備", ""))
    st.session_state.new_buffer["次設備"] = sub_custom.strip() if sub_custom.strip() else sub_sel

    # 設備
    eq_sel = st.selectbox("設備（下拉選）", eq_options + [""], index=len(eq_options))
    eq_custom = st.text_input("設備（可自行輸入）", value=st.session_state.new_buffer.get("設備", ""))
    st.session_state.new_buffer["設備"] = eq_custom.strip() if eq_custom.strip() else eq_sel

    # 其他欄位
    for col in columns:
        if col not in ["主設備", "次設備", "設備"]:
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

def clean_buffer(buffer):
    for k, v in buffer.items():
        if str(v).strip() == "":
            buffer[k] = None
        elif "日期" in k and v:
            try:
                buffer[k] = pd.to_datetime(v).strftime("%Y-%m-%d")
            except:
                buffer[k] = None
        elif any(w in k for w in ["數量", "週期"]):
            try:
                buffer[k] = int(v)
            except:
                buffer[k] = None
        elif "是否有備品" == k:
            val = str(v).strip()
            buffer[k] = True if val in ["1", "True", "true", "yes", "有"] else False if val in ["0", "False", "false", "no", "無"] else None
    return buffer

if save:
    try:
        new_data = clean_buffer(st.session_state.new_buffer.copy())
        for drop_col in ["id", "created_at"]:
            if drop_col in new_data:
                del new_data[drop_col]
        supabase.table("main_equipment_system").insert([new_data]).execute()
        st.success(f"✅ 已新增設備：{new_data.get('設備')}（{new_data.get('設備請購維修編號')}）")
        st.session_state.new_buffer = {col: "" for col in columns}
    except Exception as ex:
        st.error(f"❌ 新增失敗，請確認必填欄位、型態或RLS。訊息：{ex}")
        st.write(new_data)
