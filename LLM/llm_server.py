# llm_server.py
from fastapi import FastAPI
from ml.models.baseline import baseline_model
from pydantic import BaseModel

app = FastAPI(title="LLM Meal Planner")

class DishRequest(BaseModel):
    ingredients: str

@app.post("/generate")
def generate_dish(dish: DishRequest):
    result = baseline_model.generate({"ingredients": dish.ingredients}, user_id="test_user")
    return result
