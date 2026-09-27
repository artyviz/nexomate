# ai/provider_factory.py
"""AI provider factory — smart fallback chain for Nexomate.

Priority order:
  1. Groq  (if GROQ_API_KEY is set) — works everywhere, free cloud API
  2. Ollama (if running locally)    — works on local dev / VPS
  3. None                           — callers handle template fallback
"""

from ai.base import AIProvider


def get_ai_provider() -> AIProvider | None:
    """Return the best available AI provider, or None if nothing is available.

    The returned provider is guaranteed to have is_available() == True.
    """
    from config import AI_PROVIDER, GROQ_API_KEY, GROQ_MODEL, OLLAMA_HOST, OLLAMA_MODEL

    # Explicit provider selection
    if AI_PROVIDER == "groq":
        if GROQ_API_KEY:
            from ai.groq_provider import GroqProvider
            provider = GroqProvider(api_key=GROQ_API_KEY, model=GROQ_MODEL)
            if provider.is_available():
                return provider
        return None

    if AI_PROVIDER == "ollama":
        from ai.ollama_provider import OllamaProvider
        provider = OllamaProvider(host=OLLAMA_HOST, model=OLLAMA_MODEL)
        if provider.is_available():
            return provider
        return None

    # Auto mode — try Groq first, then Ollama
    if GROQ_API_KEY:
        from ai.groq_provider import GroqProvider
        provider = GroqProvider(api_key=GROQ_API_KEY, model=GROQ_MODEL)
        if provider.is_available():
            return provider

    from ai.ollama_provider import OllamaProvider
    provider = OllamaProvider(host=OLLAMA_HOST, model=OLLAMA_MODEL)
    if provider.is_available():
        return provider

    return None
