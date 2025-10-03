import re
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime


class CallCreateSchema(BaseModel):
    caller: str = Field(description="Номер телефона звонящего в международном формате, начинающийся с '+'")
    receiver: str = Field(description="Номер телефона принимающего в международном формате, начинающийся с '+'")
    started_at: datetime = Field(description="Дата и время звонка в формате '2025-09-20T10:00:00'")

    @field_validator("caller", "receiver")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        if not re.match(r'^\+\d{5,15}$', value):
            raise ValueError("Номер телефона должен начинаться с '+' и содержать от 5 до 15 цифр")
        return value

    @model_validator(mode="after")
    def validate_model(self) -> 'CallCreateSchema':
        if self.caller == self.receiver:
            raise ValueError("Номера звонящего и принимающего не могут быть одинаковыми")

        if self.started_at > datetime.now():
            raise ValueError("Дата звонка не может быть в будущем'")

        return self


class RecordingCreateSchema(BaseModel):
    call_id: int = Field(description="ID звонка")
    audio_file: bytes = Field(description="Аудиофайл в формате mp3 или wav, не более 50MB")


class RecordingResponseSchema(BaseModel):
    file_name: str
    duration: int
    transcription: str


class CallResponseSchema(BaseModel):
    id: int
    caller: str
    receiver: str
    started_at: datetime
    recording: dict[RecordingResponseSchema]
