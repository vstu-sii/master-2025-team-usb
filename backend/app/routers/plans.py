# backend/app/routers/plans.py
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import set_committed_value

from app.database import get_db, async_session
from app.models import User, MealPlan
from app.schemas import MealPlanCreate, MealPlanResponse
from app.auth import get_current_user
from app.services.llm_service import generate_meal_plan

router = APIRouter(prefix="/plans", tags=["plans"])

# Словарь для отслеживания активных задач генерации (plan_id -> bool)
_generating_plans: dict[int, bool] = {}


async def _background_generate_plan(plan_id: int, user_id: int):
    """Фоновая генерация плана питания"""
    async with async_session() as db:
        try:
            result = await db.execute(
                select(MealPlan).where(MealPlan.id == plan_id)
            )
            plan = result.scalar_one_or_none()

            if not plan:
                return

            plan.status = "generating"
            await db.commit()

            await generate_meal_plan(plan, db)

            plan.status = "ready"
            await db.commit()

        except Exception as e:
            print(f"Background generation error: {e}")
            try:
                result = await db.execute(
                    select(MealPlan).where(MealPlan.id == plan_id)
                )
                plan = result.scalar_one_or_none()
                if plan:
                    plan.status = "error"
                    await db.commit()
            except:
                pass
        finally:
            _generating_plans.pop(plan_id, None)


@router.get("", response_model=list[MealPlanResponse])
async def get_plans(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MealPlan)
        .options(selectinload(MealPlan.meals))
        .where(MealPlan.user_id == user.id)
        .order_by(MealPlan.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=MealPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    data: MealPlanCreate,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    plan = MealPlan(
        user_id=user.id,
        goal=data.goal,
        calories=data.calories,
        budget=data.budget,
        preferences=data.preferences,
        allergies=data.allergies,
        status="pending"
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)

    # --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
    # Вместо plan.meals = [] используем set_committed_value.
    # Это "насильно" устанавливает значение без запроса к БД.
    set_committed_value(plan, "meals", [])
    # -------------------------

    # Запускаем генерацию в фоне
    _generating_plans[plan.id] = True
    asyncio.create_task(_background_generate_plan(plan.id, user.id))

    return plan


@router.get("/{plan_id}", response_model=MealPlanResponse)
async def get_plan(
    plan_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MealPlan)
        .options(selectinload(MealPlan.meals))
        .where(MealPlan.id == plan_id, MealPlan.user_id == user.id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.get("/{plan_id}/status")
async def get_plan_status(
    plan_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Эндпоинт для проверки статуса генерации"""
    result = await db.execute(
        select(MealPlan).where(MealPlan.id ==
                               plan_id, MealPlan.user_id == user.id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    return {"status": plan.status, "is_generating": plan.id in _generating_plans}


@router.post("/{plan_id}/regenerate", response_model=MealPlanResponse)
async def regenerate_plan(
    plan_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Перегенерация плана (защита от повторных запросов)"""
    if plan_id in _generating_plans:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Plan generation is already in progress"
        )

    result = await db.execute(
        select(MealPlan)
        .options(selectinload(MealPlan.meals))
        .where(MealPlan.id == plan_id, MealPlan.user_id == user.id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    for meal in plan.meals:
        await db.delete(meal)

    plan.status = "pending"
    await db.commit()

    # Запускаем генерацию в фоне
    _generating_plans[plan.id] = True
    asyncio.create_task(_background_generate_plan(plan.id, user.id))

    await db.refresh(plan)
    # Здесь тоже на всякий случай, так как meals мы удалили
    set_committed_value(plan, "meals", [])

    return plan


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MealPlan).where(MealPlan.id ==
                               plan_id, MealPlan.user_id == user.id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    _generating_plans.pop(plan_id, None)

    await db.delete(plan)
    await db.commit()
