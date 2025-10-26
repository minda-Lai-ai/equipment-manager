import streamlit as st
from supabase import create_client
import pandas as pd
import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from fpdf import FPDF
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

st.set_page_config(page_title="📤 匯出異常報告", layout="wide")
st.title("📤 匯出異常報告")

if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

image_folder = "abnormal_images"
os.makedirs(image_folder, exist_ok=True)

# 從 Supabase 載入異常紀錄
result = supabase.table("abnormal_log").select("*").execute()
df = pd.DataFrame(result.data)

if df.empty:
    st.info("目前沒有異常紀錄")
    st.stop()

selected_index = st.selectbox("選擇異常紀錄編號", df.index.tolist())
row = df.loc[selected_index]

# 顯示異常資訊
st.markdown("---")
st.subheader("📋 異常資訊")
for col in ["回報時間", "主設備", "次設備", "設備請購維修編號", "異常描述", "報告者"]:
    st.markdown(f"**{col}**：{row[col]}")

# 顯示照片
st.markdown("### 📷 現場照片")
photo_list = str(row["照片檔名列表"]).split(",")
for name in photo_list:
    path = os.path.join(image_folder, name.strip())
    if os.path.exists(path):  # 本地檔案如有即顯示（如今照片要雲端可串雲端檔案服務）
        st.image(path, caption=name, use_column_width=True)

st.markdown("---")
st.subheader("📤 分享異常報告")

share_method = st.selectbox("選擇分享方式", ["LINE 群組", "Email", "Google 雲端", "暫不分享"])

if st.button("📤 執行分享"):
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
    # 直接更新雲端分享狀態
    record_id = row["id"]  # 必須有 id 欄位
    supabase.table("abnormal_log").update({"分享狀態": f"已分享（{share_method}）"}).eq("id", record_id).execute()
    st.success(f"✅ 已模擬分享至 {share_method}，並更新紀錄")

if st.button("📄 匯出 PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="📸 設備異常回報", ln=True)
    for col in ["回報時間", "主設備", "次設備", "設備請購維修編號", "異常描述", "報告者"]:
        pdf.multi_cell(0, 10, f"{col}：{row[col]}")
    for name in photo_list:
        path = os.path.join(image_folder, name.strip())
        if os.path.exists(path):
            pdf.image(path, w=100)
    filename = f"異常報告_{row['設備請購維修編號']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    export_path = os.path.join("abnormal_exports", filename)
    pdf.output(export_path)
    st.success(f"✅ 已匯出 PDF：{filename}")
    with open(export_path, "rb") as f:
        st.download_button("📥 下載 PDF", f, file_name=filename)

if st.button("🖼️ 匯出圖片"):
    base_image = Image.new("RGB", (800, 1000), "white")
    draw = ImageDraw.Draw(base_image)
    font = ImageFont.load_default()
    y = 20
    draw.text((20, y), "📸 設備異常回報", font=font, fill="black")
    y += 30
    for col in ["回報時間", "主設備", "次設備", "設備請購維修編號", "異常描述", "報告者"]:
        draw.text((20, y), f"{col}：{row[col]}", font=font, fill="black")
        y += 25
    if photo_list:
        path = os.path.join(image_folder, photo_list[0].strip())
        if os.path.exists(path):
            img = Image.open(path).resize((760, 500))
            base_image.paste(img, (20, y))
    filename = f"異常報告_{row['設備請購維修編號']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    export_path = os.path.join("abnormal_exports", filename)
    base_image.save(export_path)
    st.success(f"✅ 已匯出圖片：{filename}")
    with open(export_path, "rb") as f:
        st.download_button("🖼️ 下載圖片", f, file_name=filename)

if st.button("📁 匯出 PDF 與圖片"):
    result = export_abnormal_report(row)
    pdf_path = result["pdf_path"]
    image_path = result["image_path"]
    st.success("✅ 匯出完成！")
    with st.expander("📄 PDF 檔案"):
        st.markdown(f"📎 檔名：`{os.path.basename(pdf_path)}`")
        with open(pdf_path, "rb") as f:
            st.download_button("📥 下載 PDF", f, file_name=os.path.basename(pdf_path))
            st.code(pdf_path, language="bash")
    with st.expander("🖼️ 圖片檔案"):
        st.markdown(f"📎 檔名：`{os.path.basename(image_path)}`")
        with open(image_path, "rb") as f:
            st.download_button("🖼️ 下載圖片", f, file_name=os.path.basename(image_path))
            st.code(image_path, language="bash")

st.caption("📌 匯出功能將整合異常資訊與照片，後續可串接 LINE、Email、雲端分享")
