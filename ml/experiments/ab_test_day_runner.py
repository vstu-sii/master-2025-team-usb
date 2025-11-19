import csv
import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv
import logging

from langfuse import observe
from langfuse.openai import OpenAI
from ml.models.schemas import MealReplacement

from ml.models.schemas import WeekPlan



load_dotenv()

# -----------------------------------------
# Logging
# -----------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("AB_TEST")

# -------------------------
# Модели
# -------------------------
client_openai = OpenAI()  # GPT-4o-mini генерация плана

client_judge = OpenAI()

# -------------------------
# Пути
# -------------------------
BASE_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = BASE_DIR / "prompts"

PROMPT_A = (PROMPTS_DIR / "replace_A.txt").read_text(encoding="utf-8")
PROMPT_B = (PROMPTS_DIR / "replace_B.txt").read_text(encoding="utf-8")
#PROMPT_V2 = (BASE_DIR / "prompts_v2" / "replace_meal_v2.txt").read_text(encoding="utf-8")

RESULTS_CSV = BASE_DIR / "ab_test_day_v2.csv"
# -------------------------
# Schema судьи (числовые оценки)
# -------------------------
SCHEMA = {
    "type": "object",
    "properties": {
        "calorie_match": {"type": "number"},
        "meal_type_match": {"type": "number"},
        "preference_match": {"type": "number"},
        "allergy_safety": {"type": "number"},
        "replacement_quality": {"type": "number"},
        "overall": {"type": "number"},
        "comments": {"type": "string"}
    },
    "required": [
        "calorie_match",
        "meal_type_match",
        "preference_match",
        "allergy_safety",
        "replacement_quality",
        "overall",
        "comments"
    ]
}

# -------------------------
# Промпт для судьи
# -------------------------
JUDGE_PROMPT = """
Ты — эксперт по оценке качества замены блюда.

Оцени JSON MealReplacement по шкале 0–10:

1) calorie_match — точность калорийности замены.
   0–3: большие отклонения
   4–6: умеренно
   7–10: почти совпадает

2) meal_type_match — соблюдение meal_type.
   0–3: неверно
   4–6: частично
   7–10: правильно

3) preference_match — соблюдение предпочтений.
   0–3: не соблюдены
   4–6: частично
   7–10: полностью

4) allergy_safety — безопасность.
   0–3: содержит аллерген
   4–6: возможно
   7–10: безопасно

5) replacement_quality — логичность и полезность блюда.
   0–3: плохая замена
   4–6: приемлемо
   7–10: высокая

6) overall — общая оценка замены (интегральная).
   0–3: плохая
   4–6: нормальная
   7–10: отличная

Верни JSON по схеме.
"""

@observe(as_type="generation")
def generate_replacement(prompt, user_data, variant):
    response = client_openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "Ты диетолог."},
                  {"role": "user", "content": prompt.format(**user_data)}],
        response_format={"type": "json_schema",
                         "json_schema": {
                             "name": "MealReplacement",
                             "schema": MealReplacement.model_json_schema()
                         }}
    )
    content = response.choices[0].message.content
    plan = MealReplacement.model_validate_json(content)
    return plan.model_dump()

@observe(as_type="evaluator")
def evaluate_replacement(data: dict):
    logger.info("→ Оценка замены блюда (GPT-4o)...")

    response = client_judge.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Ты помощник-оценщик, отвечай строго JSON."},
            {"role": "user",
             "content": JUDGE_PROMPT + "\n\nMealReplacement:\n" + json.dumps(data, ensure_ascii=False)}
        ],
        temperature=0.1,
        max_tokens=400,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "MealReplacementEvaluation",
                "schema": SCHEMA
            }
        }
    )

    content = response.choices[0].message.content
    return json.loads(content)


def avg_score(scores):
    fields = ["calorie_match", "meal_type_match", "preference_match",
              "allergy_safety", "replacement_quality", "overall"]
    return sum(scores[f] for f in fields) / len(fields)

def save_csv(variant, scores, avg):
    exists = RESULTS_CSV.exists()
    with open(RESULTS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["timestamp", "variant",
                             "calorie_match", "meal_type_match", "preference_match",
                             "allergy_safety", "replacement_quality", "overall",
                             "avg_score"])
        writer.writerow([
            time.strftime("%Y-%m-%d %H:%M:%S"), variant,
            scores["calorie_match"],
            scores["meal_type_match"],
            scores["preference_match"],
            scores["allergy_safety"],
            scores["replacement_quality"],
            scores["overall"],
            avg
        ])

def run_replacement_ab(user_data):
    # A
    dishA = generate_replacement(PROMPT_A, user_data, "A")
    scoreA = evaluate_replacement(dishA)
    avgA = avg_score(scoreA)
    save_csv("A", scoreA, avgA)

    # B
    dishB = generate_replacement(PROMPT_V2, user_data, "B")
    scoreB = evaluate_replacement(dishB)
    avgB = avg_score(scoreB)
    save_csv("B", scoreB, avgB)

    winner = "A" if avgA > avgB else "B"
    return {"A": avgA, "B": avgB, "winner": winner}

if __name__ == "__main__":
    user = {
        "day_of_week": "Среда",
        "meal_type": "Обед",
        "old_dish": "Овощной суп",
        "meal_calories": 250,
        "goal": "похудение",
        "calories": 1800,
        "budget": 1500,
        "preferences": "вегетарианская диета",
        "allergies": "орехи"
    }
    print(run_replacement_ab(user))
