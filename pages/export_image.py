import streamlit as st

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("尚未登入或權限不足，請由主畫面登入後再瀏覽此頁。")
    st.stop()

from PIL import Image, ImageDraw, ImageFont
import pandas as pd

st.set_page_config(page_title="圖片儲存模組", layout="wide")
st.title("🖼️ 圖片儲存模組")

# 返回主控面板
if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

st.markdown("---")

# 取得設備資料
data = st.session_state.get("equipment_snapshot", None)

if not data:
    st.warning("⚠️ 尚未選取設備，請從設備詳細資料頁進入")
    st.stop()

st.subheader(f"📷 將設備資料儲存為圖片：{data.get('設備', '')}")

# 建立圖片
img_width = 1200
img_height = 50 + len(data) * 40 + 50
image = Image.new("RGB", (img_width, img_height), color="white")
draw = ImageDraw.Draw(image)

# 字型設定（macOS 預設字型）
try:
    font = ImageFont.truetype("Arial.ttf", 24)
except:
    font = ImageFont.load_default()

# 標題
draw.text((50, 20), f"設備資料：{data.get('設備', '')}", fill="black", font=font)

# 欄位內容
y = 70
for key, value in data.items():
    draw.text((50, y), f"{key}：{value}", fill="black", font=font)
    y += 40

# 顯示圖片
st.image(image, caption="設備資料圖片預覽", use_column_width=True)

# 儲存按鈕
if st.button("💾 儲存圖片"):
    filename = f"data/equipment_snapshot_{data.get('設備請購維修編號', 'unknown')}.png"
    image.save(filename)
    st.success(f"✅ 圖片已儲存：{filename}")

