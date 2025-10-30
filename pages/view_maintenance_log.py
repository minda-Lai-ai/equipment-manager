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

result = supabase.table("history_maintenance_log").select("*").execute()
df = pd.DataFrame(result.data)

# 主設備自訂排序（最後五個+空白排最後）
main_order = [
    "亞冠", "瑞弘一代", "瑞弘二代",  # 先排這三個
    # 以下五個排最後
    "超馬480V", "祐旭480V", "超馬460V", "檢測設備", "車輛相關"
]
def get_main_rank(val):
    if pd.isna(val) or (str(val).strip() == ""):
        return 999  # 空白永遠最後
    if val in main_order:
        return main_order.index(val)
    # 未列在指定名單者在這三個之間（保守處理）
    return len(main_order)

df["主設備_序"] = df["主設備"].apply(get_main_rank)

# 次設備自訂排序
sub_order = [
    "壓縮機(C1~C4-2或C401~C702)", "凝結箱", "進氣系統", "散熱風車",
    "空壓油壓系統", "除霜系統", "回收油系統", "活性碳系統", "電控系統"
]
def get_sub_rank(val):
    if pd.isna(val) or (str(val).strip() == ""):
        return 999
    if val in sub_order:
        return sub_order.index(val)
    return len(sub_order)

df["次設備_序"] = df["次設備"].apply(get_sub_rank)

# 日期處理（由新到舊）
if "發生異常日期" in df.columns:
    df["發生異常日期"] = pd.to_datetime(df["發生異常日期"], errors="coerce")

# 排序：先主設備順序，再主設備名，再次設備順序，再次設備名，再日期新到舊
df = df.sort_values(
    by=["主設備_序", "主設備", "次設備_序", "次設備", "發生異常日期"],
    ascending=[True, True, True, True, False]
)

view_df = df.drop(columns=["主設備_序", "次設備_序"])
st.dataframe(view_df, use_container_width=True)

st.markdown("---")
st.markdown("💾 若需另存資料（下載至本地裝置），請選擇格式：")

csv_data = '\ufeff' + view_df.to_csv(index=False)
st.download_button(
    "下載 CSV",
    data=csv_data.encode("utf-8"),
    file_name="history_maintenance_log.csv",
    mime="text/csv"
)
excel_buffer = BytesIO()
view_df.to_excel(excel_buffer, index=False, engine="openpyxl")
st.download_button(
    "下載 Excel",
    data=excel_buffer.getvalue(),
    file_name="history_maintenance_log.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.markdown("📸 若需將表格存為圖片（PNG），請點選按鈕自動生成一張全部欄位的圖片：")

def df_to_image(dataframe, title="保養履歷總表"):
    font = ImageFont.load_default()
    col_list = list(dataframe.columns)
    rows = dataframe.astype(str).values.tolist()
    cell_width = 200
    cell_height = 30
    img_width = cell_width * len(col_list)
    img_height = cell_height * (len(rows) + 2)
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
    img_buf = df_to_image(view_df)
    st.download_button("🖼️ 下載 PNG 圖片", img_buf, file_name="history_maintenance_log.png", mime="image/png")
