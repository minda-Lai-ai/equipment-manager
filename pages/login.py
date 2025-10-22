import streamlit as st
import json
from firebase_init import get_firestore_client
from google.api_core.exceptions import PermissionDenied, NotFound, GoogleAPICallError
import sys # 匯入 sys 用於顯示錯誤詳情

st.set_page_config(page_title="🔐 使用者登入", layout="centered")
st.title("🔐 使用者登入")

# 1. 嘗試初始化 Firestore 客戶端
try:
    db = get_firestore_client()
except Exception as e:
    # 如果初始化失敗（通常是 secrets.toml 或網路問題），直接顯示錯誤
    st.error(f"❌ Firebase 連線或初始化失敗。請檢查 secrets.toml。錯誤詳情: {type(e).__name__}，{e}")
    st.stop()
    
# 如果初始化成功，顯示一個綠色提示 (方便快速判斷連線狀態)
st.success("✅ Firebase 連線成功，請登入或註冊。")

# --- 登入表單 ---
st.header("👤 登入系統")
email = st.text_input("Email", key="login_email")
password = st.text_input("密碼", type="password", key="login_password")

if st.button("登入", use_container_width=True):
    if not email or not password:
        st.error("請輸入 Email 和密碼")
        st.stop()
        
    try:
        user_ref = db.collection("users").document(email)
        user_doc = user_ref.get()

        if user_doc.exists:
            user_data = user_doc.to_dict()
            
            # 💡 除錯：顯示從 Firestore 讀取到的資料，用來比對密碼欄位名稱
            st.info(f"💡 從 Firestore 讀取到的文件內容：{user_data}")
            
            # 注意：這裡直接比對明文密碼，請考慮安全風險
            if "password" in user_data and user_data["password"] == password:
                st.session_state["user"] = {
                    "email": email,
                    "name": user_data.get("name", "未命名使用者"),
                    "role": user_data.get("role", "user")
                }
                st.success("✅ 登入成功，正在導向主頁...")
                # 使用 switch_page 導航到主頁的 page_title
                st.switch_page("🧭 設備管理主控面板") 
            else:
                st.error("❌ 登入失敗：密碼錯誤，或 Firestore 文件中缺少 'password' 欄位。")
        else:
            st.error("❌ 登入失敗：此帳號在 Firestore 的 users collection 中不存在。")

    except PermissionDenied:
        st.error("❌ 登入失敗：Firestore 權限不足 (Permission Denied)。請檢查您的 Firebase Security Rules 是否允許 Admin SDK 讀取 users collection。")
    except Exception as e:
        # 捕捉其他所有操作錯誤，避免頁面卡住
        st.error(f"❌ 登入時發生無法預期的錯誤。錯誤類型: {type(e).__name__}，詳情: {e}")

# --- 註冊新帳號 (測試用) ---
st.markdown("---")
with st.expander("📝 註冊新帳號 (測試用 - 確保資料庫有初始資料)"):
    reg_email = st.text_input("註冊 Email (用作文件 ID)", key="reg_email")
    reg_password = st.text_input("註冊密碼", type="password", key="reg_password")
    reg_name = st.text_input("顯示名稱", key="reg_name", value="")
    
    if st.button("註冊新帳號", type="primary", use_container_width=True):
        if not reg_email or not reg_password:
            st.error("Email 和密碼不能為空")
            st.stop()

        try:
            user_ref = db.collection("users").document(reg_email)
            
            # 檢查帳號是否已存在
            if user_ref.get().exists:
                st.warning("⚠️ 此帳號已存在，請直接登入。")
            else:
                # 新增使用者文件（明文儲存密碼）
                user_ref.set({
                    "email": reg_email,
                    "password": reg_password, # 🚨 嚴重安全風險！強烈建議使用 Firebase Auth 進行密碼雜湊
                    "name": reg_name,
                    "role": "user",
                    "created_at": firestore.SERVER_TIMESTAMP
                })
                st.success(f"✅ 帳號 {reg_email} 註冊成功！請使用此帳號登入。")
                
        except PermissionDenied:
            st.error("❌ 註冊失敗：Firestore 權限不足 (Permission Denied)。請檢查您的 Firebase Security Rules 是否允許 Admin SDK 寫入 users collection。")
        except Exception as e:
            st.error(f"❌ 註冊時發生無法預期的錯誤。錯誤類型: {type(e).__name__}，詳情: {e}")
