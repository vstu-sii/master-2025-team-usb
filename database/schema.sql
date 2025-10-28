-- 1. Таблица пользователей
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    auth_provider VARCHAR(50) DEFAULT 'google',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Планы питания
CREATE TABLE meal_plans (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    goal VARCHAR(255) NOT NULL,
    calories INT CHECK (calories BETWEEN 1000 AND 6000),
    budget NUMERIC(10,2) CHECK (budget >= 0),
    preferences TEXT,
    allergies TEXT,
    total_days INT DEFAULT 7,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Блюда в плане
CREATE TABLE meals (
    id SERIAL PRIMARY KEY,
    meal_plan_id INT NOT NULL REFERENCES meal_plans(id) ON DELETE CASCADE,
    day_of_week VARCHAR(20) NOT NULL,
    meal_type VARCHAR(50) NOT NULL, -- Завтрак, Обед, Ужин, Перекус
    dish_name VARCHAR(255) NOT NULL,
    calories INT,
    protein INT,
    fat INT,
    carbs INT,
    recipe TEXT
);

-- 4. Список покупок
CREATE TABLE shopping_lists (
    id SERIAL PRIMARY KEY,
    meal_plan_id INT NOT NULL REFERENCES meal_plans(id) ON DELETE CASCADE,
    category VARCHAR(100),
    item_name VARCHAR(255),
    quantity VARCHAR(50),
    checked BOOLEAN DEFAULT FALSE
);

-- 5. История взаимодействия с LLM
CREATE TABLE llm_requests (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    meal_plan_id INT REFERENCES meal_plans(id) ON DELETE CASCADE,
    request_json JSONB,
    response_json JSONB,
    status VARCHAR(50) DEFAULT 'success',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 🔍 Индексы
CREATE INDEX idx_mealplan_user ON meal_plans(user_id);
CREATE INDEX idx_meals_plan ON meals(meal_plan_id);
CREATE INDEX idx_llm_user ON llm_requests(user_id);
CREATE INDEX idx_shopping_plan ON shopping_lists(meal_plan_id);
