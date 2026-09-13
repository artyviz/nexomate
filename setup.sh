#!/usr/bin/env bash
set -e

echo "============================================"
echo "  NEXOMATE MVP — Setup"
echo "============================================"
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed."
    echo "Install Python 3.11+ and try again."
    exit 1
fi

echo "[1/5] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "[2/5] Installing dependencies..."
pip install -r requirements.txt

echo "[3/5] Checking Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "[WARNING] Ollama is not installed."
    echo "Download from https://ollama.com"
    echo "After installing, run: ollama pull llama3.1"
else
    echo "Ollama found. Pulling llama3.1 model..."
    ollama pull llama3.1
fi

echo "[4/5] Initializing database..."
python3 -c "from database.database import engine, Base; from database import models; Base.metadata.create_all(bind=engine); print('Database ready.')"

echo "[5/5] Creating .env from .env.example..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env — edit it with your SMTP credentials."
else
    echo ".env already exists, skipping."
fi

echo
echo "============================================"
echo "  Setup complete!"
echo
echo "  Run Nexomate with:"
echo "    source venv/bin/activate"
echo "    streamlit run app.py"
echo "============================================"
