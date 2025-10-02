from functools import wraps
from src.db.engine import async_session_maker


def connection(method):
    """
    Декоратор для управления сессиями БД (автоматический commit/rollback)
    """

    @wraps(method)
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            try:
                result = await method(*args, session=session, **kwargs)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                raise
            finally:
                await session.close()

    return wrapper
