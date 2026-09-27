# dashboard/settings.py
"""Settings page — Noir Press Broadsheet Edition."""

import streamlit as st
from database.database import SessionLocal
from database.models import Client, Lead, Campaign, Message, Reply
from outreach.email_sender import is_smtp_configured
from outreach.reply_tracker import is_imap_configured
from ai.provider_factory import get_ai_provider
from config import OLLAMA_HOST, OLLAMA_MODEL, SMTP_HOST, SMTP_PORT, SMTP_USER, IMAP_HOST
from config import GROQ_API_KEY, GROQ_MODEL, AI_PROVIDER
import json


def settings_page():
    st.markdown("""
    <div class="editorial-masthead" style="margin-bottom: 1.5rem; padding: 1rem 0.5rem;">
        <div class="masthead-meta-row">
            <span>TERMINAL ARCHITECTURE</span>
            <span>HARDWARE & PROTOCOL CONFIGURATION</span>
            <span>DIAGNOSTICS SUITE</span>
        </div>
        <h1 class="masthead-main-title" style="font-size: 2.2rem;">SYSTEM ARCHITECTURE & PROTOCOLS</h1>
        <div class="masthead-sub-rule">Interface parameters · Neural engine status · Transmission relays · Database metrics</div>
    </div>
    """, unsafe_allow_html=True)

    db = SessionLocal()
    try:
        tab_status, tab_clients, tab_backup = st.tabs([
            "🔌 Hardware & Relays", "👤 Client Entities", "💾 Vault & Storage"
        ])

        # ── System Status ────────────────────────────────────────────────
        with tab_status:
            st.markdown("### Protocol Telemetry")

            # AI Provider
            ai = get_ai_provider()
            ai_ok = ai is not None

            # Determine which provider is active
            if ai_ok:
                provider_name = type(ai).__name__.replace("Provider", "")
                if provider_name == "Groq":
                    ai_detail = f"GROQ CLOUD · MODEL: {GROQ_MODEL}"
                else:
                    ai_detail = f"OLLAMA LOCAL · HOST: {OLLAMA_HOST} · MODEL: {OLLAMA_MODEL}"
            else:
                if GROQ_API_KEY:
                    ai_detail = f"GROQ KEY SET BUT UNREACHABLE · OLLAMA OFFLINE"
                else:
                    ai_detail = f"NO GROQ KEY · OLLAMA OFFLINE"

            st.markdown(f"""
            <div class="noir-card" style="padding: 1.25rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-family: 'Playfair Display', serif; font-size: 1.2rem; font-weight: 700; color: #F3F3EF;">
                            🤖 Neural Engine (AI Provider)
                        </div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #888888; margin-top: 4px;">
                            MODE: {AI_PROVIDER.upper()} · {ai_detail}
                        </div>
                    </div>
                    <span class="badge-{'high' if ai_ok else 'low'}">{'ONLINE' if ai_ok else 'OFFLINE'}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if not ai_ok:
                st.warning("Neural engine disconnected. Options:\n\n"
                           "**Cloud (Recommended):** Get a free API key from https://console.groq.com and set `GROQ_API_KEY` in your environment.\n\n"
                           "**Local:** Launch Ollama:\n```bash\nollama serve\nollama pull llama3.1\n```")

            # SMTP
            st.markdown(f"""
            <div class="noir-card" style="padding: 1.25rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-family: 'Playfair Display', serif; font-size: 1.2rem; font-weight: 700; color: #F3F3EF;">
                            📧 Outbound SMTP Relay
                        </div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #888888; margin-top: 4px;">
                            HOST: {SMTP_HOST or 'NOT CONFIGURED'} · PORT: {SMTP_PORT}
                        </div>
                    </div>
                    <span class="badge-{'high' if is_smtp_configured() else 'low'}">{'CONFIGURED' if is_smtp_configured() else 'UNSET'}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if not is_smtp_configured():
                st.info("Configure SMTP parameters in `.env` (SMTP_HOST, SMTP_USER, SMTP_PASSWORD).")

            # IMAP
            st.markdown(f"""
            <div class="noir-card" style="padding: 1.25rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-family: 'Playfair Display', serif; font-size: 1.2rem; font-weight: 700; color: #F3F3EF;">
                            📬 Inbound Wire Intercept (IMAP)
                        </div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #888888; margin-top: 4px;">
                            HOST: {IMAP_HOST or 'NOT CONFIGURED'}
                        </div>
                    </div>
                    <span class="badge-{'high' if is_imap_configured() else 'low'}">{'CONFIGURED' if is_imap_configured() else 'UNSET'}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # WhatsApp / SMS
            st.markdown("""
            <div class="noir-card" style="padding: 1.25rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-family: 'Playfair Display', serif; font-size: 1.2rem; font-weight: 700; color: #F3F3EF;">
                            💬 WhatsApp Gateway
                        </div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #888888; margin-top: 4px;">
                            MODE: DIRECT PROTOCOL LAUNCH (WEB/APP)
                        </div>
                    </div>
                    <span class="badge-bone">OPERATIONAL</span>
                </div>
            </div>
            <div class="noir-card" style="padding: 1.25rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-family: 'Playfair Display', serif; font-size: 1.2rem; font-weight: 700; color: #F3F3EF;">
                            📱 SMS Relay Network
                        </div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #888888; margin-top: 4px;">
                            MODE: MANUAL PROTOCOL BUFFER
                        </div>
                    </div>
                    <span class="badge-medium">STANDBY</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Client Management ────────────────────────────────────────────
        with tab_clients:
            st.markdown("### Registered Client Entities")
            clients = db.query(Client).all()

            if clients:
                for client in clients:
                    with st.expander(f"🏢 {client.company_name}"):
                        st.write(f"**Website:** {client.website or 'Not set'}")
                        st.write(f"**Industry:** {client.industry or 'Not set'}")
                        st.write(f"**Services:** {client.services or 'Not set'}")
                        st.write(f"**Target:** {client.target_country or client.country or 'Not set'}")
                        st.write(f"**Tone:** {client.preferred_tone}")
                        st.write(f"**Sender:** {client.sender_name or 'Not set'} ({client.sender_email or 'Not set'})")
                        st.write(f"**Created:** {client.created_at}")

                        if st.button(f"TERMINATE ENTITY: {client.company_name}", key=f"del_client_{client.client_id}"):
                            db.delete(client)
                            db.commit()
                            st.success("Entity removed.")
                            st.rerun()
            else:
                st.info("No client entities configured. Formulate one in Reconnaissance.")

        # ── Database ─────────────────────────────────────────────────────
        with tab_backup:
            st.markdown("### Vault Storage Telemetry")
            lead_count = db.query(Lead).count()
            campaign_count = db.query(Campaign).count()
            message_count = db.query(Message).count()
            reply_count = db.query(Reply).count()

            cols = st.columns(4)
            with cols[0]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{lead_count}</div>
                    <div class="metric-label">VAULT PROSPECTS</div>
                </div>
                """, unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{campaign_count}</div>
                    <div class="metric-label">DEPLOYED CAMPAIGNS</div>
                </div>
                """, unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{message_count}</div>
                    <div class="metric-label">TRANSMISSION LOGS</div>
                </div>
                """, unsafe_allow_html=True)
            with cols[3]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{reply_count}</div>
                    <div class="metric-label">INTERCEPTED REPLIES</div>
                </div>
                """, unsafe_allow_html=True)

    finally:
        db.close()
