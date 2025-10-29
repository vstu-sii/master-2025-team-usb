## 📘 Введение

Документ описывает архитектуру веб-приложения **AI Meal Planner** на уровнях C4: **Context** и **Container**.

---

## 1. Context Diagram

```mermaid
graph TD
    U[Пользователь] -->|Вводит цели, предпочтения, бюджет| S[AI Meal Planner System]
    S -->|Генерирует меню, рецепты, список покупок| U
    S -->|Запрос данных о продуктах и калориях| API[Внешние API: Edamam, Spoonacular]
    S -->|Генерация рекомендаций и текстов| LLM[AI Engine: OpenAI API / HuggingFace]

````

---

```mermaid
graph TD
    %% Контейнеры
    FE[Frontend Web App]
    BE[Backend Server]
    DB[Database]
    AD[Admin Dashboard]
    AI[AI Engine]
    API[External APIs]
    LOG[Monitoring & Logging]
    WORK[Background Workers]
    STORAGE[File Storage]

    %% Взаимодействия
    FE -->|REST API: регистрация, создание планов, просмотр рецептов, экспорт списка| BE
    BE -->|SQL / ORM: хранение и получение данных| DB
    BE -->|Prompt / Response: генерация рекомендаций| AI
    BE -->|External Data: продукты и рецепты| API
    BE -->|Metrics / Logs| LOG
    BE -->|Background tasks: обработка очередей| WORK
    BE -->|File storage: сохранение изображений и документов| STORAGE
    AD -->|Управление базой данных и анализ статистики| BE




````

## 2. Container Diagram

```mermaid
graph TD
    A[Frontend] -->|REST API / HTTPS| B[Backend]
    B -->|SQL Queries / ORM| C[Database]
    B -->|Prompt / Response| D[AI Engine]
    B -->|External Data| E[External APIs]
    B -->|Metrics / Logs| F[Monitoring]
    B -->|Background jobs| G[Workers]
    B -->|File storage| H[Storage]
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

- [x] Context и Container диаграммы созданы.
- [x] Таблицы контейнеров, технологий и интерфейсов компонентов заполнены
- [x] Документ сохранён как `docs/architecture/c4-diagrams.md`
- [x] Проведен walkthrough документа с командой, получен ✅ от всех участников.













