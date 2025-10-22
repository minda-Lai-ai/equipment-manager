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
import os
from PIL import Image
from datetime import datetime
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="📤 匯出異常報告", layout="wide")
st.title("📤 匯出異常報告")

if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

log_path = "data/abnormal_log.csv"
image_folder = "abnormal_images"

# 載入異常紀錄
try:
    df = pd.read_csv(log_path)
except:
    st.error("❌ 找不到異常紀錄檔案")
    st.stop()

if df.empty:
    st.info("目前沒有異常紀錄")
    st.stop()

# 選擇一筆紀錄
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
    if os.path.exists(path):
        st.image(path, caption=name, use_column_width=True)

# 匯出選項
st.markdown("---")
st.subheader("📤 分享異常報告")

share_method = st.selectbox("選擇分享方式", ["LINE 群組", "Email", "Google 雲端", "暫不分享"])

if st.button("📤 執行分享"):
    # 模擬分享內容
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

    # 更新分享狀態
    df.at[selected_index, "分享狀態"] = f"已分享（{share_method}）"
    df.to_csv(log_path, index=False)
    st.success(f"✅ 已模擬分享至 {share_method}，並更新紀錄")

if st.button("📄 匯出 PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # 加入文字內容
    pdf.cell(200, 10, txt="📸 設備異常回報", ln=True)
    for col in ["回報時間", "主設備", "次設備", "設備請購維修編號", "異常描述", "報告者"]:
        pdf.multi_cell(0, 10, f"{col}：{row[col]}")

    # 加入照片
    for name in photo_list:
        path = os.path.join(image_folder, name.strip())
        if os.path.exists(path):
            pdf.image(path, w=100)

    # 儲存 PDF
    filename = f"異常報告_{row['設備請購維修編號']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    export_path = os.path.join("abnormal_exports", filename)
    pdf.output(export_path)
    st.success(f"✅ 已匯出 PDF：{filename}")

if st.button("🖼️ 匯出圖片"):
    base_image = Image.new("RGB", (800, 1000), "white")
    draw = ImageDraw.Draw(base_image)
    font = ImageFont.load_default()

    # 加入文字
    y = 20
    draw.text((20, y), "📸 設備異常回報", font=font, fill="black")
    y += 30
    for col in ["回報時間", "主設備", "次設備", "設備請購維修編號", "異常描述", "報告者"]:
        draw.text((20, y), f"{col}：{row[col]}", font=font, fill="black")
        y += 25

    # 加入第一張照片
    if photo_list:
        path = os.path.join(image_folder, photo_list[0].strip())
        if os.path.exists(path):
            img = Image.open(path).resize((760, 500))
            base_image.paste(img, (20, y))

    # 儲存圖片
    filename = f"異常報告_{row['設備請購維修編號']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    export_path = os.path.join("abnormal_exports", filename)
    base_image.save(export_path)
    st.success(f"✅ 已匯出圖片：{filename}")

from modules.export_tools import export_abnormal_report

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


col1, col2, col3 = st.columns(3)
with col1:
    st.button("📄 匯出 PDF（暫不實作）")
with col2:
    st.button("🖼️ 匯出圖片（暫不實作）")
with col3:
    st.button("📤 分享（暫不實作）")

st.caption("📌 匯出功能將整合異常資訊與照片，後續可串接 LINE、Email、雲端分享")

