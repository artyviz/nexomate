# dashboard/campaigns.py
"""Campaigns management page — Noir Press Broadsheet Edition."""

import streamlit as st
from database.database import SessionLocal
from database.models import Campaign, Lead, Message, Client
from config import CAMPAIGN_STATUSES


def campaigns_page():
    st.markdown("""
    <div class="editorial-masthead" style="margin-bottom: 1.5rem; padding: 1rem 0.5rem;">
        <div class="masthead-meta-row">
            <span>TACTICAL OPERATIONS</span>
            <span>CAMPAIGN DIRECTORY & DEPLOYMENT</span>
            <span>LIVE TARGETING</span>
        </div>
        <h1 class="masthead-main-title" style="font-size: 2.2rem;">CAMPAIGN OPERATIONS</h1>
        <div class="masthead-sub-rule">Autonomous outreach cohorts · Performance metrics · Operational status</div>
    </div>
    """, unsafe_allow_html=True)

    db = SessionLocal()
    try:
        tab_list, tab_create = st.tabs(["📋 Active Deployments", "➕ Formulate Campaign"])

        # ── Campaign List ────────────────────────────────────────────────
        with tab_list:
            campaigns = db.query(Campaign).filter(Campaign.is_demo == False).order_by(Campaign.created_at.desc()).all()

            if campaigns:
                for campaign in campaigns:
                    status_badge = "badge-high" if campaign.status == "RUNNING" else (
                        "badge-medium" if campaign.status in ("READY", "DRAFT") else "badge-low"
                    )

                    st.markdown(f"""
                    <div class="noir-card" style="padding: 1.5rem; margin-bottom: 1rem;">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                            <div>
                                <div style="font-family: 'Playfair Display', serif; font-size: 1.3rem; font-weight: 700; color: #F3F3EF;">
                                    {campaign.name}
                                </div>
                                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #888888; margin-top: 4px;">
                                    {campaign.industry or 'GENERAL SECTOR'} · {campaign.location or 'ALL TERRITORIES'}
                                    {(' · ' + campaign.description) if campaign.description else ''}
                                </div>
                            </div>
                            <span class="{status_badge}">{campaign.status}</span>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem; margin-top: 1.2rem; border-top: 1px solid #262626; padding-top: 1rem; text-align: center;">
                            <div>
                                <div style="font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 900; color: #F3F3EF;">{campaign.total_leads}</div>
                                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #888888; text-transform: uppercase;">Total Leads</div>
                            </div>
                            <div>
                                <div style="font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 900; color: #F3F3EF;">{campaign.selected_leads}</div>
                                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #888888; text-transform: uppercase;">Selected</div>
                            </div>
                            <div>
                                <div style="font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 900; color: #F3F3EF;">{campaign.emails_sent}</div>
                                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #888888; text-transform: uppercase;">Emails Sent</div>
                            </div>
                            <div>
                                <div style="font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 900; color: #F3F3EF;">{campaign.replies_count}</div>
                                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #888888; text-transform: uppercase;">Replies</div>
                            </div>
                            <div>
                                <div style="font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 900; color: #4ADE80;">{campaign.interested_count}</div>
                                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #888888; text-transform: uppercase;">Interested</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Campaign actions
                    acol1, acol2, acol3 = st.columns(3)
                    with acol1:
                        new_status = st.selectbox("Operational State", CAMPAIGN_STATUSES,
                                                  index=CAMPAIGN_STATUSES.index(campaign.status) if campaign.status in CAMPAIGN_STATUSES else 0,
                                                  key=f"cs_{campaign.campaign_id}")
                    with acol2:
                        if st.button("COMMIT STATUS", key=f"cu_{campaign.campaign_id}"):
                            campaign.status = new_status
                            db.commit()
                            st.success(f"Operational status set to {new_status}")
                            st.rerun()
                    with acol3:
                        if st.button("TERMINATE CAMPAIGN", key=f"cd_{campaign.campaign_id}"):
                            db.delete(campaign)
                            db.commit()
                            st.success("Deployment purged.")
                            st.rerun()

                    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
            else:
                st.info("No active campaigns catalogued. Formulate your first operation.")

        # ── Create Campaign ──────────────────────────────────────────────
        with tab_create:
            st.markdown("### Formulate New Deployment")
            with st.form("create_campaign"):
                name = st.text_input("Campaign Codename*")
                description = st.text_area("Operational Objective & Description", height=70)
                c1, c2 = st.columns(2)
                with c1:
                    industry = st.text_input("Target Sector", value="Solar Energy & Commercial Clean Tech")
                    location = st.text_input("Target Territory", value="Australia")
                with c2:
                    clients = db.query(Client).all()
                    client_id = None
                    if clients:
                        client_names = {c.company_name: c.client_id for c in clients}
                        selected = st.selectbox("Originating Client", list(client_names.keys()))
                        client_id = client_names[selected]

                submitted = st.form_submit_button("AUTHORIZE & LAUNCH DEPLOYMENT")
                if submitted and name:
                    new_campaign = Campaign(
                        client_id=client_id,
                        name=name,
                        description=description or None,
                        industry=industry or None,
                        location=location or None,
                        status="DRAFT",
                    )
                    db.add(new_campaign)
                    db.commit()
                    st.success(f"Deployment '{name}' formulated!")
                    st.rerun()
    finally:
        db.close()
