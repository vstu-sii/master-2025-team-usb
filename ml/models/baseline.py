# ml/models/baseline.py

import os
import time
from dotenv import load_dotenv
from langfuse import observe, propagate_attributes
from langfuse.openai import AsyncOpenAI

from ..prompt_templates import MEAL_PLAN_TEMPLATE_WEEK, MEAL_REPLACEMENT_TEMPLATE
from .schemas import WeekPlan, MealReplacement

load_dotenv()

openai = AsyncOpenAI()
class BaselineModel:
    """
    Модель генерации недельного плана питания и замены блюд.
    Интеграция с Langfuse через @observe и structured outputs.
    """

    def __init__(self, model_name="gpt-4o-mini", temperature=0.7, max_tokens=4000):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    # ------------------------------------------------------------------
    # ГЕНЕРАЦИЯ НЕДЕЛЬНОГО ПЛАНА
    # ------------------------------------------------------------------
    @observe(as_type="generation")
    async def generate(
        self,
        user_data: dict,
        user_id: str = "anonymous",
        retries: int = 3,
        delay: int = 3,
    ) -> dict:
        """
        Генерация недельного плана питания за один вызов.
        Использует промпт MEAL_PLAN_TEMPLATE_WEEK.
        """
        with propagate_attributes(user_id=str(user_id)):
            prompt = MEAL_PLAN_TEMPLATE_WEEK.format(**user_data)
            raw_output = ""

            for attempt in range(1, retries + 1):
                try:
                    response = await openai.chat.completions.create(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": "Ты профессиональный диетолог и нутриционист."},
                            {"role": "user", "content": prompt},
                        ],
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        response_format={
                            "type": "json_schema",
                            "json_schema": {
                                "name": "WeekPlan",
                                "schema": WeekPlan.model_json_schema(),
                            },
                        },
                    )

                    content = response.choices[0].message.content

                    if isinstance(content, str):
                        parsed = WeekPlan.model_validate_json(content)
                    else:
                        parsed = WeekPlan(**content)

                    print("Недельный план успешно сгенерирован")
                    return parsed.model_dump()

                except Exception as e:
                    print(f"Ошибка генерации недельного плана (попытка {attempt}/{retries}): {e}")
                    if attempt < retries:
                        time.sleep(delay)
                    else:
                        return {
                            "error": str(e),
                            "raw_output": raw_output,
                        }

    # ------------------------------------------------------------------
    # ЗАМЕНА БЛЮДА
    # ------------------------------------------------------------------
    @observe(as_type="generation")
    async def replace_meal(
        self,
        data: dict,
        user_id: str = "anonymous",
    ) -> dict:
        """
        Генерация замены блюда.
        Использует промпт MEAL_REPLACEMENT_TEMPLATE.
        """
        with propagate_attributes(user_id=str(user_id)):
            prompt = MEAL_REPLACEMENT_TEMPLATE.format(**data)

            try:
                response = await openai.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "Ты профессиональный диетолог и планировщик питания."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.5,
                    max_tokens=800,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": "MealReplacement",
                            "schema": MealReplacement.model_json_schema(),
                        },
                    },
                )

                content = response.choices[0].message.content

                if isinstance(content, str):
                    parsed = MealReplacement.model_validate_json(content)
                else:
                    parsed = MealReplacement(**content)

                print("Замена блюда успешно сгенерирована")
                return parsed.model_dump()

            except Exception as e:
                print(f"Ошибка при замене блюда: {e}")
                return {
                    "day_of_week": data.get("day_of_week"),
                    "meal_type": data.get("meal_type"),
                    "old_dish": data.get("old_dish"),
                    "new_dish": "NONE",
                    "new_calories": 0,
                    "error": str(e),
                }


baseline_model = BaselineModel()
