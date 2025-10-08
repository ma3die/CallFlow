from sqlalchemy.ext.asyncio import AsyncSession

from src.callflow.dao import CallDAO, CallRecordingDAO
from src.callflow.models import Call, CallRecording


class RecordingService:
    def __init__(self, session: AsyncSession):
        self.call_dao = CallDAO(session)
        self.recording_dao = CallRecordingDAO(session)

    async def get_call(self, call_id: int) -> Call:
        """Находит звонок"""
        return await self.call_dao.find_one(id=call_id)

    async def save_recording(
            self,
            call_id: int,
            file_name: str,
            file_path: str
    ) -> CallRecording:
        """Сохраняет запись разговора"""

        existing_recording = await self.recording_dao.find_one(call_id=call_id)
        if existing_recording:
            raise ValueError(f"Запись уже существует для звонка {call_id}")

        recording_values = {
            "call_id": call_id,
            "file_name": file_name,
            "file_path": file_path
        }
        recording = await self.recording_dao.add_one(**recording_values)

        return recording
