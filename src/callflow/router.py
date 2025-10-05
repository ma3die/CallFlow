from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from description import CALL_POST, CALL_GET, RECORDING_POST
from src.core.settings import UPLOAD_DIR
from src.callflow.schemas import (
    CallIDResponse,
    CallCreateSchema,
    CallResponseSchema,
    RecordingUploadResponse
)
from src.callflow.services.call_service import CallService
from src.callflow.services.recording_service import RecordingService
from src.db.connection import get_session_with_commit, get_session_without_commit

router = APIRouter(
    prefix="/calls",
    tags=["callflow"]
)


@router.post(
    path="",
    response_model=CallIDResponse,
    description=CALL_POST
)
async def post_call(
        call: CallCreateSchema,
        session: AsyncSession = Depends(get_session_with_commit)
) -> CallIDResponse:
    """Создание новой записи о звонке"""
    try:
        call_service = CallService(session)
        new_call = await call_service.create_call(call)
        return CallIDResponse(id=new_call.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post(
    path="/{call_id}/recording",
    response_model=RecordingUploadResponse,
    description=RECORDING_POST
)
async def upload_recording(
        call_id: int,
        audio_file: UploadFile = File(..., description="Аудиофайл в формате MP3 или WAV"),
        session: AsyncSession = Depends(get_session_with_commit)
) -> RecordingUploadResponse:
    """Загрузка аудиозаписи разговора"""
    try:
        # Валидация файла
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл должен быть аудиофайлом"
            )

        recording_service = RecordingService(session, UPLOAD_DIR)
        recording = await recording_service.save_recording(
            call_id=call_id,
            audio_file=audio_file,
            original_filename=audio_file.filename or "unknown"
        )

        return RecordingUploadResponse(
            recording_id=recording.id,
            call_id=recording.call_id,
            file_name=recording.file_name,
            processing_status=recording.processing_status
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка сохранения файла: {str(e)}"
        )


@router.get(
    path="/{call_id}",
    response_model=CallResponseSchema,
    description=CALL_GET
)
async def get_call(
        call_id: int,
        session: AsyncSession = Depends(get_session_without_commit)
) -> CallResponseSchema:
    """Получение информации о звонке по ID"""
    call_service = CallService(session)
    call = await call_service.get_call_with_recording(call_id)

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Звонок с ID {call_id} не найден"
        )

    return CallResponseSchema.model_validate(call)
