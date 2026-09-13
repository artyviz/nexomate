# scoring/lead_scorer.py
"""Configurable lead scoring engine for Nexomate."""

from ai.ollama_provider import OllamaProvider
from ai.prompts import LEAD_SCORING_PROMPT
from ai.parser import extract_json
from config import OLLAMA_HOST, OLLAMA_MODEL


# Default scoring weights (editable via settings)
DEFAULT_WEIGHTS = {
    "icp_match": 25,
    "location_match": 15,
    "industry_match": 15,
    "job_title_match": 15,
    "company_size_match": 10,
    "buying_signals": 10,
    "data_quality": 10,
}


def score_level(score: float) -> str:
    """Convert a numeric score to HIGH/MEDIUM/LOW."""
    if score >= 75:
        return "HIGH"
    elif score >= 50:
        return "MEDIUM"
    else:
        return "LOW"


def rule_based_score(lead: dict, icp: dict, weights: dict | None = None) -> dict:
    """Score a lead using rule-based matching (no AI required).

    Returns:
        dict with score, level, reason, breakdown.
    """
    w = weights or DEFAULT_WEIGHTS
    breakdown = {}
    total = 0

    # ICP match — check if lead matches target customer description
    icp_target = (icp.get("target_customer") or "").lower()
    lead_info = f"{lead.get('company', '')} {lead.get('job_title', '')} {lead.get('industry', '')}".lower()
    if icp_target:
        overlap = sum(1 for word in icp_target.split() if word in lead_info)
        ratio = min(overlap / max(len(icp_target.split()), 1), 1.0)
        breakdown["icp_match"] = round(ratio * w["icp_match"])
    else:
        breakdown["icp_match"] = 0
    total += breakdown["icp_match"]

    # Location match
    icp_loc = (icp.get("location") or "").lower()
    lead_loc = f"{lead.get('city', '')} {lead.get('state', '')} {lead.get('country', '')}".lower()
    if icp_loc and any(part in lead_loc for part in icp_loc.split(",")):
        breakdown["location_match"] = w["location_match"]
    elif icp_loc and any(part.strip() in lead_loc for part in icp_loc.split()):
        breakdown["location_match"] = round(w["location_match"] * 0.6)
    else:
        breakdown["location_match"] = 0
    total += breakdown["location_match"]

    # Industry match
    icp_ind = (icp.get("industry") or "").lower()
    lead_ind = (lead.get("industry") or "").lower()
    if icp_ind and lead_ind and (icp_ind in lead_ind or lead_ind in icp_ind):
        breakdown["industry_match"] = w["industry_match"]
    elif icp_ind and lead_ind:
        breakdown["industry_match"] = round(w["industry_match"] * 0.3)
    else:
        breakdown["industry_match"] = 0
    total += breakdown["industry_match"]

    # Job title match
    icp_titles = icp.get("job_titles", [])
    if isinstance(icp_titles, str):
        icp_titles = [t.strip() for t in icp_titles.split(",")]
    lead_title = (lead.get("job_title") or "").lower()
    if lead_title and any(t.lower() in lead_title for t in icp_titles):
        breakdown["job_title_match"] = w["job_title_match"]
    elif lead_title:
        breakdown["job_title_match"] = round(w["job_title_match"] * 0.3)
    else:
        breakdown["job_title_match"] = 0
    total += breakdown["job_title_match"]

    # Company size match
    breakdown["company_size_match"] = round(w["company_size_match"] * 0.5) if lead.get("company_size") else 0
    total += breakdown["company_size_match"]

    # Buying signals
    icp_signals = icp.get("buying_signals", [])
    if isinstance(icp_signals, str):
        icp_signals = [s.strip() for s in icp_signals.split(",")]
    lead_signals = (lead.get("buying_signals") or lead.get("notes") or "").lower()
    if lead_signals and any(s.lower() in lead_signals for s in icp_signals):
        breakdown["buying_signals"] = w["buying_signals"]
    else:
        breakdown["buying_signals"] = 0
    total += breakdown["buying_signals"]

    # Data quality — bonus for having email/phone
    dq = 0
    if lead.get("email") and lead["email"] != "Not Found":
        dq += 5
    if lead.get("phone") and lead["phone"] != "Not Found":
        dq += 3
    if lead.get("full_name") and lead["full_name"] != "Not Found":
        dq += 2
    breakdown["data_quality"] = min(dq, w["data_quality"])
    total += breakdown["data_quality"]

    level = score_level(total)
    reason_parts = []
    if breakdown["icp_match"] > w["icp_match"] * 0.5:
        reason_parts.append("strong ICP match")
    if breakdown["location_match"] > 0:
        reason_parts.append("location match")
    if breakdown["industry_match"] > 0:
        reason_parts.append("industry relevance")
    if breakdown["job_title_match"] > 0:
        reason_parts.append("relevant job title")
    reason = f"{level} priority lead with " + ", ".join(reason_parts) if reason_parts else f"{level} priority lead"

    return {
        "score": total,
        "level": level,
        "reason": reason,
        "breakdown": breakdown,
    }


def ai_score_lead(lead: dict, icp: dict) -> dict:
    """Score a lead using AI for richer context analysis.

    Falls back to rule-based scoring if AI is unavailable.
    """
    ai = OllamaProvider(host=OLLAMA_HOST, model=OLLAMA_MODEL)
    if not ai.is_available():
        result = rule_based_score(lead, icp)
        result["method"] = "rule_based"
        result["note"] = "AI unavailable — used rule-based scoring."
        return result

    prompt = LEAD_SCORING_PROMPT.format(
        icp_target=icp.get("target_customer", ""),
        icp_industry=icp.get("industry", ""),
        icp_location=icp.get("location", ""),
        icp_company_size=icp.get("company_size", ""),
        icp_job_titles=", ".join(icp.get("job_titles", [])) if isinstance(icp.get("job_titles"), list) else icp.get("job_titles", ""),
        icp_buying_signals=", ".join(icp.get("buying_signals", [])) if isinstance(icp.get("buying_signals"), list) else icp.get("buying_signals", ""),
        icp_pain_points=", ".join(icp.get("pain_points", [])) if isinstance(icp.get("pain_points"), list) else icp.get("pain_points", ""),
        lead_name=lead.get("full_name", "Not Found"),
        lead_company=lead.get("company", "Not Found"),
        lead_title=lead.get("job_title", "Not Found"),
        lead_industry=lead.get("industry", "Not Found"),
        lead_location=f"{lead.get('city', '')} {lead.get('state', '')} {lead.get('country', '')}".strip() or "Not Found",
        lead_company_size=lead.get("company_size", "Not Found"),
        lead_notes=lead.get("notes", ""),
    )

    raw = ai.generate(prompt)
    parsed = extract_json(raw)

    if parsed and "score" in parsed:
        parsed["method"] = "ai"
        if "level" not in parsed:
            parsed["level"] = score_level(parsed["score"])
        return parsed

    # Fallback to rule-based
    result = rule_based_score(lead, icp)
    result["method"] = "rule_based"
    result["note"] = "AI response could not be parsed — used rule-based scoring."
    return result
