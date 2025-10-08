import re
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.callflow.dao import CallDAO
from src.callflow.models import Call
from src.callflow.enums import CallStatus
from src.callflow.schemas import CallCreateSchema, CallResponseSchema


class CallService:
    """Сервис для работы со звонками"""

    def __init__(self, session: AsyncSession):
        self._session = session
        self.call_dao = CallDAO(session)

    async def create_call(self, call_data: CallCreateSchema) -> Call:
        """Создание нового звонка"""
        logger.info(f"Создание звонка от {call_data.caller} к {call_data.receiver}")

        call_dict = call_data.model_dump()
        call = await self.call_dao.add_one(**call_dict)

        logger.info(f"Звонок создан с ID: {call.id}")
        return call

    async def get_call_with_recording(self, call_id: int) -> Optional[Call]:
        """Получение звонка с информацией о записи"""

        call = await self.call_dao.find_call_with_recording(call_id=call_id)
        if not call:
            logger.warning(f"Звонок с ID {call_id} не найден")
            return None

        logger.info(f"Звонок {call_id} найден с записью: {bool(call.callrecording)}")

        return call

    async def update_call_status(self, call_id: int, status: CallStatus) -> None:
        """Обновление статуса звонка"""
        logger.info(f"Обновление статуса звона {call_id} на {status}")

        call = await self.call_dao.find_one(id=call_id)
        if call:
            call.status = status
            await self._session.flush()
            logger.info(f"Статус звонка {call_id} обновлен на {status}")

    async def search_calls_by_phone(self, phone_number: str) -> List[CallResponseSchema]:
        """Поиск звонков по номеру телефона"""
        logger.info(f"Поиск звонков для номера: {phone_number}")

        pattern = r'^\+\d{1,3}\d{5,14}$'
        if not re.match(pattern, phone_number):
            raise ValueError(
                "Номер должен быть в формате: +[код страны][номер], "
                "например: +79991234567"
            )

        calls = await self.call_dao.search_by_phone_number(phone_number)

        call_schemas = []
        for call in calls:
            call_schema = CallResponseSchema.model_validate(call)
            call_schemas.append(call_schema)

        logger.info(f"Найдено звонков: {len(call_schemas)}")
        return call_schemas
