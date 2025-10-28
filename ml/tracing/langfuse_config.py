# ml/tracing/langfuse_config.py

import os
from dotenv import load_dotenv
from langfuse import Langfuse

load_dotenv()

LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

if not LANGFUSE_SECRET_KEY or not LANGFUSE_PUBLIC_KEY:
    raise ValueError("Не найдены ключи Langfuse в .env")

# Создаём глобальный клиент
langfuse = Langfuse(
    secret_key=LANGFUSE_SECRET_KEY,
    public_key=LANGFUSE_PUBLIC_KEY,
    host=LANGFUSE_HOST
)
