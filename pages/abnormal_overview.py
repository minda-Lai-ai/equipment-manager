import streamlit as st
import pandas as pd
import os
from firebase_init import get_firestore
db = get_firestore()
from modules.export_tools import export_abnormal_report

st.set_page_config(page_title="📋 異常紀錄總覽", layout="wide")
st.title("📋 異常紀錄總覽")

log_path = "data/abnormal_log.csv"
image_folder = "abnormal_images"
export_folder = "abnormal_exports"
os.makedirs(export_folder, exist_ok=True)

# 載入資料
try:
    df = pd.read_csv(log_path)
except:
    st.error("❌ 找不到異常紀錄檔案")
    st.stop()

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

# 📋 顯示表格
st.markdown("### 📑 異常紀錄表格")
st.dataframe(df, use_container_width=True)

# 選擇操作紀錄
st.markdown("---")
st.subheader("🛠️ 操作異常紀錄")
selected_index = st.selectbox("選擇紀錄編號", df.index.tolist())
row = df.loc[selected_index]

# 顯示摘要
st.markdown(f"**主設備：** {row['主設備']}　｜　**次設備：** {row['次設備']}　｜　**報告者：** {row['報告者']}")
st.markdown(f"**異常描述：** {row['異常描述']}")
st.markdown(f"**分享狀態：** {row['分享狀態']}　｜　**備註：** {row['備註']}")

# 📄 匯出
if st.button("📁 匯出 PDF 與圖片"):
    result = export_abnormal_report(row, image_folder=image_folder, export_folder=export_folder, log_path=log_path)
    st.success("✅ 匯出完成")
    st.code(result["pdf_path"], language="bash")
    st.code(result["image_path"], language="bash")

# 📤 分享模擬
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
    df.at[selected_index, "分享狀態"] = "已分享（模擬）"
    df.to_csv(log_path, index=False)
    st.success("✅ 分享狀態已更新")

# 🗑️ 刪除紀錄
if st.button("🗑️ 刪除此筆紀錄"):
    df.drop(index=selected_index, inplace=True)
    df.to_csv(log_path, index=False)
    st.warning("⚠️ 已刪除該筆紀錄")
    st.experimental_rerun()

