import asyncio
import logging

from src.database.run_init_db import init_db

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Initialize database
    asyncio.run(init_db())
