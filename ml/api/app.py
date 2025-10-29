from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from ml.models.baseline import baseline_model

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

class MealReplacementRequest(BaseModel):
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
def replace_meal(req: MealReplacementRequest):
    """
    Заменяет одно блюдо в дневном плане.
    Если подходящей замены не найдено, возвращает "NONE".
    """
    try:
        input_data = req.model_dump()
        result = baseline_model.replace_meal(input_data)

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
async def generate_meal_plan(user_data: UserData):
    """
    Эндпоинт генерации плана питания.
    Предобработка и валидация выполняются через Pydantic.
    """
    try:
        cleaned_data = user_data.model_dump()
        result = baseline_model.generate(cleaned_data, user_id="user_123")

        if "error" in result:
            raise HTTPException(status_code=500, detail=result)

        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
