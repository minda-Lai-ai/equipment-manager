import streamlit as st

# 權限檢查
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("尚未登入或登入已逾時，請回主畫面重新登入。")
    st.stop()

# 顯示登入者資訊於頁首或側邊欄
st.sidebar.markdown("---")
st.sidebar.write(f"👤 使用者：{st.session_state['username']}")
st.sidebar.write(f"🧩 角色：{st.session_state['role']}")

import pandas as pd
from modules.four_level_selector import four_level_selector
from datetime import datetime

st.set_page_config(page_title="✏️ 編輯設備資料", layout="wide")
st.title("✏️ 編輯設備資料")

if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

# 資料路徑
main_path = "data/main_equipment_system.csv"
log_path = "data/edit_log.csv"

# 載入資料庫
main_df = pd.read_csv(main_path)

# 四階選單
result = four_level_selector(main_df)
filtered_df = result["filtered_df"]

if filtered_df.empty:
    st.warning("⚠️ 找不到符合條件的設備")
    st.stop()

row = filtered_df.iloc[0]
original = row.to_dict()

# 初始化 session_state
if "edit_buffer" not in st.session_state:
    st.session_state.edit_buffer = original.copy()
    st.session_state.original_data = original.copy()
    st.session_state.edit_mode = True

st.markdown("---")
st.subheader("✏️ 編輯欄位")

with st.form("edit_form"):
    for col in original:
        st.session_state.edit_buffer[col] = st.text_input(f"{col}", value=st.session_state.edit_buffer[col])
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        back = st.form_submit_button("🔙 上一步")
    with col2:
        reset = st.form_submit_button("🔄 復原")
    with col3:
        compare = st.form_submit_button("⏭️ 下一步")
    with col4:
        save = st.form_submit_button("💾 儲存")

# 操作邏輯
if reset:
    st.session_state.edit_buffer = st.session_state.original_data.copy()
    st.info("🔄 已復原為原始資料")

if compare:
    st.markdown("---")
    st.subheader("🧮 修改前後比較")
    diff = []
    for col in original:
        old = str(original[col])
        new = str(st.session_state.edit_buffer[col])
        if old != new:
            diff.append(col)
            st.markdown(f"🔸 **{col}**：`{old}` → `🆕 {new}`")
        else:
            st.markdown(f"▫️ {col}：`{old}`（未變更）")
    if not diff:
        st.info("✅ 所有欄位皆未變動")

if save:
    # 儲存修改
    updated_row = pd.DataFrame([st.session_state.edit_buffer])[main_df.columns]
    target_index = main_df.index[main_df["設備請購維修編號"] == original["設備請購維修編號"]].tolist()
    if target_index:
        main_df.loc[target_index[0]] = updated_row.iloc[0]
        main_df.to_csv(main_path, index=False)
        st.success(f"✅ 已儲存修改：{st.session_state.edit_buffer.get('設備')}（{st.session_state.edit_buffer.get('設備請購維修編號')}）")
    else:
        st.error("❌ 找不到對應設備編號，無法儲存")

    main_df.to_csv(main_path, index=False)
    st.success(f"✅ 已儲存修改：{st.session_state.edit_buffer.get('設備')}（{st.session_state.edit_buffer.get('設備請購維修編號')}）")

    # 寫入修改紀錄
    try:
        log_df = pd.read_csv(log_path)
    except:
        log_df = pd.DataFrame(columns=["時間戳記", "設備請購維修編號", "欄位名稱", "原始值", "新值", "來源模組"])

    for col in original:
        old = str(original[col])
        new = str(st.session_state.edit_buffer[col])
        if old != new:
            log_df = pd.concat([log_df, pd.DataFrame([{
                "時間戳記": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "設備請購維修編號": original["設備請購維修編號"],
                "欄位名稱": col,
                "原始值": old,
                "新值": new,
                "來源模組": "edit_data.py"
            }])], ignore_index=True)

    log_df.to_csv(log_path, index=False)
