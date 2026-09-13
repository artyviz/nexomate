# sourcing/prospect_finder.py
"""Discover prospects by scraping search results and extracting business info."""

import time
from sourcing.search_engine import search_duckduckgo, generate_search_queries
from sourcing.website_analyzer import fetch_page, extract_text, extract_contact_info
from sourcing.deduplicator import is_duplicate_url


def discover_prospects(icp: dict, max_per_query: int = 5, progress_callback=None) -> list[dict]:
    """Run prospect discovery based on an ICP.

    Args:
        icp: ICP profile dict with industry, location, job_titles, etc.
        max_per_query: Max results to process per search query.
        progress_callback: Optional callable(message: str) for progress updates.

    Returns:
        List of prospect dicts with extracted information.
    """
    queries = generate_search_queries(icp)
    prospects = []
    seen_urls = set()

    for i, query in enumerate(queries):
        if progress_callback:
            progress_callback(f"🔍 Searching: {query} ({i+1}/{len(queries)})")

        results = search_duckduckgo(query, max_results=max_per_query)
        time.sleep(1)  # Polite delay

        for result in results:
            url = result.get("url", "")
            if not url or is_duplicate_url(url, seen_urls):
                continue
            seen_urls.add(url)

            prospect = {
                "company": result.get("title", "Not Found"),
                "website": url,
                "source": "Web Search",
                "source_url": url,
                "source_type": "web_search",
                "search_query": query,
                "snippet": result.get("snippet", ""),
            }

            # Try to extract contact information from the page
            try:
                if progress_callback:
                    progress_callback(f"  📄 Analyzing: {url[:60]}...")
                html = fetch_page(url)
                if not html.startswith("[ERROR]"):
                    contacts = extract_contact_info(html, url)
                    prospect["emails"] = contacts.get("emails", [])
                    prospect["phones"] = contacts.get("phones", [])
                    prospect["contact_page"] = contacts.get("contact_page")

                    # Try to get location from page text
                    text = extract_text(html, max_chars=2000)
                    prospect["page_text_preview"] = text[:500]
                time.sleep(0.5)  # Polite delay between page fetches
            except Exception:
                prospect["emails"] = []
                prospect["phones"] = []

            prospects.append(prospect)

    return prospects
