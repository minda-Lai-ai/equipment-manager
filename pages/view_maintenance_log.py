import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
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

st.set_page_config(page_title="🔍 保養履歷資料總覽", layout="wide")
st.title("🔍 保養履歷資料總覽")
if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

# 取得雲端資料
result = supabase.table("history_maintenance_log").select("*").execute()
df = pd.DataFrame(result.data)
st.dataframe(df, use_container_width=True)

st.markdown("---")
st.markdown("💾 若需另存資料（下載至本地裝置），請選擇格式：")

csv_data = '\ufeff' + df.to_csv(index=False)
st.download_button(
    "下載 CSV",
    data=csv_data.encode("utf-8"),
    file_name="history_maintenance_log.csv",
    mime="text/csv"
)
excel_buffer = BytesIO()
df.to_excel(excel_buffer, index=False, engine="openpyxl")
st.download_button(
    "下載 Excel",
    data=excel_buffer.getvalue(),
    file_name="history_maintenance_log.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.markdown("📸 若需將表格存為圖片（PNG），請點選按鈕自動生成一張全部欄位的圖片：")

def df_to_image(dataframe, title="保養履歷總表"):
    # 基本表格文字渲染（需支援中文字型/雲端環境要換字型路徑）
    font = ImageFont.load_default()
    col_list = list(dataframe.columns)
    rows = dataframe.astype(str).values.tolist()
    cell_width = 200
    cell_height = 30
    img_width = cell_width * len(col_list)
    img_height = cell_height * (len(rows)+2)
    image = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(image)
    draw.text((20, 10), title, font=font, fill="black")
    for i, col in enumerate(col_list):
        draw.text((i * cell_width + 10, cell_height), col, font=font, fill="blue")
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            draw.text((c * cell_width + 10, (r+2) * cell_height), val, font=font, fill="black")
    buf = BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    return buf

if st.button("🖼️ 下載履歷總表圖片"):
    img_buf = df_to_image(df)
    st.download_button("🖼️ 下載 PNG 圖片", img_buf, file_name="history_maintenance_log.png", mime="image/png")
