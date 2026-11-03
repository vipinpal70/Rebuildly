import asyncio

import pytest
from sqlalchemy import delete, or_

# Place-id prefixes used by tests that save businesses into the real database. Deleting the
# business cascades to its audits, outreach lead and signal findings.
TEST_PLACE_ID_PREFIXES = ("outreach_test_", "celery_test_")


async def purge_test_businesses() -> int:
    from src.storage.db_session import AsyncSessionLocal
    from src.storage.models import BusinessModel
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(delete(BusinessModel).where(
                or_(*(BusinessModel.place_id.like(f"{p}%") for p in TEST_PLACE_ID_PREFIXES))))
    return result.rowcount


@pytest.fixture(scope="session", autouse=True)
def _cleanup_test_businesses():
    """Tests persist leads to the configured database; remove them when the run ends so
    they don't pile up in the dashboard's lead list."""
    yield
    try:
        asyncio.run(purge_test_businesses())
    except Exception:
        pass  # database unavailable — nothing was written either
