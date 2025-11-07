from fastapi import FastAPI, HTTPException, APIRouter, Query
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, field_validator
from ml.models.baseline import baseline_model
from langfuse import propagate_attributes

app = FastAPI(title="Meal Plan LLM API")

class UserData(BaseModel):
    goal: str
    calories: int
    budget: float
    preferences: str = ""
    allergies: str = ""

    # --- Предобработка ---
    @field_validator("goal", "preferences", "allergies", mode="before")
    @classmethod
    def clean_text_fields(cls, v):
        v = (v or "").strip().lower()
        return v if v else "отсутствуют"

    # --- Валидация калорий ---
    @field_validator("calories")

    @classmethod
    def validate_calories(cls, v):
        if not (1000 <= v <= 6000):
            raise ValueError("Калорийность должна быть в диапазоне от 1000 до 6000")
        return v

    # --- Валидация бюджета ---
    @field_validator("budget")
    @classmethod
    def validate_budget(cls, v):
        if v < 0:
            raise ValueError("Бюджет не может быть отрицательным")
        return v

class MealReplacementData(BaseModel):
    day_of_week: str
    meal_type: str
    old_dish: str
    meal_calories: int
    goal: str
    calories: int
    budget: float
    preferences: str = ""
    allergies: str = ""

@app.post("/replace_meal/")
async def replace_meal(meal_data: MealReplacementData, user_id: str = Query(..., description="ID пользователя")):
    """
    Замена блюда для конкретного дня.
    """
    try:
        cleaned_data = meal_data.model_dump()
        with propagate_attributes(user_id=user_id):
            result = await baseline_model.replace_meal(cleaned_data, user_id)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post(
    "/generate_meal_plan/",
    response_model=dict,
    summary="Генерация недельного плана питания",
    description="Принимает параметры пользователя и возвращает JSON с планом питания на неделю.",
    response_description="JSON с недельным планом питания"
)

@app.post("/generate_meal_plan/")
async def generate_meal_plan(user_data: UserData, user_id: str = Query(..., description="ID пользователя")):
    """
    Эндпоинт генерации плана питания.
    Предобработка и валидация выполняются через Pydantic.
    """
    try:
        cleaned_data = user_data.model_dump()
        with propagate_attributes(user_id=user_id):
            result = await baseline_model.generate(cleaned_data, user_id)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
