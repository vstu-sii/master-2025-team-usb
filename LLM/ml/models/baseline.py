from dotenv import load_dotenv
from langfuse import observe
from openai import OpenAI
import os
import json
from ..prompt_templates import MEAL_PLAN_TEMPLATE

load_dotenv()  # Загружает переменные из .env в os.environ

# Пример доступа:
openai_api_key = os.environ.get("OPENAI_API_KEY")
langfuse_secret = os.environ.get("LANGFUSE_SECRET_KEY")

# Настройка клиента OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class BaselineModel:
    """
    Простейшая LLM модель с поддержкой Langfuse.
    """

    def __init__(self, model_name="gpt-4o-mini", temperature=0.7):
        self.model_name = model_name
        self.temperature = temperature

    @observe(as_type="generation")
    def generate(self, user_data: dict, user_id: str) -> dict:
        """
        Генерация недельного плана питания.
        """
        # Формируем промпт
        prompt = MEAL_PLAN_TEMPLATE.format(**user_data)

        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
            )

            raw_output = response.choices[0].message.content

            # --- Очищаем JSON от тройных кавычек ---
            clean_output = raw_output.strip()
            if clean_output.startswith("```json"):
                clean_output = clean_output[len("```json"):].strip()
            if clean_output.endswith("```"):
                clean_output = clean_output[:-3].strip()

            # Пытаемся распарсить JSON
            try:
                parsed_output = json.loads(clean_output)
                return parsed_output
            except json.JSONDecodeError:
                return {"error": "Failed to decode JSON", "raw_output": raw_output}

        except Exception as e:
            return {"error": str(e), "raw_output": ""}

# Создаём экземпляр модели
baseline_model = BaselineModel()
