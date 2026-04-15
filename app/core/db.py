from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declared_attr, declarative_base, sessionmaker

from app.core.config import settings

engine = create_async_engine(settings.database_url)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


Base = declarative_base()


class AbstractBase(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(model_class):
        return model_class.__name__.lower()
