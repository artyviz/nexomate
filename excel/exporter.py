# excel/exporter.py
"""Export leads to formatted Excel workbooks."""

import pandas as pd
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import Lead
from config import EXPORTS_DIR
from excel.formatter import apply_formatting


def leads_to_dataframe(leads: list[Lead]) -> pd.DataFrame:
    """Convert a list of Lead ORM objects to a DataFrame."""
    rows = []
    for lead in leads:
        rows.append({
            "ID": lead.lead_id,
            "Name": lead.full_name or "",
            "Title": lead.job_title or "",
            "Company": lead.company or "",
            "Email": lead.email or "",
            "Phone": lead.phone or "",
            "Location": ", ".join(filter(None, [lead.city, lead.state, lead.country])),
            "Industry": lead.industry or "",
            "Source": lead.source or "",
            "Source URL": lead.source_url or "",
            "Fit Score": lead.fit_score,
            "Score Level": lead.score_level or "",
            "Score Reason": lead.score_reason or "",
            "Status": lead.lead_status or "",
            "Notes": lead.notes or "",
            "Created At": lead.created_at.strftime("%Y-%m-%d %H:%M") if lead.created_at else "",
        })
    return pd.DataFrame(rows)


def export_leads(db: Session, filter_level: str = None, lead_ids: list[int] = None, is_demo: bool = False) -> str:
    """Export leads to a multi-sheet Excel workbook.

    Args:
        db: Database session.
        filter_level: Optional — "HIGH", "MEDIUM", "LOW" to export only that level.
        lead_ids: Optional — specific lead IDs to export.
        is_demo: Whether to export demo leads or live leads.

    Returns:
        Path to the generated Excel file.
    """
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

    query = db.query(Lead).filter(Lead.is_demo == is_demo)

    if lead_ids:
        query = query.filter(Lead.lead_id.in_(lead_ids))

    all_leads = query.order_by(Lead.fit_score.desc().nullslast()).all()

    # Split by priority
    high_leads = [l for l in all_leads if l.score_level == "HIGH"]
    medium_leads = [l for l in all_leads if l.score_level == "MEDIUM"]
    low_leads = [l for l in all_leads if l.score_level == "LOW"]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Nexomate_Leads_{timestamp}.xlsx"
    filepath = EXPORTS_DIR / filename

    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        # All Leads sheet
        df_all = leads_to_dataframe(all_leads)
        df_all.to_excel(writer, sheet_name="All Leads", index=False)

        # HIGH Priority sheet
        if high_leads:
            leads_to_dataframe(high_leads).to_excel(writer, sheet_name="HIGH Priority", index=False)

        # MEDIUM Priority sheet
        if medium_leads:
            leads_to_dataframe(medium_leads).to_excel(writer, sheet_name="MEDIUM Priority", index=False)

        # LOW Priority sheet
        if low_leads:
            leads_to_dataframe(low_leads).to_excel(writer, sheet_name="LOW Priority", index=False)

        # Summary sheet
        summary_data = {
            "Metric": [
                "Total Leads",
                "HIGH Priority",
                "MEDIUM Priority",
                "LOW Priority",
                "Unscored",
                "Average Score",
                "With Email",
                "With Phone",
                "Export Date",
            ],
            "Value": [
                len(all_leads),
                len(high_leads),
                len(medium_leads),
                len(low_leads),
                len([l for l in all_leads if not l.score_level]),
                round(sum(l.fit_score or 0 for l in all_leads) / max(len(all_leads), 1), 1),
                len([l for l in all_leads if l.email and l.email != "Not Found"]),
                len([l for l in all_leads if l.phone and l.phone != "Not Found"]),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ],
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name="Summary", index=False)

    # Apply formatting
    apply_formatting(filepath)

    return str(filepath)
