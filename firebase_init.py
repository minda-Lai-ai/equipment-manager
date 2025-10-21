# firebase_init.py - Firebase Admin SDK 初始化邏輯
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import json

APP_NAME = "equipment_manager_app" # 確保使用唯一的應用程式名稱

# 使用 st.cache_resource 確保 Firebase 僅初始化一次
@st.cache_resource
def get_firestore_client():
    """
    初始化 Firebase Admin SDK 並回傳 Firestore 客戶端實例。
    從 st.secrets['firebase_adminsdk'] 載入憑證。
    """
    try:
        # 檢查是否已經使用 APP_NAME 初始化
        app = firebase_admin.get_app(APP_NAME)
        st.toast("✅ Firebase 客戶端已從快取載入。", icon="🔑")
    except ValueError:
        # 尚未初始化，進行初始化
        try:
            # 嘗試解析 JSON 格式的服務帳戶憑證
            secret_json = json.loads(st.secrets["firebase_adminsdk"])
            cred = credentials.Certificate(secret_json)
            # 這裡使用 name=APP_NAME 確保多次呼叫時不會報錯
            app = firebase_admin.initialize_app(cred, name=APP_NAME) 
            st.toast("✅ Firebase Admin SDK 初始化成功 (已快取)", icon="🔑")
        except KeyError:
            st.error("❌ 錯誤：請在 .streamlit/secrets.toml 中設定 'firebase_adminsdk' 金鑰。")
            raise
        except json.JSONDecodeError:
             st.error("❌ 錯誤：`firebase_adminsdk` 的值不是有效的 JSON 格式字串。")
             raise
        except Exception as e:
            st.error(f"❌ 錯誤：無法初始化 Firebase。錯誤詳情: {e}")
            raise
            
    return firestore.client(app)
