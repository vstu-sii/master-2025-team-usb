# ml/models/baseline.py

import os
import json
import time
from dotenv import load_dotenv
import requests
from langfuse import observe  # единственная связь с Langfuse
from openai import OpenAI
from ..prompt_templates import MEAL_PLAN_TEMPLATE_DAY, MEAL_REPLACEMENT_TEMPLATE

load_dotenv()

# --- Настройка OpenAI ---
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# --- Настройка Mistral ---
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"


class BaselineModel:
    """
    LLM модель с выбором между OpenAI и Mistral.
    provider:
      1 = OpenAI (ChatGPT)
      2 = Mistral
    """

    def __init__(self, model_name="gpt-4o-mini", mistral_model="mistral-medium", temperature=0.7, max_tokens=3000):
        self.model_name = model_name
        self.mistral_model = mistral_model
        self.temperature = temperature
        self.max_tokens = max_tokens
    def build_prompt_day(self, day_data: dict) -> str:
        """Формируем промпт для одного дня."""
        return MEAL_PLAN_TEMPLATE_DAY.format(**day_data)

    def _call_openai(self, prompt: str) -> str:
        """Вызов модели OpenAI"""
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs strict JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content.strip()

    def _call_mistral(self, prompt: str) -> str:
        """Вызов модели Mistral"""
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.mistral_model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that outputs strict JSON."},
                {"role": "user", "content": prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        response = requests.post(MISTRAL_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    @observe(as_type="generation")
    def generate(self, user_data: dict, user_id: str, provider: int = 1, retries: int = 3, delay: int = 5) -> dict:
        """
        Генерация недельного плана день за днем.
        Langfuse автоматически трассирует все вызовы LLM через декоратор.
        """
        weekly_plan = []

        days = [
            {"day_of_week": d, **user_data}
            for d in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        ]

        for day_idx, day_data in enumerate(days, start=1):
            prompt = self.build_prompt_day(day_data)
            raw_output = ""

            for attempt in range(1, retries + 1):
                time.sleep(delay)
                try:
                    if provider == 1:
                        raw_output = self._call_openai(prompt)
                    elif provider == 2:
                        raw_output = self._call_mistral(prompt)
                    else:
                        raise ValueError("Некорректное значение provider. Используйте 1 (OpenAI) или 2 (Mistral).")
                    clean_output = raw_output
                    if clean_output.startswith("```json"):
                        clean_output = clean_output[len("```json"):].strip()
                    if clean_output.endswith("```"):
                        clean_output = clean_output[:-3].strip()

                    day_plan = json.loads(clean_output)
                    weekly_plan.append(day_plan)

                    print(f"День {day_idx}/7 обработан успешно")
                    break  # выход из цикла попыток

                except Exception as e:
                    print(f"Ошибка генерации дня {day_idx} (attempt {attempt}/{retries}): {e}")
                    if attempt < retries:
                        time.sleep(delay ** attempt)
                    else:
                        weekly_plan.append({
                            "error": str(e),
                            "raw_output": raw_output,
                            "day_of_week": day_data.get("day_of_week")
                        })

        return {"weekly_plan": weekly_plan}

    def replace_meal(self, data: dict) -> dict:
        """
        Генерация замены блюда на день с использованием шаблона MEAL_REPLACEMENT_TEMPLATE
        """
        prompt = MEAL_REPLACEMENT_TEMPLATE.format(**data)

        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Ты помощник, генерирующий JSON для замены блюда."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500,
            )

            raw_output = response.choices[0].message.content.strip()
            if raw_output.startswith("```json"):
                raw_output = raw_output[len("```json"):].strip()
            if raw_output.endswith("```"):
                raw_output = raw_output[:-3].strip()

            return json.loads(raw_output)

        except Exception as e:
            return {
                "day_of_week": data['day_of_week'],
                "meal_type": data['meal_type'],
                "old_dish": data['old_dish'],
                "new_dish": "NONE",
                "new_calories": 0,
                "error": str(e)
            }


baseline_model = BaselineModel()
