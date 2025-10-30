import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from supabase import create_client

supabase = create_client(
    "https://todjfbmcaxecrqlkkvkd.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvZGpmYm1jYXhlY3JxbGtrdmtkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzMjk3NDgsImV4cCI6MjA3NjkwNTc0OH0.0uTJcrHwvnGM8YT1bPHzMyGkQHIJUZWXsVEwEPjp0sA"
)

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

#MINDA

# 取得履歷資料
result = supabase.table("history_maintenance_log").select("*").execute()
df = pd.DataFrame(result.data)

# ====== 在這裡加入你需求的格式處理 ======

# 處理、包裝函數（可放在上面，也可放此）
def wrap_text(...): ...
def get_colwidths(...): ...
def df_to_html_custom(...): ...

if "事件處理說明" in df.columns:
    df["事件處理說明"] = df["事件處理說明"].apply(wrap_text)

st.markdown("""
<style>
td, th { vertical-align:top !important; }
</style>
""", unsafe_allow_html=True)

# ====== 在原本 st.write(df) 的地方改成下面這行 ======
st.write(df_to_html_custom(df), unsafe_allow_html=True)

#MINDA

main_order_top = ["亞冠", "瑞弘一代", "瑞弘二代"]
main_order_bottom = ["超馬480V", "祐旭480V", "超馬460V", "檢測設備", "車輛相關"]
def get_main_rank(val):
    if pd.isna(val) or str(val).strip() == "":
        return 999
    if val in main_order_top:
        return main_order_top.index(val)
    if val in main_order_bottom:
        # 保證這幾項在正常主設備之後、空白之前，順序依 main_order_bottom
        return 100 + main_order_bottom.index(val)
    # 沒包含在固定排序的在中間
    return 50

df["主設備_序"] = df["主設備"].apply(get_main_rank)

sub_order = [
    "壓縮機(C1~C4-2或C401~C702)", "凝結箱", "進氣系統", "散熱風車",
    "空壓油壓系統", "除霜系統", "回收油系統", "活性碳系統", "電控系統"
]
def get_sub_rank(val):
    if pd.isna(val) or str(val).strip() == "":
        return 999
    if val in sub_order:
        return sub_order.index(val)
    return 50

df["次設備_序"] = df["次設備"].apply(get_sub_rank)

if "發生異常日期" in df.columns:
    df["發生異常日期"] = pd.to_datetime(df["發生異常日期"], errors="coerce")

df = df.sort_values(
    by=["主設備_序", "主設備", "次設備_序", "次設備", "發生異常日期"],
    ascending=[True, True, True, True, False]
)

view_df = df.drop(columns=["主設備_序", "次設備_序"])

# 事件處理說明欄位換行顯示
def wrap_text(text, width=30):
    # 一般中文字約2字元寬，30-35較佳
    import textwrap
    if not isinstance(text, str):
        return ""
    # 以全形字寬計算（寬度指純中文字）可視需求調整
    lines = []
    current = 0
    while current < len(text):
        lines.append(text[current:current+30])
        current += 30
    return "\n".join(lines)
if "事件處理說明" in view_df.columns:
    view_df["事件處理說明"] = view_df["事件處理說明"].apply(wrap_text)

# 用 st.dataframe 顯示時自動調整欄寬（streamlit 1.28+ 支援 column_config）
col_configs = {}
for col in view_df.columns:
    col_len = max(view_df[col].astype(str).map(len).max(), len(col))
    col_configs[col] = st.column_config.TextColumn(width="large" if col_len > 20 else "medium")
st.dataframe(view_df, column_config=col_configs, use_container_width=True)

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
    # 動態調整欄寬
    cell_widths = []
    for i, col in enumerate(col_list):
        maxlen = max([len(str(x)) for x in [col] + list(dataframe[col])])
        width = max(200, min(40*maxlen, 400))
        cell_widths.append(width)
    cell_height = 30
    img_width = sum(cell_widths)
    img_height = cell_height * (len(rows) + 2)
    image = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(image)
    x = 0
    for i, col in enumerate(col_list):
        draw.text((x + 10, cell_height), col, font=font, fill="blue")
        x += cell_widths[i]
    for r, row in enumerate(rows):
        x = 0
        for c, val in enumerate(row):
            # 強制換行長字串
            val_lines = wrap_text(str(val), width=30 if col_list[c]=="事件處理說明" else 40)
            draw.text((x + 10, (r+2) * cell_height), val_lines, font=font, fill="black")
            x += cell_widths[c]
    buf = BytesIO()
    draw.text((20, 10), title, font=font, fill="black")
    image.save(buf, format="PNG")
    buf.seek(0)
    return buf

if st.button("🖼️ 下載履歷總表圖片"):
    img_buf = df_to_image(view_df)
    st.download_button("🖼️ 下載 PNG 圖片", img_buf, file_name="history_maintenance_log.png", mime="image/png")
