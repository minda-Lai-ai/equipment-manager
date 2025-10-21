import streamlit as st
# 從 firebase_init 匯入快取函式
from firebase_init import get_firestore_client 
import time 
# 只需要 firestore 來處理 SERVER_TIMESTAMP，不執行初始化
from firebase_admin import firestore 

st.set_page_config(page_title="🔐 使用者登入", layout="centered")
st.title("🔐 使用者登入")

# 檢查是否已登入
if "user" in st.session_state:
    st.info("您已登入，導向主控面板...")
    # 確保跳轉到正確的檔案名稱
    st.switch_page("main_dashboard.py") 

# 🚨 安全性警告 (建議未來改用 Firebase Auth)
st.warning("⚠️ 安全警告：您目前是以手動方式將使用者密碼直接存入 Firestore。建議使用 Firebase Authentication 服務。")

try:
    # 呼叫快取過的函式，穩定取得 db 客戶端
    db = get_firestore_client() 
except Exception:
    # 如果 Firebase 初始化失敗，則停止應用程式
    st.error("❌ 無法連線到 Firestore。請檢查 secrets.toml 和網路連線。")
    st.stop()
    
# --- 登入表單 ---
st.header("🔑 登入")
with st.form("login_form"):
    login_email = st.text_input("Email", key="login_email")
    login_password = st.text_input("密碼", type="password", key="login_password")
    login_button = st.form_submit_button("登入")

# 登入邏輯
if login_button:
    if not login_email or not login_password:
        st.error("❌ Email 和密碼皆為必填。")
        st.stop()

    # 顯示正在驗證，消除卡頓感
    with st.spinner("正在驗證帳號..."):
        user_ref = db.collection("users").document(login_email)
        try:
            # 嘗試從 Firestore 讀取文件
            user_doc = user_ref.get()

            if not user_doc.exists:
                st.error("❌ 登入失敗：此帳號在 Firestore 的 `users` collection 中**不存在**。")
                st.info(f"🔍 嘗試讀取的文件 ID: {login_email}")
                st.stop()

            user_data = user_doc.to_dict()
            
            # --- 顯示從 Firestore 讀取到的資料 (除錯資訊) ---
            st.subheader("💡 讀取到的使用者資料 (請核對欄位名稱)：")
            st.json(user_data)
            
            if "password" not in user_data:
                st.error("❌ 登入失敗：使用者文件缺少 **`password`** 欄位。")
                st.stop()
                
            stored_password = user_data.get("password")

            # 核心密碼比對
            if stored_password == login_password:
                # 登入成功，設定 Session State
                st.session_state["user"] = {
                    "email": login_email,
                    "name": user_data.get("name", "未命名使用者"),
                    "role": user_data.get("role", "user")
                }
                
                st.balloons() 
                st.success("🎉 登入成功！正在導向主頁...")
                time.sleep(1) 
                st.switch_page("main_dashboard.py")

            else:
                st.error("❌ 登入失敗：密碼錯誤。")
                st.warning(f"ℹ️ 輸入密碼長度: {len(login_password)}, 儲存密碼長度: {len(stored_password)}")
                st.warning("請確保輸入的密碼與 Firestore 中 `password` 欄位的值**完全一致**。")

        except Exception as e:
            st.error(f"❌ 發生致命錯誤，通常是連線或權限問題。")
            st.subheader("完整錯誤堆疊：")
            st.exception(e)
        

st.markdown("---")

# --- 註冊區塊 ---
st.header("🆕 註冊新帳號 (測試用)")
with st.expander("點擊展開註冊表單"):
    with st.form("register_form"):
        reg_email = st.text_input("Email (作為帳號)", key="reg_email_reg")
        reg_password = st.text_input("密碼", type="password", key="reg_password_reg")
        reg_name = st.text_input("名稱", key="reg_name_reg", value="測試用戶")
        register_button = st.form_submit_button("註冊")

    if register_button:
        if not reg_email or not reg_password:
            st.error("Email 和密碼皆為必填。")
        else:
            new_user_ref = db.collection("users").document(reg_email)
            # 檢查使用者是否已存在
            if new_user_ref.get().exists:
                st.error("❌ 註冊失敗，此 Email 已經存在。")
            else:
                try:
                    # 寫入新使用者資料到 Firestore
                    new_user_ref.set({
                        "email": reg_email,
                        "password": reg_password,
                        "name": reg_name,
                        "role": "user",
                        "created_at": firestore.SERVER_TIMESTAMP
                    })
                    st.success(f"🎉 帳號 {reg_email} 註冊成功！您現在可以登入了。")
                except Exception as e:
                    st.error(f"❌ 註冊時發生 Firestore 錯誤: {e}")
