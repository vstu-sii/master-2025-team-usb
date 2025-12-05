# backend/app/routers/meals.py
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db, async_session
from app.models import User, MealPlan, ShoppingItem, Meal
from app.schemas import MealResponse, MealReplaceRequest, ShoppingItemResponse, ShoppingListStatusResponse, MealUpdate
from app.auth import get_current_user
from app.services.llm_service import replace_meal, generate_shopping_list

router = APIRouter(prefix="/meals", tags=["meals"])

# Отслеживание активных операций
_replacing_meals: dict[str, bool] = {}  # "plan_id:dish_name" -> bool
_generating_shopping: dict[int, bool] = {}  # plan_id -> bool


async def _get_user_plan(plan_id: int, user: User, db: AsyncSession) -> MealPlan:
    result = await db.execute(
        select(MealPlan)
        .options(selectinload(MealPlan.meals), selectinload(MealPlan.shopping_items))
        .where(MealPlan.id == plan_id, MealPlan.user_id == user.id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.post("/{plan_id}/replace", response_model=list[MealResponse])
async def replace_dish(
    plan_id: int,
    data: MealReplaceRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Ключ для отслеживания
    replace_key = f"{plan_id}:{data.dish_name}"

    # Проверка на повторный запрос
    if replace_key in _replacing_meals:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Replacement already in progress for this dish"
        )

    try:
        _replacing_meals[replace_key] = True
        plan = await _get_user_plan(plan_id, user, db)
        alternatives = await replace_meal(plan, data.dish_name, data.reason, db)
        return alternatives
    finally:
        _replacing_meals.pop(replace_key, None)


@router.get("/{plan_id}/shopping-list", response_model=ShoppingListStatusResponse)
async def get_shopping_list(
    plan_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    plan = await _get_user_plan(plan_id, user, db)

    # Если список уже есть - возвращаем
    if plan.shopping_items:
        total = sum(item.estimated_price or 0 for item in plan.shopping_items)
        return ShoppingListStatusResponse(
            status="ready",
            items=plan.shopping_items,
            total_price=total
        )

    # Если генерация уже идёт
    if plan_id in _generating_shopping:
        return ShoppingListStatusResponse(status="generating", items=[], total_price=None)

    # Возвращаем pending, клиент должен вызвать generate
    return ShoppingListStatusResponse(status="pending", items=[], total_price=None)


@router.post("/{plan_id}/shopping-list/generate", response_model=ShoppingListStatusResponse)
async def generate_shopping_list_endpoint(
    plan_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Запуск генерации списка покупок"""
    # Проверка на повторный запрос
    if plan_id in _generating_shopping:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Shopping list generation already in progress"
        )

    plan = await _get_user_plan(plan_id, user, db)

    # Если уже есть - возвращаем
    if plan.shopping_items:
        total = sum(item.estimated_price or 0 for item in plan.shopping_items)
        return ShoppingListStatusResponse(
            status="ready",
            items=plan.shopping_items,
            total_price=total
        )

    try:
        _generating_shopping[plan_id] = True
        items = await generate_shopping_list(plan, db)
        total = sum(item.estimated_price or 0 for item in items)
        return ShoppingListStatusResponse(
            status="ready",
            items=items,
            total_price=total
        )
    finally:
        _generating_shopping.pop(plan_id, None)


@router.patch("/{meal_id}", response_model=MealResponse)
async def update_meal(
    meal_id: int,
    data: MealUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновление конкретного блюда (сохранение замены)"""
    # Ищем блюдо и проверяем права доступа через meal_plan -> user_id
    result = await db.execute(
        select(Meal)
        .join(MealPlan)
        .where(Meal.id == meal_id, MealPlan.user_id == user.id)
    )
    meal = result.scalar_one_or_none()

    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    # Обновляем поля
    meal.dish_name = data.dish_name
    if data.calories is not None:
        meal.calories = data.calories
    if data.recipe is not None:
        meal.recipe = data.recipe

    # Можно обновить и БЖУ, если ИИ их вернул
    # meal.protein = data.protein ...

    await db.commit()
    await db.refresh(meal)
    return meal


@router.delete("/{plan_id}/shopping-list")
async def clear_shopping_list(
    plan_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Очистить список покупок для перегенерации"""
    plan = await _get_user_plan(plan_id, user, db)

    for item in plan.shopping_items:
        await db.delete(item)

    await db.commit()
    return {"status": "cleared"}
