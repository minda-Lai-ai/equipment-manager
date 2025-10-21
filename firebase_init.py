# firebase_init.py
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import json
from functools import lru_cache

APP_NAME = "equipment_manager_app"

@st.cache_resource
def get_firestore_client():
    """
    初始化並返回 Firestore 客戶端。
    使用 st.cache_resource 確保 Firebase Admin SDK 只初始化一次，避免多頁面衝突。
    同時加入詳細的錯誤處理，以診斷 secrets.toml 中的金鑰問題。
    """
    try:
        # 1. 嘗試從 st.secrets 載入 JSON 憑證字串
        service_account_json = st.secrets["firebase_adminsdk"]
        cred_info = json.loads(service_account_json)
        
        # 2. 初始化 Firebase Admin SDK
        cred = credentials.Certificate(cred_info)
        
        # 檢查是否已存在名為 APP_NAME 的 App
        try:
            app = firebase_admin.get_app(APP_NAME)
        except ValueError:
            # 如果不存在，則初始化它
            app = firebase_admin.initialize_app(cred, name=APP_NAME)
            
        # 3. 返回 Firestore 客戶端
        return firestore.client(app)

    except KeyError:
        # secrets.toml 中缺少 firebase_adminsdk 金鑰
        st.error("❌ 錯誤：請在 .streamlit/secrets.toml 中設定 'firebase_adminsdk' 金鑰。")
        st.stop()
    except json.JSONDecodeError as e:
        # 金鑰字串不是合法的 JSON 格式 (例如缺少三重引號, 內部引號錯誤)
        st.error(f"❌ 金鑰 JSON 格式錯誤！請檢查 secrets.toml 中的 'firebase_adminsdk' 是否為有效的 JSON 字串，並使用三重雙引號包裹。錯誤詳情: {e}")
        st.stop()
    except Exception as e:
        # 捕捉其他所有 Firebase 或初始化錯誤 (如網路問題、憑證無效等)
        st.error(f"❌ Firebase 連線或初始化失敗。請檢查金鑰內容或服務帳戶權限。錯誤: {type(e).__name__}: {e}")
        st.stop()

# 為了兼容舊版程式碼，但建議使用 get_firestore_client
get_firestore = get_firestore_client
