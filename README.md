Отлично 👍
Вот готовый содержательный `README.md` (полностью оформленный, можно вставить в репозиторий как есть):

---

# 🧠 AI Meal Planner — умный планировщик питания

AI Meal Planner — это **интеллектуальный сервис питания**, который с помощью **LLM (GPT-4o-mini)** создает персонализированные планы питания с учетом целей, бюджета, предпочтений и аллергий пользователя.  
Встроена интеграция с **Langfuse** для трейсинга LLM-запросов и поддерживается **асинхронная обработка запросов** через FastAPI.

---

## 🚀 Возможности

- ✅ Генерация **недельного плана питания** по персональным параметрам  
- 🔁 Замена блюд с сохранением калорийности  
- 🧩 Использование **JSON Schema валидации** для надежного вывода моделей  
- 🧠 “LLM as a Judge” — оценка корректности генерации (с помощью Mistral)  
- 🕒 Метрики: *latency*, *token count*, *overall score*  
- ⚡ Асинхронная обработка (`async/await`)  
- 🔍 Интеграция с **Langfuse** для логирования LLM-вызовов  

---


## 1. Настройка `.env`

Создай файл `.env` в корне и добавь туда ключи:

```bash
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxx
MISTRAL_API_KEY=xxxxxxxxxxxxxxxxxxxx
LANGFUSE_PUBLIC_KEY=pk-xxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-xxxxxxxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

## 2. Запуск FastAPI-сервера

```bash
uvicorn app.main:app --reload
```

После запуска открой документацию API:

* 📘 Swagger UI → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* 📗 ReDoc → [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🔌 API Endpoints

| Метод  | Endpoint                   | Назначение                         |
| :----- | :------------------------- | :--------------------------------- |
| `POST` | `/meal-plans/generate`     | Генерация недельного плана питания |
| `POST` | `/meal-plans/replace-meal` | Замена блюда в текущем плане       |

---

### 🥗 Пример запроса: `/meal-plans/generate`

```json
{
  "goal": "Похудение",
  "calories": 1800,
  "budget": 2000,
  "preferences": "вегетарианская диета",
  "allergies": "орехи"
}
```

### 📦 Пример ответа

```json
{
  "weekly_plan": [
    {
      "day_of_week": "Понедельник",
      "daily_summary": {
        "total_calories": 1800,
        "total_protein": 80,
        "total_fat": 60,
        "total_carbs": 200
      },
      "meals": [
        {
          "meal_type": "Завтрак",
          "dish_name": "Овсянка с ягодами",
          "calories": 400,
          "recipe": "Сварите овсянку на воде, добавьте ягоды."
        }
      ]
    }
  ]
}
```

---

## 🤖 Архитектура LLM

```
User Request
   │
   ▼
FastAPI Endpoint
   │
   ▼
BaselineModel (GPT)
   │
   ├── Формирование промпта (prompt_templates.py)
   ├── Генерация JSON по схемам (WeekPlan, DayPlan)
   ├── Langfuse Observability
   ▼
LLM Response (JSON)
```

---

## ⚖️ “LLM as a Judge” (Mistral Evaluation)

Mistral проверяет каждое сгенерированное меню по критериям:

| Поле                    | Описание                             |
| :---------------------- | :----------------------------------- |
| `goal_match`            | План соответствует цели пользователя |
| `meal_type_correctness` | На завтрак — завтрак, на обед — обед |
| `calorie_match`         | Соответствие калорийности            |
| `preferences_respected` | Учитываются предпочтения             |
| `allergies_respected`   | Исключены аллергены                  |
| `diversity`             | Рацион разнообразный                 |
| `comments`              | Краткие замечания                    |

💡 Далее вычисляется `overall_score` — доля `True` среди метрик.


## 🧰 Используемые технологии

| Категория  | Инструменты                |
| :--------- | :------------------------- |
| Backend    | FastAPI                    |
| LLM        | OpenAI GPT, Mistral        |
| Monitoring | Langfuse                   |
| Schemas    | Pydantic v2                |
| Evaluation | Jupyter, Pandas            |

```
