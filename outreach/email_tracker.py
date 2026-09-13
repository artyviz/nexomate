# outreach/email_tracker.py
"""Track email sending status in the database."""

from datetime import datetime
from sqlalchemy.orm import Session
from database.models import Message, Lead


def create_email_record(db: Session, lead_id: int, subject: str, body: str,
                        campaign_id: int = None, status: str = "DRAFT") -> Message:
    """Create a message record in the database."""
    msg = Message(
        lead_id=lead_id,
        campaign_id=campaign_id,
        channel="email",
        subject=subject,
        body=body,
        status=status,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def update_email_status(db: Session, message_id: int, status: str,
                        smtp_message_id: str = None, error: str = None):
    """Update the status of a sent email."""
    msg = db.query(Message).filter(Message.message_id == message_id).first()
    if msg:
        msg.status = status
        if smtp_message_id:
            msg.smtp_message_id = smtp_message_id
        if error:
            msg.error_message = error
        if status == "SENT":
            msg.sent_at = datetime.now()
        db.commit()

        # Also update the lead's email_status
        lead = db.query(Lead).filter(Lead.lead_id == msg.lead_id).first()
        if lead:
            lead.email_status = status
            if status in ("SENT", "DELIVERED"):
                lead.lead_status = "CONTACTED"
            db.commit()


def get_messages_for_lead(db: Session, lead_id: int) -> list[Message]:
    """Get all messages for a specific lead."""
    return db.query(Message).filter(Message.lead_id == lead_id).order_by(Message.created_at.desc()).all()


def get_campaign_messages(db: Session, campaign_id: int) -> list[Message]:
    """Get all messages for a campaign."""
    return db.query(Message).filter(Message.campaign_id == campaign_id).order_by(Message.created_at.desc()).all()
