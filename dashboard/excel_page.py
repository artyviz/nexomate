# dashboard/excel_page.py
"""Excel import/export page — Noir Press Broadsheet Edition."""

import streamlit as st
from pathlib import Path
from database.database import SessionLocal
from database.models import Lead
from excel.importer import import_from_file
from excel.exporter import export_leads
from config import IMPORTS_DIR, EXPORTS_DIR


def excel_page():
    st.markdown("""
    <div class="editorial-masthead" style="margin-bottom: 1.5rem; padding: 1rem 0.5rem;">
        <div class="masthead-meta-row">
            <span>DATA TRANSMISSION PORTAL</span>
            <span>BULK INGESTION & DISPATCH EXPORT</span>
            <span>SPREADSHEET FORMATS (XLSX / CSV)</span>
        </div>
        <h1 class="masthead-main-title" style="font-size: 2.2rem;">DATA INGEST & BROADCAST EXPORT</h1>
        <div class="masthead-sub-rule">External database ingestion · Schema mapping · Broadsheet tabular compilation</div>
    </div>
    """, unsafe_allow_html=True)

    db = SessionLocal()
    try:
        tab_import, tab_export = st.tabs(["📥 Ingest Archive", "📤 Export Dispatch"])

        # ── Import Tab ───────────────────────────────────────────────────
        with tab_import:
            st.markdown("### Bulk Dossier Ingestion")
            st.markdown("Transmit a `.xlsx` or `.csv` dossier. Field columns will be automatically mapped to internal schema.")

            uploaded_file = st.file_uploader(
                "Select File Payload",
                type=["xlsx", "csv", "xls"],
                key="excel_upload",
            )

            if uploaded_file:
                IMPORTS_DIR.mkdir(parents=True, exist_ok=True)
                save_path = IMPORTS_DIR / uploaded_file.name
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                st.info(f"Payload buffered: {save_path.name}")

                import pandas as pd
                try:
                    if uploaded_file.name.endswith(".csv"):
                        df_preview = pd.read_csv(save_path)
                    else:
                        df_preview = pd.read_excel(save_path)
                    st.markdown(f"**Payload Inspection** ({len(df_preview)} records, {len(df_preview.columns)} attributes)")
                    st.dataframe(df_preview.head(10), use_container_width=True)
                except Exception as e:
                    st.error(f"Failed to inspect payload: {e}")

                if st.button("📥 INGEST INTO PERMANENT RECORD"):
                    with st.spinner("Ingesting into database..."):
                        result = import_from_file(save_path, db)

                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.success(
                            f"Ingestion finalized:\n\n"
                            f"- Ingested: {result['imported']}\n"
                            f"- Skipped (duplicates): {result['skipped']}\n"
                            f"- Total rows parsed: {result['total_rows']}"
                        )
                        if result.get("errors"):
                            with st.expander("⚠ Schema Anomalies"):
                                for err in result["errors"]:
                                    st.write(err)

            # Column mapping reference
            with st.expander("📋 SCHEMA FIELD MAPPINGS"):
                st.markdown("""
                Automatic attribute parser connects the following table headers:

                | Source Attribute | Internal Database Column |
                |---|---|
                | Name, Full Name | `full_name` |
                | First Name | `first_name` |
                | Last Name | `last_name` |
                | Email, Email Address | `email` |
                | Phone, Phone Number, Telephone | `phone` |
                | Company, Company Name, Organization | `company` |
                | Job Title, Title, Role, Position | `job_title` |
                | Website, URL | `website` |
                | City, Location | `city` |
                | State, Province | `state` |
                | Country | `country` |
                | Industry, Sector | `industry` |
                | Company Size, Employees | `company_size` |
                | Source | `source` |
                | Notes | `notes` |
                """)

        # ── Export Tab ───────────────────────────────────────────────────
        with tab_export:
            st.markdown("### Export Dispatch Broadsheet")

            total_leads = db.query(Lead).filter(Lead.is_demo == False).count()
            high_count = db.query(Lead).filter(Lead.is_demo == False, Lead.score_level == "HIGH").count()
            med_count = db.query(Lead).filter(Lead.is_demo == False, Lead.score_level == "MEDIUM").count()
            low_count = db.query(Lead).filter(Lead.is_demo == False, Lead.score_level == "LOW").count()

            st.markdown(f"""
            <div class="noir-card" style="padding: 1.25rem; margin-bottom: 1.5rem;">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #CCCCCC;">
                    <strong style="color: #F3F3EF;">RECORD INVENTORY:</strong> {total_leads} Total Accounts Catalogued
                    · <span style="color: #4ADE80; font-weight: 700;">{high_count} HIGH</span>
                    · <span style="color: #FACC15; font-weight: 700;">{med_count} MED</span>
                    · <span style="color: #F87171; font-weight: 700;">{low_count} LOW</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            ecol1, ecol2 = st.columns(2)
            with ecol1:
                export_type = st.selectbox("Export Classification Filter", [
                    "All Leads",
                    "HIGH Priority Only",
                    "MEDIUM Priority Only",
                    "LOW Priority Only",
                ])
            with ecol2:
                st.markdown("<div style='margin-top: 1.8rem;'></div>", unsafe_allow_html=True)
                if st.button("GENERATE EXCEL DISPATCH"):
                    filter_level = None
                    if "HIGH" in export_type:
                        filter_level = "HIGH"
                    elif "MEDIUM" in export_type:
                        filter_level = "MEDIUM"
                    elif "LOW" in export_type:
                        filter_level = "LOW"

                    with st.spinner("Compiling spreadsheet..."):
                        filepath = export_leads(db, filter_level=filter_level, is_demo=False)

                    st.success(f"Compiled dispatch to: `{filepath}`")

                    with open(filepath, "rb") as f:
                        st.download_button(
                            label="⬇️ DOWNLOAD SPREADSHEET DISPATCH",
                            data=f,
                            file_name=Path(filepath).name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        )
    finally:
        db.close()
