# outreach/email_sender.py
"""SMTP email sender for Nexomate — single and batch sending."""

import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_BATCH_DELAY_SECONDS


def is_smtp_configured() -> bool:
    """Check if SMTP credentials are configured."""
    return bool(SMTP_HOST and SMTP_USER and SMTP_PASSWORD)


def _fill_template(template: str, lead: dict) -> str:
    """Replace template variables with lead data.

    Supported variables: {first_name}, {last_name}, {full_name}, {company},
    {job_title}, {email}, {city}, {state}, {country}, {industry}
    """
    replacements = {
        "first_name": lead.get("first_name") or (lead.get("full_name", "").split()[0] if lead.get("full_name") else "there"),
        "last_name": lead.get("last_name") or (lead.get("full_name", "").split()[-1] if lead.get("full_name") and " " in lead.get("full_name", "") else ""),
        "full_name": lead.get("full_name") or "there",
        "company": lead.get("company") or "your company",
        "job_title": lead.get("job_title") or "your role",
        "email": lead.get("email") or "",
        "city": lead.get("city") or "",
        "state": lead.get("state") or "",
        "country": lead.get("country") or "",
        "industry": lead.get("industry") or "your industry",
    }

    result = template
    for key, value in replacements.items():
        result = result.replace("{" + key + "}", str(value))
    return result


def send_email(
    to_email: str,
    subject: str,
    body: str,
    sender_name: str = "",
    sender_email: str = "",
) -> dict:
    """Send an email via SMTP.

    Returns dict with status, message_id, error (if any).
    """
    if not is_smtp_configured():
        return {
            "status": "FAILED",
            "error": "SMTP not configured. Set SMTP_HOST, SMTP_USER, and SMTP_PASSWORD in .env",
        }

    from_email = sender_email or SMTP_USER
    from_name = sender_name or from_email

    msg = MIMEMultipart("alternative")
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = to_email
    msg["Subject"] = subject

    # Plain text part
    msg.attach(MIMEText(body, "plain"))

    # Simple HTML part
    html_body = body.replace("\n", "<br>")
    msg.attach(MIMEText(f"<html><body><p>{html_body}</p></body></html>", "html"))

    try:
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
            server.starttls()

        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(from_email, [to_email], msg.as_string())
        message_id = msg.get("Message-ID", "")
        server.quit()

        return {
            "status": "SENT",
            "message_id": message_id,
            "sent_at": datetime.now().isoformat(),
        }
    except smtplib.SMTPAuthenticationError:
        return {
            "status": "FAILED",
            "error": "SMTP authentication failed. Check your email/password in .env",
        }
    except smtplib.SMTPConnectError:
        return {
            "status": "FAILED",
            "error": f"Could not connect to SMTP server {SMTP_HOST}:{SMTP_PORT}",
        }
    except Exception as e:
        return {
            "status": "FAILED",
            "error": f"Email sending error: {str(e)}",
        }


def send_batch_emails(
    leads: list[dict],
    subject_template: str,
    body_template: str,
    sender_name: str = "",
    sender_email: str = "",
    delay: int | None = None,
    progress_callback=None,
) -> dict:
    """Send batch emails to multiple leads with template variable substitution.

    Args:
        leads: List of lead dicts with at least 'email' key. Each dict can contain
               first_name, last_name, full_name, company, job_title, etc.
        subject_template: Email subject with {variable} placeholders.
        body_template: Email body with {variable} placeholders.
        sender_name: Display name for the sender.
        sender_email: Sender email address.
        delay: Seconds to wait between sends. Defaults to EMAIL_BATCH_DELAY_SECONDS.
        progress_callback: Optional callable(sent, failed, total, current_lead) for progress.

    Returns:
        dict with total, sent, failed, results (list of per-lead results).
    """
    if not is_smtp_configured():
        return {
            "total": len(leads),
            "sent": 0,
            "failed": len(leads),
            "error": "SMTP not configured",
            "results": [],
        }

    if delay is None:
        delay = EMAIL_BATCH_DELAY_SECONDS

    from_email = sender_email or SMTP_USER
    from_name = sender_name or from_email

    results = []
    sent_count = 0
    failed_count = 0

    # Open a single SMTP connection for the batch
    try:
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
            server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
    except Exception as e:
        return {
            "total": len(leads),
            "sent": 0,
            "failed": len(leads),
            "error": f"SMTP connection failed: {str(e)}",
            "results": [],
        }

    for i, lead in enumerate(leads):
        to_email = lead.get("email", "")
        if not to_email or to_email in ("—", "Not Found", ""):
            results.append({
                "lead": lead.get("full_name") or lead.get("company", "Unknown"),
                "email": to_email,
                "status": "SKIPPED",
                "error": "No valid email address",
            })
            failed_count += 1
            continue

        # Fill template variables
        subject = _fill_template(subject_template, lead)
        body = _fill_template(body_template, lead)

        msg = MIMEMultipart("alternative")
        msg["From"] = f"{from_name} <{from_email}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        html_body = body.replace("\n", "<br>")
        msg.attach(MIMEText(f"<html><body><p>{html_body}</p></body></html>", "html"))

        try:
            server.sendmail(from_email, [to_email], msg.as_string())
            message_id = msg.get("Message-ID", "")
            results.append({
                "lead": lead.get("full_name") or lead.get("company", "Unknown"),
                "email": to_email,
                "status": "SENT",
                "message_id": message_id,
                "sent_at": datetime.now().isoformat(),
            })
            sent_count += 1
        except Exception as e:
            results.append({
                "lead": lead.get("full_name") or lead.get("company", "Unknown"),
                "email": to_email,
                "status": "FAILED",
                "error": str(e),
            })
            failed_count += 1

            # Try to reconnect if connection was lost
            try:
                server.quit()
            except Exception:
                pass
            try:
                if SMTP_PORT == 465:
                    server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30)
                else:
                    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
                    server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
            except Exception:
                pass

        if progress_callback:
            progress_callback(sent_count, failed_count, len(leads), lead)

        # Delay between sends to avoid rate limits
        if delay > 0 and i < len(leads) - 1:
            time.sleep(delay)

    try:
        server.quit()
    except Exception:
        pass

    return {
        "total": len(leads),
        "sent": sent_count,
        "failed": failed_count,
        "results": results,
    }
