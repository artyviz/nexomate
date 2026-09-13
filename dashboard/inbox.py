# dashboard/inbox.py
"""Unified Inbox page — Noir Press Broadsheet Edition."""

import streamlit as st
from database.database import SessionLocal
from database.models import Reply, Lead, Message
from outreach.reply_tracker import check_for_replies, classify_reply, is_imap_configured
from config import REPLY_CLASSIFICATIONS


def inbox_page():
    st.markdown("""
    <div class="editorial-masthead" style="margin-bottom: 1.5rem; padding: 1rem 0.5rem;">
        <div class="masthead-meta-row">
            <span>COMMUNICATIONS INTERCEPT</span>
            <span>INCOMING WIRE DISPATCHES</span>
            <span>UNIFIED INBOX</span>
        </div>
        <h1 class="masthead-main-title" style="font-size: 2.2rem;">INCOMING WIRE & REPLIES</h1>
        <div class="masthead-sub-rule">Direct communication intercept channel · Automated sentiment classification</div>
    </div>
    """, unsafe_allow_html=True)

    db = SessionLocal()
    try:
        # ── Controls ─────────────────────────────────────────────────────
        col1, col2 = st.columns([3, 1])
        with col1:
            if is_imap_configured():
                if st.button("🔄 SCAN WIRE FOR INCOMING REPLIES"):
                    with st.spinner("Intercepting incoming mail..."):
                        new_replies = check_for_replies(db)
                    if new_replies:
                        if "error" in new_replies[0]:
                            st.error(new_replies[0]["error"])
                        else:
                            st.success(f"Intercepted {len(new_replies)} transmissions!")
                            st.rerun()
                    else:
                        st.info("No new dispatches detected on the wire.")
            else:
                st.info("IMAP protocol not configured. Set IMAP_HOST, IMAP_USER, IMAP_PASSWORD in `.env`.")
        with col2:
            filter_class = st.selectbox("Classification Filter", ["All"] + REPLY_CLASSIFICATIONS, key="inbox_filter")

        # ── Display replies ──────────────────────────────────────────────
        query = db.query(Reply).filter(Reply.is_demo == False)
        if filter_class != "All":
            query = query.filter(
                (Reply.classification == filter_class) | (Reply.user_override == filter_class)
            )
        replies = query.order_by(Reply.received_at.desc()).all()

        if replies:
            for reply in replies:
                lead = db.query(Lead).filter(Lead.lead_id == reply.lead_id).first()
                classification = reply.user_override or reply.classification or "UNKNOWN"

                badge_class = "badge-high" if classification == "INTERESTED" else (
                    "badge-low" if classification == "NOT_INTERESTED" else "badge-medium"
                )

                st.markdown(f"""
                <div class="noir-card" style="padding: 1.25rem; margin-bottom: 0.8rem;">
                    <div style="display:flex; justify-content:space-between; align-items:start;">
                        <div>
                            <div style="font-family: 'Playfair Display', serif; font-size: 1.2rem; font-weight: 700; color: #F3F3EF;">
                                {lead.full_name if lead else reply.sender}
                            </div>
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #888888; margin-top: 2px;">
                                {lead.company if lead else ''} · {reply.sender or ''} · {reply.received_at or ''}
                            </div>
                        </div>
                        <span class="{badge_class}">{classification}</span>
                    </div>
                    <div style="font-family: 'Lora', serif; color: #CCCCCC; margin: 0.8rem 0; padding: 1rem; background: #0E0E0E; border-left: 3px solid #FF3333; font-size: 0.95rem; font-style: italic;">
                        "{(reply.body or '')[:350]}{'...' if reply.body and len(reply.body) > 350 else ''}"
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Action buttons
                acol1, acol2, acol3, acol4 = st.columns(4)
                with acol1:
                    if st.button("INTERESTED", key=f"int_{reply.reply_id}"):
                        reply.user_override = "INTERESTED"
                        if lead:
                            lead.lead_status = "INTERESTED"
                        db.commit()
                        st.rerun()
                with acol2:
                    if st.button("FOLLOW UP", key=f"fu_{reply.reply_id}"):
                        reply.user_override = "FOLLOW_UP"
                        if lead:
                            lead.lead_status = "FOLLOW_UP"
                        db.commit()
                        st.rerun()
                with acol3:
                    if st.button("NOT INTERESTED", key=f"ni_{reply.reply_id}"):
                        reply.user_override = "NOT_INTERESTED"
                        if lead:
                            lead.lead_status = "NOT_INTERESTED"
                        db.commit()
                        st.rerun()
                with acol4:
                    if st.button("AI CLASSIFY", key=f"ai_{reply.reply_id}"):
                        with st.spinner("Analyzing sentiment..."):
                            result = classify_reply(reply)
                        reply.classification = result.get("classification", "UNKNOWN")
                        reply.confidence = result.get("confidence", 0)
                        db.commit()
                        st.success(f"Classified: {result['classification']} ({result.get('confidence', 0):.0%})")
                        st.rerun()

                st.markdown("<div style='margin-bottom: 0.8rem;'></div>", unsafe_allow_html=True)
        else:
            st.info("No incoming wire dispatches intercepted yet.")

        # ── Manual Reply Entry ───────────────────────────────────────────
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        with st.expander("▾ LOG EXTERNAL WIRE REPLY MANUALLY"):
            st.markdown("Record a response received through external channels.")
            leads_all = db.query(Lead).filter(Lead.is_demo == False).all()
            if leads_all:
                lead_map = {f"{l.full_name or l.company} ({l.email or 'no email'})": l for l in leads_all}
                selected = st.selectbox("Originating Prospect", list(lead_map.keys()), key="manual_reply_lead")
                reply_body = st.text_area("Transcript / Response Content", key="manual_reply_body")
                reply_class = st.selectbox("Classification", REPLY_CLASSIFICATIONS, key="manual_reply_class")

                if st.button("LOG TRANSMISSION RECORD"):
                    from datetime import datetime
                    lead_obj = lead_map[selected]
                    new_reply = Reply(
                        lead_id=lead_obj.lead_id,
                        sender=lead_obj.email,
                        subject="Manual Dispatch Record",
                        body=reply_body,
                        classification=reply_class,
                        user_override=reply_class,
                        received_at=datetime.now(),
                    )
                    db.add(new_reply)
                    lead_obj.lead_status = "REPLIED"
                    db.commit()
                    st.success("Dispatch logged to permanent wire archive!")
                    st.rerun()
    finally:
        db.close()
