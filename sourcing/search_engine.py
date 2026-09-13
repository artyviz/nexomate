# sourcing/search_engine.py
"""Web search engine for prospect discovery using DuckDuckGo."""

import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus


def search_duckduckgo(query: str, max_results: int = 10) -> list[dict]:
    """Search DuckDuckGo HTML and extract results.

    Returns a list of dicts with keys: title, url, snippet.
    """
    encoded = quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    results = []

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for item in soup.select(".result"):
            title_el = item.select_one(".result__title a")
            snippet_el = item.select_one(".result__snippet")
            if not title_el:
                continue

            link = title_el.get("href", "")
            # DuckDuckGo sometimes wraps URLs
            if "uddg=" in link:
                match = re.search(r"uddg=([^&]+)", link)
                if match:
                    from urllib.parse import unquote
                    link = unquote(match.group(1))

            results.append({
                "title": title_el.get_text(strip=True),
                "url": link,
                "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
            })
            if len(results) >= max_results:
                break
    except Exception as e:
        results.append({"title": "Search Error", "url": "", "snippet": str(e)})

    return results


def generate_search_queries(icp: dict) -> list[str]:
    """Generate search queries from an ICP profile."""
    queries = []
    industry = icp.get("industry", "")
    location = icp.get("location", "")
    job_titles = icp.get("job_titles", [])
    company_type = icp.get("company_type", "")
    keywords = icp.get("search_keywords", [])

    if isinstance(job_titles, str):
        job_titles = [t.strip() for t in job_titles.split(",")]
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(",")]

    # Generate query combinations
    if industry and location:
        queries.append(f"{industry} companies {location}")
    if company_type and location:
        queries.append(f"{company_type} {location}")
    for title in job_titles[:3]:
        if location:
            queries.append(f"{title} {location}")
    for kw in keywords[:3]:
        if location:
            queries.append(f"{kw} {location}")
        else:
            queries.append(kw)

    return queries[:10]  # Cap at 10 queries
