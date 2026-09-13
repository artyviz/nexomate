# outreach/message_generator.py
"""AI-powered outreach message generator with offline fallback templates."""

from ai.ollama_provider import OllamaProvider
from ai.prompts import EMAIL_GENERATION_PROMPT, WHATSAPP_MESSAGE_PROMPT, SMS_MESSAGE_PROMPT
from ai.parser import extract_json
from config import OLLAMA_HOST, OLLAMA_MODEL


def generate_fallback_email(lead: dict, client: dict) -> dict:
    """Generate high-quality outreach email from deterministic templates when AI is unavailable."""
    lead_name = lead.get("full_name") or lead.get("first_name") or "there"
    lead_company = lead.get("company") or "your company"
    sender_name = client.get("sender_name") or "The Team"
    sender_company = client.get("company_name") or "our team"
    services = client.get("services") or "growth and automation solutions"
    value_prop = client.get("value_proposition") or "help businesses scale efficiently"
    tone = (client.get("preferred_tone") or "Professional").capitalize()

    if tone == "Friendly":
        subject = f"Quick hello from {sender_name} / {lead_company}"
        body = (
            f"Hi {lead_name},\n\n"
            f"Hope your week is off to a great start! I've been following {lead_company} "
            f"and really admire the work you're doing in your space.\n\n"
            f"At {sender_company}, we specialize in {services}. We typically {value_prop}, "
            f"and I thought this could be very relevant to what you're working on right now.\n\n"
            f"Would you be open to a quick 10-minute chat sometime this week?\n\n"
            f"Warm regards,\n\n"
            f"{sender_name}\n"
            f"{sender_company}"
        )
    elif tone == "Direct":
        subject = f"Question regarding {lead_company}"
        body = (
            f"Hi {lead_name},\n\n"
            f"I'm reaching out from {sender_company}. We provide {services} to {value_prop}.\n\n"
            f"We recently worked with similar organizations to streamline their operations "
            f"and wanted to see if exploring this makes sense for {lead_company}.\n\n"
            f"Do you have 5 minutes for a brief call on Thursday?\n\n"
            f"Best,\n\n"
            f"{sender_name}\n"
            f"{sender_company}"
        )
    elif tone == "Casual":
        subject = f"{lead_company} + {sender_company}?"
        body = (
            f"Hey {lead_name},\n\n"
            f"Came across {lead_company} and wanted to drop a quick line.\n\n"
            f"We build {services} over at {sender_company}—primarily focused on helping teams {value_prop}.\n\n"
            f"Think this could be helpful for you guys? Happy to share a quick walkthrough if you're interested.\n\n"
            f"Cheers,\n\n"
            f"{sender_name}"
        )
    else:  # Professional (Default)
        subject = f"Partnership opportunity: {sender_company} & {lead_company}"
        body = (
            f"Dear {lead_name},\n\n"
            f"I hope this message finds you well. I am contacting you on behalf of {sender_company}.\n\n"
            f"We specialize in {services}, helping organizations like {lead_company} {value_prop}.\n\n"
            f"Given your focus in the industry, I believe an exploratory conversation would be valuable. "
            f"Are you available for a brief introductory call next week?\n\n"
            f"Sincerely,\n\n"
            f"{sender_name}\n"
            f"{sender_company}"
        )

    return {
        "subject": subject,
        "body": body,
        "method": "template",
        "note": "Generated using built-in template fallback (Ollama offline).",
    }


def generate_email(lead: dict, client: dict) -> dict:
    """Generate a personalized email for a lead.

    Tries AI first; falls back to deterministic template if Ollama is offline.
    """
    ai = OllamaProvider(host=OLLAMA_HOST, model=OLLAMA_MODEL)
    if not ai.is_available():
        return generate_fallback_email(lead, client)

    prompt = EMAIL_GENERATION_PROMPT.format(
        sender_company=client.get("company_name", ""),
        sender_services=client.get("services", ""),
        sender_value_prop=client.get("value_proposition", ""),
        lead_name=lead.get("full_name") or lead.get("first_name", ""),
        lead_company=lead.get("company", ""),
        lead_title=lead.get("job_title", ""),
        lead_location=f"{lead.get('city', '')} {lead.get('state', '')}".strip(),
        lead_industry=lead.get("industry", ""),
        lead_notes=lead.get("notes", ""),
        pain_points=lead.get("pain_points", ""),
        tone=client.get("preferred_tone", "Professional"),
        sender_name=client.get("sender_name", ""),
    )

    try:
        raw = ai.generate(prompt)
        parsed = extract_json(raw)

        if parsed and "subject" in parsed:
            parsed["method"] = "ai"
            return parsed

        if raw and not raw.startswith("[ERROR]"):
            return {
                "subject": f"Quick question about {lead.get('company', 'your business')}",
                "body": raw,
                "method": "ai_raw",
                "note": "AI response was not structured JSON — raw text used.",
            }
    except Exception:
        pass

    return generate_fallback_email(lead, client)


def generate_whatsapp_message(lead: dict, client: dict) -> dict:
    """Generate a short WhatsApp message with fallback."""
    lead_name = lead.get("full_name") or lead.get("first_name") or "there"
    lead_company = lead.get("company") or "your company"
    sender_name = client.get("sender_name") or "our team"
    sender_company = client.get("company_name") or "Nexomate"
    value_prop = client.get("value_proposition") or "streamline operations"

    fallback_text = (
        f"Hi {lead_name}, this is {sender_name} from {sender_company}. "
        f"I came across {lead_company} and loved what you're building! "
        f"We help teams {value_prop}. Would you be open to a brief chat this week?"
    )

    ai = OllamaProvider(host=OLLAMA_HOST, model=OLLAMA_MODEL)
    if not ai.is_available():
        return {"message": fallback_text, "method": "template"}

    prompt = WHATSAPP_MESSAGE_PROMPT.format(
        sender_company=sender_company,
        lead_name=lead_name,
        lead_company=lead_company,
        value_prop=value_prop,
        tone=client.get("preferred_tone", "Friendly"),
    )

    try:
        raw = ai.generate(prompt)
        parsed = extract_json(raw)
        if parsed and "message" in parsed:
            parsed["method"] = "ai"
            return parsed
        if raw and not raw.startswith("[ERROR]"):
            return {"message": raw, "method": "ai"}
    except Exception:
        pass

    return {"message": fallback_text, "method": "template"}


def generate_sms_message(lead: dict, client: dict) -> dict:
    """Generate a short SMS message with fallback."""
    lead_name = lead.get("full_name") or lead.get("first_name") or "there"
    sender_company = client.get("company_name") or "Nexomate"
    value_prop = client.get("value_proposition") or "grow revenue"

    fallback_text = (
        f"Hi {lead_name}, {sender_company} here. We help companies {value_prop}. "
        f"Interested in a quick 5-min intro? Reply YES to connect."
    )

    ai = OllamaProvider(host=OLLAMA_HOST, model=OLLAMA_MODEL)
    if not ai.is_available():
        return {"message": fallback_text, "method": "template"}

    prompt = SMS_MESSAGE_PROMPT.format(
        sender_company=sender_company,
        lead_name=lead_name,
        value_prop=value_prop,
    )

    try:
        raw = ai.generate(prompt)
        parsed = extract_json(raw)
        if parsed and "message" in parsed:
            parsed["method"] = "ai"
            return parsed
        if raw and not raw.startswith("[ERROR]"):
            return {"message": raw, "method": "ai"}
    except Exception:
        pass

    return {"message": fallback_text, "method": "template"}
