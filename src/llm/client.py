import json
import logging
from typing import Dict, Any, Optional
import httpx
from config.settings import settings

logger = logging.getLogger(__name__)

# Sensible current default when using Anthropic (fast + cheap, ideal for copy).
DEFAULT_ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"


class FlexibleLLMClient:
    """Flexible LLM Client supporting OpenAI, Groq, Ollama, Together AI, Anthropic (native) & OpenAI-compatible endpoints."""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.api_key = settings.LLM_API_KEY or settings.OPENAI_API_KEY
        self.model = settings.LLM_MODEL
        self.base_url = settings.LLM_BASE_URL

        # Standard base URL / model defaults if not explicitly set.
        if not self.base_url:
            if self.provider == "groq":
                self.base_url = "https://api.groq.com/openai/v1"
                self.model = self.model or "llama-3.3-70b-versatile"
            elif self.provider == "ollama":
                self.base_url = "http://localhost:11434/v1"
                self.model = self.model or "qwen2.5-coder"
            elif self.provider == "together":
                self.base_url = "https://api.together.xyz/v1"
                self.model = self.model or "meta-llama/Llama-3.3-70B-Instruct-Turbo"
            elif self.provider == "anthropic":
                self.base_url = "https://api.anthropic.com/v1"
            else:
                self.base_url = "https://api.openai.com/v1"
                self.model = self.model or "gpt-4o-mini"

        # Anthropic uses different model ids — if the model is unset or still an
        # OpenAI id (e.g. the default gpt-4o-mini), swap to a Claude model.
        if self.provider == "anthropic" and (not self.model or self.model.startswith("gpt")):
            self.model = DEFAULT_ANTHROPIC_MODEL

    @staticmethod
    def _strip_fences(content: str) -> str:
        if "```json" in content:
            return content.split("```json")[1].split("```")[0].strip()
        if "```" in content:
            return content.split("```")[1].split("```")[0].strip()
        return content.strip()

    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Executes an LLM request expecting a structured JSON response."""
        if not self.api_key and self.provider != "ollama":
            logger.info(f"No API key provided for {self.provider}. LLM Client will return None (falling back to smart template engine).")
            return None

        if self.provider == "anthropic":
            return await self._generate_anthropic(prompt, system_prompt)
        return await self._generate_openai_compatible(prompt, system_prompt)

    async def _generate_openai_compatible(self, prompt: str, system_prompt: Optional[str]) -> Optional[Dict[str, Any]]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt or "You are a JSON-only generating assistant. Output ONLY valid JSON."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
        }
        if self.provider in ["openai", "groq", "custom"]:
            payload["response_format"] = {"type": "json_object"}

        endpoint = f"{self.base_url.rstrip('/')}/chat/completions"
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                res = await client.post(endpoint, json=payload, headers=headers)
                res.raise_for_status()
                content = res.json()["choices"][0]["message"]["content"]
                return json.loads(self._strip_fences(content))
        except Exception as e:
            logger.warning(f"FlexibleLLMClient request to {self.provider} ({self.model}) failed: {e}")
            return None

    async def _generate_anthropic(self, prompt: str, system_prompt: Optional[str]) -> Optional[Dict[str, Any]]:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "temperature": 0.7,
            "system": system_prompt or "You are a JSON-only generating assistant. Output ONLY valid JSON — no prose, no markdown code fences.",
            "messages": [{"role": "user", "content": prompt}],
        }
        endpoint = f"{self.base_url.rstrip('/')}/messages"
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(endpoint, json=payload, headers=headers)
                res.raise_for_status()
                data = res.json()
                # Anthropic returns content as a list of blocks; concat text blocks.
                text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
                return json.loads(self._strip_fences(text))
        except Exception as e:
            logger.warning(f"FlexibleLLMClient (anthropic {self.model}) request failed: {e}")
            return None
