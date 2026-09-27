# Nexomate

<p align="center">
  <strong>Autonomous B2B Lead Intelligence & Cold Outreach Engine</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Cloud%20AI-Groq%20(Free)-F05032?style=flat" alt="Groq AI" />
  <img src="https://img.shields.io/badge/Local%20AI-Ollama-000000?style=flat" alt="Ollama" />
  <img src="https://img.shields.io/badge/Database-SQLite%20%2B%20SQLAlchemy-003B57?style=flat&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/Deploy-Render.com-46E3B7?style=flat&logo=render&logoColor=white" alt="Render" />
</p>

---

## ⚡ Overview

**Nexomate** is an autonomous, self-hosted lead discovery, scoring, and cold outreach platform. It enables businesses to systematically find high-fit B2B prospects, analyze websites, generate deeply personalized email sequences, send outbound campaigns via SMTP, and automatically classify incoming replies via AI.

### Key Capabilities
- 🌐 **100% Free Autonomous Prospector**: Discovers leads via open search engines (DuckDuckGo Lite), crawls company websites, and parses verified business emails, phones, and leadership contacts with zero third-party API subscription costs.
- ⚡ **Dual AI Architecture**:
  - **Groq Cloud AI (Default & Free)**: Lightning-fast cloud inference (`qwen/qwen3.8-27b`, `openai/gpt-oss-120b`). Requires zero GPU/RAM overhead on your server.
  - **Ollama Local AI (Fallback / Offline)**: Private, fully offline inference running directly on your workstation or server.
  - **Auto Provider Selection**: Automatically picks Groq if an API key is present; gracefully falls back to Ollama if running locally; enables manual operation if offline.
- 🎯 **Lead Scoring & ICP Engine**: Evaluates prospect relevance, buying signals, and pain points against defined Ideal Customer Profiles (ICPs).
- ✉️ **Cold Outreach Sequence Engine**: Generates context-aware, personalized emails with merge tags, handles automated batch sending with rate throttling, and logs full audit trails.
- 📥 **IMAP Inbound Reply Intercept**: Monitors inboxes for replies, links them back to prospects, and leverages AI to categorize responses (Interested, Question, Follow-up, Not Interested, Out of Office).
- 📊 **Executive Command Center**: Built on Streamlit with custom dark aesthetic, metrics charts, lead management tables, and Excel import/export pipelines.

---

## 🏗️ Architecture

```
nexomate/
├── app.py                  # Main Streamlit application & navigation router
├── config.py               # Environment configuration & provider settings
├── live_init.py            # CLI verification, health checks, & seed data utility
├── render.yaml             # Render.com Infrastructure-as-Code blueprint
├── render_start.sh         # Production startup script with data persistence
├── requirements.txt        # Production Python dependencies
├── setup.bat / setup.sh    # 1-click local setup scripts (Windows & Linux/macOS)
│
├── ai/                     # AI provider abstraction layer
│   ├── base.py             # Abstract base class for AI providers
│   ├── groq_provider.py    # Free Groq Cloud AI provider
│   ├── ollama_provider.py  # Local Ollama AI provider
│   ├── provider_factory.py # Smart factory (Groq → Ollama → None)
│   ├── prompts.py          # System prompts for scoring, messaging, & classification
│   └── parser.py           # Robust JSON extraction & schema parsing
│
├── core/                   # Core application utilities
│   └── logging.py          # Centralized rotating file + console logging
│
├── dashboard/              # Streamlit dashboard views & UI components
│   ├── overview.py         # Executive KPIs & activity feed
│   ├── sourcing.py         # Autonomous lead discovery interface
│   ├── leads.py            # Lead intelligence directory & detail inspector
│   ├── outreach_page.py    # Campaign creation & batch email dispatcher
│   ├── replies_page.py     # Inbound reply tracker & sentiment triage
│   ├── analytics.py        # Conversion funnels & performance charts
│   ├── excel_page.py       # Two-way Excel import / export tools
│   ├── settings.py         # Service diagnostics, SMTP/IMAP & AI status
│   └── styles.py           # Design system tokens & CSS injection
│
├── database/               # Relational persistence layer
│   ├── database.py         # SQLAlchemy engine & session factory
│   ├── models.py           # Clean database models (Client, Lead, Campaign, Message, Reply)
│   └── migrations.py       # Idempotent schema migration runner
│
├── excel/                  # Spreadsheet ingestion & extraction
│   ├── importer.py         # Smart column mapping for lead lists
│   └── exporter.py         # Formatted Excel report generation
│
├── outreach/               # Multi-channel communication engine
│   ├── email_sender.py     # SMTP single & throttled batch dispatcher
│   ├── reply_tracker.py    # IMAP listener & AI reply classifier
│   ├── sms_sender.py       # SMS dispatch interface
│   └── whatsapp_sender.py  # WhatsApp click-to-chat generator
│
├── scoring/                # Relevance & priority scoring
│   └── lead_scorer.py      # Rule-based + AI lead evaluation
│
├── sourcing/               # Lead intelligence & web scraping
│   ├── free_prospector.py  # Multi-threaded web crawler & email extractor
│   ├── website_analyzer.py # Target domain scraper & profiler
│   └── competitor_finder.py# Competitor research engine
│
├── data/                   # SQLite database (nexomate.db) & cached exports
└── logs/                   # Application logs (nexomate.log)
```

---

## 🚀 Quick Start (Local)

### Automated Setup

**Windows:**
```cmd
setup.bat
```

**Linux / macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

### Manual Setup

1. **Clone and create a virtual environment:**
   ```bash
   git clone https://github.com/artyviz/nexomate
   cd nexomate
   python -m venv venv
   source venv/bin/activate      # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   ```
   Open `.env` and fill in your details:
   - **Groq AI (Free):** Get a free API key at [console.groq.com](https://console.groq.com) and paste it into `GROQ_API_KEY`.
   - **SMTP / IMAP:** Enter your email host credentials (e.g. Hostinger, Gmail App Password, Zoho).

4. **Initialize database & verify setup:**
   ```bash
   python live_init.py --seed-demo
   ```

5. **Start the application:**
   ```bash
   streamlit run app.py
   ```
   Access the dashboard at `http://localhost:8501`.

---

## ☁️ Free 24/7 Cloud Deployment (Render.com)

Nexomate is pre-configured for 1-click free deployment on [Render.com](https://render.com) with **zero server cost**:

1. **Push your repository to GitHub** (make sure `.env` is ignored by `.gitignore`).
2. Go to **[Render.com Dashboard](https://dashboard.render.com)** → Click **New +** → **Blueprint**.
3. Select your repository. Render will detect `render.yaml`.
4. Enter your environment variables in the Render dashboard:
   - `GROQ_API_KEY`: Your free key from [console.groq.com](https://console.groq.com)
   - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`: Your outbound email credentials
   - `IMAP_HOST`, `IMAP_PORT`, `IMAP_USER`, `IMAP_PASSWORD`: Your inbound reply credentials
5. Click **Apply**. Render will build and deploy Nexomate with persistent disk storage for your SQLite database.

---

## ⚙️ Environment Configuration Reference

| Variable | Description | Default |
|---|---|---|
| `AI_PROVIDER` | AI routing strategy (`auto`, `groq`, `ollama`) | `auto` |
| `GROQ_API_KEY` | Groq Cloud API key (free tier available) | *None* |
| `GROQ_MODEL` | Groq model identifier | `qwen/qwen3.8-27b` |
| `OLLAMA_HOST` | Ollama service endpoint (for local inference) | `http://localhost:11434` |
| `OLLAMA_MODEL` | Ollama model identifier | `llama3.1` |
| `SMTP_HOST` | Outbound email relay host | *None* |
| `SMTP_PORT` | Outbound email port (`465` for SSL, `587` for TLS) | `587` |
| `SMTP_USER` | Email account username | *None* |
| `SMTP_PASSWORD` | Email account password or App Password | *None* |
| `IMAP_HOST` | Inbound IMAP server host | *None* |
| `IMAP_PORT` | Inbound IMAP port | `993` |
| `IMAP_USER` | Inbound email account username | *None* |
| `IMAP_PASSWORD` | Inbound email account password | *None* |
| `LOG_LEVEL` | Application logging level (`DEBUG`, `INFO`, `WARN`, `ERROR`) | `INFO` |

---

## 🔒 Security & Privacy

- **Never commit `.env`**: `.gitignore` is pre-configured to strictly protect `.env`, SQLite databases (`*.db`), application logs, and internal company documents.
- **Sensitive Credentials**: Passwords and API tokens are loaded strictly via environment variables and never logged or serialized into client-side state.

---

## 📄 License

Proprietary & Confidential — All rights reserved.
"# nexomate_dev" 
"# nexomate_dev" 
