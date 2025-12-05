from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, LLMRequest
from app.schemas import LLMLogResponse
from app.auth import get_current_user

router = APIRouter(prefix="/llm", tags=["llm"])


@router.get("/logs", response_model=list[LLMLogResponse])
async def get_llm_logs(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(LLMRequest)
        .where(LLMRequest.user_id == user.id)
        .order_by(LLMRequest.created_at.desc())
        .limit(50)
    )
    return result.scalars().all()