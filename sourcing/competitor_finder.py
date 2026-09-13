# sourcing/competitor_finder.py
"""Find competitors for a business using web search."""

from sourcing.search_engine import search_duckduckgo
from ai.ollama_provider import OllamaProvider
from ai.prompts import COMPETITOR_ANALYSIS_PROMPT
from ai.parser import extract_json
from config import OLLAMA_HOST, OLLAMA_MODEL


def find_competitors(business_name: str, industry: str, services: str, location: str) -> dict:
    """Use AI to generate competitor search strategies, then search the web.

    Returns a dict with competitor_types, search_queries, and results.
    """
    ai = OllamaProvider(host=OLLAMA_HOST, model=OLLAMA_MODEL)

    if not ai.is_available():
        # Fallback: generate basic queries without AI
        queries = [
            f"{industry} companies {location}",
            f"{industry} competitors {location}",
        ]
        results = []
        for q in queries:
            results.extend(search_duckduckgo(q, max_results=5))
        return {
            "competitor_types": [],
            "search_queries": queries,
            "results": results,
            "note": "AI unavailable — used basic search.",
        }

    prompt = COMPETITOR_ANALYSIS_PROMPT.format(
        business_name=business_name,
        industry=industry,
        services=services,
        location=location,
    )
    raw = ai.generate(prompt)
    parsed = extract_json(raw)

    queries = []
    if parsed and "search_queries" in parsed:
        queries = parsed["search_queries"]
    else:
        queries = [f"{industry} competitors {location}"]

    results = []
    for q in queries[:5]:
        results.extend(search_duckduckgo(q, max_results=5))

    return {
        "competitor_types": parsed.get("competitor_types", []) if parsed else [],
        "search_queries": queries,
        "results": results,
    }
