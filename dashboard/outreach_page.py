# dashboard/outreach_page.py
"""Outreach page — Batch email + single email dispatch."""

import streamlit as st
import pandas as pd
from database.database import SessionLocal
from database.models import Lead, Client, Message
from outreach.message_generator import generate_email, generate_whatsapp_message, generate_sms_message
from outreach.email_sender import send_email, send_batch_emails, is_smtp_configured
from outreach.email_tracker import create_email_record, update_email_status
from outreach.whatsapp_sender import format_whatsapp_url
from outreach.sms_sender import send_sms
from config import EMAIL_BATCH_SIZE


# ── Email Templates ──────────────────────────────────────────────────────────
EMAIL_TEMPLATES = {
    "Professional Intro": {
        "subject": "Partnership opportunity: {company}",
        "body": (
            "Dear {first_name},\n\n"
            "I hope this message finds you well. I came across {company} and was impressed by your work.\n\n"
            "I'd love to explore how we might collaborate. Would you be open to a brief call this week?\n\n"
            "Best regards"
        ),
    },
    "Friendly Outreach": {
        "subject": "Quick hello — {company}",
        "body": (
            "Hi {first_name},\n\n"
            "Hope your week is going great! I've been following {company} and really admire what you're building.\n\n"
            "I thought there might be some interesting synergies between our teams. Would you be open to a quick chat?\n\n"
            "Cheers"
        ),
    },
    "Direct Value Prop": {
        "subject": "Question about {company}",
        "body": (
            "Hi {first_name},\n\n"
            "I noticed {company} is growing fast — congrats!\n\n"
            "We help companies like yours scale operations and boost efficiency. Would it make sense to explore this together?\n\n"
            "5 minutes is all I'd need. How about Thursday?\n\n"
            "Best"
        ),
    },
    "Custom (write your own)": {
        "subject": "",
        "body": "",
    },
}


def outreach_page():
    st.markdown("""
    <div class="editorial-masthead" style="margin-bottom: 1.5rem; padding: 1rem 0.5rem;">
        <div class="masthead-meta-row">
            <span>TRANSMISSION TERMINAL</span>
            <span>OUTBOUND DISPATCH CONDUIT</span>
            <span>SINGLE · BATCH · MULTI-CHANNEL</span>
        </div>
        <h1 class="masthead-main-title" style="font-size: 2.2rem;">OUTREACH & DISPATCH</h1>
        <div class="masthead-sub-rule">Batch Email Blasts · Single Dispatch · WhatsApp · SMS · Dispatch Log</div>
    </div>
    """, unsafe_allow_html=True)

    db = SessionLocal()
    try:
        tab_batch, tab_email, tab_whatsapp, tab_sms, tab_history = st.tabs([
            "📨 Batch Email", "📧 Single Email", "💬 WhatsApp", "📱 SMS", "📋 Dispatch Log"
        ])

        # Get clients
        clients = db.query(Client).all()
        active_client = clients[0] if clients else None

        # ══════════════════════════════════════════════════════════════════
        # TAB: BATCH EMAIL (New — the core feature)
        # ══════════════════════════════════════════════════════════════════
        with tab_batch:
            st.markdown("""
            <div class="section-header">
                <span>Select Leads & Send Batch Emails</span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #888888;">BATCH MODE</span>
            </div>
            """, unsafe_allow_html=True)

            if not is_smtp_configured():
                st.error("⚠ **SMTP not configured.** Set `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` in `.env`")
                st.stop()

            # ── Filter leads ─────────────────────────────────────────────
            with st.expander("▾ FILTER LEADS", expanded=True):
                fcol1, fcol2, fcol3 = st.columns(3)
                with fcol1:
                    score_filter = st.multiselect("Priority", ["HIGH", "MEDIUM", "LOW"], default=["HIGH", "MEDIUM"], key="batch_score")
                with fcol2:
                    source_filter = st.selectbox("Source", ["All", "Autonomous Scout", "Manual", "Web Search", "Excel Import"], key="batch_source")
                with fcol3:
                    verified_only = st.checkbox("Verified emails only", value=False, key="batch_verified")

            # Query leads with emails
            query = db.query(Lead).filter(
                Lead.is_demo == False,
                Lead.email.isnot(None),
                Lead.email != "",
                Lead.email != "Not Found",
                Lead.email != "—",
            )

            if score_filter:
                query = query.filter(Lead.score_level.in_(score_filter))
            if source_filter != "All":
                source_map = {
                    "Autonomous Scout": "Free Autonomous Web Scout", "Manual": "Manual Intelligence Entry",
                    "Web Search": "Web Search", "Excel Import": "Excel Import",
                }
                query = query.filter(Lead.source == source_map.get(source_filter, source_filter))
            if verified_only:
                query = query.filter(Lead.email_verified == True)

            query = query.order_by(Lead.fit_score.desc().nullslast())
            leads = query.all()

            if not leads:
                st.info("No leads with email addresses found. Use **Find Leads** to discover contacts.")
            else:
                # Build selectable table
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

                    rows.append({
                        "Select": lead.score_level in ("HIGH", "MEDIUM"),  # Pre-select HIGH + MEDIUM
                        "ID": lead.lead_id,
                        "Name": lead.full_name or "—",
                        "Company": lead.company or "—",
                        "Title": lead.job_title or "—",
                        "Email": lead.email or "—",
                        "Score": score_display,
                        "Verified": "✓" if lead.email_verified else "—",
                        "Status": lead.lead_status or "—",
                    })

                df = pd.DataFrame(rows)

                # Quick actions
                qcol1, qcol2, qcol3, qcol4 = st.columns(4)
                with qcol1:
                    st.markdown(f"""
                    <div class="metric-card" style="padding: 0.8rem; text-align: center;">
                        <div class="metric-value" style="font-size: 1.8rem;">{len(leads)}</div>
                        <div class="metric-label">TOTAL WITH EMAIL</div>
                    </div>
                    """, unsafe_allow_html=True)
                with qcol2:
                    high_count = sum(1 for l in leads if l.score_level == "HIGH")
                    st.markdown(f"""
                    <div class="metric-card" style="padding: 0.8rem; text-align: center;">
                        <div class="metric-value" style="font-size: 1.8rem; color: #4ADE80;">{high_count}</div>
                        <div class="metric-label">HIGH PRIORITY</div>
                    </div>
                    """, unsafe_allow_html=True)
                with qcol3:
                    verified_count = sum(1 for l in leads if l.email_verified)
                    st.markdown(f"""
                    <div class="metric-card" style="padding: 0.8rem; text-align: center;">
                        <div class="metric-value" style="font-size: 1.8rem; color: #60A5FA;">{verified_count}</div>
                        <div class="metric-label">VERIFIED EMAILS</div>
                    </div>
                    """, unsafe_allow_html=True)
                with qcol4:
                    contacted = sum(1 for l in leads if l.lead_status == "CONTACTED")
                    st.markdown(f"""
                    <div class="metric-card" style="padding: 0.8rem; text-align: center;">
                        <div class="metric-value" style="font-size: 1.8rem; color: #FACC15;">{contacted}</div>
                        <div class="metric-label">ALREADY CONTACTED</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)

                edited_df = st.data_editor(
                    df,
                    use_container_width=True,
                    height=min(450, 40 + len(rows) * 35),
                    column_config={
                        "Select": st.column_config.CheckboxColumn("✓", default=False, width="small"),
                        "ID": st.column_config.NumberColumn("ID", width="small"),
                        "Score": st.column_config.TextColumn("Score", width="small"),
                        "Verified": st.column_config.TextColumn("✓Email", width="small"),
                    },
                    disabled=["ID", "Name", "Company", "Title", "Email", "Score", "Verified", "Status"],
                    key="batch_table",
                )

                selected_mask = edited_df["Select"] == True
                selected_ids = edited_df[selected_mask]["ID"].tolist()
                selected_count = len(selected_ids)

                st.markdown(f"**{selected_count} leads selected** for batch email")

                # ── Email Template ───────────────────────────────────────
                st.markdown("""
                <div class="section-header" style="margin-top: 1.5rem;">
                    <span>Compose Email Template</span>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #888888;">TEMPLATE</span>
                </div>
                """, unsafe_allow_html=True)

                template_name = st.selectbox("Choose Template", list(EMAIL_TEMPLATES.keys()), key="batch_template")
                template = EMAIL_TEMPLATES[template_name]

                subject_template = st.text_input(
                    "Subject Line (use {first_name}, {company}, etc.)",
                    value=template["subject"],
                    key="batch_subject",
                )
                body_template = st.text_area(
                    "Email Body (use {first_name}, {company}, {job_title}, {industry}, etc.)",
                    value=template["body"],
                    height=200,
                    key="batch_body",
                )

                # Sender info
                scol1, scol2 = st.columns(2)
                with scol1:
                    sender_name = st.text_input(
                        "Sender Name",
                        value=active_client.sender_name if active_client and active_client.sender_name else "",
                        key="batch_sender_name",
                    )
                with scol2:
                    sender_email = st.text_input(
                        "Sender Email",
                        value=active_client.sender_email if active_client and active_client.sender_email else "",
                        key="batch_sender_email",
                    )

                # Preview
                if selected_count > 0 and st.checkbox("Preview first email", key="batch_preview"):
                    first_lead = db.query(Lead).filter(Lead.lead_id == selected_ids[0]).first()
                    if first_lead:
                        from outreach.email_sender import _fill_template
                        lead_dict = {
                            "first_name": first_lead.first_name, "last_name": first_lead.last_name,
                            "full_name": first_lead.full_name, "company": first_lead.company,
                            "job_title": first_lead.job_title, "email": first_lead.email,
                            "city": first_lead.city, "state": first_lead.state,
                            "country": first_lead.country, "industry": first_lead.industry,
                        }
                        preview_subject = _fill_template(subject_template, lead_dict)
                        preview_body = _fill_template(body_template, lead_dict)
                        st.markdown(f"""
                        <div class="noir-card" style="padding: 1.2rem; margin: 0.5rem 0;">
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #888888; margin-bottom: 0.5rem;">
                                TO: {first_lead.full_name} &lt;{first_lead.email}&gt;
                            </div>
                            <div style="font-family: 'Playfair Display', serif; font-size: 1.1rem; font-weight: 700; color: #F3F3EF; margin-bottom: 0.8rem;">
                                {preview_subject}
                            </div>
                            <div style="font-family: 'Lora', serif; color: #CCCCCC; font-size: 0.9rem; white-space: pre-wrap; line-height: 1.6;">
                                {preview_body}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                # ── Send Batch ───────────────────────────────────────────
                batch_limit = st.slider(
                    "Batch Size Limit",
                    min_value=5, max_value=100, value=min(EMAIL_BATCH_SIZE, selected_count) if selected_count > 0 else EMAIL_BATCH_SIZE,
                    step=5, key="batch_limit",
                    help="Maximum emails to send in this batch. Prevents SMTP throttling."
                )

                if st.button("🚀 SEND BATCH EMAIL", key="send_batch", use_container_width=True, type="primary"):
                    if selected_count == 0:
                        st.warning("No leads selected. Check the boxes next to the leads you want to email.")
                    elif not subject_template or not body_template:
                        st.warning("Subject and body templates are required.")
                    else:
                        # Get lead objects
                        send_ids = selected_ids[:batch_limit]
                        send_leads = db.query(Lead).filter(Lead.lead_id.in_(send_ids)).all()

                        # Convert to dicts for batch sender
                        lead_dicts = []
                        lead_map = {}
                        for lead in send_leads:
                            ld = {
                                "lead_id": lead.lead_id,
                                "first_name": lead.first_name,
                                "last_name": lead.last_name,
                                "full_name": lead.full_name,
                                "company": lead.company,
                                "job_title": lead.job_title,
                                "email": lead.email,
                                "city": lead.city,
                                "state": lead.state,
                                "country": lead.country,
                                "industry": lead.industry,
                            }
                            lead_dicts.append(ld)
                            lead_map[lead.email] = lead

                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        def on_progress(sent, failed, total, current):
                            progress_bar.progress((sent + failed) / total)
                            status_text.markdown(
                                f"📤 Sending... **{sent + failed}/{total}** "
                                f"(✅ {sent} sent · ❌ {failed} failed) — "
                                f"Current: {current.get('full_name', 'Unknown')}"
                            )

                        # Send batch
                        batch_result = send_batch_emails(
                            leads=lead_dicts,
                            subject_template=subject_template,
                            body_template=body_template,
                            sender_name=sender_name,
                            sender_email=sender_email,
                            progress_callback=on_progress,
                        )

                        progress_bar.empty()
                        status_text.empty()

                        # Save results to database
                        for r in batch_result["results"]:
                            email = r.get("email", "")
                            lead_obj = lead_map.get(email)
                            if lead_obj:
                                # Create message record
                                from outreach.email_sender import _fill_template
                                filled_subject = _fill_template(subject_template, {
                                    "first_name": lead_obj.first_name, "full_name": lead_obj.full_name,
                                    "company": lead_obj.company, "job_title": lead_obj.job_title,
                                    "industry": lead_obj.industry,
                                })
                                filled_body = _fill_template(body_template, {
                                    "first_name": lead_obj.first_name, "full_name": lead_obj.full_name,
                                    "company": lead_obj.company, "job_title": lead_obj.job_title,
                                    "industry": lead_obj.industry,
                                })

                                msg_record = Message(
                                    lead_id=lead_obj.lead_id,
                                    channel="email",
                                    subject=filled_subject,
                                    body=filled_body,
                                    status=r["status"],
                                    sent_at=datetime.now() if r["status"] == "SENT" else None,
                                    smtp_message_id=r.get("message_id"),
                                    error_message=r.get("error"),
                                )
                                db.add(msg_record)

                                # Update lead status
                                if r["status"] == "SENT":
                                    lead_obj.lead_status = "CONTACTED"
                                    lead_obj.email_status = "SENT"

                        db.commit()

                        # Show results
                        from datetime import datetime
                        if batch_result["sent"] > 0:
                            st.success(f"""
                            ✅ **Batch Complete!**
                            - 📤 Sent: **{batch_result['sent']}**
                            - ❌ Failed: **{batch_result['failed']}**
                            - 📊 Total: **{batch_result['total']}**
                            """)
                        if batch_result["failed"] > 0:
                            with st.expander("View Failed Emails"):
                                failed = [r for r in batch_result["results"] if r["status"] != "SENT"]
                                for f in failed:
                                    st.write(f"❌ **{f['lead']}** ({f['email']}): {f.get('error', 'Unknown error')}")

        # ══════════════════════════════════════════════════════════════════
        # TAB: SINGLE EMAIL (kept from original)
        # ══════════════════════════════════════════════════════════════════
        with tab_email:
            st.markdown("### Single Email Composer")

            # Select lead
            email_leads = db.query(Lead).filter(
                Lead.is_demo == False,
                Lead.email.isnot(None),
                Lead.email != "",
                Lead.email != "Not Found",
            ).order_by(Lead.fit_score.desc().nullslast()).all()

            if not email_leads:
                st.info("No leads with email addresses. Use **Find Leads** to discover contacts.")
            else:
                lead_options = {
                    f"{l.full_name or l.company} ({l.email}) — [{l.score_level or 'UNSCORED'}]": l
                    for l in email_leads
                }
                selected_lead_name = st.selectbox("Select Recipient", list(lead_options.keys()))
                lead = lead_options[selected_lead_name]

                # Lead info card
                st.markdown(f"""
                <div class="noir-card" style="padding: 1.2rem; margin: 1rem 0;">
                    <div style="font-family: 'Playfair Display', serif; font-size: 1.25rem; font-weight: 700; color: #F3F3EF;">
                        {lead.full_name or 'Target Prospect'}
                    </div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #888888; margin-top: 4px;">
                        {lead.job_title or 'Executive'} · {lead.company or 'Commercial Account'} · {lead.email}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col_gen, col_manual = st.columns(2)
                with col_gen:
                    generate_btn = st.button("🤖 DRAFT WITH AI ENGINE")
                with col_manual:
                    manual_mode = st.checkbox("Manual Composition Mode")

                if generate_btn and active_client:
                    with st.spinner("Formulating personalized message..."):
                        client_dict = {
                            "company_name": active_client.company_name,
                            "services": active_client.services or "",
                            "value_proposition": active_client.value_proposition or "",
                            "preferred_tone": active_client.preferred_tone or "Professional",
                            "sender_name": active_client.sender_name or "",
                        }
                        lead_dict = {
                            "full_name": lead.full_name, "first_name": lead.first_name,
                            "company": lead.company, "job_title": lead.job_title,
                            "city": lead.city, "state": lead.state,
                            "industry": lead.industry, "notes": lead.notes,
                            "pain_points": lead.pain_points,
                        }
                        result = generate_email(lead_dict, client_dict)

                    if "error" in result and result["error"]:
                        st.error(result["error"])
                    else:
                        st.session_state["email_subject"] = result.get("subject", "")
                        st.session_state["email_body"] = result.get("body", "")

                to_email = st.text_input("To", value=f"{lead.full_name or ''} <{lead.email}>")
                subject = st.text_input("Subject", value=st.session_state.get("email_subject", ""))
                body = st.text_area("Body", value=st.session_state.get("email_body", ""), height=220)

                bcol1, bcol2 = st.columns(2)
                with bcol1:
                    if st.button("💾 SAVE DRAFT"):
                        msg = create_email_record(db, lead.lead_id, subject, body, status="DRAFT")
                        st.success(f"Draft saved (#{msg.message_id})")
                with bcol2:
                    if st.button("📤 DISPATCH"):
                        if not subject or not body:
                            st.warning("Subject and body are required.")
                        else:
                            msg = create_email_record(db, lead.lead_id, subject, body, status="SENDING")
                            result = send_email(
                                to_email=lead.email, subject=subject, body=body,
                                sender_name=active_client.sender_name if active_client else "",
                                sender_email=active_client.sender_email if active_client else "",
                            )
                            if result["status"] == "SENT":
                                update_email_status(db, msg.message_id, "SENT", smtp_message_id=result.get("message_id"))
                                st.success(f"✅ Delivered to {lead.email}!")
                            else:
                                update_email_status(db, msg.message_id, "FAILED", error=result.get("error"))
                                st.error(f"Failed: {result.get('error')}")

        # ══════════════════════════════════════════════════════════════════
        # TAB: WHATSAPP
        # ══════════════════════════════════════════════════════════════════
        with tab_whatsapp:
            st.markdown("### WhatsApp Direct Wire")

            leads_with_phone = db.query(Lead).filter(
                Lead.is_demo == False,
                Lead.phone.isnot(None),
                Lead.phone != "",
                Lead.phone != "Not Found",
            ).all()

            if not leads_with_phone:
                st.info("No leads with phone numbers.")
            else:
                wa_options = {
                    f"{l.full_name or l.company} ({l.phone})": l for l in leads_with_phone
                }
                selected_wa = st.selectbox("Select Contact", list(wa_options.keys()), key="wa_lead")
                wa_lead = wa_options[selected_wa]

                if st.button("🤖 DRAFT WHATSAPP"):
                    wa_client = active_client or Client(company_name="Nexomate", value_proposition="scale operations")
                    client_dict = {
                        "company_name": wa_client.company_name,
                        "value_proposition": wa_client.value_proposition or "",
                        "preferred_tone": wa_client.preferred_tone or "Friendly",
                    }
                    lead_dict = {"full_name": wa_lead.full_name, "first_name": wa_lead.first_name, "company": wa_lead.company}
                    result = generate_whatsapp_message(lead_dict, client_dict)
                    st.session_state["wa_message"] = result.get("message", "")

                wa_msg = st.text_area("WhatsApp Message", value=st.session_state.get("wa_message", ""), height=100, key="wa_text")
                if wa_lead.phone:
                    url = format_whatsapp_url(wa_lead.phone, wa_msg)
                    st.markdown(f"[📱 OPEN WHATSAPP]({url})")

        # ══════════════════════════════════════════════════════════════════
        # TAB: SMS
        # ══════════════════════════════════════════════════════════════════
        with tab_sms:
            st.markdown("### SMS Gateway")

            sms_leads = db.query(Lead).filter(
                Lead.is_demo == False,
                Lead.phone.isnot(None),
                Lead.phone != "",
                Lead.phone != "Not Found",
            ).all()

            if not sms_leads:
                st.info("No leads with phone numbers.")
            else:
                sms_options = {
                    f"{l.full_name or l.company} ({l.phone})": l for l in sms_leads
                }
                selected_sms = st.selectbox("Select Contact", list(sms_options.keys()), key="sms_lead")
                sms_lead = sms_options[selected_sms]

                if st.button("🤖 DRAFT SMS"):
                    sms_client = active_client or Client(company_name="Nexomate", value_proposition="scale operations")
                    result = generate_sms_message(
                        {"full_name": sms_lead.full_name, "first_name": sms_lead.first_name},
                        {"company_name": sms_client.company_name, "value_proposition": sms_client.value_proposition or ""},
                    )
                    st.session_state["sms_message"] = result.get("message", "")

                sms_msg = st.text_area("SMS Body", value=st.session_state.get("sms_message", ""), height=80, key="sms_text")
                if st.button("📋 COPY SMS"):
                    st.code(sms_msg)

        # ══════════════════════════════════════════════════════════════════
        # TAB: DISPATCH HISTORY
        # ══════════════════════════════════════════════════════════════════
        with tab_history:
            st.markdown("### Dispatch History")
            messages = db.query(Message).filter(Message.is_demo == False).order_by(Message.created_at.desc()).limit(100).all()

            if messages:
                # Summary stats
                total_sent = sum(1 for m in messages if m.status == "SENT")
                total_failed = sum(1 for m in messages if m.status == "FAILED")
                total_draft = sum(1 for m in messages if m.status == "DRAFT")

                hcol1, hcol2, hcol3 = st.columns(3)
                with hcol1:
                    st.markdown(f"""
                    <div class="metric-card" style="padding: 0.8rem; text-align: center;">
                        <div class="metric-value" style="font-size: 1.6rem; color: #4ADE80;">{total_sent}</div>
                        <div class="metric-label">SENT</div>
                    </div>
                    """, unsafe_allow_html=True)
                with hcol2:
                    st.markdown(f"""
                    <div class="metric-card" style="padding: 0.8rem; text-align: center;">
                        <div class="metric-value" style="font-size: 1.6rem; color: #F87171;">{total_failed}</div>
                        <div class="metric-label">FAILED</div>
                    </div>
                    """, unsafe_allow_html=True)
                with hcol3:
                    st.markdown(f"""
                    <div class="metric-card" style="padding: 0.8rem; text-align: center;">
                        <div class="metric-value" style="font-size: 1.6rem; color: #FACC15;">{total_draft}</div>
                        <div class="metric-label">DRAFTS</div>
                    </div>
                    """, unsafe_allow_html=True)

                for msg in messages:
                    lead = db.query(Lead).filter(Lead.lead_id == msg.lead_id).first()
                    badge_style = "badge-high" if msg.status == "SENT" else "badge-medium" if msg.status == "DRAFT" else "badge-low"
                    st.markdown(f"""
                    <div class="noir-card" style="padding: 1rem 1.25rem; margin-bottom: 0.6rem;">
                        <div style="display:flex; justify-content:space-between; align-items: baseline;">
                            <div style="font-family: 'Playfair Display', serif; font-size: 1.15rem; font-weight: 700; color: #F3F3EF;">
                                {lead.full_name if lead else 'Unknown'}
                                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #888888; font-weight: 400;"> · {lead.email if lead else ''}</span>
                            </div>
                            <span class="{badge_style}">{msg.status}</span>
                        </div>
                        <div style="font-family: 'Lora', serif; color: #CCCCCC; font-size: 0.9rem; margin-top: 0.4rem;">
                            <strong>{msg.subject or 'No Subject'}</strong>
                        </div>
                        <div style="font-family: 'JetBrains Mono', monospace; color: #888888; font-size: 0.7rem; margin-top: 0.4rem;">
                            VIA: {msg.channel} · {msg.created_at}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No outbound messages on record.")
    finally:
        db.close()
