# excel/importer.py
"""Import leads from Excel/CSV files into the database."""

import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session
from database.models import Lead
from sourcing.deduplicator import is_duplicate_lead
from datetime import datetime


# Column name mapping — handles common variations
COLUMN_MAP = {
    "name": "full_name",
    "full name": "full_name",
    "first name": "first_name",
    "first_name": "first_name",
    "last name": "last_name",
    "last_name": "last_name",
    "job title": "job_title",
    "title": "job_title",
    "role": "job_title",
    "position": "job_title",
    "company": "company",
    "company name": "company",
    "organization": "company",
    "email": "email",
    "email address": "email",
    "phone": "phone",
    "phone number": "phone",
    "telephone": "phone",
    "website": "website",
    "url": "website",
    "country": "country",
    "state": "state",
    "province": "state",
    "city": "city",
    "location": "city",
    "industry": "industry",
    "sector": "industry",
    "company size": "company_size",
    "size": "company_size",
    "employees": "company_size",
    "employee count": "company_size",
    "source": "source",
    "notes": "notes",
    "description": "notes",
    "company description": "notes",
    "about": "notes",
    "summary": "notes",
}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names to match the Lead model."""
    rename_map = {}
    for col in df.columns:
        lower = col.strip().lower()
        if lower in COLUMN_MAP:
            rename_map[col] = COLUMN_MAP[lower]
    return df.rename(columns=rename_map)


def import_from_file(filepath: str | Path, db: Session, client_id: int = None) -> dict:
    """Import leads from an Excel or CSV file.

    Returns dict with counts: imported, skipped, errors.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        return {"error": f"File not found: {filepath}"}

    try:
        if filepath.suffix.lower() == ".csv":
            df = pd.read_csv(filepath)
        elif filepath.suffix.lower() in (".xlsx", ".xls"):
            df = pd.read_excel(filepath)
        else:
            return {"error": f"Unsupported file type: {filepath.suffix}"}
    except Exception as e:
        return {"error": f"Could not read file: {str(e)}"}

    df = normalize_columns(df)
    df = df.where(pd.notnull(df), None)  # Replace NaN with None

    imported = 0
    skipped = 0
    errors = []

    # Get existing leads for dedup
    existing = db.query(Lead).all()
    existing_dicts = [
        {"email": l.email, "phone": l.phone, "full_name": l.full_name, "company": l.company}
        for l in existing
    ]

    def _clean(val):
        if val is None or pd.isna(val):
            return None
        s = str(val).strip()
        return s if s else None

    for idx, row in df.iterrows():
        row_dict = {k: _clean(v) for k, v in row.to_dict().items()}

        # Build full_name if not present
        if not row_dict.get("full_name"):
            first = row_dict.get("first_name") or ""
            last = row_dict.get("last_name") or ""
            full = f"{first} {last}".strip()
            row_dict["full_name"] = full or row_dict.get("company")

        # Check for duplicates
        if is_duplicate_lead(row_dict, existing_dicts):
            skipped += 1
            continue

        try:
            lead = Lead(
                client_id=client_id,
                first_name=row_dict.get("first_name"),
                last_name=row_dict.get("last_name"),
                full_name=row_dict.get("full_name"),
                job_title=row_dict.get("job_title"),
                company=row_dict.get("company"),
                website=row_dict.get("website"),
                email=row_dict.get("email"),
                phone=row_dict.get("phone"),
                country=row_dict.get("country"),
                state=row_dict.get("state"),
                city=row_dict.get("city"),
                industry=row_dict.get("industry"),
                company_size=row_dict.get("company_size"),
                source="Excel Import",
                source_type="excel_import",
                source_url=str(filepath.name),
                notes=row_dict.get("notes"),
                lead_status="NEW",
                discovery_date=datetime.now(),
            )
            db.add(lead)
            existing_dicts.append(row_dict)  # Add to dedup list
            imported += 1
        except Exception as e:
            errors.append(f"Row {idx + 2}: {str(e)}")

    db.commit()

    return {
        "imported": imported,
        "skipped": skipped,
        "errors": errors,
        "total_rows": len(df),
    }
