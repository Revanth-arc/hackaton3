import streamlit as st
import sys
import os

# Ensure the root directory is in the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.sqlite import init_db
from frontend.upload import render_upload_page
from frontend.history import render_history_page

st.set_page_config(page_title="FIRStruct AI", layout="wide")

# Initialize database on app startup
init_db()

st.sidebar.title("FIRStruct AI")
page = st.sidebar.radio("Navigation", ["Upload Complaint", "History & Search"])

if page == "Upload Complaint":
    render_upload_page()
elif page == "History & Search":
    render_history_page()
