import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from supabase import create_client

# Supabase 連線資訊 (保持不變)
supabase = create_client(
    "https://todjfbmcaxecrqlkkvkd.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvZGpmYm1jYXhlY3JxbGtrdmtkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzMjk3NDgsImV4cCI6MjA3NjkwNTc0OH0.0uTJcrHwvnGM8YT1bPHzMyGkQHIJUZWXsVEwEPjp0sA"
)

# 登入檢查 (保持不變)
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("尚未登入或登入已逾時，請回主畫面重新登入。")
    st.stop()

# 側邊欄顯示資訊 (保持不變)
st.sidebar.markdown("---")
st.sidebar.write(f"👤 使用者：{st.session_state['username']}")
st.sidebar.write(f"🧩 角色：{st.session_state['role']}")

# 頁面配置 (保持不變)
st.set_page_config(page_title="🔍 保養履歷資料總覽", layout="wide")
st.title("🔍 保養履歷資料總覽")
if st.button("🔙 返回主控面板"):
    st.switch_page("main_dashboard.py")

# 獲取資料 (保持不變)
result = supabase.table("history_maintenance_log").select("*").execute()
df = pd.DataFrame(result.data)

# 排序邏輯 (保持不變)
main_order_top = ["亞冠", "瑞弘一代", "瑞弘二代"]
main_order_bottom = ["超馬480V", "祐旭480V", "超馬460V", "檢測設備", "車輛相關"]
def get_main_rank(val):
    if pd.isna(val) or str(val).strip() == "":
        return 999
    if val in main_order_top:
        return main_order_top.index(val)
    if val in main_order_bottom:
        return 100 + main_order_bottom.index(val)
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

# 事件處理說明欄位換行顯示函數
def wrap_text(text, width=30):
    import textwrap
    if not isinstance(text, str):
        return ""
    # 這裡的 width 主要是用於計算字元數來換行
    return "\n".join(textwrap.wrap(text, width=width, break_long_words=False))
    # 原始以 index 切割的邏輯 (中文可能較準確):
    # lines = []
    # current = 0
    # while current < len(text):
    #     lines.append(text[current:current+width])
    #     current += width
    # return "\n".join(lines)


if "事件處理說明" in view_df.columns:
    # 這裡在 Streamlit DataFrame 顯示時套用換行 (使用 30 個字元寬度)
    view_df["事件處理說明"] = view_df["事件處理說明"].apply(lambda x: wrap_text(x, width=30))

# 用 st.dataframe 顯示時自動調整欄寬（保持不變）
col_configs = {}
for col in view_df.columns:
    col_len = max(view_df[col].astype(str).map(len).max(), len(col))
    col_configs[col] = st.column_config.TextColumn(width="large" if col_len > 20 else "medium")
st.dataframe(view_df, column_config=col_configs, use_container_width=True)

# 下載按鈕 (保持不變)
st.markdown("---")
st.markdown("💾 若需另存資料（下載至本地裝置），請選擇格式：")
csv_data = '\ufeff' + df.drop(columns=["主設備_序", "次設備_序"]).to_csv(index=False) # 下載時用未換行的 df
st.download_button(
    "下載 CSV",
    data=csv_data.encode("utf-8"),
    file_name="history_maintenance_log.csv",
    mime="text/csv"
)
excel_buffer = BytesIO()
df.drop(columns=["主設備_序", "次設備_序"]).to_excel(excel_buffer, index=False, engine="openpyxl") # 下載時用未換行的 df
st.download_button(
    "下載 Excel",
    data=excel_buffer.getvalue(),
    file_name="history_maintenance_log.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.markdown("📸 若需將表格存為圖片（PNG），請點選按鈕自動生成一張全部欄位的圖片：")

# 圖片生成函數 (核心修改處)
def df_to_image(dataframe, title="保養履歷總表"):
    # 使用預設字體，每個字元寬度固定
    font = ImageFont.load_default()
    # 假設預設字體單行文字高度 (約 10)
    default_text_height = 10
    # 儲存格最小高度 (包含上下的間隔)
    cell_height_padding = 10 
    cell_height = default_text_height + cell_height_padding

    col_list = list(dataframe.columns)
    
    # 1. 準備數據，這裡使用未經換行處理的原始 df，並將字串化
    df_raw = df.drop(columns=["主設備_序", "次設備_序"]).astype(str) 
    rows = df_raw.values.tolist()

    # 2. 動態調整欄寬 (核心修改)
    cell_widths = []
    # 假設一個字元的寬度約為 6 pixels (點陣字體經驗值)
    char_width_approx = 6 
    
    # 特殊處理的欄位及其字元數寬度
    SPECIAL_COL = "事件處理說明"
    SPECIAL_WIDTH_CHARS = 30 # 固定 30 個字元寬度
    
    for i, col in enumerate(col_list):
        if col == SPECIAL_COL:
            # 特殊欄位：固定寬度
            width = SPECIAL_WIDTH_CHARS * char_width_approx + 20 # 額外加 20 pixels 邊距
        else:
            # 其他欄位：依據標題和內容中最長字串的字元數決定寬度
            maxlen = max([len(str(x)) for x in [col] + list(df_raw[col])])
            # 最小寬度 80，最大寬度 400
            width = max(80, min(char_width_approx * maxlen + 20, 400)) 
        cell_widths.append(width)

    img_width = sum(cell_widths) + 20 # 總寬度 + 左右邊距

    # 3. 計算圖片高度 (需考慮多行文字)
    max_row_heights = [] # 儲存每一列的實際最大高度
    for r, row in enumerate(rows):
        max_lines_in_row = 1
        for c, val in enumerate(row):
            # 取得該欄位在圖片生成時的換行字元數限制
            wrap_limit = SPECIAL_WIDTH_CHARS if col_list[c] == SPECIAL_COL else 40
            
            # 使用 wrap_text 函數計算換行後的行數
            lines = wrap_text(str(val), width=wrap_limit).count('\n') + 1
            max_lines_in_row = max(max_lines_in_row, lines)
            
        max_row_heights.append(max_lines_in_row * cell_height) # 該行實際像素高度

    header_height = cell_height + 20 # 標題與第一行 (欄位名稱) 的高度
    img_height = header_height + sum(max_row_heights) + 20 # 總高度 + 底部邊距

    # 4. 繪圖
    image = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(image)

    # 繪製總標題
    draw.text((10, 5), title, font=font, fill="black")

    # 繪製欄位名稱 (表頭)
    current_x = 0
    for i, col in enumerate(col_list):
        draw.text((current_x + 10, cell_height), col, font=font, fill="blue")
        # 繪製分隔線
        draw.line([(current_x, cell_height), (current_x, img_height)], fill="gray", width=1)
        current_x += cell_widths[i]
    # 繪製最右側線
    draw.line([(current_x, cell_height), (current_x, img_height)], fill="gray", width=1)
    # 繪製欄位名稱與資料分隔線
    draw.line([(0, cell_height * 2), (img_width, cell_height * 2)], fill="blue", width=2)
    
    # 繪製資料
    current_y = cell_height * 2
    for r, row in enumerate(rows):
        current_x = 0
        for c, val in enumerate(row):
            # 取得換行限制
            wrap_limit = SPECIAL_WIDTH_CHARS if col_list[c] == SPECIAL_COL else 40
            
            # 換行文字
            val_lines = wrap_text(str(val), width=wrap_limit)
            
            # 繪製文字
            draw.text((current_x + 10, current_y + 5), val_lines, font=font, fill="black")
            
            # 繪製欄位分隔線 (垂直線已在表頭時繪製)
            current_x += cell_widths[c]
            
        # 繪製行分隔線 (水平線)
        draw.line([(0, current_y + max_row_heights[r]), (img_width, current_y + max_row_heights[r])], fill="lightgray", width=1)
        
        # 移動到下一行起始 Y 座標
        current_y += max_row_heights[r]
        

    # 5. 儲存為 BytesIO
    buf = BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    return buf

if st.button("🖼️ 下載履歷總表圖片"):
    # 將未經換行處理的原始 df 傳入，讓 df_to_image 內部處理換行
    img_buf = df_to_image(df.drop(columns=["主設備_序", "次設備_序"])) 
    st.download_button("🖼️ 下載 PNG 圖片", img_buf, file_name="history_maintenance_log.png", mime="image/png")
