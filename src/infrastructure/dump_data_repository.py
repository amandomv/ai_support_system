import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from asyncpg import Connection

from src.application.interfaces.dump_data_interface import DumpDataInterface
from src.database.connection import get_connection
from src.types.documents import FaqDocument
from src.types.user import User


class DumpDataRepository(DumpDataInterface):
    """
    Repository for dumping data into the database.

    This class handles the insertion of FAQ documents and user data
    into their respective database tables.
    """

    def __init__(self, connection: Connection):
        """
        Initialize the repository with a database connection.

        Args:
            connection: The database connection to use.
        """
        self.conn = connection
        self.logger = logging.getLogger(__name__)

    async def dump_faq_documents(self, faq_documents: list[FaqDocument]) -> None:
        """
        Dump FAQ documents into the database.

        Args:
            faq_documents: List of FAQ documents to insert.

        Raises:
            Exception: If there's an error during the database operation.
        """
        try:
            # Prepare the insert statement using unnest
            insert_query = """
                INSERT INTO platform_information.faq_documents
                (title, link, text, category, embedding, created_at, updated_at)
                SELECT
                    unnest($1::text[]) as title,
                    unnest($2::text[]) as link,
                    unnest($3::text[]) as text,
                    unnest($4::platform_information.faq_category[]) as category,
                    unnest($5::vector[]) as embedding,
                    unnest($6::timestamptz[]) as created_at,
                    unnest($7::timestamptz[]) as updated_at
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    link = EXCLUDED.link,
                    text = EXCLUDED.text,
                    category = EXCLUDED.category,
                    embedding = EXCLUDED.embedding,
                    updated_at = CURRENT_TIMESTAMP
            """

            # Prepare the data for batch insert
            titles = [doc.title for doc in faq_documents]
            links = [doc.link for doc in faq_documents]
            texts = [doc.text for doc in faq_documents]
            categories = [doc.category.value for doc in faq_documents]
            embeddings = [
                f"[{', '.join(map(str, doc.embedding))}]" for doc in faq_documents
            ]
            created_ats = [doc.created_at for doc in faq_documents]
            updated_ats = [doc.updated_at for doc in faq_documents]

            # Execute single batch insert
            await self.conn.execute(
                insert_query,
                titles,
                links,
                texts,
                categories,
                embeddings,
                created_ats,
                updated_ats,
            )
            self.logger.info(f"Successfully dumped {len(faq_documents)} FAQ documents")
        except Exception as e:
            self.logger.error(f"Error dumping FAQ documents: {str(e)}")
            raise

    async def dump_user_data(self, user_data: list[User]) -> None:
        """
        Dump user data into the database.

        Args:
            user_data: List of users to insert.

        Raises:
            Exception: If there's an error during the database operation.
        """
        try:
            # Prepare the insert statement using unnest
            insert_query = """
                INSERT INTO user_management.user
                (email, password_hash, user_name, created_at, updated_at)
                SELECT * FROM unnest(
                    $1::text[],
                    $2::text[],
                    $3::text[],
                    $4::timestamptz[],
                    $5::timestamptz[]
                )
                ON CONFLICT (email) DO UPDATE SET
                    password_hash = EXCLUDED.password_hash,
                    user_name = EXCLUDED.user_name,
                    updated_at = CURRENT_TIMESTAMP
            """

            # Prepare the data for batch insert
            emails = [user.email for user in user_data]
            password_hashes = [user.password_hash for user in user_data]
            user_names = [user.user_name for user in user_data]
            created_ats = [user.created_at for user in user_data]
            updated_ats = [user.updated_at for user in user_data]

            # Execute single batch insert
            await self.conn.execute(
                insert_query,
                emails,
                password_hashes,
                user_names,
                created_ats,
                updated_ats,
            )
            self.logger.info(f"Successfully dumped {len(user_data)} users")
        except Exception as e:
            self.logger.error(f"Error dumping user data: {str(e)}")
            raise


@asynccontextmanager
async def get_dump_data_repository() -> AsyncGenerator[DumpDataInterface, None]:
    """
    Get an instance of the DumpDataRepository as a context manager.

    Yields:
        DumpDataInterface: An instance of the repository for dumping data.
    """
    async with get_connection() as connection:
        repository = DumpDataRepository(connection)
        yield repository
