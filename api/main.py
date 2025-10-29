import requests
from fastapi import FastAPI

app = FastAPI()

LLM_URL = "http://llm:5000/generate"


@app.get("/ask_llm")
def ask_llm(prompt: str):
    response = requests.post(LLM_URL, json={"prompt": prompt})
    return response.json()
