from src.db.database import Base
from src.callflow.models import Call, CallRecording
from src.db.engine import engine


async def create_tables():
    # engine = create_async_engine(postgres_settings.get_db_url())
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # await engine.dispose()


async def onstartup():
    await create_tables()