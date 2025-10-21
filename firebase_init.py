# firebase_init.py
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

def get_firestore():
    try:
        # 嘗試取得已初始化的 Firebase App
        app = firebase_admin.get_app()
    except ValueError:
        # 尚未初始化 → 執行初始化
        cred = credentials.Certificate(eval(st.secrets["firebase_adminsdk"]))
        app = firebase_admin.initialize_app(cred)
    return firestore.client(app)
