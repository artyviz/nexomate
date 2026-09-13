# sourcing/deduplicator.py
"""Lead deduplication utilities."""

from urllib.parse import urlparse


def normalize_url(url: str) -> str:
    """Normalize a URL for comparison."""
    if not url:
        return ""
    parsed = urlparse(url if "://" in url else f"https://{url}")
    domain = parsed.netloc.lower().replace("www.", "")
    path = parsed.path.rstrip("/").lower()
    return f"{domain}{path}"


def is_duplicate_url(url: str, seen_urls: set) -> bool:
    """Check if a URL is already in the seen set (normalized)."""
    norm = normalize_url(url)
    return norm in {normalize_url(u) for u in seen_urls}


def normalize_email(email) -> str:
    """Normalize an email for comparison."""
    if not email or not isinstance(email, str):
        return ""
    return email.strip().lower()


def normalize_name(name) -> str:
    """Normalize a name for comparison."""
    if not name or not isinstance(name, str):
        return ""
    return " ".join(name.strip().lower().split())


def is_duplicate_lead(lead: dict, existing_leads: list[dict]) -> bool:
    """Check if a lead is a duplicate of any existing lead.

    Duplicate detection uses combinations of:
    - email
    - phone
    - company + name
    - company + email
    """
    lead_email = normalize_email(lead.get("email"))
    lead_phone = str(lead.get("phone") or "").strip()
    lead_name = normalize_name(lead.get("full_name") or lead.get("company"))
    lead_company = normalize_name(lead.get("company"))

    for existing in existing_leads:
        ex_email = normalize_email(existing.get("email"))
        ex_phone = str(existing.get("phone") or "").strip()
        ex_name = normalize_name(existing.get("full_name") or existing.get("company"))
        ex_company = normalize_name(existing.get("company"))

        # Match by email
        if lead_email and ex_email and lead_email == ex_email:
            return True

        # Match by phone
        if lead_phone and ex_phone and lead_phone == ex_phone and len(lead_phone) >= 7:
            return True

        # Match by company + name
        if lead_company and ex_company and lead_name and ex_name:
            if lead_company == ex_company and lead_name == ex_name:
                return True

    return False
