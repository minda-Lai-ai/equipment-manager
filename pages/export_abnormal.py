import streamlit as st
from supabase import create_client
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from fpdf import FPDF
import io

supabase = create_client(
    "https://todjfbmcaxecrqlkkvkd.supabase.co",
    "你的 supabase key"
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

# 載入異常紀錄
result = supabase.table("abnormal_log").select("*").execute()
df = pd.DataFrame(result.data)
if df.empty:
    st.info("目前沒有異常紀錄")
    st.stop()

selected_index = st.selectbox("選擇異常紀錄編號", df.index.tolist())
row = df.loc[selected_index]

st.markdown("---")
st.subheader("📋 異常資訊")
for col in ["回報時間", "主設備", "次設備", "設備請購維修編號", "異常描述", "報告者"]:
    st.markdown(f"**{col}**：{row[col]}")

st.markdown("### 📷 現場照片")
photo_list = str(row["照片檔名列表"]).split(",")
for name in photo_list:
    # 若來源支援雲端圖片，這裡可放url；如暫無，僅展示檔名
    st.write(f"照片: {name}（如需展示請改用URL）")

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
    record_id = row["id"]
    supabase.table("abnormal_log").update({"分享狀態": f"已分享（{share_method}）"}).eq("id", record_id).execute()
    st.success(f"✅ 已模擬分享至 {share_method}，並更新紀錄")

if st.button("📄 匯出 PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="📸 設備異常回報", ln=True)
    for col in ["回報時間", "主設備", "次設備", "設備請購維修編號", "異常描述", "報告者"]:
        pdf.multi_cell(0, 10, f"{col}：{row[col]}")
    filename = f"異常報告_{row['設備請購維修編號']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
    st.download_button("📥 下載 PDF", pdf_buffer, file_name=filename, mime="application/pdf")

if st.button("🖼️ 匯出圖片"):
    base_image = Image.new("RGB", (800, 500), "white")
    draw = ImageDraw.Draw(base_image)
    font = ImageFont.load_default()
    y = 20
    draw.text((20, y), "📸 設備異常回報", font=font, fill="black")
    y += 30
    for col in ["回報時間", "主設備", "次設備", "設備請購維修編號", "異常描述", "報告者"]:
        draw.text((20, y), f"{col}：{row[col]}", font=font, fill="black")
        y += 25
    img_buffer = io.BytesIO()
    base_image.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    img_filename = f"異常報告_{row['設備請購維修編號']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    st.download_button("🖼️ 下載圖片", img_buffer, file_name=img_filename, mime="image/png")

st.caption("📌 下載按鈕直接由瀏覽器端觸發下載到用戶裝置，無伺服器路徑問題。")
