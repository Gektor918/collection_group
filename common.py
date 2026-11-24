import logging
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


@asynccontextmanager
async def managed_transaction(session: AsyncSession):
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise


async def delete_file_by_url(storage_manager, url: str | None) -> None:
    if not url: return 
    try:
        await storage_manager.process_delete_file(url)
    except Exception:
        logger.warning("Failed delete storage object %s", url, exc_info=True)
