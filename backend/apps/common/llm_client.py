"""
Thin, provider-agnostic wrapper around the LLM APIs used for:
  - resume parsing / structured extraction
  - technical interview question generation
  - candidate evaluation scoring
  - text embeddings for semantic job matching + RAG retrieval

Swapping providers (Anthropic <-> OpenAI <-> Google) only requires changing
`LLM_PROVIDER` in settings/.env — call sites never touch the SDKs directly.
"""
import json
from django.conf import settings


class LLMClient:
    def __init__(self, provider: str | None = None):
        self.provider = provider or settings.LLM_PROVIDER

    # ---- chat / structured generation ----------------------------------
    def generate_json(self, system: str, prompt: str, max_tokens: int = 2000) -> dict:
        """Call the LLM and parse a JSON object from its response.

        Raises ValueError if the response cannot be parsed as JSON so callers
        can decide whether to retry or fall back.
        """
        raw_text = self._complete(system=system, prompt=prompt, max_tokens=max_tokens)
        cleaned = raw_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(f"LLM did not return valid JSON: {exc}\nRaw: {raw_text[:500]}") from exc

    def _complete(self, system: str, prompt: str, max_tokens: int = 2000) -> str:
        if self.provider == "anthropic":
            return self._complete_anthropic(system, prompt, max_tokens)
        if self.provider == "openai":
            return self._complete_openai(system, prompt, max_tokens)
        if self.provider == "google":
            return self._complete_google(system, prompt, max_tokens)
        raise ValueError(f"Unknown LLM_PROVIDER: {self.provider}")

    def _complete_anthropic(self, system: str, prompt: str, max_tokens: int) -> str:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if block.type == "text")

    def _complete_openai(self, system: str, prompt: str, max_tokens: int) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content

    def _google_headers(self) -> dict:
        """AQ.-prefixed Google AI Studio 'authorization keys' must be sent via
        the x-goog-api-key header, not the old ?key= query parameter that
        legacy AIza-format keys used."""
        return {
            "Content-Type": "application/json",
            "x-goog-api-key": settings.GOOGLE_API_KEY,
        }

    def _complete_google(self, system: str, prompt: str, max_tokens: int) -> str:
        """Uses Google's free-tier Gemini API via plain REST (no extra SDK dependency)."""
        import requests

        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        body = {
            "system_instruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": max_tokens},
        }
        response = requests.post(url, json=body, headers=self._google_headers(), timeout=60)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    # ---- embeddings (used for semantic matching + RAG retrieval) -------
    def embed(self, text: str) -> list[float]:
        """Returns a dense embedding vector for `text`.

        For the 'google' provider, uses Gemini's embedding model with
        outputDimensionality pinned to settings.EMBEDDING_DIM so the vector
        size matches the database schema regardless of provider. For
        'anthropic', falls back to OpenAI's embeddings endpoint since
        Anthropic doesn't expose a first-party embeddings API.
        """
        if self.provider == "google":
            return self._embed_google(text)
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.embeddings.create(model=settings.EMBEDDING_MODEL, input=text)
        return response.data[0].embedding

    def _embed_google(self, text: str) -> list[float]:
        import requests

        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"
        body = {
            "model": "models/gemini-embedding-001",
            "content": {"parts": [{"text": text}]},
            "outputDimensionality": settings.EMBEDDING_DIM,
        }
        response = requests.post(url, json=body, headers=self._google_headers(), timeout=60)
        response.raise_for_status()
        return response.json()["embedding"]["values"]


llm_client = LLMClient()
