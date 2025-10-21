# firebase_init.py
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
from google.cloud.firestore.exceptions import PermissionDenied, GoogleAPICallError
from google.api_core.exceptions import InternalServerError, DeadlineExceeded
import time

APP_NAME = "equipment_manager_app"
# 使用 st.cache_resource 確保 Firebase Admin SDK 只初始化一次，避免衝突和卡頓
@st.cache_resource(ttl=3600)
def get_firestore_client():
    """
    獲取 Firestore 客戶端實例。
    包含初始化邏輯和錯誤診斷，確保連線正常。
    """
    try:
        # 嘗試從 Streamlit secrets 載入 JSON
        firebase_config_str = st.secrets["firebase_adminsdk"]
        # 使用 json.loads 替代 eval，更安全穩定
        cred_dict = json.loads(firebase_config_str)
        
        # 1. 初始化 Firebase App
        try:
            # 嘗試獲取已初始化的 App
            app = firebase_admin.get_app(APP_NAME)
        except ValueError:
            # 如果 App 不存在，則進行初始化
            cred = credentials.Certificate(cred_dict)
            app = firebase_admin.initialize_app(cred, name=APP_NAME)
        
        db = firestore.client(app)

        # 2. 🚨 關鍵步驟：連線測試 🚨
        # 嘗試讀取一個絕對不存在的文件來測試網路連線和讀取權限。
        # 這會強制拋出 PermissionDenied 或網路錯誤，避免應用程式靜默卡住。
        test_doc_ref = db.collection("__connection_test_collection").document("__test_doc")
        
        # 使用 try-except 區塊來執行測試讀取
        try:
            test_doc_ref.get(timeout=5) # 設定 5 秒超時
            # 如果讀取成功（通常不會發生），則無需動作
        except PermissionDenied:
            # 如果連線成功，但被規則拒絕 (這是最常見的卡住原因)
            st.error("❌ Firebase 連線成功，但 **Firestore 安全規則拒絕了操作**。請檢查您的 Firestore Rules，確保 Admin SDK 有讀寫權限。")
            raise  # 拋出錯誤，阻止應用程式繼續運行
        except InternalServerError:
            st.error("❌ Firebase 連線失敗：Google 服務內部錯誤。請稍後再試。")
            raise
        except DeadlineExceeded:
            st.error("❌ Firebase 連線失敗：**網路超時 (Timeout)**。請檢查部署環境的網路連線是否允許對 Firebase 的出站連線。")
            raise
        except GoogleAPICallError as e:
            # 捕捉所有其他的 API 錯誤，例如網路問題
            st.error(f"❌ Firebase 連線或操作失敗。請檢查網路或金鑰。錯誤詳情: {e}")
            raise
        except Exception as e:
             # 捕捉其他未預期的錯誤
            st.error(f"❌ Firebase 初始化時發生未預期錯誤。錯誤類型: {type(e).__name__}，詳情: {e}")
            raise

        # 測試通過或失敗並顯示錯誤後，返回客戶端
        return db

    except json.JSONDecodeError:
        st.error("❌ Firebase 初始化失敗：金鑰 JSON 格式錯誤！請檢查 `.streamlit/secrets.toml` 中 `firebase_adminsdk` 的三重引號和內容是否符合 JSON 格式。")
        raise
    except Exception as e:
        # 捕捉所有 Admin SDK 初始化前的錯誤
        st.error(f"❌ Firebase 連線或初始化失敗。請檢查金鑰內容。錯誤：{e}")
        raise
