"""Lightweight auth: PBKDF2 password hashing + HMAC-signed stateless tokens.

No external deps (no bcrypt/JWT libs) — stdlib only, which keeps the admin login
simple and dependency-free for this internal tool.
"""
import hmac
import json
import base64
import hashlib
import secrets
import time
from typing import Optional, Dict, Any

from sqlalchemy.future import select

from config.settings import settings
from src.storage.db_session import AsyncSessionLocal
from src.storage.models import AdminUserModel
from src.utils.logger import logger

# Signing secret for tokens. Falls back to a static dev secret; override with
# ADMIN_SECRET / LLM_API_KEY-style env in production.
_SECRET = (getattr(settings, "ADMIN_SECRET", None) or "opportunity-finder-admin-secret-v1").encode()
_TOKEN_TTL = 60 * 60 * 12  # 12 hours

# Default seeded admin (per request).
DEFAULT_ADMIN = {
    "username": "vipinpal7060",
    "email": "manisha@elevanaconsultancy.com",
    "password": "12345",
    "role": "admin",
}


# ------------------------------- passwords --------------------------------
def hash_password(password: str, *, salt: Optional[str] = None) -> str:
    salt = salt or secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000)
    return f"pbkdf2_sha256$120000${salt}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, iters, salt, digest = stored.split("$")
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iters))
        return hmac.compare_digest(dk.hex(), digest)
    except Exception:
        return False


# --------------------------------- tokens ---------------------------------
def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _unb64(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def create_token(username: str, role: str = "admin") -> str:
    payload = {"sub": username, "role": role, "exp": int(time.time()) + _TOKEN_TTL}
    body = _b64(json.dumps(payload, separators=(",", ":")).encode())
    sig = _b64(hmac.new(_SECRET, body.encode(), hashlib.sha256).digest())
    return f"{body}.{sig}"


def verify_token(token: Optional[str]) -> Optional[Dict[str, Any]]:
    if not token or "." not in token:
        return None
    body, _, sig = token.partition(".")
    expected = _b64(hmac.new(_SECRET, body.encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(sig, expected):
        return None
    try:
        payload = json.loads(_unb64(body))
    except Exception:
        return None
    if payload.get("exp", 0) < int(time.time()):
        return None
    return payload


# ------------------------------- seeding ----------------------------------
async def seed_admin_user() -> None:
    """Idempotently ensure the default admin exists in the DB with admin role."""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            existing = (
                await session.execute(
                    select(AdminUserModel).where(AdminUserModel.username == DEFAULT_ADMIN["username"])
                )
            ).scalars().first()
            if existing:
                return
            session.add(
                AdminUserModel(
                    username=DEFAULT_ADMIN["username"],
                    email=DEFAULT_ADMIN["email"],
                    password_hash=hash_password(DEFAULT_ADMIN["password"]),
                    role=DEFAULT_ADMIN["role"],
                )
            )
    logger.info(f"Seeded default admin user '{DEFAULT_ADMIN['username']}' (role=admin).")
