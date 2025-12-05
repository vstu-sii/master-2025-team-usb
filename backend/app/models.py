# backend/app/models.py
from datetime import datetime
from sqlalchemy import Integer, String, Text, Numeric, Boolean, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)

    meal_plans: Mapped[list["MealPlan"]] = relationship(
        back_populates="user", cascade="all, delete-orphan")
    llm_requests: Mapped[list["LLMRequest"]] = relationship(
        back_populates="user", cascade="all, delete-orphan")


class MealPlan(Base):
    __tablename__ = "meal_plans"
    __table_args__ = (
        CheckConstraint("calories BETWEEN 1000 AND 6000",
                        name="check_calories"),
        CheckConstraint("budget >= 0", name="check_budget"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    goal: Mapped[str] = mapped_column(String(255), nullable=False)
    calories: Mapped[int] = mapped_column(Integer)
    budget: Mapped[float] = mapped_column(Numeric(10, 2))
    preferences: Mapped[str | None] = mapped_column(Text)
    allergies: Mapped[str | None] = mapped_column(Text)
    total_days: Mapped[int] = mapped_column(Integer, default=7)
    # NEW: pending, generating, ready, error
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="meal_plans")
    meals: Mapped[list["Meal"]] = relationship(
        back_populates="meal_plan", cascade="all, delete-orphan")
    shopping_items: Mapped[list["ShoppingItem"]] = relationship(
        back_populates="meal_plan", cascade="all, delete-orphan")
    llm_requests: Mapped[list["LLMRequest"]] = relationship(
        back_populates="meal_plan", cascade="all, delete-orphan")


class Meal(Base):
    __tablename__ = "meals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    meal_plan_id: Mapped[int] = mapped_column(ForeignKey(
        "meal_plans.id", ondelete="CASCADE"), nullable=False)
    day_of_week: Mapped[str] = mapped_column(String(20), nullable=False)
    meal_type: Mapped[str] = mapped_column(String(50), nullable=False)
    dish_name: Mapped[str] = mapped_column(String(255), nullable=False)
    calories: Mapped[int | None] = mapped_column(Integer)
    protein: Mapped[int | None] = mapped_column(Integer)
    fat: Mapped[int | None] = mapped_column(Integer)
    carbs: Mapped[int | None] = mapped_column(Integer)
    recipe: Mapped[str | None] = mapped_column(Text)

    meal_plan: Mapped["MealPlan"] = relationship(back_populates="meals")


class ShoppingItem(Base):
    __tablename__ = "shopping_lists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    meal_plan_id: Mapped[int] = mapped_column(ForeignKey(
        "meal_plans.id", ondelete="CASCADE"), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100))
    item_name: Mapped[str | None] = mapped_column(String(255))
    quantity: Mapped[str | None] = mapped_column(String(50))
    estimated_price: Mapped[float | None] = mapped_column(
        Numeric(10, 2))  # NEW: стоимость
    checked: Mapped[bool] = mapped_column(Boolean, default=False)

    meal_plan: Mapped["MealPlan"] = relationship(
        back_populates="shopping_items")


class LLMRequest(Base):
    __tablename__ = "llm_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"))
    meal_plan_id: Mapped[int | None] = mapped_column(
        ForeignKey("meal_plans.id", ondelete="CASCADE"))
    request_json: Mapped[dict | None] = mapped_column(JSONB)
    response_json: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(50), default="success")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="llm_requests")
    meal_plan: Mapped["MealPlan"] = relationship(back_populates="llm_requests")
