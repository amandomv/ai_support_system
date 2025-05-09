import asyncio
import logging

from src.database.connection import get_connection
from src.database.updates_store import UpdatesStore

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def init_db() -> None:
    """Initialize the database with the most up-to-date schema."""

    try:
        async with get_connection() as conn:
            # Get database connection            # Run updates
            await UpdatesStore.run_updates(conn)
        logger.info("Database initialization completed successfully!")

    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(init_db())
