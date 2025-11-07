# ml/models/schemas.py

from pydantic import BaseModel, Field
from typing import List

class Meal(BaseModel):
    meal_type: str
    dish_name: str
    calories: int
    protein: int
    fat: int
    carbs: int
    recipe: str

class DailySummary(BaseModel):
    total_calories: int
    total_protein: float
    total_fat: float
    total_carbs: float

class DayPlan(BaseModel):
    day_of_week: str
    daily_summary: dict
    meals: List[Meal]

class WeekPlan(BaseModel):
    """Структура для недельного плана"""
    weekly_plan: List[DayPlan] = Field(..., description="План питания на 7 дней")
class MealReplacement(BaseModel):
    day_of_week: str
    meal_type: str
    old_dish: str
    new_dish: str
    new_calories: int
