"""
AbstractRepository — barcha repository'lar amalga oshirishi shart
bo'lgan shartnoma (contract).

Bu klass hech qanday haqiqiy DB bilan ishlamaydi — u faqat "qanday
metodlar bo'lishi kerak"ni belgilaydi. Haqiqiy ishni keyingi darsda
yozadigan SQLAlchemyProductRepository bajaradi.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class AbstractRepository(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Barcha repository'lar amalga oshirishi shart bo'lgan shartnoma (contract)"""

    @abstractmethod
    async def get(self, id: int) -> Optional[ModelType]:
        ...

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        ...

    @abstractmethod
    async def create(self, data: CreateSchemaType) -> ModelType:
        ...

    @abstractmethod
    async def update(self, id: int, data: UpdateSchemaType) -> Optional[ModelType]:
        ...

    @abstractmethod
    async def delete(self, id: int) -> bool:
        ...