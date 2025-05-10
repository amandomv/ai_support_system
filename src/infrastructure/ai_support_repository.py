import json

from asyncpg import Connection

from src.application.interfaces.ai_support_interface import AISupportInterface
from src.types.documents import FaqDocument


class AISupportRepository(AISupportInterface):
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    async def get_faq_documents_by_similarity(
        self, embeddings: list[float], max_documents: int = 5
    ) -> list[FaqDocument]:
        query = """
        SELECT * FROM platform_information.faq_documents
        ORDER BY embedding <> $1
        LIMIT $2
        """
        faq_similar_documents = await self.connection.fetch(
            query, f"[{', '.join(map(str, embeddings))}]", max_documents
        )

        # Convert the documents and ensure embedding is a list
        documents = []
        for doc in faq_similar_documents:
            doc_dict = dict(doc)
            # Convert embedding string to list if it's a string
            if isinstance(doc_dict["embedding"], str):
                try:
                    doc_dict["embedding"] = json.loads(doc_dict["embedding"])
                except json.JSONDecodeError:
                    # If it's not valid JSON, try to parse it as a comma-separated list
                    doc_dict["embedding"] = [
                        float(x.strip())
                        for x in doc_dict["embedding"].strip("[]").split(",")
                    ]
            documents.append(FaqDocument(**doc_dict))

        return documents
