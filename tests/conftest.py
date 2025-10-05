import asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.core.app import app
from src.db.database import Base

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/test_callflow_db"


@pytest.fixture(scope="session")
def event_loop():
    """Создаем event loop для тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Тестовый движок БД"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture
async def session(test_engine):
    """Тестовая сессия БД"""
    async with async_sessionmaker(
            test_engine, expire_on_commit=False, class_=AsyncSession
    )() as session:
        yield session

        await session.rollback()


@pytest.fixture
async def client():
    """AsyncClient для тестирования API"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def call_data():
    """Тестовые данные для звонка"""
    return {
        "caller": "+79991234567",
        "receiver": "+74951234567",
        "started_at": "2025-10-02T10:00:00"
    }


@pytest.fixture
def future_call_data():
    """Данные для звонка в будущем (для теста валидации)"""
    return {
        "caller": "+79991234567",
        "receiver": "+74951234567",
        "started_at": "2026-01-01T10:00:00"
    }
