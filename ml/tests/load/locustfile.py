from locust import HttpUser, task, between
import random

class MealPlannerUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        # уникальный ID для каждого виртуального пользователя
        self.user_id = random.randint(1, 999999)

    @task(3)
    def generate_plan(self):
        payload = {
            "goal": "похудение",
            "calories": 1800,
            "budget": 1500,
            "preferences": "вегетарианская",
            "allergies": "орехи"
        }
        self.client.post(
            f"/meal-plans/generate/?user_id={self.user_id}",
            json=payload,
            name="/meal-plans/generate/"
        )

    @task(1)
    def replace_meal(self):
        payload = {
            "day_of_week": "понедельник",
            "meal_type": "обед",
            "old_dish": "овсянка",
            "meal_calories": 350,
            "goal": "похудение",
            "calories": 1800,
            "budget": 1500,
            "preferences": "вегетарианская",
            "allergies": "орехи"
        }
        self.client.patch(
            f"/meal-plans/replace/?user_id={self.user_id}",
            json=payload,
            name="/meal-plans/replace/"
        )
