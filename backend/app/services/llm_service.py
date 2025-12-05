# backend/app/services/llm_service.py
import json
import re
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import MealPlan, Meal, ShoppingItem, LLMRequest

# MODEL_NAME = "z-ai/glm-4.5-air:free"
MODEL_NAME = "openai/gpt-oss-20b:free"

client = None

if settings.OPENAI_API_KEY:
    client = AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Meal Planner App",
        }
    )


def clean_json_response(content: str) -> str:
    """Очищает ответ от markdown-обертки ```json ... ```"""
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(json)?", "", content, flags=re.MULTILINE)
        content = re.sub(r"```$", "", content, flags=re.MULTILINE)
    return content.strip()


async def generate_meal_plan(plan: MealPlan, db: AsyncSession) -> list[Meal]:
    """Генерация плана питания через LLM"""
    prompt = f"""
    Ты диетолог. Создай план питания на {plan.total_days} дней.
    Цель: {plan.goal}
    Калории в день: {plan.calories}
    Бюджет: {plan.budget} руб
    Предпочтения: {plan.preferences or 'нет'}
    Аллергии/ограничения: {plan.allergies or 'нет'}

    Для каждого дня укажи завтрак, обед, ужин и перекус.
    Формат JSON (строго массив объектов):
    [
        {{"day_of_week": "Понедельник", "meal_type": "Завтрак", "dish_name": "Название", "calories": 300, "protein": 15, "fat": 10, "carbs": 35, "recipe": "Краткий рецепт"}}
    ]
    ВЕРНИ ТОЛЬКО ЧИСТЫЙ JSON. НИКАКОГО ВСТУПИТЕЛЬНОГО ТЕКСТА ИЛИ MARKDOWN.
    """

    request_data = {"prompt": prompt,
                    "goal": plan.goal, "calories": plan.calories}

    if not client:
        meals_data = _generate_mock_meals(plan)
        response_data = {"meals": meals_data, "mock": True}
    else:
        try:
            response = await client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            content = response.choices[0].message.content
            cleaned_content = clean_json_response(content)
            meals_data = json.loads(cleaned_content)
            response_data = {"meals": meals_data}
        except Exception as e:
            print(f"LLM Error: {e}")
            meals_data = _generate_mock_meals(plan)
            response_data = {"error": str(e), "mock_fallback": True}

    llm_log = LLMRequest(
        user_id=plan.user_id,
        meal_plan_id=plan.id,
        request_json=request_data,
        response_json=response_data,
        status="success" if "error" not in response_data else "error"
    )
    db.add(llm_log)

    meals = []
    data_to_iterate = meals_data if isinstance(
        meals_data, list) else meals_data.get("meals", [])

    for m in data_to_iterate:
        meal = Meal(
            meal_plan_id=plan.id,
            day_of_week=m.get("day_of_week", "День"),
            meal_type=m.get("meal_type", "Прием пищи"),
            dish_name=m.get("dish_name", "Блюдо"),
            calories=m.get("calories", 0),
            protein=m.get("protein", 0),
            fat=m.get("fat", 0),
            carbs=m.get("carbs", 0),
            recipe=m.get("recipe", "")
        )
        db.add(meal)
        meals.append(meal)

    await db.commit()
    return meals


async def replace_meal(plan: MealPlan, dish_name: str, reason: str | None, db: AsyncSession) -> list[Meal]:
    """Замена блюда через LLM"""
    prompt = f"""
    Предложи 3 альтернативных блюда вместо "{dish_name}".
    Причина замены: {reason or 'не указана'}
    Цель плана: {plan.goal}, калории в день: {plan.calories}

    Формат JSON (строго массив):
    [{{"dish_name": "Название", "calories": 300, "recipe": "Рецепт"}}]
    ВЕРНИ ТОЛЬКО ЧИСТЫЙ JSON.
    """

    request_data = {"dish_name": dish_name, "reason": reason}

    if not client:
        alternatives = [
            {"dish_name": "Овсянка с ягодами",
                "calories": 280, "recipe": "Сварить овсянку"},
            {"dish_name": "Творог с медом", "calories": 250, "recipe": "Смешать"},
            {"dish_name": "Яичница", "calories": 320, "recipe": "Пожарить"},
        ]
        response_data = {"alternatives": alternatives, "mock": True}
    else:
        try:
            response = await client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.choices[0].message.content
            cleaned_content = clean_json_response(content)
            alternatives = json.loads(cleaned_content)
            response_data = {"alternatives": alternatives}
        except Exception as e:
            print(f"LLM Error: {e}")
            alternatives = []
            response_data = {"error": str(e)}

    llm_log = LLMRequest(
        user_id=plan.user_id,
        meal_plan_id=plan.id,
        request_json=request_data,
        response_json=response_data,
        status="success" if "error" not in response_data else "error"
    )
    db.add(llm_log)
    await db.commit()

    return [
        Meal(
            meal_plan_id=plan.id,
            day_of_week="",
            meal_type="",
            dish_name=a.get("dish_name", "Альтернатива"),
            calories=a.get("calories", 0),
            recipe=a.get("recipe", "")
        ) for a in alternatives
    ]


async def generate_shopping_list(plan: MealPlan, db: AsyncSession) -> list[ShoppingItem]:
    """Генерация списка покупок с ценами"""
    meals_names = [m.dish_name for m in plan.meals]

    # ОБНОВЛЁННЫЙ ПРОМПТ с ценами
    prompt = f"""
    Составь список покупок для этих блюд: {', '.join(meals_names)}
    Бюджет: {plan.budget} руб
    
    Укажи примерную стоимость каждого продукта в рублях.

    Формат JSON (строго массив):
    [{{"item_name": "Продукт", "category": "Категория", "quantity": "Количество", "estimated_price": 150.00}}]
    
    Категории: Мясо, Рыба, Молочные продукты, Овощи, Фрукты, Крупы, Специи, Напитки, Разное
    
    ВЕРНИ ТОЛЬКО ЧИСТЫЙ JSON.
    """

    request_data = {"meals": meals_names, "budget": float(plan.budget)}

    if not client:
        items_data = [
            {"item_name": "Куриная грудка", "category": "Мясо",
                "quantity": "1 кг", "estimated_price": 350.00},
            {"item_name": "Рис басмати", "category": "Крупы",
                "quantity": "500 г", "estimated_price": 180.00},
            {"item_name": "Брокколи", "category": "Овощи",
                "quantity": "400 г", "estimated_price": 150.00},
            {"item_name": "Яйца", "category": "Молочные продукты",
                "quantity": "10 шт", "estimated_price": 120.00},
            {"item_name": "Оливковое масло", "category": "Разное",
                "quantity": "250 мл", "estimated_price": 450.00},
        ]
        response_data = {"items": items_data, "mock": True}
    else:
        try:
            response = await client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.choices[0].message.content
            cleaned_content = clean_json_response(content)
            items_data = json.loads(cleaned_content)
            response_data = {"items": items_data}
        except Exception as e:
            print(f"LLM Error: {e}")
            items_data = []
            response_data = {"error": str(e)}

    llm_log = LLMRequest(
        user_id=plan.user_id,
        meal_plan_id=plan.id,
        request_json=request_data,
        response_json=response_data,
        status="success" if "error" not in response_data else "error"
    )
    db.add(llm_log)

    items = []
    data_to_iterate = items_data if isinstance(
        items_data, list) else items_data.get("items", [])

    for i in data_to_iterate:
        # Безопасное преобразование цены
        price = i.get("estimated_price")
        if price is not None:
            try:
                price = float(price)
            except (ValueError, TypeError):
                price = None

        item = ShoppingItem(
            meal_plan_id=plan.id,
            item_name=i.get("item_name", "Продукт"),
            category=i.get("category", "Разное"),
            quantity=i.get("quantity", "1 шт"),
            estimated_price=price
        )
        db.add(item)
        items.append(item)

    await db.commit()
    return items


def _generate_mock_meals(plan: MealPlan) -> list[dict]:
    """Генерация мок-данных"""
    days = ["Понедельник", "Вторник", "Среда",
            "Четверг", "Пятница", "Суббота", "Воскресенье"]
    meal_types = ["Завтрак", "Обед", "Ужин", "Перекус"]

    meals = []
    for day in days[:min(plan.total_days, 7)]:
        for meal_type in meal_types:
            meals.append({
                "day_of_week": day,
                "meal_type": meal_type,
                "dish_name": f"Блюдо ({day}, {meal_type})",
                "calories": plan.calories // 4,
                "protein": 25,
                "fat": 15,
                "carbs": 45,
                "recipe": f"Рецепт для {meal_type.lower()}"
            })
    return meals
