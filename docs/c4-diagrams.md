## 📘 Введение

Документ описывает архитектуру веб-приложения **AI Meal Planner** на уровнях C4: **Context** и **Container**.

---

## 1. Context Diagram

```mermaid
graph TD
    U[Пользователь] -->|Вводит цели, предпочтения, бюджет| S[AI Meal Planner System]
    S -->|Генерирует меню, рецепты, список покупок| U
    S -->|Запрос данных о продуктах и калориях| API[Внешние API (Edamam, Spoonacular)]
    S -->|Генерация рекомендаций и текстов| LLM[AI Engine (OpenAI API / HuggingFace)]
    S -->|Платежи/подписки| P[Платёжный сервис (Stripe/YooKassa)]
````

---

## 2. Container Diagram

```mermaid
graph TD
    A[Frontend (React + TailwindCSS)] -->|REST API / HTTPS| B[Backend (FastAPI / Django REST Framework)]
    B -->|SQL Queries / ORM| C[PostgreSQL Database]
    B -->|Prompt / Response (HTTPS)| D[AI Engine (OpenAI API / HuggingFace)]
    B -->|External Data (HTTPS)| E[Food & Recipe APIs (Edamam / Spoonacular)]
    B -->|Metrics / Logs| F[Monitoring & Logging (Prometheus, Grafana, Sentry)]
    B -->|Background jobs| G[Workers (Celery / RQ) + Redis]
    B -->|File storage| H[S3-compatible Storage]
```

### Контейнеры

| Контейнер     | Технологии                      | Назначение             |
| ------------- | ------------------------------- | ---------------------- |
| Frontend      | React + TailwindCSS             | UI                     |
| Backend       | FastAPI / Django REST Framework | REST API и логика      |
| Database      | PostgreSQL                      | Хранение данных        |
| AI Engine     | OpenAI API / HuggingFace        | Генерация рекомендаций |
| External APIs | Edamam / Spoonacular            | Данные о продуктах     |
| Monitoring    | Prometheus, Grafana, Sentry     | Метрики и логирование  |
| Workers       | Celery / RQ + Redis             | Фоновые задачи         |
| Storage       | S3-compatible                   | Хранение файлов        |

---

## 3. Обоснование технологий

| Компонент  | Технология            | Обоснование                   |
| ---------- | --------------------- | ----------------------------- |
| Frontend   | React + TailwindCSS   | UI                            |
| Backend    | Django REST Framework | REST API                      |
| Database   | PostgreSQL            | Надёжная БД                   |
| AI Engine  | OpenAI API            | Рекомендации                  |
| Monitoring | Grafana + Sentry      | Метрики и логирование         |
| CI/CD      | GitHub Actions        | Автоматизация тестов и деплоя |

---

## 4. Интерфейсы компонентов

| Компонент               | Взаимодействие | Формат  |
| ----------------------- | -------------- | ------- |
| Frontend → Backend      | REST API       | JSON    |
| Backend → Database      | ORM / SQL      | Таблицы |
| Backend → AI Engine     | HTTP           | JSON    |
| Backend → External APIs | REST           | JSON    |

---

## 5. Definition of Done

* Context и Container диаграммы созданы в формате Mermaid
* Таблицы контейнеров, технологий и интерфейсов компонентов заполнены
* Документ сохранён как `docs/architecture/c4-diagrams.md`
* Walkthrough проведён, получен ✅ от команды или ментора

```

---
