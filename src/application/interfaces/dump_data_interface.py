from abc import ABC, abstractmethod

from src.types.documents import FaqDocument
from src.types.user import User


class DumpDataInterface(ABC):
    @abstractmethod
    async def dump_faq_documents(self, faq_documents: list[FaqDocument]) -> None:
        pass

    @abstractmethod
    async def dump_user_data(self, user_data: list[User]) -> None:
        pass
