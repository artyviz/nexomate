# streamlit_app.py
"""Streamlit Cloud default entry point for Nexomate."""
import runpy
from pathlib import Path

app_file = Path(__file__).resolve().parent / "app.py"
runpy.run_path(str(app_file), run_name="__main__")
