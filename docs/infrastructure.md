# 🧠 AI Meal Planner — Dev Environment Guide

<div align="center">
  
## 🚀 Инструкции запуска Dev-окружения

</div>

### 🔧 Основная команда

```bash
docker compose -f docker-compose.dev.yml up --build -d
```

### 💡 Что делает команда:

- **`docker compose`** — запускает контейнеры из указанного файла.  
- **`-f docker-compose.dev.yml`** — указывает файл конфигурации dev-среды.  
- **`--build`** — пересобирает образы перед запуском.  
- **`-d`** — запускает контейнеры **в фоновом режиме** (*detached mode*), чтобы терминал оставался свободным.

---

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

## 🧩 Архитектура инфраструктуры

</div>

```text
┌────────────────────────────┐
│     Frontend (Vue/React)   │  ← порт 8080
└────────────┬───────────────┘
             │ REST API
             ▼
┌────────────────────────────┐
│       FastAPI backend      │  ← порт 8000
│   ├── взаимодействует с БД │
│   └── запрашивает LLM      │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│        LLM-сервис          │  ← порт 5000
│  (обработка запросов, ML)  │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│          PostgreSQL        │  ← порт 5432
│      (хранение данных)     │
└────────────────────────────┘

┌────────────────────────────┐
│     Monitoring Stack       │
│ Prometheus | Grafana | Loki│
└────────────────────────────┘
```

📦 Каждый блок — отдельный **Docker-контейнер**, управляемый `docker-compose`.  
🧩 Все сервисы связаны через **общую Docker-сеть**, что позволяет им обращаться по именам (`db`, `llm`, `api` и т.д.).

---

<div align="center">

## 🧰 Cheat Sheet для команды

</div>

| Действие | Команда |
|----------|----------|
| ▶️ Запуск dev-окружения | ```docker compose -f docker-compose.dev.yml up --build -d``` |
| ⛔ Остановка окружения | ```docker compose -f docker-compose.dev.yml down``` |
| 🔄 Перезапуск с очисткой данных | ```docker compose -f docker-compose.dev.yml down --volumes --remove-orphans``` |
| 📜 Логи контейнера | ```docker logs <container_name>``` |
| 🧩 Войти в контейнер | ```docker exec -it <container_name> bash``` |
| 📋 Проверить запущенные контейнеры | ```docker ps``` |
| 🧠 Проверить healthcheck | ```docker inspect --format='{{json .State.Health}}' <container_name>``` |
| 🏗️ Пересобрать образы без запуска | ```docker compose -f docker-compose.dev.yml build``` |
| 🧾 Проверить CI/CD логи | GitHub → Actions → Workflow runs |

---

<div align="center">

## ⚙️ CI/CD Workflows

</div>

### 🧪 Continuous Integration — `.github/workflows/ci.yml`

**Запускается при** `push` или `pull_request` в ветку `MLOps-branch`.

#### 🔍 Этапы:
1. **Checkout кода**
2. **Установка Python 3.11**
3. **Установка зависимостей** из `requirements.txt`
4. **Линтинг кода** через [Black](https://black.readthedocs.io/en/stable/)
5. **Запуск тестов** через `unittest`

#### 🧹 Пример автоматического линтинга:
```bash
black .
```

💡 Если CI падает:
- Проверьте ошибки **`E501`** (строки > 79 символов)
- Убедитесь, что тесты находятся в директории **`tests/`**

---

### 🚀 Continuous Deployment — `.github/workflows/cd.yml`

**Запускается автоматически при push** в ветку `MLOps-branch`.

#### 🔧 Этапы деплоя:

1. **Остановка старых контейнеров**
   ```bash
   docker compose -f docker-compose.dev.yml down --volumes --remove-orphans
   ```
2. **Пересборка и запуск нового окружения**
   ```bash
   docker compose -f docker-compose.dev.yml up --build -d
   ```

После успешного выполнения CD приложение автоматически обновляется до последней версии.  
🟢 Каждый `push` в `MLOps-branch` = новый билд в dev-среде.

---

<div align="center">

## 🧯 Troubleshooting Guide

</div>

| Проблема | Возможная причина | Решение |
|----------|------------------|----------|
| ❌ `Connection refused` при обращении к API | Контейнер ещё не готов | Подожди 20–30 секунд, проверь `docker ps` |
| 🐘 `Database connection error` | БД не готова / volume повреждён | ```docker compose down --volumes``` → ```up --build``` |
| ⚠️ `Module not found` | Неактуальные зависимости | ```pip freeze > requirements.txt``` |
| 💥 CI падает с `E501` | Строки длиннее 79 символов | ```black .``` |
| 💤 Нет обновления после push | Старые контейнеры не пересобрались | ```docker image prune -a``` |
| 📉 Prometheus не видит метрики | Ошибка в `targets` | Проверь файл `prometheus.yml` |
| 🪣 Grafana пустая | Нет источника данных | Добавь Loki/Prometheus вручную через UI Grafana |

---

## 🧩 Краткое резюме

- 🧪 **CI** — автоматическая проверка кода (линтер + тесты)  
- 🚀 **CD** — автодеплой при каждом push  
- 🧰 **Docker Compose** — микросервисная инфраструктура  
- 📊 **Monitoring Stack** — сбор метрик и логов  

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

