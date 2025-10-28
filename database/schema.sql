-- Схема для таблицы пользователей
-- Пользователи аутентифицируются только через Google OAuth2, поэтому пароль не хранится.
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), -- Уникальный идентификатор пользователя
    google_id VARCHAR(255) UNIQUE NOT NULL,       -- Уникальный ID от Google
    email VARCHAR(255) UNIQUE NOT NULL,           -- Email пользователя, используется как основной идентификатор
    full_name VARCHAR(255),                       -- Полное имя из Google-профиля
    avatar_url TEXT,                              -- URL аватара из Google-профиля
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- Дата создания профиля
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()  -- Дата последнего обновления профиля
);

-- Схема для таблицы планов питания
-- Хранит параметры, которые пользователь вводил для генерации плана.
CREATE TABLE meal_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), -- Уникальный идентификатор плана
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE, -- Связь с пользователем
    goal TEXT NOT NULL,                           -- Цель (например, "Похудение")
    calories_target INT NOT NULL,                 -- Целевая калорийность
    budget_target INT,                            -- Целевой бюджет (опционально)
    preferences TEXT,                             -- Пищевые предпочтения (опционально)
    allergies TEXT,                               -- Аллергии (опционально)
    status VARCHAR(50) DEFAULT 'active',          -- Статус плана ('active', 'archived')
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- Дата создания
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()  -- Дата последнего обновления
);

-- Схема для хранения результатов генерации от LLM
-- Хранит как исходный промпт, так и полученный JSON.
CREATE TABLE llm_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                                -- Уникальный идентификатор генерации
    meal_plan_id UUID NOT NULL REFERENCES meal_plans(id) ON DELETE CASCADE,       -- Связь с конкретным планом питания
    llm_prompt TEXT NOT NULL,                                                     -- Промпт, отправленный в LLM
    llm_response_json JSONB NOT NULL,                                             -- JSON-ответ от LLM
    estimated_cost NUMERIC(10, 2),                                                -- Примерная стоимость, рассчитанная из ответа
    generation_time_ms INT,                                                       -- Время генерации в миллисекундах
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()                                 -- Дата генерации
);

-- Индексы для ускорения запросов
CREATE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_meal_plans_user_id ON meal_plans(user_id);
CREATE INDEX idx_llm_generations_meal_plan_id ON llm_generations(meal_plan_id);