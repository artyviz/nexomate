# main.py
"""Alternative entry point for Nexomate — runs setup then launches Streamlit."""

import subprocess
import sys
from pathlib import Path
from database.database import engine, Base
from database import models  # noqa: F401

def main():
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database ready.")

    # Ensure data directories exist
    data_dir = Path(__file__).parent / "data"
    (data_dir / "exports").mkdir(parents=True, exist_ok=True)
    (data_dir / "imports").mkdir(parents=True, exist_ok=True)
    Path(__file__).parent.joinpath("logs").mkdir(exist_ok=True)

    # Launch Streamlit
    app_path = Path(__file__).parent / "app.py"
    print(f"🚀 Launching Nexomate at http://localhost:8501")
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path),
                    "--server.headless", "true"])

if __name__ == "__main__":
    main()
