from typing import Optional, Sequence
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from loguru import logger

from src.db.basedao import BaseDAO
from src.callflow.models import Call, CallRecording


class CallDAO(BaseDAO):
    model = Call

    async def find_call_with_recording(self, call_id: int) -> Optional[Call]:
        """Получение звонка с информацией о записи"""
        logger.info(f"Получение звонка с ID: {call_id}")

        query = (
            select(self.model)
            .options(selectinload(self.model.callrecording))
            .where(self.model.id == call_id)
        )

        result = await self._session.execute(query)

        return result.scalar_one_or_none()

    async def search_by_phone_number(self, phone_number: str) -> Sequence[Call]:
        """Поиск звонков по номеру телефона (звонящего или принимающего)"""
        logger.info(f"Поиск звонков по номеру: {phone_number}")

        query = (
            select(self.model)
            .options(selectinload(self.model.callrecording))
            .where(
                or_(
                    self.model.caller == phone_number,
                    self.model.receiver == phone_number
                )
            )
            .order_by(self.model.started_at.desc())
        )

        result = await self._session.execute(query)
        calls = result.scalars().all()

        logger.info(f"Найдено звонков: {len(calls)}")
        return calls


class CallRecordingDAO(BaseDAO):
    model = CallRecording
