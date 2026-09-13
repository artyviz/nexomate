# setup_db.py

"""Utility script to create the SQLite database and tables for Nexomate MVP.

Run with:
    python setup_db.py
"""

from database.database import engine
from database.models import Base

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created.")

if __name__ == "__main__":
    create_tables()
