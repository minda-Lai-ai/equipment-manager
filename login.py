import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# ✅ Firebase 初始化（絕對穩定版本）
if not firebase_admin._apps:
    cred = credentials.Certificate(eval(st.secrets["firebase_adminsdk"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()
