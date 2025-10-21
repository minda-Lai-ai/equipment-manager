# firebase_init.py
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

def get_firestore():
    """
    初始化 Firebase Admin SDK 並回傳 Firestore 物件。
    確保只初始化一次，避免 ValueError。
    """
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(eval(st.secrets["firebase_adminsdk"]))
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"❌ Firebase 初始化失敗：{e}")
            st.stop()
    return firestore.client()
