import logging
from pathlib import Path

from asyncpg import Connection

from src.database.init_db_schemas import get_schema_paths

logger = logging.getLogger(__name__)


class UpdatesStore:
    @staticmethod
    async def init(conn: Connection) -> None:
        """Initialize the updates table if it doesn't exist."""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS updates (
                update_file VARCHAR PRIMARY KEY,
                applied_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)
        logger.info("Updates table initialized")

    @staticmethod
    async def exists(conn: Connection, update_file: str) -> bool:
        """Check if an update has already been applied."""
        result = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM updates WHERE update_file = $1)", update_file
        )
        return bool(result)

    @staticmethod
    async def add(conn: Connection, update_file: str) -> None:
        """Mark an update as applied."""
        await conn.execute("INSERT INTO updates (update_file) VALUES ($1)", update_file)

    @staticmethod
    def load_update(update_path: Path) -> str:
        """Load SQL content from an update file."""
        with open(update_path) as f:
            return f.read().strip()

    @staticmethod
    async def run_updates(conn: Connection) -> None:
        """Run all pending database updates."""
        # Initialize updates table
        await UpdatesStore.init(conn)

        # Get schema paths
        schema_paths = get_schema_paths()

        # Apply updates
        for schema_path in schema_paths:
            update_file = schema_path.name
            async with conn.transaction():
                if await UpdatesStore.exists(conn, update_file):
                    logger.info(f"Update already applied: {update_file}")
                    continue

                update_sql = UpdatesStore.load_update(schema_path)
                if update_sql:
                    await conn.execute(update_sql)
                await UpdatesStore.add(conn, update_file)
                logger.info(f"Applied update: {update_file}")

        logger.info("All updates applied successfully")
