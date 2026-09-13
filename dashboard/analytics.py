# dashboard/analytics.py
"""Analytics dashboard with charts and KPIs — Noir Press Broadsheet Edition."""

import streamlit as st
import pandas as pd
from database.database import SessionLocal
from database.models import Lead, Campaign, Message, Reply


def analytics_page():
    st.markdown("""
    <div class="editorial-masthead" style="margin-bottom: 1.5rem; padding: 1rem 0.5rem;">
        <div class="masthead-meta-row">
            <span>INTELLIGENCE METRICS</span>
            <span>DATA DIVISION: STATISTICAL DISPATCH</span>
            <span>SYNCHRONIZED AUDIT</span>
        </div>
        <h1 class="masthead-main-title" style="font-size: 2.2rem;">TELEMETRY & ANALYTICS</h1>
        <div class="masthead-sub-rule">Prospect distribution · Transmission volumes · Conversion efficacy · Geographic dispersion</div>
    </div>
    """, unsafe_allow_html=True)

    db = SessionLocal()
    try:
        leads = db.query(Lead).filter(Lead.is_demo == False).all()
        messages = db.query(Message).filter(Message.is_demo == False).all()
        replies = db.query(Reply).filter(Reply.is_demo == False).all()

        if not leads:
            st.info("No records available in database to compile telemetry.")
            return

        # ── KPI Cards ────────────────────────────────────────────────────
        total = len(leads)
        high = sum(1 for l in leads if l.score_level == "HIGH")
        medium = sum(1 for l in leads if l.score_level == "MEDIUM")
        low = sum(1 for l in leads if l.score_level == "LOW")
        with_email = sum(1 for l in leads if l.email and l.email != "Not Found")
        sent = sum(1 for m in messages if m.status == "SENT")
        reply_count = len(replies)
        interested = sum(1 for l in leads if l.lead_status == "INTERESTED")

        cols = st.columns(4)
        kpis = [
            ("Total Catalogued", f"{total:,}"),
            ("Transmissions Sent", f"{sent:,}"),
            ("Intercepted Replies", f"{reply_count:,}"),
            ("Affirmative Leads", f"{interested:,}"),
        ]
        for col, (label, value) in zip(cols, kpis):
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

        # ── Charts ───────────────────────────────────────────────────────
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("""
            <div class="section-header">
                <span>Priority Classification Distribution</span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #888888;">SCORING</span>
            </div>
            """, unsafe_allow_html=True)
            score_data = pd.DataFrame({
                "Tier": ["HIGH", "MEDIUM", "LOW", "Unscored"],
                "Count": [
                    high, medium, low,
                    total - high - medium - low,
                ],
            })
            st.bar_chart(score_data.set_index("Tier"))

        with chart_col2:
            st.markdown("""
            <div class="section-header">
                <span>Outreach Conduit State</span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #888888;">MESSAGING</span>
            </div>
            """, unsafe_allow_html=True)
            status_counts = {}
            for m in messages:
                status_counts[m.status] = status_counts.get(m.status, 0) + 1
            if status_counts:
                status_df = pd.DataFrame(
                    list(status_counts.items()),
                    columns=["Status", "Count"],
                )
                st.bar_chart(status_df.set_index("Status"))
            else:
                st.info("No outbound transmissions on record.")

        chart_col3, chart_col4 = st.columns(2)

        with chart_col3:
            st.markdown("""
            <div class="section-header">
                <span>Intelligence Origin Sources</span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #888888;">PROVENANCE</span>
            </div>
            """, unsafe_allow_html=True)
            source_counts = {}
            for l in leads:
                src = l.source or "Unknown"
                source_counts[src] = source_counts.get(src, 0) + 1
            if source_counts:
                source_df = pd.DataFrame(
                    list(source_counts.items()),
                    columns=["Source", "Count"],
                )
                st.bar_chart(source_df.set_index("Source"))

        with chart_col4:
            st.markdown("""
            <div class="section-header">
                <span>Territorial Jurisdiction</span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #888888;">GEOGRAPHY</span>
            </div>
            """, unsafe_allow_html=True)
            loc_counts = {}
            for l in leads:
                loc = l.state or l.country or l.city or "Unknown"
                loc_counts[loc] = loc_counts.get(loc, 0) + 1
            if loc_counts:
                loc_df = pd.DataFrame(
                    list(loc_counts.items()),
                    columns=["Territory", "Count"],
                )
                st.bar_chart(loc_df.set_index("Territory"))

        # ── Summary Stats ────────────────────────────────────────────────
        st.markdown("""
        <div class="section-header" style="margin-top: 2rem;">
            <span>Performance Telemetry Summary</span>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #888888;">AUDIT RATIOS</span>
        </div>
        """, unsafe_allow_html=True)

        avg_score = sum(l.fit_score or 0 for l in leads) / max(total, 1)
        scol1, scol2, scol3, scol4 = st.columns(4)
        with scol1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_score:.1f}</div>
                <div class="metric-label">AVERAGE FIT SCORE</div>
            </div>
            """, unsafe_allow_html=True)
        with scol2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{with_email*100//max(total,1)}%</div>
                <div class="metric-label">EMAIL ENRICHED ({with_email})</div>
            </div>
            """, unsafe_allow_html=True)
        with scol3:
            reply_rate = (reply_count / max(sent, 1)) * 100
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{reply_rate:.1f}%</div>
                <div class="metric-label">TRANSMISSION REPLY RATE</div>
            </div>
            """, unsafe_allow_html=True)
        with scol4:
            interest_rate = (interested / max(reply_count, 1)) * 100
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #4ADE80;">{interest_rate:.1f}%</div>
                <div class="metric-label">AFFIRMATIVE CONVERSION</div>
            </div>
            """, unsafe_allow_html=True)
    finally:
        db.close()
