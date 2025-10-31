import json
import time
from dotenv import load_dotenv
from openai import OpenAI
from ml.evaluation.prompt_tests import FEW_SHOT_PROMPT
import os
import requests

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"


# --- Чтение JSON файла с ингредиентами ---
with open("../data/FoodData.json", "r", encoding="utf-8") as f:
    dishes_list = json.load(f)

all_results = []
# --- Параметры ---
provider = 2  # 1 - OpenAI, 2 - Mistral
retries = 3
delay = 10  # секунд между запросами

for idx, dish in enumerate(dishes_list, start=1):
    ingredients_text = dish["ingredients"]
    prompt = FEW_SHOT_PROMPT.format(ingredients=ingredients_text)

    print(f"\n🧠 Отправляем блюдо {idx}/{len(dishes_list)} в LLM...")
    print(f"Промпт для модели:\n{prompt}\n")  # Полный вывод промпта

    for attempt in range(1, retries + 1):
        try:
            if provider == 1:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    temperature=0.3,
                    messages=[
                        {"role": "system", "content": "Ты профессиональный диетолог. Отвечай строго в формате JSON."},
                        {"role": "user", "content": prompt}
                    ]
                )
                content = response.choices[0].message.content
                try:
                    output = json.loads(content)
                except json.JSONDecodeError:
                    output = {"error": "Invalid JSON", "raw": content}


            elif provider == 2:

                headers = {

                    "Authorization": f"Bearer {MISTRAL_API_KEY}",

                    "Content-Type": "application/json",

                }

                # JSON Schema для структуры вывода

                schema = {

                    "type": "object",

                    "properties": {

                        "category": {"type": "string"},

                        "calories": {"type": "number"},

                        "protein": {"type": "number"},

                        "fats": {"type": "number"},

                        "carb": {"type": "number"},

                        "lac_int": {"type": "string"},

                    },

                    "required": ["category", "calories", "protein", "fats", "carb", "lac_int"]

                }

                payload = {

                    "model": "mistral-medium",  # <--- правильная модель

                    "messages": [

                        {"role": "system",
                         "content": "You are a helpful nutrition assistant. Output must be valid JSON."},

                        {"role": "user", "content": prompt},

                    ],

                    "response_format": {

                        "type": "json_schema",

                        "json_schema": {

                            "name": "nutrition_response",

                            "schema": schema

                        }

                    },

                    "temperature": 0.3,

                    "max_tokens": 1000,

                }

                response = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=payload)

                if response.status_code == 200:

                    resp_json = response.json()

                    content = resp_json["choices"][0]["message"]["content"]

                    try:

                        output = json.loads(content)

                    except json.JSONDecodeError:

                        output = {"error": "Invalid JSON", "raw": content}


                else:

                    raise ValueError(f"Mistral API error: {response.status_code} - {response.text}")

            else:
                raise ValueError("Некорректный provider. 1 - OpenAI, 2 - Mistral")

            all_results.append(output)
            print(f"✅ Блюдо {idx} обработано")
            break  # успешно, выходим из retries

        except Exception as e:
            print(f"❌ Ошибка блюда {idx}, попытка {attempt}/{retries}: {e}")
            if attempt < retries:
                print(f"⏱ Ждём {delay} секунд перед повторной попыткой...")
                time.sleep(delay)
            else:
                all_results.append({"error": str(e), "ingredients": ingredients_text})

        # --- Пауза перед следующим блюдом ---
    print(f"⏱ Ждём {delay} секунд перед следующим блюдом...")
    time.sleep(delay)

# --- Сохраняем все ответы в один JSON ---
with open("FoodData_answers_mistral.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=4)

print("\n📂 Все блюда обработаны. Результаты сохранены в FoodData_answers.json")
