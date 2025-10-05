import re
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from typing import Optional


class CallCreateSchema(BaseModel):
    """Схема загрузки звонка"""
    caller: str = Field(description="Номер телефона звонящего в международном формате, начинающийся с '+'")
    receiver: str = Field(description="Номер телефона принимающего в международном формате, начинающийся с '+'")
    started_at: datetime = Field(description="Дата и время звонка в формате '2025-09-20T10:00:00'")

    @field_validator("caller", "receiver")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        pattern = r'^\+\d{1,3}\d{5,14}$'
        if not re.match(pattern, value):
            raise ValueError(
                "Номер должен быть в формате: +[код страны][номер], "
                "например: +79991234567"
            )
        return value

    @model_validator(mode="after")
    def validate_model(self) -> 'CallCreateSchema':
        if self.caller == self.receiver:
            raise ValueError("Номера звонящего и принимающего не могут быть одинаковыми")

        if self.started_at > datetime.now():
            raise ValueError("Дата звонка не может быть в будущем'")

        return self


class CallIDResponse(BaseModel):
    """Схема овета с информацией о ID звонка"""
    id: int = Field(description="ID звонка")


class RecordingCreateSchema(BaseModel):
    """Схема загрузки аудиофайла"""
    call_id: int = Field(description="ID звонка")
    audio_file: bytes = Field(description="Аудиофайл в формате mp3 или wav, не более 50MB")


class RecordingResponseSchema(BaseModel):
    """Схема ответа с информацией о записи"""
    file_name: str = Field(..., description="Имя файла записи")
    duration: Optional[int] = Field(None, description="Длительность записи в секундах")
    transcription: Optional[str] = Field(None, description="Транскрипция разговора")
    processing_status: str = Field(..., description="Статус обработки")

    class Config:
        from_attributes = True


class CallResponseSchema(BaseModel):
    """Схема ответа с полной информацией о звонке"""
    id: int = Field(..., description="ID звонка")
    caller: str = Field(..., description="Номер звонящего")
    receiver: str = Field(..., description="Номер принимающего")
    started_at: datetime = Field(..., description="Время начала звонка")
    status: str = Field(..., description="Статус звонка")
    created_at: datetime = Field(..., description="Время создания записи")
    recording: Optional[RecordingResponseSchema] = Field(
        None,
        description="Информация о записи разговора"
    )

    class Config:
        from_attributes = True


class RecordingUploadResponse(BaseModel):
    """Схема ответа после загрузки записи"""
    recording_id: int = Field(..., description="ID созданной записи")
    call_id: int = Field(..., description="ID звонка")
    file_name: str = Field(..., description="Имя загруженного файла")
    processing_status: str = Field(..., description="Статус обработки")
