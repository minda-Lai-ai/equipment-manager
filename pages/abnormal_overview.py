import streamlit as st
import pandas as pd
import os
from supabase import create_client
from modules.export_tools import export_abnormal_report

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

st.set_page_config(page_title="📋 異常紀錄總覽", layout="wide")
st.title("📋 異常紀錄總覽")

image_folder = "abnormal_images"
export_folder = "abnormal_exports"
os.makedirs(export_folder, exist_ok=True)

# 從 Supabase 取異常log
result = supabase.table("abnormal_log").select("*").execute()
df = pd.DataFrame(result.data)

if df.empty:
    st.info("目前沒有異常紀錄")
    st.stop()

# 🔍 搜尋與篩選
with st.expander("🔍 搜尋與篩選"):
    keyword = st.text_input("關鍵字搜尋（主設備 / 次設備 / 描述 / 報告者）")
    status_filter = st.selectbox("分享狀態篩選", ["全部", "未分享", "已分享"], index=0)

    if keyword:
        df = df[df.apply(lambda row: keyword.lower() in str(row).lower(), axis=1)]
    if status_filter == "未分享":
        df = df[df["分享狀態"].str.contains("未分享", na=False)]
    elif status_filter == "已分享":
        df = df[df["分享狀態"].str.contains("已分享", na=False)]

st.markdown("### 📑 異常紀錄表格")
st.dataframe(df, use_container_width=True)

# 操作紀錄（以ID自動選擇&多端唯一）
st.markdown("---")
st.subheader("🛠️ 操作異常紀錄")
if "selected_abnormal_id" not in st.session_state:
    st.session_state["selected_abnormal_id"] = df.iloc[0]["id"]

selected_id = st.selectbox("選擇紀錄編號", df["id"].tolist(), index=0)
row = df[df["id"] == selected_id].iloc[0]

st.markdown(f"**主設備：** {row['主設備']}　｜　**次設備：** {row['次設備']}　｜　**報告者：** {row['報告者']}")
st.markdown(f"**異常描述：** {row['異常描述']}")
st.markdown(f"**分享狀態：** {row['分享狀態']}　｜　**備註：** {row['備註']}")

# 匯出 PDF/圖片
if st.button("📁 匯出 PDF 與圖片"):
    result_export = export_abnormal_report(row, image_folder=image_folder, export_folder=export_folder)
    st.success("✅ 匯出完成")
    st.code(result_export["pdf_path"], language="bash")
    st.code(result_export["image_path"], language="bash")

# 分享狀態
if st.button("📤 模擬分享"):
    share_text = f"""
📸 設備異常回報
🕒 時間：{row['回報時間']}
🧩 主設備：{row['主設備']}
🧩 次設備：{row['次設備']}
📝 描述：{row['異常描述']}
👤 報告者：{row['報告者']}
📷 照片：{row['照片檔名列表']}
🔗 來源模組：{row['來源模組']}
"""
    st.text_area("📋 分享內容預覽", value=share_text, height=200)
    supabase.table("abnormal_log").update({"分享狀態": "已分享（模擬）"}).eq("id", row["id"]).execute()
    st.success("✅ 分享狀態已更新")
    st.experimental_rerun()

if st.button("🗑️ 刪除此筆紀錄"):
    supabase.table("abnormal_log").delete().eq("id", row["id"]).execute()
    st.warning("⚠️ 已刪除該筆紀錄")
    st.experimental_rerun()
