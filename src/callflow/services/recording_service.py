import uuid
from pathlib import Path
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.callflow.models import Call, CallRecording
from src.callflow.enums import CallStatus
from src.worker.tasks import process_recording_task


class RecordingService:
    """Сервис для работы с аудиозаписями звонков"""

    def __init__(self, session: AsyncSession, upload_dir: Path):
        self.session = session
        self.upload_dir = upload_dir
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_recording(
            self,
            call_id: int,
            audio_file,
            original_filename: str
    ) -> CallRecording:
        """Сохранение аудиофайла и создание записи в БД"""
        logger.info(f"Сохранение записи звонка {call_id}, файл: {original_filename}")

        call = await self.session.get(Call, call_id)
        if not call:
            raise ValueError(f"Звонок с ID {call_id} не найжен")

        existing_recording = await self._get_recording_by_call_id(call_id)
        if existing_recording:
            raise ValueError(f"Запись уже существует для звонка с ID {call_id}")

        file_extension = Path(original_filename).suffix.lower()
        if file_extension not in ['.mp3', '.wav']:
            raise ValueError("Не поддерживаемый формат файла. Только MP3 или WAV")

        unique_filename = f"{call_id}_{uuid.uuid4()}{file_extension}"
        file_path = self.upload_dir / unique_filename

        try:
            contents = await audio_file.read()
            with open(file_path, 'wb') as f:
                f.write(contents)
            logger.info(f"Файл сохранен, путь: {file_path}")
        except Exception as e:
            logger.error(f"Ошибка сохранения файла: {e}")
            raise

        recording = CallRecording(
            call_id=call_id,
            file_path=str(file_path),
            file_name=original_filename,
            processing_status="pending"
        )

        self.session.add(recording)
        await self.session.flush()

        call.status = CallStatus.PROCESSING
        await self.session.flush()

        process_recording_task.delay(recording.id)

        logger.info(f"Запись создана с ID: {recording.id}, задача поставлена в очередь на обработку")
        return recording

    async def _get_recording_by_call_id(self, call_id: int) -> Optional[CallRecording]:
        """Внутренний метод для поиска записи по call_id"""
        from sqlalchemy import select
        query = select(CallRecording).where(CallRecording.call_id == call_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    def get_recording_file_path(self, recording: CallRecording) -> Path:
        """Получение пути к файлу записи"""
        return Path(recording.file_path)
