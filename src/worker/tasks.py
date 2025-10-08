from pathlib import Path
from celery import current_task
import librosa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from loguru import logger

from src.worker.app import celery_app
from src.callflow.models import CallRecording, Call
from src.callflow.enums import CallStatus
from src.core.db import postgres_settings
from src.core.settings import UPLOAD_DIR

DATABASE_URL = postgres_settings.get_db_url()
SYNC_DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")

engine = create_engine(SYNC_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@celery_app.task(bind=True, )
def process_recording_task(self, recording_id: int):
    """Фоновая задача обработки аудиозаписи"""
    session = SessionLocal()
    logger.info(f"Таска запустилась")

    try:
        recording = session.get(CallRecording, recording_id)
        if not recording:
            raise ValueError(f"Запись с ID {recording_id} не найдена")

        current_task.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 100, "status": "Обработка началась"}
        )
        upload_dir = Path(UPLOAD_DIR)
        file_path = Path(str(recording.file_path))

        if not file_path.exists():
            raise FileNotFoundError(f"Аудиофайл не найден: {file_path}")

        current_task.update_state(
            state="PROGRESS",
            meta={"current": 30, "total": 100, "status": "Анализ аудиофайла"}
        )

        audio_data, sample_rate = librosa.load(file_path, sr=None)
        logger.info(f"audio_data={audio_data}, sample_rate={sample_rate}")
        duration = int(len(audio_data) / sample_rate)
        logger.info(f"duration={duration}")

        current_task.update_state(
            state="PROGRESS",
            meta={"current": 70, "total": 100, "status": "Создание транскрипции"}
        )

        transcription = _generate_pseudo_transcription(duration)

        logger.info(f"duration={duration}, transcription= {transcription}")

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
        logger.info(f"Какая-то херня {e}")
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


def _generate_pseudo_transcription(duration: int) -> str:
    """Генерация псевдотранскрипции (заглушка)"""
    # sample_duration = min(20000, duration * 1000)

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
    time_per_phrase = duration / len(phrases)

    for i, phrase in enumerate(phrases):
        speaker = speakers[i % 2]
        start_time = i * time_per_phrase
        end_time = (i + 1) * time_per_phrase
        transcription_parts.append(
            f"[{start_time:.1f}-{end_time:.1f}s] {speaker}: {phrase}"
        )

    transcription = "\n".join(transcription_parts)

    return f"Detected speech fragment:\n{transcription}"
