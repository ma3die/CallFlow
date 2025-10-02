from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.core.db import postgres_settings

DATABASE_URL = postgres_settings.get_db_url()
engine = create_async_engine(DATABASE_URL)

async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
