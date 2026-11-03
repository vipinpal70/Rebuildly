"""Runtime LLM configuration: the admin picks a provider (Claude or ChatGPT) and pastes an
API key in the dashboard; every LLM call resolves it from here at call time, so a change
takes effect without a restart. With nothing saved, the .env settings apply as before."""
import base64
import hashlib
import time
from dataclasses import dataclass
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy.future import select

from config.settings import settings
from src.utils.logger import logger

PROVIDERS = {
    "anthropic": {"label": "Claude (Anthropic)", "default_model": "claude-haiku-4-5-20251001",
                  "base_url": "https://api.anthropic.com/v1"},
    "openai": {"label": "ChatGPT (OpenAI)", "default_model": "gpt-4o-mini",
               "base_url": "https://api.openai.com/v1"},
}
SETTING_KEY = "llm_config"
_CACHE_TTL = 15.0


@dataclass
class LLMConfig:
    provider: str
    api_key: Optional[str]
    model: Optional[str]
    source: str  # "admin" (saved in dashboard) or "env"


_cache: Optional[tuple] = None  # (expires_at, LLMConfig)


def _fernet() -> Fernet:
    key = settings.SETTINGS_ENCRYPTION_KEY
    if not key:
        secret = getattr(settings, "ADMIN_SECRET", None) or "opportunity-finder-admin-secret-v1"
        key = base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest()).decode()
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_secret(plain: str) -> str:
    return _fernet().encrypt(plain.encode()).decode()


def decrypt_secret(token: str) -> Optional[str]:
    try:
        return _fernet().decrypt(token.encode()).decode()
    except (InvalidToken, ValueError):
        logger.error("Could not decrypt the saved LLM API key (SETTINGS_ENCRYPTION_KEY changed?). Re-enter it in Settings.")
        return None


def mask_key(key: Optional[str]) -> Optional[str]:
    if not key:
        return None
    return f"{key[:7]}…{key[-4:]}" if len(key) > 14 else "…" + key[-4:]


def saved_key_previews(saved: Optional[dict]) -> dict:
    """{provider: masked key or None} for every provider — shown in Settings, never the full key."""
    out = {}
    for p in PROVIDERS:
        enc = ((saved or {}).get("keys") or {}).get(p)
        out[p] = mask_key(decrypt_secret(enc)) if enc else None
    return out


def env_config() -> LLMConfig:
    """What the .env settings resolve to, mirroring the pre-dashboard behaviour."""
    provider = (settings.LLM_PROVIDER or "anthropic").lower()
    key = settings.LLM_API_KEY or settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY or settings.CLAUDE_API_KEY
    return LLMConfig(provider=provider, api_key=key, model=settings.LLM_MODEL, source="env")


def _env_key_for(provider: str) -> Optional[str]:
    if provider == "anthropic":
        return settings.ANTHROPIC_API_KEY or settings.CLAUDE_API_KEY or (
            settings.LLM_API_KEY if (settings.LLM_PROVIDER or "").lower() == "anthropic" else None)
    return settings.OPENAI_API_KEY or (
        settings.LLM_API_KEY if (settings.LLM_PROVIDER or "").lower() == "openai" else None)


async def load_saved() -> Optional[dict]:
    from src.storage.db_session import AsyncSessionLocal
    from src.storage.models import AppSettingModel
    try:
        async with AsyncSessionLocal() as session:
            row = (await session.execute(
                select(AppSettingModel).where(AppSettingModel.key == SETTING_KEY))).scalars().first()
            return dict(row.value) if row else None
    except Exception as err:
        logger.warning(f"Could not read saved LLM settings (using .env): {err}")
        return None


async def save_llm_config(provider: str, api_key: Optional[str], model: Optional[str]) -> None:
    """Persist the admin's choice. Keys and models are stored per provider so both a Claude
    and a ChatGPT key can be kept and switched between. `api_key=None` keeps that provider's
    saved key; "" removes it."""
    from src.storage.db_session import AsyncSessionLocal
    from src.storage.models import AppSettingModel
    if provider not in PROVIDERS:
        raise ValueError(f"Unsupported provider '{provider}'")
    current = await load_saved() or {}
    keys = dict(current.get("keys") or {})
    models = dict(current.get("models") or {})
    if api_key is not None:
        if api_key.strip():
            keys[provider] = encrypt_secret(api_key.strip())
        else:
            keys.pop(provider, None)
    if model is not None:
        if model.strip():
            models[provider] = model.strip()
        else:
            models.pop(provider, None)
    value = {"provider": provider, "keys": keys, "models": models}
    async with AsyncSessionLocal() as session:
        async with session.begin():
            row = await session.get(AppSettingModel, SETTING_KEY)
            if row:
                row.value = value
            else:
                session.add(AppSettingModel(key=SETTING_KEY, value=value))
    invalidate_cache()


def invalidate_cache() -> None:
    global _cache
    _cache = None


async def load_llm_config(use_cache: bool = True) -> LLMConfig:
    """Saved dashboard settings if present, else .env. A saved provider with no saved key
    falls back to that provider's key in .env."""
    global _cache
    if use_cache and _cache and _cache[0] > time.monotonic():
        return _cache[1]

    saved = await load_saved()
    if saved and saved.get("provider") in PROVIDERS:
        provider = saved["provider"]
        enc = (saved.get("keys") or {}).get(provider)
        key = decrypt_secret(enc) if enc else None
        cfg = LLMConfig(provider=provider, api_key=key or _env_key_for(provider),
                        model=(saved.get("models") or {}).get(provider) or PROVIDERS[provider]["default_model"],
                        source="admin")
    else:
        cfg = env_config()
    _cache = (time.monotonic() + _CACHE_TTL, cfg)
    return cfg
