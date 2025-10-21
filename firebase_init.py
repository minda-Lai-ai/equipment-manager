# firebase_init.py
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

APP_NAME = "equipment_manager_app"

def get_firestore():
    try:
        app = firebase_admin.get_app(APP_NAME)
    except ValueError:
        cred = credentials.Certificate(eval(st.secrets["firebase_adminsdk"]))
        app = firebase_admin.initialize_app(cred, name=APP_NAME)
    return firestore.client(app)
