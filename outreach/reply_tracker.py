# outreach/reply_tracker.py
"""IMAP-based reply tracking for Nexomate."""

import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.models import Reply, Lead, Message
from ai.ollama_provider import OllamaProvider
from ai.prompts import REPLY_CLASSIFICATION_PROMPT
from ai.parser import extract_json
from config import IMAP_HOST, IMAP_PORT, IMAP_USER, IMAP_PASSWORD, OLLAMA_HOST, OLLAMA_MODEL


def is_imap_configured() -> bool:
    """Check if IMAP credentials are configured."""
    return bool(IMAP_HOST and IMAP_USER and IMAP_PASSWORD)


def decode_subject(subject) -> str:
    """Decode an email subject header."""
    if subject is None:
        return ""
    decoded_parts = decode_header(subject)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(part)
    return " ".join(result)


def get_email_body(msg) -> str:
    """Extract plain text body from an email message."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    return part.get_payload(decode=True).decode(errors="replace")
                except Exception:
                    continue
    else:
        try:
            return msg.get_payload(decode=True).decode(errors="replace")
        except Exception:
            return ""
    return ""


def check_for_replies(db: Session, days_back: int = 7) -> list[dict]:
    """Check the IMAP inbox for replies to outreach emails.

    Returns list of dicts with reply info and matched lead_id.
    """
    if not is_imap_configured():
        return []

    found_replies = []

    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(IMAP_USER, IMAP_PASSWORD)
        mail.select("INBOX")

        # Search for recent unseen emails
        since_date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
        status, messages = mail.search(None, f'(SINCE "{since_date}" UNSEEN)')

        if status != "OK":
            mail.logout()
            return []

        for num in messages[0].split():
            status, data = mail.fetch(num, "(RFC822)")
            if status != "OK":
                continue

            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            sender = msg.get("From", "")
            subject = decode_subject(msg.get("Subject", ""))
            body = get_email_body(msg)
            message_id = msg.get("Message-ID", "")
            in_reply_to = msg.get("In-Reply-To", "")
            date_str = msg.get("Date", "")

            # Extract sender email
            sender_email = ""
            if "<" in sender and ">" in sender:
                sender_email = sender.split("<")[1].split(">")[0].strip().lower()
            else:
                sender_email = sender.strip().lower()

            # Try to match to a lead
            lead = db.query(Lead).filter(
                Lead.email.ilike(f"%{sender_email}%")
            ).first()

            if lead:
                # Check if we already recorded this reply
                existing = db.query(Reply).filter(
                    Reply.lead_id == lead.lead_id,
                    Reply.sender == sender_email,
                    Reply.subject == subject,
                ).first()

                if not existing:
                    # Find the original message
                    original_msg = None
                    if in_reply_to:
                        original_msg = db.query(Message).filter(
                            Message.smtp_message_id == in_reply_to
                        ).first()

                    reply_record = Reply(
                        lead_id=lead.lead_id,
                        message_id=original_msg.message_id if original_msg else None,
                        sender=sender_email,
                        subject=subject,
                        body=body[:5000],
                        received_at=datetime.now(),
                    )
                    db.add(reply_record)

                    # Update lead status
                    lead.lead_status = "REPLIED"
                    lead.email_status = "REPLIED"
                    db.commit()
                    db.refresh(reply_record)

                    found_replies.append({
                        "reply_id": reply_record.reply_id,
                        "lead_id": lead.lead_id,
                        "lead_name": lead.full_name,
                        "lead_company": lead.company,
                        "sender": sender_email,
                        "subject": subject,
                        "body_preview": body[:200],
                    })

        mail.logout()
    except Exception as e:
        return [{"error": f"IMAP error: {str(e)}"}]

    return found_replies


def classify_reply(reply: Reply, context: str = "") -> dict:
    """Use AI to classify a reply's intent."""
    ai = OllamaProvider(host=OLLAMA_HOST, model=OLLAMA_MODEL)
    if not ai.is_available():
        return {"classification": "UNKNOWN", "confidence": 0, "summary": "AI unavailable"}

    prompt = REPLY_CLASSIFICATION_PROMPT.format(
        context=context,
        sender=reply.sender or "",
        subject=reply.subject or "",
        body=reply.body or "",
    )
    raw = ai.generate(prompt)
    parsed = extract_json(raw)

    if parsed and "classification" in parsed:
        return parsed

    return {"classification": "UNKNOWN", "confidence": 0, "summary": "Could not classify"}
