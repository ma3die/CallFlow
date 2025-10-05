from pathlib import Path
from celery import current_task
from pydub import AudioSegment
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.worker.app import celery_app
from src.callflow.models import CallRecording, Call
from src.callflow.enums import CallStatus
from src.core.db import postgres_settings

DATABASE_URL = postgres_settings.get_db_url()

engine = create_engine(DATABASE_URL.replace('+asyncpg', ''))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@celery_app.task(bind=True, name="process_recording")
def process_recording_task(self, recording_id: int):
    """Фоновая задача обработки аудиозаписи"""
    session = SessionLocal()

    try:
        recording = session.get(CallRecording, recording_id)
        if not recording:
            raise ValueError(f"Запись с ID {recording_id} не найдена")

        current_task.update_state(
            state="PROGRESS",
            meta={"curren": 0, "total": 100, "status": "Обработка началась"}
        )

        file_path = Path(recording.file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Аудиофайл не найден: {file_path}")

        current_task.update_state(
            state="PROGRESS",
            meta={"current": 30, "total": 100, "status": "Анализ аудиофайла"}
        )

        audio = AudioSegment.from_file(str(file_path))
        duration = len(audio) // 1000  # конвертируем в секунды

        current_task.update_state(
            state="PROGRESS",
            meta={"current": 70, "total": 100, "status": "Создание транскрипции"}
        )

        transcription = _generate_pseudo_transcription(audio, duration)

        recording.duration = duration
        recording.transcription = transcription
        recording.processing_status = "completed"

        call = session.get(Call, recording.call_id)
        if call:
            call.status = CallStatus.READY

        session.commit()

        current_task.update_state(
            state="SUCCESS",
            meta={"current": 100, "total": 100, "status": "Создание завершено"}
        )

        return {
            "recording_id": recording_id,
            "duration": duration,
            "transcription_length": len(transcription)
        }

    except Exception as e:
        session.rollback()

        if "recording" in locals() and recording:
            recording.processing_status = "failed"
            session.commit()

        current_task.update_state(
            state="FAILURE",
            meta={"current": 0, "total": 100, "status": str(e)}
        )
        raise
    finally:
        session.close()


def _generate_pseudo_transcription(audio: AudioSegment, duration: int) -> str:
    """Генерация псевдотранскрипции (заглушка)"""
    sample_duration = min(20000, duration * 1000)

    speakers = ["Абонент 1", "Абонент 2"]
    phrases = [
        "Здравствуйте!",
        "Добрый день! Чем могу помочь?",
        "Мне нужно узнать информацию о моем счете",
        "Конечно, сейчас проверю",
        "Спасибо за обращение!",
        "Всего доброго!"
    ]

    transcription_parts = []
    time_per_phrase = sample_duration / len(phrases)

    for i, phrase in enumerate(phrases):
        speaker = speakers[i % 2]
        start_time = i * time_per_phrase / 1000  # в секундах
        transcription_parts.append(
            f"[{start_time:.1f}s] {speaker}: {phrase}"
        )

    transcription = "\n".join(transcription_parts)

    return f"Detected speech fragment:\n{transcription}"
