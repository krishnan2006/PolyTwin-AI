import asyncpg
from app.core.config import settings

pool = None


async def create_pool():
    """
    Create the PostgreSQL connection pool.
    Called once when FastAPI starts.
    """
    global pool

    pool = await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=2,
        max_size=10,
    )


async def close_pool():
    """
    Close the connection pool.
    Called once when FastAPI shuts down.
    """
    global pool

    if pool is not None:
        await pool.close()


def get_pool():
    """
    Return the active connection pool.
    """
    return pool