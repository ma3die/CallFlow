from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from src.callflow.dao import CallDAO
from src.callflow.models import Call, CallRecording
from src.callflow.enums import CallStatus
from src.callflow.schemas import CallCreateSchema


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
        logger.info(f"Получение звонка с ID: {call_id}")

        query = (
            select(Call)
            .outerjoin(CallRecording)
            .where(Call.id == call_id)
        )

        result = await self._session.execute(query)
        call = result.scalar_one_or_none()

        if not call:
            logger.warning(f"Звонок с ID {call_id} не найден")
            return None

        # logger.info(f"Звонок {call_id} найден с записью: {bool(call.callrecording)}")
        return call

    async def update_call_status(self, call_id: int, status: CallStatus) -> None:
        """Обновление статуса звонка"""
        logger.info(f"Обновление статуса звона {call_id} на {status}")

        call = await self.call_dao.find_one(id=call_id)
        if call:
            call.status = status
            await self._session.flush()
            logger.info(f"Статус звонка {call_id} обновлен на {status}")
