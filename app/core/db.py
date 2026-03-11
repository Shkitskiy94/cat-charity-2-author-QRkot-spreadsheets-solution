from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, declared_attr

from app.core.config import settings


class PreBase:

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)


class Base(DeclarativeBase, PreBase):
    pass

engine = create_async_engine(settings.database_url)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session
