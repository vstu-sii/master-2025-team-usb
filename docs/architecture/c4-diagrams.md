## 📘 Введение

Документ описывает архитектуру веб-приложения **AI Meal Planner** на уровнях C4: **Context** и **Container**.

---

## 1. Context Diagram

<p align="center">
  <img src="https://github.com/vstu-sii/master-2025-team-usb/blob/SA/PO-branch/docs/architecture/img_for_git/context.png?raw=true" alt="Context Diagram" width="600"/>
</p>

---

## 2. Container Diagram

<p align="center">
  <img src="https://github.com/vstu-sii/master-2025-team-usb/blob/SA/PO-branch/docs/architecture/img_for_git/container.png?raw=true" alt="Context Diagram" width="1000"/>
</p>



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


















