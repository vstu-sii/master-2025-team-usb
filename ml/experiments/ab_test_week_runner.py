import csv
import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv
import logging

from langfuse import observe
from langfuse.openai import OpenAI

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
# GPT-4o как judge
client_judge = OpenAI()

# -------------------------
# Пути
# -------------------------
BASE_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = BASE_DIR / "prompts"

PROMPT_A = (PROMPTS_DIR / "week_A.txt").read_text(encoding="utf-8")
PROMPT_B = (PROMPTS_DIR / "week_B.txt").read_text(encoding="utf-8")
#PROMPT_V2 = (BASE_DIR / "prompts_v2" / "generate_plan_v2.txt").read_text(encoding="utf-8")

RESULTS_CSV = BASE_DIR / "ab_test_week_v2.csv"
# -------------------------
# Schema судьи (числовые оценки)
# -------------------------
SCHEMA = {
    "type": "object",
    "properties": {
        "goal_match": {"type": "number"},
        "meal_type_correctness": {"type": "number"},
        "calorie_match": {"type": "number"},
        "preferences_respected": {"type": "number"},
        "allergies_respected": {"type": "number"},
        "diversity": {"type": "number"},
        "comments": {"type": "string"}
    },
    "required": [
        "goal_match", "meal_type_correctness", "calorie_match",
        "preferences_respected", "allergies_respected",
        "diversity", "comments"
    ]
}

# -------------------------
# Промпт для судьи
# -------------------------
JUDGE_PROMPT = """
Оцени план питания по следующим критериям (каждый 0–10):

1) goal_match — соответствие цели пользователя.
   0–3 = плохо, 4–6 = приемлемо, 7–10 = отлично.

2) meal_type_correctness — корректность типов блюд (завтрак/обед/ужин).
   0–3 = неверно, 4–6 = частично, 7–10 = корректно.

3) calorie_match — соответствие целевой калорийности.
   0–3 = сильно отклоняется, 4–6 = нормально, 7–10 = отлично.

4) preferences_respected — соблюдение предпочтений пользователя.
   0–3 = не соблюдается, 4–6 = частично, 7–10 = соблюдается.

5) allergies_respected — безопасность для аллергий.
   0–3 = есть опасные ингредиенты, 4–6 = сомнения, 7–10 = безопасно.

6) diversity — разнообразие рациона.
   0–3 = однообразно, 4–6 = умеренно, 7–10 = разнообразно.

Верни JSON строго по схеме.
"""

# -----------------------------------------
# Generate plan
# -----------------------------------------
@observe(as_type="generation")
def generate_plan(prompt: str, user_data: dict, variant: str):
    logger.info(f"=== Генерация плана ({variant})... ===")

    response = client_openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Ты профессиональный диетолог."},
            {"role": "user", "content": prompt.format(**user_data)}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "WeekPlan",
                "schema": WeekPlan.model_json_schema()
            }
        }
    )

    raw = response.choices[0].message.content
    plan = WeekPlan.model_validate_json(raw)

    logger.info(f"[{variant}] План успешно сгенерирован.")
    return plan.model_dump()


@observe(as_type="evaluator")
def evaluate_plan(plan_json):
    logger.info("→ Оценка через GPT-4o...")

    response = client_judge.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Ты помощник-оценщик. Отвечай строго JSON."},
            {"role": "user",
             "content": JUDGE_PROMPT + "\n\nПлан:\n" + json.dumps(plan_json, ensure_ascii=False)}
        ],
        temperature=0.1,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "MealPlanEvaluation",
                "schema": SCHEMA
            }
        }
    )

    return json.loads(response.choices[0].message.content)



# -----------------------------------------
# Compute mean score
# -----------------------------------------
def compute_mean_score(scores: dict) -> float:
    fields = [
        "goal_match",
        "meal_type_correctness",
        "calorie_match",
        "preferences_respected",
        "allergies_respected",
        "diversity"
    ]
    return sum(scores[f] for f in fields) / len(fields)


# -----------------------------------------
# Save CSV
# -----------------------------------------
def save_csv(variant: str, scores: dict, avg: float):
    file_exists = RESULTS_CSV.exists()

    with open(RESULTS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "timestamp", "variant",
                "goal_match", "meal_type_correctness", "calorie_match",
                "preferences_respected", "allergies_respected", "diversity",
                "avg_score"
            ])

        writer.writerow([
            time.strftime("%Y-%m-%d %H:%M:%S"),
            variant,
            scores["goal_match"],
            scores["meal_type_correctness"],
            scores["calorie_match"],
            scores["preferences_respected"],
            scores["allergies_respected"],
            scores["diversity"],
            avg
        ])


# -----------------------------------------
# A/B Test
# -----------------------------------------
def run_ab_test(user_data):
    logger.info("=== START A/B TEST ===")

    # ---- A ----
    planA = generate_plan(PROMPT_A, user_data, "A")
    scoreA = evaluate_plan(planA)

    if scoreA is None:
        logger.error("Оценка A не получена! Пропуск.")
        return

    avgA = compute_mean_score(scoreA)

    logger.info(f"Промпт A: оценки = "
                f"[{scoreA['goal_match']}, {scoreA['meal_type_correctness']}, "
                f"{scoreA['calorie_match']}, {scoreA['preferences_respected']}, "
                f"{scoreA['allergies_respected']}, {scoreA['diversity']}], "
                f"средний балл = {avgA:.2f}")

    save_csv("A", scoreA, avgA)

    # ---- B ----
    planB = generate_plan(PROMPT_B, user_data, "B")
    scoreB = evaluate_plan(planB)

    if scoreB is None:
        logger.error("Оценка B не получена!")
        return

    avgB = compute_mean_score(scoreB)

    logger.info(f"Промпт B: оценки = "
                f"[{scoreB['goal_match']}, {scoreB['meal_type_correctness']}, "
                f"{scoreB['calorie_match']}, {scoreB['preferences_respected']}, "
                f"{scoreB['allergies_respected']}, {scoreB['diversity']}], "
                f"средний балл = {avgB:.2f}")

    save_csv("B", scoreB, avgB)

    # Winner
    winner = "A" if avgA > avgB else "B"
    logger.info(f"ПОБЕДИТЕЛЬ: Промпт {winner}")

    return {"A": avgA, "B": avgB, "winner": winner}


# -----------------------------------------
# CLI
# -----------------------------------------
if __name__ == "__main__":
    user = {
        "goal": "похудение",
        "calories": 1800,
        "budget": 1500,
        "preferences": "вегетарианская диета",
        "allergies": "орехи"
    }

    print(run_ab_test(user))
