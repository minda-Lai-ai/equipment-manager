# firebase_init.py
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
# 關鍵修正：將所有 Firestore 相關的異常，改從更通用的 google.api_core 匯入
from google.api_core.exceptions import PermissionDenied, GoogleAPICallError, InternalServerError, DeadlineExceeded
import time

APP_NAME = "equipment_manager_app"
# 使用 st.cache_resource 確保 Firebase Admin SDK 只初始化一次，避免衝突和卡頓
@st.cache_resource(ttl=3600)
def get_firestore_client():
    """
    獲取 Firestore 客戶端實例。
    包含初始化邏輯和錯誤診斷，確保連線正常。
    """
    db = None
    try:
        # 嘗試從 Streamlit secrets 載入 JSON
        firebase_config_str = st.secrets["firebase_adminsdk"]
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
        test_doc_ref = db.collection("__connection_test_collection").document("__test_doc")
        
        # 使用 try-except 區塊來執行測試讀取
        try:
            # 讀取不存在文件，並將超時時間延長到 15 秒
            test_doc_ref.get(timeout=15)
        except PermissionDenied:
            st.error("❌ Firebase 連線成功，但 **Firestore 安全規則拒絕了操作**。請檢查您的 Firestore Rules，確保 Admin SDK 有讀寫權限。")
            raise  # 拋出錯誤，阻止應用程式繼續運行
        except InternalServerError:
            st.error("❌ Firebase 連線失敗：Google 服務內部錯誤。請稍後再試。")
            raise
        except DeadlineExceeded:
            st.error("❌ Firebase 連線失敗：**網路超時 (Timeout)**。請檢查部署環境的網路連線是否允許對 Firebase 的出站連線。")
            raise
        except Exception as e:
            error_type = type(e).__name__
            # NotFoundError 是正常的連線測試結果，表示讀取成功但文件不存在。
            if error_type not in ["NotFound", "NotFoundError"]: 
                st.error(f"❌ Firebase 連線或操作失敗。錯誤類型: {error_type}，詳情: {e}")
                raise

        # 測試通過後 (捕捉到 NotFound 錯誤是正常的)，返回客戶端
        return db

    except json.JSONDecodeError:
        st.error("❌ Firebase 初始化失敗：金鑰 JSON 格式錯誤！請檢查 `.streamlit/secrets.toml` 中 `firebase_adminsdk` 的三重引號和內容是否符合 JSON 格式。")
        raise
    except Exception as e:
        # 捕捉所有 Admin SDK 初始化前的錯誤
        # 如果 db 已經被初始化但後面失敗，則只返回 db
        if db:
            return db

        st.error(f"❌ Firebase 連線或初始化失敗。請檢查金鑰內容。錯誤：{e}")
        raise
