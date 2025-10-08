import uuid
from typing import  Tuple
from pathlib import Path
from fastapi import UploadFile
import aiofiles
import magic
from loguru import logger

class FileStorage:
    """
    Отвечает за сохранение и удаление аудиофайлов на диске.
    """

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save(self, file: UploadFile) -> Tuple[str, str]:
        file_ext = Path(file.filename).suffix.lower()
        stored_name = f"{uuid.uuid4()}{file_ext}"
        stored_path = self.base_path / stored_name
        logger.info(f"stored_path={stored_path}")

        head = await file.read(2048)
        mime_type = magic.from_buffer(head, mime=True)
        await file.seek(0)

        if not mime_type.startswith("audio/"):
            raise ValueError("Загружен файл недопустимого типа (не аудио).")

        async with aiofiles.open(stored_path, "wb") as f:
            while chunk := await file.read(1024 * 1024):
                await f.write(chunk)

        return stored_name, str(stored_path)
