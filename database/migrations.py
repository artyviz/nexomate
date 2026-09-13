# database/migrations.py
"""Database schema migrations for Nexomate.

Adds new columns to existing tables without losing data.
Safe to run multiple times (idempotent).
"""

import sqlite3
from pathlib import Path


def run_migrations():
    """Run all pending migrations."""
    BASE_DIR = Path(__file__).resolve().parent.parent
    db_path = str(BASE_DIR / "data" / "nexomate.db")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get existing columns for leads table
    cursor.execute("PRAGMA table_info(leads)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    # Migrations for leads table — add new Explee fields
    new_lead_columns = {
        "linkedin_url": "TEXT",
        "explee_relevance": "REAL",
        "email_verified": "INTEGER DEFAULT 0",
        "explee_company_id": "TEXT",
    }

    for col_name, col_type in new_lead_columns.items():
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE leads ADD COLUMN {col_name} {col_type}")
                print(f"  [OK] Added column leads.{col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    print(f"  [WARN] Could not add leads.{col_name}: {e}")

    # Create batch_jobs table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS batch_jobs (
            job_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            job_type TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            result_count INTEGER DEFAULT 0,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("  [OK] Migrations complete!")


if __name__ == "__main__":
    run_migrations()
