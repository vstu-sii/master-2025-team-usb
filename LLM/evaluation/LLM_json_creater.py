import json
import time
import os
from dotenv import load_dotenv
from openai import OpenAI
from prompt_tests import FEW_SHOT_PROMPT

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(BASE_DIR, "../data/FoodData.json")

# --- Чтение JSON файла с ингредиентами ---
with open(data_path, "r", encoding="utf-8") as f:
    dishes_list = json.load(f)

all_results = []

for idx, dish in enumerate(dishes_list, start=1):
    ingredients_text = dish["ingredients"]
    prompt = FEW_SHOT_PROMPT.format(ingredients=ingredients_text)

    print(f"\n🧠 Отправляем блюдо {idx}/{len(dishes_list)} в LLM...")
    print(f"Промпт для модели:\n{prompt}\n")  # Полный вывод промпта

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.3,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "Ты профессиональный диетолог. Отвечай строго в формате JSON.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        content = response.choices[0].message.content
        try:
            llm_output_json = json.loads(content)
        except json.JSONDecodeError:
            llm_output_json = {"error": "Invalid JSON", "raw": content}

        all_results.append(llm_output_json)
        print(f"✅ Блюдо {idx} обработано")

    except Exception as e:
        print(f"❌ Ошибка при обработке блюда {idx}: {e}")
        all_results.append({"error": str(e), "ingredients": ingredients_text})

    # --- Пауза 10 секунд перед следующим запросом ---
    print("⏱ Ждём 10 секунд перед следующим блюдом...")
    time.sleep(10)

# --- Сохраняем все ответы в один JSON ---
with open("FoodData_answers.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=4)

print("\n📂 Все блюда обработаны. Результаты сохранены в FoodData_answers.json")
