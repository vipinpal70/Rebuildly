import pytest

from config.settings import settings
from src.llm import config as llm_config
from src.llm.client import FlexibleLLMClient
from src.llm.config import LLMConfig, decrypt_secret, encrypt_secret, mask_key


def test_encrypt_roundtrip_and_no_plaintext():
    token = encrypt_secret("sk-ant-secret-1234567890")
    assert "secret" not in token and decrypt_secret(token) == "sk-ant-secret-1234567890"
    assert decrypt_secret("garbage") is None


def test_mask_key_never_reveals_full_key():
    key = "sk-proj-abcdefghijklmnop1234"
    assert mask_key(key) == "sk-proj…1234" and key not in mask_key(key)
    assert mask_key(None) is None


@pytest.mark.asyncio
async def test_client_uses_admin_config_over_env(monkeypatch):
    async def fake_load(use_cache=True):
        return LLMConfig(provider="openai", api_key="sk-admin", model="gpt-4o", source="admin")
    monkeypatch.setattr(llm_config, "load_llm_config", fake_load)
    monkeypatch.setattr(settings, "LLM_PROVIDER", "anthropic")
    monkeypatch.setattr(settings, "LLM_API_KEY", "env-key")
    c = FlexibleLLMClient()
    assert c.provider == "anthropic"
    assert await c.is_configured()
    assert (c.provider, c.api_key, c.model) == ("openai", "sk-admin", "gpt-4o")
    assert c.base_url == "https://api.openai.com/v1"


@pytest.mark.asyncio
async def test_client_keeps_env_when_nothing_saved(monkeypatch):
    async def fake_load(use_cache=True):
        return LLMConfig(provider="anthropic", api_key="env-key", model="m", source="env")
    monkeypatch.setattr(llm_config, "load_llm_config", fake_load)
    monkeypatch.setattr(settings, "LLM_PROVIDER", "groq")
    monkeypatch.setattr(settings, "LLM_API_KEY", "groq-key")
    c = FlexibleLLMClient()
    await c.is_configured()
    assert (c.provider, c.api_key) == ("groq", "groq-key")


@pytest.mark.asyncio
async def test_saved_provider_without_key_falls_back_to_env_key(monkeypatch):
    async def fake_saved():
        return {"provider": "openai", "models": {}, "keys": {}}
    monkeypatch.setattr(llm_config, "load_saved", fake_saved)
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-env-openai")
    llm_config.invalidate_cache()
    cfg = await llm_config.load_llm_config(use_cache=False)
    assert (cfg.provider, cfg.api_key, cfg.model, cfg.source) == ("openai", "sk-env-openai", "gpt-4o-mini", "admin")


@pytest.mark.asyncio
async def test_no_key_returns_none_without_network(monkeypatch):
    async def fake_load(use_cache=True):
        return LLMConfig(provider="openai", api_key=None, model=None, source="admin")
    monkeypatch.setattr(llm_config, "load_llm_config", fake_load)
    assert await FlexibleLLMClient().generate_json("hi") is None


@pytest.mark.asyncio
async def test_keys_are_per_provider(monkeypatch):
    saved = {"provider": "anthropic", "models": {"openai": "gpt-4o"},
             "keys": {"openai": encrypt_secret("sk-openai-only-key-123456")}}

    async def fake_saved():
        return saved
    monkeypatch.setattr(llm_config, "load_saved", fake_saved)
    for attr in ("ANTHROPIC_API_KEY", "CLAUDE_API_KEY", "LLM_API_KEY"):
        monkeypatch.setattr(settings, attr, None)
    cfg = await llm_config.load_llm_config(use_cache=False)
    assert cfg.provider == "anthropic" and cfg.api_key is None  # the OpenAI key must not leak across
    saved["provider"] = "openai"
    cfg = await llm_config.load_llm_config(use_cache=False)
    assert (cfg.api_key, cfg.model) == ("sk-openai-only-key-123456", "gpt-4o")
    previews = llm_config.saved_key_previews(saved)
    assert previews["anthropic"] is None and "openai-only" not in previews["openai"]
