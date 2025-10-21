# firebase_init.py
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

def get_firestore():
    if not firebase_admin._apps:
        cred = credentials.Certificate(eval(st.secrets["firebase_adminsdk"]))
        firebase_admin.initialize_app(cred)
    return firestore.client()
