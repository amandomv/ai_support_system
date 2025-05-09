import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from src.application.dump_data_manager import DumpDataManager
from src.infrastructure.ai_repository import get_ai_repository
from src.infrastructure.dump_data_repository import get_dump_data_repository


async def init_base_data() -> None:
    """
    Initialize the base data by creating and running the DumpDataManager.

    This function:
    1. Loads FAQ documents from JSON and Markdown files
    2. Initializes the DumpDataManager with required repositories
    3. Executes the data dump process

    Raises:
        Exception: If there's an error during the initialization process
    """
    logger = logging.getLogger(__name__)

    try:
        # Initialize repositories
        async with get_dump_data_repository() as dump_data_repository:
            ai_repository = await get_ai_repository()

            # Load FAQ documents from JSON
            json_path = Path("base_data/faq_documents_list.json")
            with open(json_path) as f:
                data = json.load(f)
                faq_documents = data["faq_documents"]

            # Process each FAQ document
            base_data: list[dict[str, Any]] = []
            for doc in faq_documents:
                # Read the markdown content
                md_path = Path(doc["text_path"])
                with open(md_path) as f:
                    text = f.read()

                # Create document data
                base_data.append(
                    {
                        "title": doc["title"],
                        "link": doc["link"],
                        "text": text,
                        "category": doc["category"],
                    }
                )

            logger.info("Initializing DumpDataManager")
            manager = DumpDataManager(dump_data_repository, ai_repository)

            logger.info("Starting data dump process")
            await manager.dump_data(base_data)
            logger.info("Base data initialization completed successfully")

    except Exception as e:
        logger.error(f"Error during base data initialization: {str(e)}")
        raise


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run the initialization
    asyncio.run(init_base_data())
