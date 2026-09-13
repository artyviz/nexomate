# dashboard/leads.py
"""Leads dashboard page — Noir Press Broadsheet Edition."""

import streamlit as st
import pandas as pd
from database.database import SessionLocal
from database.models import Lead
from config import LEAD_STATUSES


def leads_page():
    db = SessionLocal()
    try:
        # ── Masthead ─────────────────────────────────────────────────────────
        st.markdown("""
        <div class="editorial-masthead" style="margin-bottom: 1.5rem; padding: 1rem 0.5rem;">
            <div class="masthead-meta-row">
                <span>PROSPECT REGISTRY</span>
                <span>DATA CLASSIFICATION: LIVE PRODUCTION</span>
                <span>ZERO RADIUS INDEX</span>
            </div>
            <h1 class="masthead-main-title" style="font-size: 2.2rem;">THE PROSPECT DIRECTORY</h1>
            <div class="masthead-sub-rule">Complete intelligence registry of verified commercial accounts & decision-makers</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Filters ──────────────────────────────────────────────────────────
        with st.expander("▾ WIRE FILTERS & QUERY PARAMETERS", expanded=False):
            fcol1, fcol2, fcol3, fcol4 = st.columns(4)
            with fcol1:
                score_filter = st.multiselect("Priority Tier", ["HIGH", "MEDIUM", "LOW"], default=[])
            with fcol2:
                status_filter = st.multiselect("Pipeline Status", LEAD_STATUSES, default=[])
            with fcol3:
                source_filter = st.selectbox("Source", ["All", "Free Autonomous Web Scout", "Manual Intelligence Entry", "Web Search", "Excel Import"])
            with fcol4:
                has_email = st.selectbox("Email", ["All", "Yes", "No", "Verified Only"])

            scol1, scol2 = st.columns(2)
            with scol1:
                search_text = st.text_input("Search (Name, Company, Email)", "")
            with scol2:
                sort_by = st.selectbox("Sort", [
                    "Highest Score", "Lowest Score", "Newest", "Oldest", "Company"
                ])

        # ── Query ────────────────────────────────────────────────────────────
        query = db.query(Lead).filter(Lead.is_demo == False)

        if score_filter:
            query = query.filter(Lead.score_level.in_(score_filter))
        if status_filter:
            query = query.filter(Lead.lead_status.in_(status_filter))
        if source_filter != "All":
            query = query.filter(Lead.source == source_filter)
        if has_email == "Yes":
            query = query.filter(Lead.email.isnot(None), Lead.email != "", Lead.email != "Not Found")
        elif has_email == "No":
            query = query.filter((Lead.email.is_(None)) | (Lead.email == "") | (Lead.email == "Not Found"))
        elif has_email == "Verified Only":
            query = query.filter(Lead.email_verified == True)

        if search_text:
            like = f"%{search_text}%"
            query = query.filter(
                (Lead.full_name.ilike(like)) |
                (Lead.company.ilike(like)) |
                (Lead.email.ilike(like)) |
                (Lead.phone.ilike(like))
            )

        # Sorting
        if sort_by == "Highest Score":
            query = query.order_by(Lead.fit_score.desc().nullslast())
        elif sort_by == "Lowest Score":
            query = query.order_by(Lead.fit_score.asc().nullsfirst())
        elif sort_by == "Newest":
            query = query.order_by(Lead.created_at.desc())
        elif sort_by == "Oldest":
            query = query.order_by(Lead.created_at.asc())
        elif sort_by == "Company":
            query = query.order_by(Lead.company.asc())

        leads = query.all()

        # ── Summary Stats ────────────────────────────────────────────────────
        total = len(leads)
        high_count = sum(1 for l in leads if l.score_level == "HIGH")
        med_count = sum(1 for l in leads if l.score_level == "MEDIUM")
        low_count = sum(1 for l in leads if l.score_level == "LOW")
        verified_count = sum(1 for l in leads if l.email_verified)

        scols = st.columns(5)
        with scols[0]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total}</div>
                <div class="metric-label">TOTAL PROSPECTS</div>
            </div>
            """, unsafe_allow_html=True)
        with scols[1]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #4ADE80;">{high_count}</div>
                <div class="metric-label">HIGH PRIORITY</div>
            </div>
            """, unsafe_allow_html=True)
        with scols[2]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #FACC15;">{med_count}</div>
                <div class="metric-label">MEDIUM PRIORITY</div>
            </div>
            """, unsafe_allow_html=True)
        with scols[3]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #F87171;">{low_count}</div>
                <div class="metric-label">LOW PRIORITY</div>
            </div>
            """, unsafe_allow_html=True)
        with scols[4]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #60A5FA;">{verified_count}</div>
                <div class="metric-label">VERIFIED EMAILS</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

        # ── Leads Table ──────────────────────────────────────────────────────
        if leads:
            rows = []
            for lead in leads:
                score_display = ""
                if lead.score_level == "HIGH":
                    score_display = f"HIGH ({int(lead.fit_score or 0)})"
                elif lead.score_level == "MEDIUM":
                    score_display = f"MED ({int(lead.fit_score or 0)})"
                elif lead.score_level == "LOW":
                    score_display = f"LOW ({int(lead.fit_score or 0)})"
                else:
                    score_display = "—"

                # Source badge
                source_badge = "🌐" if "Autonomous" in (lead.source or "") else "🔷" if lead.source == "Explee" else "✍" if "Manual" in (lead.source or "") else "🔍" if lead.source == "Web Search" else "📁" if "Excel" in (lead.source or "") else "—"

                rows.append({
                    "ID": lead.lead_id,
                    "Priority": score_display,
                    "Name": lead.full_name or "—",
                    "Company": lead.company or "—",
                    "Title": lead.job_title or "—",
                    "Email": lead.email or "—",
                    "✓": "✓" if lead.email_verified else "",
                    "Phone": lead.phone or "—",
                    "Location": ", ".join(filter(None, [lead.city, lead.state, lead.country])) or "—",
                    "Source": f"{source_badge} {lead.source or '—'}",
                    "Status": lead.lead_status or "—",
                })

            df = pd.DataFrame(rows)
            st.dataframe(
                df,
                use_container_width=True,
                height=520,
                column_config={
                    "ID": st.column_config.NumberColumn("ID", width="small"),
                    "Priority": st.column_config.TextColumn("Priority", width="small"),
                    "Company": st.column_config.TextColumn("Company", width="medium"),
                    "Email": st.column_config.TextColumn("Email", width="medium"),
                    "✓": st.column_config.TextColumn("✓Email", width="small"),
                },
            )

            # ── Bulk Actions ─────────────────────────────────────────────────
            st.markdown("""
            <div class="section-header" style="margin-top: 2rem;">
                <span>Terminal Operations & Bulk Controls</span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #888888;">EXECUTE</span>
            </div>
            """, unsafe_allow_html=True)

            bcol1, bcol2, bcol3, bcol4 = st.columns(4)

            with bcol1:
                if st.button("📥 EXPORT TO EXCEL"):
                    from excel.exporter import export_leads
                    path = export_leads(db, is_demo=False)
                    st.success(f"Exported to {path}")

            with bcol2:
                new_status = st.selectbox("Set Status", LEAD_STATUSES, key="bulk_status")
            with bcol3:
                lead_ids_input = st.text_input("Lead IDs (e.g. 1, 2, 3)", key="bulk_ids")
            with bcol4:
                st.markdown("<div style='margin-top: 1.8rem;'></div>", unsafe_allow_html=True)
                if st.button("UPDATE STATUS"):
                    if lead_ids_input:
                        try:
                            ids = [int(i.strip()) for i in lead_ids_input.split(",")]
                            for lid in ids:
                                lead_obj = db.query(Lead).filter(Lead.lead_id == lid).first()
                                if lead_obj:
                                    lead_obj.lead_status = new_status
                            db.commit()
                            st.success(f"Updated {len(ids)} records to {new_status}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

            # ── Lead Detail View ─────────────────────────────────────────────
            st.markdown("""
            <div class="section-header" style="margin-top: 2.5rem;">
                <span>Dossier Inspection</span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #888888;">SINGLE RECORD</span>
            </div>
            """, unsafe_allow_html=True)

            detail_col1, detail_col2 = st.columns([1, 3])
            with detail_col1:
                selected_id = st.number_input("Record ID", min_value=1, step=1, key="lead_detail_id")
                inspect_btn = st.button("INSPECT DOSSIER")

            if inspect_btn or selected_id:
                lead = db.query(Lead).filter(Lead.lead_id == selected_id).first()
                if lead:
                    dcol1, dcol2 = st.columns(2)
                    with dcol1:
                        linkedin_link = f"<div><strong style='color: #888888;'>LINKEDIN:</strong> <a href='{lead.linkedin_url}' target='_blank' style='color: #60A5FA;'>{lead.linkedin_url}</a></div>" if lead.linkedin_url else "<div><strong style='color: #888888;'>LINKEDIN:</strong> Not Recorded</div>"
                        st.markdown(f"""
                        <div class="noir-card">
                            <div style="font-family: 'Playfair Display', serif; font-size: 1.4rem; font-weight: 900; margin-bottom: 0.8rem; color: #F3F3EF;">
                                {lead.full_name or lead.company or 'Unspecified Lead'}
                            </div>
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; line-height: 1.8; color: #CCCCCC;">
                                <div><strong style="color: #888888;">COMPANY:</strong> {lead.company or 'Not Recorded'}</div>
                                <div><strong style="color: #888888;">TITLE:</strong> {lead.job_title or 'Not Recorded'}</div>
                                <div><strong style="color: #888888;">EMAIL:</strong> {lead.email or 'Not Recorded'} {'<span class="badge-high">VERIFIED</span>' if lead.email_verified else ''}</div>
                                <div><strong style="color: #888888;">PHONE:</strong> {lead.phone or 'Not Recorded'}</div>
                                {linkedin_link}
                                <div><strong style="color: #888888;">LOCATION:</strong> {', '.join(filter(None, [lead.city, lead.state, lead.country])) or 'Not Recorded'}</div>
                                <div><strong style="color: #888888;">SECTOR:</strong> {lead.industry or 'Not Recorded'}</div>
                                <div><strong style="color: #888888;">SCALE:</strong> {lead.company_size or 'Not Recorded'}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with dcol2:
                        score_color = "#4ADE80" if lead.score_level == "HIGH" else "#FACC15" if lead.score_level == "MEDIUM" else "#F87171"
                        explee_rel = f"{lead.explee_relevance:.0%}" if lead.explee_relevance else "—"
                        st.markdown(f"""
                        <div class="noir-card">
                            <div style="font-family: 'Playfair Display', serif; font-size: 1.4rem; font-weight: 900; margin-bottom: 0.8rem; color: #F3F3EF;">
                                Assessment & Intelligence
                            </div>
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; line-height: 1.8; color: #CCCCCC;">
                                <div><strong style="color: #888888;">FIT SCORE:</strong> <span style="color: {score_color}; font-weight: 700;">{lead.fit_score or '—'}</span> ({lead.score_level or 'UNSCORED'})</div>
                                <div><strong style="color: #888888;">MATCH RELEVANCE:</strong> {explee_rel}</div>
                                <div><strong style="color: #888888;">ASSESSMENT:</strong> {lead.score_reason or '—'}</div>
                                <div><strong style="color: #888888;">SOURCE:</strong> {lead.source or '—'}</div>
                                <div><strong style="color: #888888;">STATUS:</strong> <span class="badge-bone">{lead.lead_status}</span></div>
                                <div><strong style="color: #888888;">NOTES:</strong> {lead.notes or 'None'}</div>
                                <div><strong style="color: #888888;">INDEXED:</strong> {lead.created_at}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Record not found.")
        else:
            st.info("No leads recorded. Use **Find Leads** to discover prospects.")

        # ── Manual Lead Entry ────────────────────────────────────────────────
        st.markdown("""
        <div class="section-header" style="margin-top: 2.5rem;">
            <span>Manual Entry</span>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #888888;">ENCODE</span>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("▾ ADD LEAD MANUALLY", expanded=False):
            with st.form("add_lead_form"):
                acol1, acol2, acol3 = st.columns(3)
                with acol1:
                    new_name = st.text_input("Name")
                    new_company = st.text_input("Company")
                    new_title = st.text_input("Job Title")
                    new_industry = st.text_input("Industry")
                with acol2:
                    new_email = st.text_input("Email")
                    new_phone = st.text_input("Phone")
                    new_website = st.text_input("Website / Domain")
                    new_linkedin = st.text_input("LinkedIn URL")
                with acol3:
                    new_city = st.text_input("City")
                    new_state = st.text_input("State")
                    new_country = st.text_input("Country")
                    new_notes = st.text_area("Notes", height=80)

                submitted = st.form_submit_button("SAVE LEAD")
                if submitted:
                    from datetime import datetime
                    new_lead = Lead(
                        full_name=new_name or None,
                        first_name=new_name.split()[0] if new_name and " " in new_name else new_name or None,
                        last_name=new_name.split()[-1] if new_name and " " in new_name else None,
                        company=new_company or None,
                        job_title=new_title or None,
                        email=new_email or None,
                        phone=new_phone or None,
                        website=new_website or None,
                        linkedin_url=new_linkedin or None,
                        industry=new_industry or None,
                        city=new_city or None,
                        state=new_state or None,
                        country=new_country or None,
                        notes=new_notes or None,
                        source="Manual Intelligence Entry",
                        source_type="manual",
                        lead_status="NEW",
                        discovery_date=datetime.now(),
                    )
                    db.add(new_lead)
                    db.commit()
                    st.success(f"Saved: {new_name or new_company}")
                    st.rerun()
    finally:
        db.close()
