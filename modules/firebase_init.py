# firebase_init.py
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

def get_firestore():
    try:
        app = firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(eval(st.secrets["firebase_adminsdk"]))
        app = firebase_admin.initialize_app(cred)
    return firestore.client(app)
