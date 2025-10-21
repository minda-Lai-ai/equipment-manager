# firebase_init.py - Streamlit Firebase Admin SDK 初始化邏輯
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import json

# 應用程式名稱，用於避免重複初始化錯誤 (ValueError)
APP_NAME = "equipment_manager_app"

@st.cache_resource
def get_firestore_client():
    """
    初始化 Firebase Admin SDK 並回傳 Firestore 客戶端。
    此函數使用 st.cache_resource 確保只執行一次，並包含錯誤診斷。
    """
    try:
        # 嘗試取得已初始化的 App
        app = firebase_admin.get_app(APP_NAME)
        # 如果成功取得，直接回傳 Firestore 客戶端
        return firestore.client(app)

    except ValueError:
        # App 尚未初始化，繼續初始化流程
        pass

    try:
        # 1. 安全地從 st.secrets 載入 JSON 字串
        # 如果 JSON 格式不正確，json.loads 會拋出 JSONDecodeError
        secrets_json = st.secrets["firebase_adminsdk"]
        cred_dict = json.loads(secrets_json)

        # 2. 建立憑證
        cred = credentials.Certificate(cred_dict)

        # 3. 初始化 App
        app = firebase_admin.initialize_app(cred, name=APP_NAME)

        st.success("✅ Firebase Admin SDK 初始化成功！")
        return firestore.client(app)

    except KeyError:
        # st.secrets 中沒有 firebase_adminsdk 這個 key
        st.error("❌ 錯誤：請在 .streamlit/secrets.toml 中設定 'firebase_adminsdk' 金鑰。")
        st.stop()
    
    except json.JSONDecodeError as e:
        # JSON 格式錯誤
        st.error(f"❌ 錯誤：金鑰 JSON 格式錯誤！請檢查 secrets.toml 中的三重引號和內容是否為有效的 JSON。詳情: {e}")
        st.stop()

    except Exception as e:
        # 捕捉所有 Admin SDK 初始化時可能拋出的其他錯誤 (如憑證無效、網路問題等)
        st.error(f"❌ Firebase 連線或初始化失敗。請檢查金鑰內容。錯誤：{e}")
        st.stop()

# 為了兼容性，保留舊的函式名稱 (雖然不推薦使用)
def get_firestore():
    return get_firestore_client()
