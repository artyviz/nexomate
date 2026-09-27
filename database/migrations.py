# database/migrations.py
"""Database schema migrations for Nexomate.

Adds new columns to existing tables without losing data.
Safe to run multiple times (idempotent).
"""

import sys
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.logging import get_logger

logger = get_logger("nexomate.migrations")


def run_migrations():
    """Run all pending schema migrations."""
    BASE_DIR = Path(__file__).resolve().parent.parent
    db_path = str(BASE_DIR / "data" / "nexomate.db")

    if not Path(db_path).exists():
        logger.info(f"Database at {db_path} does not exist yet. Skipping migrations.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get existing columns for leads table
    cursor.execute("PRAGMA table_info(leads)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    # Active schema columns that may need to be added to legacy databases
    new_lead_columns = {
        "linkedin_url": "TEXT",
        "email_verified": "INTEGER DEFAULT 0",
    }

    for col_name, col_type in new_lead_columns.items():
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE leads ADD COLUMN {col_name} {col_type}")
                logger.info(f"Added column leads.{col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    logger.warning(f"Could not add leads.{col_name}: {e}")

    conn.commit()
    conn.close()
    logger.info("Database migrations complete.")


if __name__ == "__main__":
    run_migrations()
