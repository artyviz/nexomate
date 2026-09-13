# outreach/sms_sender.py
"""SMS adapter for Nexomate.

For MVP, generates messages and provides copy functionality.
A paid SMS gateway (Twilio, etc.) can be added later.
"""


def send_sms(phone: str, message: str) -> dict:
    """Attempt to send an SMS.

    Since no free SMS provider is configured by default,
    this returns Manual status with the message for copying.
    """
    if not phone:
        return {
            "status": "Manual",
            "error": "No phone number available.",
            "message": message,
        }

    # TODO: Add SMS gateway integration (Twilio, MessageBird, etc.)
    # When configured, this function would actually send the SMS.

    return {
        "status": "Manual",
        "message": message,
        "phone": phone,
        "note": "SMS provider not configured. Copy the message and send manually.",
    }
