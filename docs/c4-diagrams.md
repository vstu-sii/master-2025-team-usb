## 📘 Введение

Документ описывает архитектуру веб-приложения **AI Meal Planner** на уровнях C4: **Context** (контекст системы) и **Container** (контейнеры).  
Цель — зафиксировать границы системы, внешние взаимодействия, ключевые подсистемы, выбор технологий, интерфейсы и риски. Документ служит основой для разработки и дальнейшей детализации.

---

## 1. Context Diagram — Контекст системы

**Цель:** показать, как система взаимодействует с пользователями и внешними сервисами.

```mermaid
graph TD
    U[Пользователь] -->|Вводит цели, предпочтения, бюджет| S[AI Meal Planner System]
    S -->|Генерирует меню, рецепты, список покупок| U
    S -->|Запрос данных о продуктах и калориях| API[Внешние API (Edamam, Spoonacular)]
    S -->|Генерация рекомендаций и текстов| LLM[AI Engine (OpenAI API / HF)]
    S -->|Платежи/подписки| P[Платёжный сервис (Stripe/YooKassa)]


## 2. Container Diagram — Контейнеры системы
graph TD
    A[Frontend (React + TailwindCSS)] -->|REST API / HTTPS| B[Backend (FastAPI / Django REST Framework)]
    B -->|SQL Queries / ORM| C[PostgreSQL Database]
    B -->|Prompt / Response (HTTPS)| D[AI Engine (OpenAI API / HuggingFace)]
    B -->|External Data (HTTPS)| E[Food & Recipe APIs (Edamam / Spoonacular)]
    B -->|Metrics / Logs| F[Monitoring & Logging (Prometheus, Grafana, Sentry)]
    B -->|Background jobs| G[Workers (Celery / RQ) + Redis]
    B -->|File storage| H[S3-compatible Storage]

---

## 3. Обоснование технологий

| Компонент | Технология | Обоснование |
|------------|-------------|-------------|
| **Frontend** | React + TailwindCSS | Современный, отзывчивый UI с быстрым рендерингом и адаптивным дизайном |
| **Backend** | Django REST Framework | Ускоряет разработку REST API, имеет встроенные средства аутентификации и сериализации данных |
| **Database** | PostgreSQL | Надёжная и масштабируемая СУБД, поддерживает сложные запросы и хранение JSON |
| **AI Engine** | OpenAI API | Позволяет генерировать персонализированные рекомендации и текстовые описания блюд |
| **Monitoring** | Grafana + Sentry | Обеспечивает мониторинг метрик и логирование ошибок для повышения стабильности |
| **CI/CD** | GitHub Actions | Автоматизирует тестирование и развертывание, снижая вероятность ошибок при деплое |

---

## 4. Интерфейсы компонентов

| Компонент | Взаимодействие | Формат |
|------------|----------------|--------|
| **Frontend → Backend** | REST API | JSON |
| **Backend → Database** | ORM / SQL | Таблицы PostgreSQL |
| **Backend → AI Engine** | HTTP-запросы | JSON |
| **Backend → External APIs** | REST-запросы | JSON |

---