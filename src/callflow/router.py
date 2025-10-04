from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from description import CALL_POST, CALL_GET
from src.callflow.schemas import CallIDResponse, CallCreateSchema, CallResponseSchema
from src.callflow.services import add_call, get_one_record
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
    try:
        new_call = await add_call(session, **call.model_dump())
        return CallIDResponse(id=new_call.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    path="/{call_id}",
    # response_model=CallResponseSchema,
    description=CALL_GET
)
async def get_call(
        call_id: int,
        session: AsyncSession = Depends(get_session_without_commit)
):
    filters = {"id": call_id}
    return await get_one_record(session, **filters)
