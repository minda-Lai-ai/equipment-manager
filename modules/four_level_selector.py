import streamlit as st
import pandas as pd

def four_level_selector(main_df: pd.DataFrame):
    st.markdown("### 🔎 設備選擇器（四階）")

    # 第一層：主設備
    main_options = ["無"] + sorted(main_df["主設備"].dropna().unique())
    selected_main = st.selectbox("選擇主設備", main_options)

    sub_df = main_df if selected_main == "無" else main_df[main_df["主設備"] == selected_main]

    # 第二層：次設備
    sub_options = ["無"] + sorted(sub_df["次設備"].dropna().unique())
    selected_sub = st.selectbox("選擇次設備", sub_options)

    equip_df = sub_df if selected_sub == "無" else sub_df[sub_df["次設備"] == selected_sub]

    # 第三層：設備
    equip_options = ["無"] + sorted(equip_df["設備"].dropna().unique())
    selected_equip = st.selectbox("選擇設備", equip_options)

    id_df = equip_df if selected_equip == "無" else equip_df[equip_df["設備"] == selected_equip]

    # 第四層：設備請購維修編號
    id_options = ["無"] + sorted(id_df["設備請購維修編號"].dropna().unique())
    selected_id = st.selectbox("選擇設備請購維修編號", id_options)

    # 回傳篩選後的資料表與選擇結果
    return {
        "selected_main": selected_main,
        "selected_sub": selected_sub,
        "selected_equip": selected_equip,
        "selected_id": selected_id,
        "filtered_df": id_df if selected_id == "無" else id_df[id_df["設備請購維修編號"] == selected_id]
    }

