import streamlit as st
import pandas as pd
from firebase_init import get_firestore
db = get_firestore()

st.set_page_config(page_title="🆕 新增設備", layout="wide")
st.title("🆕 新增設備資料")

if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

path = "data/main_equipment_system.csv"
df = pd.read_csv(path)
columns = df.columns.tolist()

if "new_buffer" not in st.session_state:
    st.session_state.new_buffer = {col: "" for col in columns}

st.markdown("---")
st.subheader("✏️ 輸入新設備欄位")

with st.form("new_form"):
    for col in columns:
        st.session_state.new_buffer[col] = st.text_input(f"{col}", value=st.session_state.new_buffer[col])
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        back = st.form_submit_button("🔙 上一步")
    with col2:
        reset = st.form_submit_button("🔄 復原")
    with col3:
        compare = st.form_submit_button("⏭️ 下一步")
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
    new_row = pd.DataFrame([st.session_state.new_buffer])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(path, index=False)
    st.success(f"✅ 已新增設備：{st.session_state.new_buffer.get('設備')}（{st.session_state.new_buffer.get('設備請購維修編號')}）")
