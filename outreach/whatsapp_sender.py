# outreach/whatsapp_sender.py
"""WhatsApp adapter for Nexomate.

For MVP, this generates messages and provides copy/open actions.
Browser automation could be added in the future but is clearly
isolated here.
"""

import webbrowser
from urllib.parse import quote


def format_whatsapp_url(phone: str, message: str) -> str:
    """Generate a WhatsApp Web URL for sending a message."""
    # Clean phone number — digits only
    clean_phone = "".join(c for c in phone if c.isdigit() or c == "+")
    if not clean_phone.startswith("+"):
        clean_phone = "+" + clean_phone
    encoded_msg = quote(message)
    return f"https://wa.me/{clean_phone.lstrip('+')}?text={encoded_msg}"


def open_whatsapp(phone: str, message: str) -> dict:
    """Open WhatsApp Web with a pre-filled message.

    Returns status dict.
    """
    if not phone:
        return {"status": "Manual", "error": "No phone number available."}

    url = format_whatsapp_url(phone, message)
    try:
        webbrowser.open(url)
        return {"status": "Opened", "url": url}
    except Exception as e:
        return {"status": "Manual", "url": url, "error": str(e)}


# TODO: Implement browser automation via selenium/playwright
# This would be isolated here and clearly marked as unofficial automation.
# It is NOT equivalent to the official WhatsApp Business API.
