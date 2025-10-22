import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
# import json  <-- 移除 json 匯入
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
            # 如果不存在，則直接從 secrets 讀取字典物件
            # IMPORTANT: 這裡假設 st.secrets["firebase_adminsdk"] 已經是 Python 字典/TOML Inline Table
            # 這是為了避免複雜的 JSON/TOML 逃逸字符問題。
            cred_data = st.secrets["firebase_adminsdk"]
            cred = credentials.Certificate(cred_data)
            app = firebase_admin.initialize_app(cred, name=APP_NAME)
        
        db = firestore.client(app)

        # 2. 執行連線和權限測試 (Read/Write)
        test_doc_ref = db.collection("__connection_test__").document("test_document")
        test_doc_ref.get() 

        # 如果成功執行到這裡，表示連線和權限通過
        st.success("✅ Firebase 連線成功，請登入或註冊。")
        return db

    except PermissionDenied as e:
        st.cache_resource.clear()
        raise PermissionDenied(f"連線成功，但權限被拒絕。請檢查 Firestore Security Rules 是否允許 Admin SDK 讀寫。詳情: {e}")
    except (GoogleAPICallError, RetryError) as e:
        st.cache_resource.clear()
        raise type(e)(f"Firebase 連線或操作失敗。錯誤類型: {type(e).__name__}，詳情: {e}")
    except Exception as e:
        st.cache_resource.clear()
        raise Exception(f"Firebase 初始化遇到未知錯誤。錯誤類型: {type(e).__name__}，詳情: {e}")
