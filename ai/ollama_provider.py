# ai/ollama_provider.py
"""Ollama-based AI provider for Nexomate."""

import json
import requests
from ai.base import AIProvider


class OllamaProvider(AIProvider):
    """AI provider that communicates with a local Ollama instance."""

    def __init__(self, host: str = "http://localhost:11434", model: str = "llama2"):
        self.host = host.rstrip("/")
        self.model = model

    def is_available(self) -> bool:
        """Check whether Ollama is running."""
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Send a prompt to the local Ollama model and return the response text."""
        url = f"{self.host}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            resp = requests.post(url, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "")
        except requests.ConnectionError:
            return "[ERROR] Ollama is not running. Please start Ollama and try again."
        except requests.Timeout:
            return "[ERROR] Ollama request timed out. The model may be loading — try again."
        except Exception as e:
            return f"[ERROR] Ollama error: {str(e)}"

    def generate_json(self, prompt: str, system_prompt: str = "") -> dict:
        """Generate a response and attempt to parse it as JSON."""
        raw = self.generate(prompt, system_prompt)
        if raw.startswith("[ERROR]"):
            return {"error": raw}
        # Try to extract JSON from the response
        try:
            # Sometimes the model wraps JSON in markdown code fences
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                # Remove first and last lines (code fences)
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
