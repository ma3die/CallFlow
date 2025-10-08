from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from description import CALL_POST, CALL_GET, CALL_SEARCH
from src.callflow.schemas import (
    CallIDResponse,
    CallCreateSchema,
    CallResponseSchema,
    CallListResponseSchema
)
from src.callflow.services.call_service import CallService
from src.db.async_session import get_session_with_commit, get_session_without_commit

router_calls = APIRouter(
    prefix="/calls",
    tags=["callflow"]
)


@router_calls.post(
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


@router_calls.get(
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


@router_calls.get(
    path="",
    response_model=CallListResponseSchema,
    description=CALL_SEARCH
)
async def search_calls(
        phone_number: str = Query(..., description="Номер телефона для поиска (в международном формате)"),
        session: AsyncSession = Depends(get_session_without_commit)
) -> CallListResponseSchema:
    """Поиск звонков по номеру телефона (звонящего или принимающего)"""
    try:
        call_service = CallService(session)
        calls = await call_service.search_calls_by_phone(phone_number)

        return CallListResponseSchema(
            calls=calls,
            total=len(calls)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при поиске: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )