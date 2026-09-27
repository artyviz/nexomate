# ai/groq_provider.py
"""Groq cloud AI provider for Nexomate — free Llama 3.1 API."""

import json
import requests
from ai.base import AIProvider


class GroqProvider(AIProvider):
    """AI provider that uses the Groq cloud API (free tier: 14,400 req/day)."""

    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant"):
        self.api_key = api_key
        self.model = model

    def is_available(self) -> bool:
        """Check whether the Groq API is reachable and the key is valid."""
        try:
            resp = requests.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )
            return resp.status_code == 200
        except Exception:
            return False

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Send a prompt to Groq and return the response text."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            resp = requests.post(
                self.API_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2048,
                },
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except requests.ConnectionError:
            return "[ERROR] Cannot reach Groq API. Check your internet connection."
        except requests.Timeout:
            return "[ERROR] Groq API request timed out. Try again."
        except requests.HTTPError as e:
            if resp.status_code == 401:
                return "[ERROR] Invalid Groq API key. Check GROQ_API_KEY in your .env file."
            if resp.status_code == 429:
                return "[ERROR] Groq rate limit exceeded. Wait a moment and try again."
            return f"[ERROR] Groq API error ({resp.status_code}): {str(e)}"
        except Exception as e:
            return f"[ERROR] Groq error: {str(e)}"

    def generate_json(self, prompt: str, system_prompt: str = "") -> dict:
        """Generate a response and attempt to parse it as JSON."""
        raw = self.generate(prompt, system_prompt)
        if raw.startswith("[ERROR]"):
            return {"error": raw}
        try:
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                json_lines = []
                inside = False
                for line in lines:
                    if line.strip().startswith("```") and not inside:
                        inside = True
                        continue
                    elif line.strip() == "```" and inside:
                        break
                    elif inside:
                        json_lines.append(line)
                cleaned = "\n".join(json_lines)
            return json.loads(cleaned, strict=False)
        except (json.JSONDecodeError, TypeError):
            return {"raw_response": raw, "parse_error": "Could not parse AI response as JSON"}
