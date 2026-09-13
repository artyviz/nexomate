# live_init.py
"""Nexomate MVP — Production & Live Environment Initializer.

Runs environment verification, health checks, database table creation,
and optional live data ingestion.

Usage:
    python live_init.py                  # Standard verification & health check
    python live_init.py --seed-demo      # Seed demo dataset (20 leads, 3 campaigns, 10 messages, 5 replies)
    python live_init.py --import-solar   # Ingest bundled 'Leads Sheet - Solar AU.xlsx' (302 leads)
    python live_init.py --all            # Run checks, seed demo, and import solar dataset
"""

import sys
import argparse
import requests
from pathlib import Path
from datetime import datetime

# Configure UTF-8 for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import config
from database.database import engine, Base, SessionLocal
from database import models
from database.models import Client, Lead, Campaign, Message, Reply, BusinessProfile, ICPProfile
from ai.ollama_provider import OllamaProvider
from outreach.email_sender import is_smtp_configured
from outreach.reply_tracker import is_imap_configured
from excel.importer import import_from_file


def check_directories() -> bool:
    """Ensure all required workspace directories exist."""
    print("📁 Checking directory structure...")
    dirs = [config.DATA_DIR, config.EXPORTS_DIR, config.IMPORTS_DIR, config.LOGS_DIR]
    all_ok = True
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        if d.exists():
            print(f"   ✓ {d.name}/ exists ({d})")
        else:
            print(f"   ✗ Failed to create {d}")
            all_ok = False
    return all_ok


def init_database() -> bool:
    """Create all SQLite tables."""
    print("\n🗄️ Initializing database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        lead_count = db.query(Lead).count()
        client_count = db.query(Client).count()
        camp_count = db.query(Campaign).count()
        db.close()
        print(f"   ✓ Database tables verified.")
        print(f"   ✓ Current records — Clients: {client_count}, Leads: {lead_count}, Campaigns: {camp_count}")
        return True
    except Exception as e:
        print(f"   ✗ Database initialization error: {e}")
        return False


def check_services():
    """Run health check against external and local services."""
    print("\n🔌 Checking service connectivity...")

    # 1. Internet / DuckDuckGo connectivity
    try:
        resp = requests.get("https://html.duckduckgo.com/html/?q=test", timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            print("   ✓ Web Search: DuckDuckGo is reachable (Lead discovery enabled).")
        else:
            print(f"   ⚠ Web Search returned status {resp.status_code}.")
    except Exception as e:
        print(f"   ⚠ Web Search: Network request failed ({e}). Offline fallback active.")

    # 2. Ollama AI
    ai = OllamaProvider(host=config.OLLAMA_HOST, model=config.OLLAMA_MODEL)
    if ai.is_available():
        print(f"   ✓ Local AI: Ollama running on {config.OLLAMA_HOST} (model: {config.OLLAMA_MODEL}).")
    else:
        print(f"   ⚠ Local AI: Ollama is offline. Template-based fallback active for scoring & messages.")

    # 3. SMTP
    if is_smtp_configured():
        print(f"   ✓ Email Outreach: SMTP configured ({config.SMTP_HOST}:{config.SMTP_PORT} as {config.SMTP_USER}).")
    else:
        print("   ℹ Email Outreach: SMTP credentials not set in .env (Manual / preview mode active).")

    # 4. IMAP
    if is_imap_configured():
        print(f"   ✓ Reply Tracking: IMAP configured ({config.IMAP_HOST}:{config.IMAP_PORT} as {config.IMAP_USER}).")
    else:
        print("   ℹ Reply Tracking: IMAP not set in .env (Manual reply logging active).")


def bootstrap_default_client():
    """Create the production Nexomate client if none exists."""
    db = SessionLocal()
    try:
        existing = db.query(Client).first()
        if not existing:
            print("\n👤 Creating Nexomate production client profile...")
            default_client = Client(
                company_name="Nexomate",
                website="https://getnexomate.com",
                industry="AI Lead Conversion & Business Automation",
                country="International",
                target_country="Australia, United States, United Kingdom",
                target_cities="Sydney, Melbourne, Brisbane, Los Angeles, New York, London",
                target_geography="English-speaking markets with active solar industry",
                services="AI-powered lead capture, instant response automation, lead qualification & scoring, automated follow-up sequences, appointment booking, CRM integration, sales team notification",
                ideal_customer_description="Established solar installation companies with regular inbound enquiries, meaningful-value projects, and a consultation or quote-based sales process — businesses that are successful enough to have real customer activity but still have manual or fragmented processes in how enquiries are handled",
                company_size="5-250 employees",
                target_job_titles="Managing Director, Operations Director, Sales Director, Business Development Manager, CEO, Founder",
                pain_points="Slow lead response times, poor lead qualification, inconsistent follow-ups, missed appointments, prospects going cold, manual processes wasting sales team time, leads leaking from the pipeline",
                value_proposition="Help solar businesses convert more of their existing leads into qualified conversations and appointments through AI automation — without replacing their sales team, just making the process faster and more consistent",
                preferred_tone="Professional",
                sender_name="Farhan (Nexomate)",
                sender_email="connect@getnexomate.com",
            )
            db.add(default_client)
            db.commit()
            db.refresh(default_client)

            # Also create corresponding business & ICP profile
            biz = BusinessProfile(
                client_id=default_client.client_id,
                business_name="Nexomate",
                industry="AI Lead Conversion & Business Automation",
                services="AI-powered lead capture and response, lead qualification and scoring (HOT/WARM/COLD), automated multi-channel follow-up, appointment booking automation, CRM integration, sales pipeline optimization",
                target_customers="Solar installation companies with active marketing, regular enquiries, and a consultation-based sales process",
                value_propositions="Convert more existing leads into appointments without hiring more staff; instant AI response to every enquiry; automated qualification saves sales team hours; consistent follow-up means no lead goes cold",
                locations="Australia, United States, United Kingdom",
            )
            icp = ICPProfile(
                client_id=default_client.client_id,
                target_customer="Solar installation companies generating regular inbound enquiries through website forms, ads, or referrals, with project values above $10,000 and a consultation or quote-based sales process",
                company_type="Established Solar Installation & Renewable Energy Companies",
                job_titles="Managing Director, Operations Director, Sales Director, Business Development Manager, CEO, Founder",
                industry="Solar Installation, Renewable Energy, Clean Energy",
                location="Australia, United States, United Kingdom",
                company_size="5-250 employees",
                buying_signals="Running Google/Facebook ads, active website with quote forms, hiring sales staff, expanding to new regions, complaints about lead response time, high lead volume with low conversion",
                pain_points="Slow response to new enquiries, manual lead qualification, inconsistent follow-up, leads going cold before consultation, sales team spending time on unqualified leads",
                search_keywords="solar installation company, solar panel installer, residential solar, commercial solar, solar energy company, solar quotes, solar EPC contractor",
            )
            db.add(biz)
            db.add(icp)
            db.commit()
            print(f"   ✓ Production client '{default_client.company_name}' bootstrapped.")
        else:
            print(f"\n👤 Active client found: '{existing.company_name}'.")
    finally:
        db.close()


def import_solar_dataset():
    """Import the bundled solar dataset if available."""
    solar_file = config.DATA_DIR / "Leads Sheet - Solar AU.xlsx"
    if not solar_file.exists():
        print(f"\n⚠ Bundled dataset not found at {solar_file}")
        return

    print(f"\n📊 Ingesting bundled dataset: {solar_file.name}...")
    db = SessionLocal()
    try:
        client = db.query(Client).first()
        client_id = client.client_id if client else None
        res = import_from_file(solar_file, db, client_id=client_id)
        print(f"   ✓ Ingestion Complete: {res.get('imported', 0)} imported, {res.get('skipped', 0)} skipped (duplicates).")
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Nexomate Production & Live Environment Initializer")
    parser.add_argument("--import-solar", action="store_true", help="Import the bundled Solar AU leads sheet")
    args = parser.parse_args()

    print("==================================================================")
    print("           NEXOMATE MVP — LIVE PRODUCTION INITIALIZER             ")
    print("==================================================================")

    # 1. Directories
    check_directories()

    # 2. Database
    init_database()

    # 3. Bootstrap Client
    bootstrap_default_client()

    # 4. Service checks
    check_services()

    # 5. Optional Solar AU import
    if args.import_solar:
        import_solar_dataset()

    print("\n==================================================================")
    print("🚀 NEXOMATE LIVE ENVIRONMENT READY")
    print("   To launch the dashboard, run: streamlit run app.py")
    print("   Then open your browser at: http://localhost:8501")
    print("   Active dataset: Pure live production leads only")
    print("==================================================================")


if __name__ == "__main__":
    main()
