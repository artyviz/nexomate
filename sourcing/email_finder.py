# sourcing/email_finder.py
"""Attempt to find email addresses from web pages."""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def find_emails_on_page(url: str) -> list[str]:
    """Scrape a URL and return any email addresses found."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    emails = set()

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        text = resp.text
        found = re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
        emails.update(found)
    except Exception:
        pass

    # Filter out common false positives
    ignore = {"example.com", "sentry.io", "wixpress.com", "w3.org", "schema.org"}
    filtered = [e for e in emails if not any(d in e.lower() for d in ignore)]
    return filtered[:5]


def find_emails_from_contact_page(base_url: str) -> list[str]:
    """Try to find a /contact page and extract emails from it."""
    common_paths = ["/contact", "/contact-us", "/about", "/about-us"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    for path in common_paths:
        try:
            full_url = urljoin(base_url, path)
            resp = requests.get(full_url, headers=headers, timeout=10)
            if resp.status_code == 200:
                found = re.findall(
                    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
                    resp.text,
                )
                if found:
                    return list(set(found))[:5]
        except Exception:
            continue

    return []
