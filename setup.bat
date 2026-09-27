@echo off
echo ============================================
echo   NEXOMATE MVP — Setup
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Download Python 3.11+ from https://python.org
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo [2/5] Installing dependencies...
pip install -r requirements.txt

echo [3/5] Checking AI configuration...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Ollama is not installed.
    echo You can use free Groq Cloud AI by setting GROQ_API_KEY in .env.
    echo Or install Ollama from https://ollama.com and run: ollama pull llama3.1
) else (
    echo [INFO] Ollama found. You can pull llama3.1 if running locally:
    echo        ollama pull llama3.1
)

echo [4/5] Initializing database...
python -c "from database.database import engine, Base; from database import models; Base.metadata.create_all(bind=engine); print('Database ready.')"

echo [5/5] Creating .env from .env.example...
if not exist .env (
    copy .env.example .env
    echo Created .env — edit it with your SMTP credentials.
) else (
    echo .env already exists, skipping.
)

echo.
echo ============================================
echo   Setup complete!
echo.
echo   Run Nexomate with:
echo     venv\Scripts\activate
echo     streamlit run app.py
echo ============================================
pause
