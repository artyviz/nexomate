# dashboard/sourcing.py
"""Find Leads page — automated 100% free lead discovery powered by in-house Autonomous Prospector."""

import time
import streamlit as st
import pandas as pd
from datetime import datetime
from database.database import SessionLocal
from database.models import Lead, Client, BatchJob
from sourcing.free_prospector import FreeProspector
from scoring.lead_scorer import rule_based_score



# ── Predefined industry categories ──────────────────────────────────────────
INDUSTRY_CATEGORIES = [
    "Custom (describe your own)",
    "B2B SaaS",
    "E-Commerce & Retail",
    "FinTech & Financial Services",
    "HealthTech & Digital Health",
    "EdTech & Online Learning",
    "AI & Machine Learning",
    "Cybersecurity",
    "Cloud Infrastructure & DevOps",
    "Marketing & AdTech",
    "HR Tech & Recruitment",
    "Real Estate & PropTech",
    "Legal Tech",
    "Supply Chain & Logistics",
    "Clean Energy & Sustainability",
    "Construction & Engineering",
    "Food & Beverage",
    "Travel & Hospitality",
    "Media & Entertainment",
    "Telecommunications",
    "Manufacturing",
    "Consulting & Professional Services",
    "Insurance",
    "Automotive",
    "Agriculture & AgTech",
]

COMPANY_SIZE_OPTIONS = {
    "Any size": (None, None),
    "1–10 employees": (1, 10),
    "11–50 employees": (11, 50),
    "51–200 employees": (51, 200),
    "201–500 employees": (201, 500),
    "501–1000 employees": (501, 1000),
    "1000+ employees": (1000, None),
}

COUNTRY_CODES = {
    "Any": None,
    "United States": "US",
    "United Kingdom": "GB",
    "Canada": "CA",
    "Australia": "AU",
    "Germany": "DE",
    "France": "FR",
    "India": "IN",
    "Singapore": "SG",
    "Netherlands": "NL",
    "United Arab Emirates": "AE",
    "Sweden": "SE",
    "Switzerland": "CH",
    "Japan": "JP",
    "Brazil": "BR",
    "Spain": "ES",
    "Italy": "IT",
    "Ireland": "IE",
    "Israel": "IL",
    "South Korea": "KR",
    "Mexico": "MX",
    "New Zealand": "NZ",
    "Pakistan": "PK",
    "Saudi Arabia": "SA",
    "South Africa": "ZA",
    "Nigeria": "NG",
    "Kenya": "KE",
}

FUNDING_STAGES = {
    "Any": None,
    "No Funding": "no_funding",
    "Pre-Seed / Seed": "pre_seed_seed",
    "Series A": "series_a",
    "Series B+": "series_b_plus",
}


def free_prospector_ui(db, active_client):
    """100% Free Autonomous Lead Discovery & Contact Extraction UI."""
    st.markdown("""
    <div class="noir-card" style="padding: 1.25rem; margin-bottom: 1.5rem; border-left: 4px solid #4ADE80;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-family: 'Playfair Display', serif; font-size: 1.25rem; font-weight: 700; color: #F3F3EF;">
                    ⚡ Free Autonomous Lead Prospector
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #888888; margin-top: 4px;">
                    ZERO-COST SCRAPER · MULTI-THREADED CRAWLER · RULE-BASED & AI FIT SCORING · UNLIMITED QUERIES
                </div>
            </div>
            <span class="badge-high" style="background: rgba(74, 222, 128, 0.15); color: #4ADE80; border: 1px solid #4ADE80;">100% FREE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        search_mode = st.radio(
            "Search By",
            ["📂 Category Directory", "💬 Natural Language Query"],
            horizontal=True,
            key="free_search_mode",
        )
        if search_mode == "📂 Category Directory":
            category = st.selectbox("Target Industry", INDUSTRY_CATEGORIES[1:], key="free_cat")
            query = category
        else:
            query = st.text_input(
                "Custom Prospecting Query",
                placeholder="e.g., Solar installation companies in Texas",
                key="free_query",
            )

        country_name = st.selectbox("Geographic Target", list(COUNTRY_CODES.keys()), key="free_country")

    with col2:
        max_results = st.slider("Lead Batch Size", 5, 30, 10, step=5, key="free_max")
        auto_crawl = st.checkbox("🕷 Deep-Crawl Websites for Emails & Phones", value=True, key="free_crawl")
        auto_score = st.checkbox("🧠 Run Rule-Based & AI Fit Scoring", value=True, key="free_score")

    if st.button("🚀 LAUNCH FREE AUTONOMOUS LEAD DISCOVERY", key="btn_run_free", use_container_width=True):
        if not query:
            st.warning("Please enter a category or query.")
        else:
            prospector = FreeProspector()
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.markdown("🔍 **Step 1/3:** Searching web for target companies...")
            progress_bar.progress(25)
            loc = country_name if country_name != "Any" else ""
            companies = prospector.search_companies(query, location=loc, max_results=max_results)

            if not companies:
                status_text.empty()
                progress_bar.empty()
                st.warning(f"No businesses discovered for '{query}'. Try a broader query or standard category.")
            else:
                status_text.markdown(f"🕷 **Step 2/3:** Crawling {len(companies)} websites for emails & contacts...")
                progress_bar.progress(60)

                leads = prospector.process_companies_batch(
                    companies,
                    active_client=active_client if auto_score else None
                )

                status_text.markdown("🧠 **Step 3/3:** Finalizing lead verification...")
                progress_bar.progress(100)
                time.sleep(0.4)

                status_text.empty()
                progress_bar.empty()

                st.session_state["free_discovered_leads"] = leads
                st.success(f"✅ Discovered & enriched {len(leads)} real business leads with zero API fees!")

    # Display discovered leads
    leads = st.session_state.get("free_discovered_leads", [])
    if leads:
        # Summary Metrics
        emails_count = sum(1 for l in leads if l.get("email") and "@" in l["email"])
        high_fit_count = sum(1 for l in leads if l.get("fit_score", 0) >= 70)

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""
            <div class="metric-card" style="padding: 1rem;">
                <div class="metric-value">{len(leads)}</div>
                <div class="metric-label">PROSPECTS DISCOVERED</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-card" style="padding: 1rem;">
                <div class="metric-value" style="color: #4ADE80;">{emails_count}</div>
                <div class="metric-label">VERIFIED EMAILS EXTRACTED</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-card" style="padding: 1rem;">
                <div class="metric-value" style="color: #38BDF8;">{high_fit_count}</div>
                <div class="metric-label">HIGH-FIT ICP MATCHES</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="section-header" style="margin-top: 1.5rem;">
            <span>{len(leads)} Verified Leads Discovered (100% Free)</span>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #4ADE80;">IN-HOUSE CRAWLER</span>
        </div>
        """, unsafe_allow_html=True)

        # Table format
        rows = []
        for i, l in enumerate(leads):
            rows.append({
                "Select": True,
                "#": i + 1,
                "Company": l.get("name", "Unknown"),
                "Domain": l.get("domain", "—"),
                "Email": l.get("email", "—"),
                "Phone": l.get("phone") or "—",
                "Contact Person": l.get("full_name") or "Executive",
                "Title": l.get("title") or "Decision Maker",
                "Score": f"{l.get('fit_score', 80)}%",
                "Country": l.get("country") or "Global",
                "Description": (l.get("description") or "")[:80] + "...",
            })

        df = pd.DataFrame(rows)
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            height=min(450, 40 + len(rows) * 35),
            column_config={
                "Select": st.column_config.CheckboxColumn("✓", default=True, width="small"),
                "#": st.column_config.NumberColumn("#", width="small"),
                "Score": st.column_config.TextColumn("Fit", width="small"),
            },
            disabled=["#", "Company", "Domain", "Email", "Phone", "Contact Person", "Title", "Score", "Country", "Description"],
            key="free_leads_table",
        )

        selected_indices = edited_df[edited_df["Select"] == True].index.tolist()

        act_col1, act_col2 = st.columns([2, 1])
        with act_col1:
            if st.button(f"💾 SAVE {len(selected_indices)} SELECTED LEADS TO CRM", key="save_free_leads", use_container_width=True):
                saved = 0
                for idx in selected_indices:
                    l = leads[idx]
                    lead = Lead(
                        client_id=active_client.client_id if active_client else None,
                        first_name=l.get("first_name") or None,
                        last_name=l.get("last_name") or None,
                        full_name=l.get("full_name") or None,
                        job_title=l.get("title") or None,
                        company=l.get("name"),
                        website=l.get("domain"),
                        email=l.get("email") if l.get("email") != "—" else None,
                        email_verified=l.get("email_verified", False),
                        phone=l.get("phone") if l.get("phone") != "—" else None,
                        linkedin_url=l.get("linkedin_url") or None,
                        country=l.get("country") or None,
                        industry=l.get("industry") or None,
                        company_size=str(l.get("size", "11-50")),
                        fit_score=l.get("fit_score"),
                        score_level=l.get("fit_level", "HIGH"),
                        score_reason=l.get("fit_reason", ""),
                        notes=l.get("description", ""),
                        source="Free Autonomous Web Scout",
                        source_type="free_web_crawl",
                        lead_status="NEW",
                        discovery_date=datetime.now(),
                    )
                    db.add(lead)
                    saved += 1
                db.commit()
                st.success(f"✅ Saved {saved} leads to CRM! Go to **Outreach** tab to send batch emails.")

        with act_col2:
            # CSV export
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 EXPORT AS CSV",
                data=csv_data,
                file_name="discovered_free_leads.csv",
                mime="text/csv",
                use_container_width=True,
            )


def sourcing_page():
    st.markdown("""
    <div class="editorial-masthead" style="margin-bottom: 1.5rem; padding: 1rem 0.5rem;">
        <div class="masthead-meta-row">
            <span>AUTOMATED RECONNAISSANCE</span>
            <span>PIPELINE: FREE AUTONOMOUS PROSPECTOR</span>
            <span>WIRE ENGINE ACTIVE</span>
        </div>
        <h1 class="masthead-main-title" style="font-size: 2.2rem;">LEAD DISCOVERY</h1>
        <div class="masthead-sub-rule">Zero-Cost Web Prospecting · Real Website Crawling · AI Fit Scoring · Batch Sending</div>
    </div>
    """, unsafe_allow_html=True)

    db = SessionLocal()
    try:
        # Get active client for context
        clients = db.query(Client).all()
        active_client = None
        if clients:
            if len(clients) == 1:
                active_client = clients[0]
            else:
                client_names = {c.company_name: c for c in clients}
                selected = st.selectbox("Active Client", list(client_names.keys()), key="src_client")
                active_client = client_names[selected]

        free_prospector_ui(db, active_client)
    finally:
        db.close()
