from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, plans, meals, llm

app = FastAPI(
    title="AI Meal Planner API",
    version="1.0.0",
    description="API для управления планами питания с LLM"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(plans.router)
app.include_router(meals.router)
app.include_router(llm.router)


@app.get("/health")
async def health():
    return {"status": "ok"}