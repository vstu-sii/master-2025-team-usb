# backend/app/schemas.py
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# Auth
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str | None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# MealPlan
class MealPlanCreate(BaseModel):
    goal: str
    calories: int = Field(ge=1000, le=6000)
    budget: float = Field(ge=0)
    preferences: str | None = None
    allergies: str | None = None


class MealPlanResponse(BaseModel):
    id: int
    goal: str
    calories: int
    budget: float
    preferences: str | None
    allergies: str | None
    total_days: int
    status: str  # NEW: статус генерации
    created_at: datetime
    meals: list["MealResponse"] = []

    class Config:
        from_attributes = True


# Meal
class MealResponse(BaseModel):
    id: int | None = None  # <--- БЫЛО: id: int. СТАЛО: int | None = None
    day_of_week: str
    meal_type: str
    dish_name: str
    recipe: str | None
    calories: int | None
    protein: int | None
    fat: int | None
    carbs: int | None

    class Config:
        from_attributes = True


class MealUpdate(BaseModel):
    dish_name: str
    calories: int | None = None
    protein: int | None = None
    fat: int | None = None
    carbs: int | None = None
    recipe: str | None = None


class MealReplaceRequest(BaseModel):
    dish_name: str
    reason: str | None = None


# Shopping - UPDATED
class ShoppingItemResponse(BaseModel):
    id: int | None = None
    item_name: str | None
    category: str | None
    quantity: str | None
    estimated_price: float | None = None  # NEW: стоимость
    checked: bool = False

    class Config:
        from_attributes = True


# NEW: Статус генерации списка покупок
class ShoppingListStatusResponse(BaseModel):
    status: str  # pending, generating, ready, error
    items: list[ShoppingItemResponse] = []
    total_price: float | None = None


# LLM
class LLMLogResponse(BaseModel):
    id: int
    request_json: dict | None
    response_json: dict | None
    created_at: datetime

    class Config:
        from_attributes = True


# Error
class ErrorResponse(BaseModel):
    error: str
    message: str
