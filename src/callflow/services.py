from sqlalchemy.ext.asyncio import AsyncSession
from src.callflow.dao import CallDAO
from loguru import logger


async def add_call(session: AsyncSession, **values: dict):
    return await CallDAO(session).add_one(**values)


async def get_one_record(session: AsyncSession, **filters):
    rec = await CallDAO(session).find_one(**filters)
    logger.info(rec)
    return rec
