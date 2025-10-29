# 🧠 AI Meal Planner — Dev Environment Guide

<div align="center">
  
## 🚀 Инструкции запуска Dev-окружения

</div>

### 🔧 Основная команда

```bash
docker compose -f docker-compose.dev.yml up --build -d
```

## ⚙️ Поднимаемые сервисы

| Сервис | Назначение | Порт |
|--------|-------------|------|
| 🐘 **db** | PostgreSQL, хранение данных | `5432` |
| ⚙️ **api** | Backend (FastAPI), общается с БД и LLM | `8000` |
| 💻 **frontend** | Веб-интерфейс | `8080` |
| 🧩 **llm** | Сервис модели (GPT-4o mini) | `5000` |
| 📓 **jupyter** | Среда экспериментов | `8888` |

---

<div align="center">
  
## 📈 Мониторинг

</div>

### 📊 Команда запуска мониторинга

```bash
docker compose -f monitoring/docker-compose.yml up --build -d
```

### 🧠 Сервисы мониторинга

| Сервис | Назначение | Порт |
|--------|-------------|------|
| 📊 **Prometheus** | Сбор метрик | `9090` |
| 📉 **Grafana** | Визуализация метрик | `3000` |
| 📜 **Loki** | Хранилище логов | `3100` |
| 🔍 **Promtail** | Сбор логов контейнеров | — |
| 🚨 **Alertmanager** | Оповещения о сбоях | `9093` |

🔐 **Grafana логин:** `admin / admin`  
🌍 **Интерфейс:** [http://localhost:3000](http://localhost:3000)

---

<div align="center">

## 🗂️ Структура проекта

</div>

```text
AI_Meal_Planner/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
├── .venv/                       # 🧩 Виртуальное окружение
├── api/                         # ⚙️ Backend (FastAPI)
│   ├── dockerfile
│   ├── main.py
│   └── openapi.yaml
├── database/                    # 🐘 PostgreSQL (инициализация и схема)
│   ├── dockerfile
│   └── schema.sql
├── design/                      # 🎨 Макеты интерфейса
├── docs/                        # 📚 Документация проекта
├── webpages/                    # 💻 Frontend (HTML, CSS, JS)
│   ├── dockerfile
│   ├── index.html
│   └── index.css
├── LLM/                         # 🤖 Модель и сервис LLM
│   ├── .env
│   ├── dockerfile
│   ├── llm_server.py
│   ├── data/                    # 📊 Датасеты
│   │   ├── FoodData.json
│   │   ├── FoodData_LLM_answers.json
│   │   └── FoodData_test.json
│   ├── evaluation/              # 🧪 Оценка и тестирование модели
│   │   ├── __init__.py
│   │   ├── evaluate.py
│   │   ├── LLM_json_creater.py
│   │   └── prompt_tests.py
│   ├── ml/                      # 🧠 Модуль модели (структура и API)
│   │   ├── __init__.py
│   │   ├── prompt_templates.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── app.py
│   │   └── models/
│   │       ├── __init__.py
│   │       └── baseline.py
│   ├── reports/                 # 📈 Отчёты и результаты
│   │   └── baseline_report.md
│   └── monitoring/              # 🧩 Мониторинг модели (Promtail, Alertmanager)
│       ├── promtail-config.yaml
│       └── alertmanager.yml
├── monitoring/                  # 📊 Prometheus, Grafana, Loki и др.
│   ├── docker-compose.yml
│   ├── prometheus.yml
│   └── promtail-config.yaml
├── tests/                       # 🧪 Тесты проекта
│   └── test_dummy.py
├── utils/                       # ⚙️ Вспомогательные скрипты
├── .env                         # 🔐 Переменные окружения
├── .gitignore
├── docker-compose.dev.yml        # 🐳 Конфигурация Dev-среды
├── requirements.txt              # 📦 Зависимости проекта
└── README.md                     # 📘 Описание проекта
```
