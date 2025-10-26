import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image
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

st.set_page_config(page_title="📸 設備異常回報", layout="wide")
st.title("📸 設備異常回報系統")

if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

# 上傳照片
st.markdown("### 📷 上傳現場照片（最多 5 張）")
uploaded_photos = st.file_uploader("拍攝或上傳照片", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_photos and len(uploaded_photos) > 5:
    st.warning("⚠️ 最多只能上傳 5 張照片")

# 填寫異常資訊
st.markdown("---")
st.markdown("### 🧩 填寫異常資訊")
main_equipment = st.text_input("主設備")
sub_equipment = st.text_input("次設備")
equipment_id = st.text_input("設備請購維修編號（可選）")
description = st.text_area("異常狀況描述")
reporter = st.text_input("報告者（登錄者）")

if st.button("✅ 提交異常回報"):
    if not main_equipment or not sub_equipment or not description or not reporter:
        st.error("❌ 請填寫所有必要欄位")
        st.stop()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    photo_names = []
    photo_folder = "abnormal_images"
    os.makedirs(photo_folder, exist_ok=True)

    # 儲存照片
    if uploaded_photos and len(uploaded_photos) <= 5:
        for i, photo in enumerate(uploaded_photos):
            filename = f"{equipment_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i+1}.jpg"
            filepath = os.path.join(photo_folder, filename)
            image = Image.open(photo)
            image.save(filepath)
            photo_names.append(filename)

    # 寫入 Supabase
    new_row = {
        "回報時間": timestamp,
        "主設備": main_equipment,
        "次設備": sub_equipment,
        "設備請購維修編號": equipment_id,
        "異常描述": description,
        "照片數量": len(photo_names),
        "照片檔名列表": ",".join(photo_names),
        "報告者": reporter,
        "裝置類型": "手機",  # 可擴充為自動判斷
        "來源模組": "report_abnormal.py",
        "分享狀態": "未分享",
        "備註": ""
    }

    supabase.table("abnormal_log").insert([new_row]).execute()
    st.success(f"✅ 已提交異常回報：{main_equipment} / {sub_equipment}（{timestamp}）")
