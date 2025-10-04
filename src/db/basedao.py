from typing import TypeVar, Type, Generic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
from src.db.database import Base


T = TypeVar("T", bound=Base)

class BaseDAO(Generic[T]):
    model: Type[T] = None

    def __init__(self, session: AsyncSession):
        self._session = session
        if self.model is None:
            raise ValueError("Модель должна быть указана в дочернем классе")


    async def add_one(self, **values: dict) -> T:
        """
        Добавить одну запись модели
        :param values: Параметры модели.
        :return: Созданный объект модели.
        """
        logger.info(f"Добавление записи {self.model.__name__} с параметрами: {values}")
        try:
            new_instance = self.model(**values)
            self._session.add(new_instance)
            await self._session.flush()
            logger.info(f"Запись {self.model.__name__} успешно добавлена.")
            return new_instance
        except SQLAlchemyError as e:
            logger.error(f"{self.model.__name__} -> Ошибка при добавлении: {e}")
            raise


    async def find_one(self, **filters) -> T:
        """
        Находит одну запись по фильтрам
        """
        try:
            query = select(self.model).filter_by(**filters)
            instance = await self._session.execute(query)
            record = instance.scalar_one_or_none()
            return record
        except SQLAlchemyError as e:
            logger.error(f"{self.model.__name__} -> Ошибка при find_one с фильтрами {filters}: {e}")
            raise
