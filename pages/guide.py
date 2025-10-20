import streamlit as st

st.set_page_config(page_title="📘 使用者手冊", layout="wide")
st.title("📘 設備管理系統使用者導引手冊")

st.markdown("本系統提供一套完整的設備管理流程，涵蓋設備請購、維修、保養、履歷紀錄、資料查詢與圖片輸出。所有模組皆採用 Streamlit 架構，資料儲存於 CSV 檔案，並支援模組化擴充與團隊協作。")

st.markdown("---")
st.header("📦 模組總覽")

st.markdown("""
| 模組名稱 | 檔案位置 | 功能說明 |
|----------|-----------|-----------|
| 主控面板 | `main_dashboard.py` | 系統入口，導向各模組頁面 |
| 設備請購維修系統 | `pages/equipment_system.py` | 四層選單：主設備 → 次設備 → 設備 → 編號 |
| 設備詳細資料 | `pages/equipment_detail.py` | 顯示完整設備欄位，導向圖片儲存模組 |
| 編輯設備資料 | `pages/edit_data.py` | 編輯現有設備資料 |
| 新增保養事件 | `pages/add_event.py` | 為設備新增履歷事件 |
| 新增設備 | `pages/new_equipment.py` | 手動輸入一筆全新設備資料 |
| 瀏覽資料庫內容 | `pages/view_data.py` | 顯示主設備與履歷資料表 |
| 圖片儲存模組 | `pages/export_image.py` | 將設備資料輸出為圖片 |
| 保養履歷總覽 | `pages/maintenance_log.py` | 顯示所有保養事件 |
| 資料儲存模組 | `pages/save_data.py` | 匯出資料庫備份（如有） |
| 刪除設備資料 | `pages/delete_data.py` | 刪除設備與履歷資料 |
""", unsafe_allow_html=True)

st.markdown("---")
st.header("📁 資料儲存結構")

st.markdown("""
| 資料檔案 | 路徑 | 說明 |
|----------|------|------|
| 主設備資料庫 | `data/main_equipment_system.csv` | 儲存所有設備的基本資訊與狀態 |
| 保養履歷資料庫 | `data/history_maintenance_log.csv` | 儲存所有設備的保養與維修紀錄 |
| 圖片輸出 | `data/equipment_snapshot_XXX.png` | 儲存設備資料圖片 |
| 備份檔案 | `data/*_before_delete_YYYYMMDD.csv` | 刪除前自動備份的資料庫版本 |
""", unsafe_allow_html=True)

st.markdown("---")
st.header("🧑‍�� 使用流程建議")

st.markdown("""
1. **新增設備資料** → 使用 `new_equipment.py` 建立新設備  
2. **新增保養事件** → 使用 `add_event.py` 為設備新增履歷  
3. **瀏覽與查詢** → 使用 `equipment_system.py` 或 `view_data.py` 查詢設備與履歷  
4. **圖片輸出** → 使用 `equipment_detail.py` → `export_image.py` 將資料存成圖片  
5. **資料刪除** → 使用 `delete_data.py` 刪除設備與履歷（含備份）  
6. **資料總覽** → 使用 `maintenance_log.py` 或 `view_data.py` 查看全系統資料  
""")

st.markdown("---")
st.header("🛡️ 防呆與錯誤處理機制")

st.markdown("""
- 所有模組皆加入欄位檢查與空值防呆  
- 刪除模組自動備份資料庫  
- 圖片儲存模組支援欄位動態擴充  
- 主控面板使用 `st.page_link()` 穩定跳轉  
""")

st.markdown("---")
st.header("🔧 建議擴充模組（可選）")

st.markdown("""
| 模組名稱 | 功能構想 |
|----------|----------|
| PDF 匯出模組 | 將設備資料或履歷輸出為 PDF 報告 |
| 圖表分析模組 | 顯示設備狀況分布、保養頻率、年度統計 |
| 登入驗證模組 | 加入使用者登入、權限控管、操作紀錄 |
| 資料檢查器 | 檢查 CSV 欄位、格式、缺值、重複編號 |
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("海運組油氣處理課")

