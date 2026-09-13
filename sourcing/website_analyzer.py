# sourcing/website_analyzer.py
"""Scrape and analyze a business website."""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from ai.ollama_provider import OllamaProvider
from ai.prompts import BUSINESS_ANALYSIS_PROMPT
from ai.parser import extract_json
from config import OLLAMA_HOST, OLLAMA_MODEL


def fetch_page(url: str, timeout: int = 15) -> str:
    """Fetch a web page and return its text content."""
    if not url.startswith("http"):
        url = "https://" + url
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        return f"[ERROR] Could not fetch {url}: {e}"


def extract_text(html: str, max_chars: int = 8000) -> str:
    """Extract readable text from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    # Remove script and style elements
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    # Collapse whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text[:max_chars]


def extract_contact_info(html: str, base_url: str) -> dict:
    """Extract emails, phones, and social links from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    full_text = soup.get_text()

    # Emails
    emails = list(set(re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", full_text)))

    # Phones
    phones = list(set(re.findall(r"[\+]?[(]?\d{1,4}[)]?[\s.\-]?\d{1,4}[\s.\-]?\d{1,9}", full_text)))
    phones = [p.strip() for p in phones if len(re.sub(r"\D", "", p)) >= 7]

    # Contact page link
    contact_link = None
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].lower()
        text = a_tag.get_text().lower()
        if "contact" in href or "contact" in text:
            contact_link = urljoin(base_url, a_tag["href"])
            break

    # About page link
    about_link = None
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].lower()
        text = a_tag.get_text().lower()
        if "about" in href or "about" in text:
            about_link = urljoin(base_url, a_tag["href"])
            break

    return {
        "emails": emails[:5],  # Limit
        "phones": phones[:5],
        "contact_page": contact_link,
        "about_page": about_link,
    }


def analyze_business(url: str) -> dict:
    """Analyze a business website: scrape content, extract contacts, run AI analysis.

    Returns a dict with business profile fields or an error.
    """
    html = fetch_page(url)
    if html.startswith("[ERROR]"):
        return {"error": html}

    text_content = extract_text(html)
    contacts = extract_contact_info(html, url)

    # Build AI prompt
    prompt = BUSINESS_ANALYSIS_PROMPT.format(url=url, content=text_content)

    ai = OllamaProvider(host=OLLAMA_HOST, model=OLLAMA_MODEL)
    if not ai.is_available():
        return {
            "error": "⚠ AI service unavailable. Ollama is not running. Start Ollama and try again.",
            "contacts": contacts,
            "raw_text": text_content[:2000],
        }

    raw_response = ai.generate(prompt)
    parsed = extract_json(raw_response)

    if parsed and "error" not in parsed:
        parsed["contacts"] = contacts
        parsed["source_url"] = url
        return parsed

    return {
        "error": "Could not parse AI response.",
        "raw_response": raw_response,
        "contacts": contacts,
    }
