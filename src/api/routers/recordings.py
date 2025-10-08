from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.async_session import get_session_with_commit
from src.callflow.services.recording_orchestrator import RecordingOrchestrator
from description import RECORDING_POST
from src.callflow.schemas import RecordingUploadResponse
from src.worker.tasks import process_recording_task

router_recordings = APIRouter(
    prefix="/calls",
    tags=["callflow"]
)


@router_recordings.post(
    path="/{call_id}/recording",
    response_model=RecordingUploadResponse,
    description=RECORDING_POST
)
async def upload_recording(
        call_id: int,
        file: UploadFile = File(...),
        session: AsyncSession = Depends(get_session_with_commit),
):
    """
    Загрузка аудиозаписи для звонка.
    Сохраняет файл, создаёт запись в БД, а после коммита ставит задачу Celery.
    """
    try:
        orchestrator = RecordingOrchestrator(session)
        recording = await orchestrator.save_recording(call_id, file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

    process_recording_task.delay(recording.id)

    return RecordingUploadResponse(
        recording_id=recording.id,
        call_id=recording.call_id,
        file_name=recording.file_name,
        processing_status=recording.processing_status
    )
