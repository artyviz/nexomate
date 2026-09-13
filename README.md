# Nexomate MVP

**Research → Find → Verify → Score → Store → Personalize → Send → Track → Learn**

Nexomate is a self-hosted lead generation and outreach automation platform. It analyzes businesses, discovers prospects, scores leads, generates personalized outreach messages, and tracks replies — all running locally.

## Quick Start

### Windows
```bash
setup.bat
```

### Linux / macOS
```bash
chmod +x setup.sh
./setup.sh
```

### Manual Setup
```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env       # Then edit .env with your credentials

# 4. Start Ollama (for AI features)
ollama serve
ollama pull llama2

# 5. Run Nexomate
streamlit run app.py
```

## Features

| Feature | Status |
|---|---|
| Client Onboarding | ✅ |
| Business Website Analysis | ✅ |
| ICP Generation (AI) | ✅ |
| Web Lead Discovery | ✅ |
| Lead Scoring | ✅ |
| SQLite Database | ✅ |
| Excel Import/Export | ✅ |
| AI Email Generation | ✅ |
| Email Sending (SMTP) | ✅ |
| Reply Tracking (IMAP) | ✅ |
| Reply Classification (AI) | ✅ |
| WhatsApp Messages | ✅ (Manual) |
| SMS Messages | ✅ (Manual) |
| Campaign Management | ✅ |
| Analytics Dashboard | ✅ |
| Demo Data | ✅ |

## Tech Stack

- **Frontend:** Streamlit (custom SaaS-style CSS)
- **Backend:** Python 3.11+
- **Database:** SQLite + SQLAlchemy
- **AI:** Ollama (local LLM)
- **Email:** smtplib / imaplib
- **Web Research:** requests + BeautifulSoup
- **Excel:** pandas + openpyxl

## Architecture

```
nexomate/
├── app.py                  # Streamlit entry point
├── main.py                 # Alternative launcher
├── config.py               # Configuration
├── database/               # SQLAlchemy models & connection
├── ai/                     # AI provider abstraction
├── sourcing/               # Lead discovery & web scraping
├── scoring/                # Lead scoring engine
├── outreach/               # Email, WhatsApp, SMS
├── excel/                  # Import/Export
├── dashboard/              # Streamlit UI pages
├── data/                   # SQLite DB, exports, imports
└── logs/                   # Application logs
```

## Configuration

Copy `.env.example` to `.env` and set your credentials:

- **SMTP:** Gmail App Password or Outlook
- **IMAP:** For reply tracking
- **Ollama:** Local AI model

## Demo Mode

Go to **Settings → Demo Data → Load Demo Data** to populate the dashboard with 20 sample leads, 3 campaigns, 10 messages, and 5 replies.
"# nexomate" 
