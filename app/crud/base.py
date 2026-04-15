from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CRDBase:
    """Базовый класс CRUD-операций."""

    model_class = None

    @classmethod
    async def get_multi(cls, session: AsyncSession):
        """Получить все объекты модели."""
        query_result = await session.execute(select(cls.model_class))
        return query_result.scalars().all()

    @classmethod
    async def get_by_id(cls, session: AsyncSession, object_id: int):
        """Получить объект по идентификатору."""
        query_result = await session.execute(
            select(cls.model_class).where(cls.model_class.id == object_id)
        )
        return query_result.scalars().first()


class CRUDCharityProject(CRDBase):
    """CRUD-операции для проектов."""

    @classmethod
    async def get_by_name(cls, session: AsyncSession, name: str):
        """Получить проект по имени."""
        query_result = await session.execute(
            select(cls.model_class).where(cls.model_class.name == name)
        )
        return query_result.scalars().first()


class CRUDDonation(CRDBase):
    """CRUD-операции для пожертвований."""
