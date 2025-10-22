import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import json
from google.api_core.exceptions import PermissionDenied, GoogleAPICallError, RetryError

# 使用一個唯一的 App Name 來避免衝突
APP_NAME = "equipment_manager_app"
# TEST_TIMEOUT_SECONDS 已經移除

# 使用 st.cache_resource 確保 Firebase 僅初始化一次
@st.cache_resource(show_spinner="⏳ 正在初始化 Firebase 連線...")
def get_firestore_client():
    try:
        # 1. 初始化 App
        try:
            # 嘗試取得已命名的 App 實例
            app = firebase_admin.get_app(APP_NAME)
        except ValueError:
            # 如果不存在，則從 secrets 載入憑證並初始化
            cred_data = json.loads(st.secrets["firebase_adminsdk"])
            cred = credentials.Certificate(cred_data)
            app = firebase_admin.initialize_app(cred, name=APP_NAME)
        
        db = firestore.client(app)

        # 2. 執行連線和權限測試 (Read/Write)
        # 嘗試讀取一個絕對不存在的文件來測試連線和權限
        test_doc_ref = db.collection("__connection_test__").document("test_document")
        
        # 移除 explicit timeout，讓底層 SDK 決定超時，通常可以更快失敗。
        test_doc_ref.get() 

        # 如果成功執行到這裡，表示連線和權限通過
        return db

    except PermissionDenied as e:
        # 如果規則不允許讀取 test collection，則清除快取，並拋出錯誤
        st.cache_resource.clear()
        raise PermissionDenied(f"連線成功，但權限被拒絕。請檢查 Firestore Security Rules 是否允許 Admin SDK 讀寫。詳情: {e}")
    except (GoogleAPICallError, RetryError) as e:
        # 如果發生網路錯誤或金鑰錯誤 (如 Invalid JWT Signature)
        st.cache_resource.clear() # 清除快取，以便下次重新載入修正過後的 secrets.toml
        # 重新拋出錯誤，讓 Streamlit 顯示詳細信息
        raise type(e)(f"Firebase 連線或操作失敗。錯誤類型: {type(e).__name__}，詳情: {e}")
    except Exception as e:
        # 捕捉其他所有潛在錯誤 (例如 JSON 格式錯誤)
        st.cache_resource.clear()
        raise Exception(f"Firebase 初始化遇到未知錯誤。錯誤類型: {type(e).__name__}，詳情: {e}")
