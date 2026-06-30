import os
import sys
from importlib.util import find_spec

import streamlit as st

# Ensure the root directory is in the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.sqlite import init_db
from frontend.history import render_history_page
from frontend.upload import render_upload_page


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(PROJECT_ROOT, ".venv", "bin", "python")


def check_runtime_environment() -> bool:
    """Return True when the app is running in the environment with OCR dependencies."""
    missing_modules = []
    for module_name in ("cv2", "fitz", "paddleocr"):
        if find_spec(module_name) is None:
            missing_modules.append(module_name)

    if not missing_modules:
        return True

    st.error(
        "This Streamlit app is running with a Python environment that is missing OCR/PDF "
        f"dependencies: {', '.join(missing_modules)}."
    )
    st.code(f"{VENV_PYTHON} -m streamlit run app.py", language="bash")
    st.info(f"Current Python: {sys.executable}")
    return False

st.set_page_config(page_title="FIRStruct AI", layout="wide")

if not check_runtime_environment():
    st.stop()

# Initialize database on app startup
init_db()

st.sidebar.title("FIRStruct AI")
page = st.sidebar.radio("Navigation", ["Upload Complaint", "History & Search"])

if page == "Upload Complaint":
    render_upload_page()
elif page == "History & Search":
    render_history_page()
