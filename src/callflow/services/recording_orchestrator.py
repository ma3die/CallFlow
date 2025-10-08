from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

from src.callflow.services.file_storage import FileStorage
from src.callflow.services.recording_service import RecordingService
from src.core.settings import UPLOAD_DIR


class RecordingOrchestrator:
    """
    Оркестратор объединяет FileStorage и RecordingService.
    """

    def __init__(self, session: AsyncSession):
        self.recording_service = RecordingService(session)
        self.storage = FileStorage(Path(UPLOAD_DIR))

    async def save_recording(self, call_id: int, file: UploadFile):
        call = await self.recording_service.get_call(call_id)
        if not call:
            raise ValueError(f"Запись с ID {call_id} не найдена")

        stored_name, stored_path = await self.storage.save(file)
        recording = await self.recording_service.save_recording(
            call_id=call_id, file_name=stored_name, file_path=stored_path
        )
        return recording
