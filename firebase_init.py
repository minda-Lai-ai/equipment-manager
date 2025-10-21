# firebase_init.py
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import json

APP_NAME = "equipment_manager_app"

def get_firestore():
    """
    初始化 Firebase Admin SDK 並回傳 Firestore 客戶端實例。
    從 st.secrets['firebase_adminsdk'] 載入憑證。
    """
    try:
        # 檢查是否已經初始化
        app = firebase_admin.get_app(APP_NAME)
    except ValueError:
        # 尚未初始化，進行初始化
        try:
            # 嘗試解析 JSON 格式的服務帳戶憑證
            secret_json = json.loads(st.secrets["firebase_adminsdk"])
            cred = credentials.Certificate(secret_json)
            app = firebase_admin.initialize_app(cred, name=APP_NAME)
        except KeyError:
            st.error("❌ 錯誤：請在 .streamlit/secrets.toml 中設定 'firebase_adminsdk' 金鑰。")
            st.stop()
        except json.JSONDecodeError:
             st.error("❌ 錯誤：`firebase_adminsdk` 的值不是有效的 JSON 格式字串。請檢查格式。")
             st.stop()
        except Exception as e:
            st.error(f"❌ 錯誤：無法初始化 Firebase。錯誤詳情: {e}")
            st.exception(e) # 顯示詳細錯誤
            st.stop()
            
    return firestore.client(app)
