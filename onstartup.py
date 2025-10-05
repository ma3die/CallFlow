from src.db.database import Base
from src.db.engine import engine


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def onstartup():
    await create_tables()
