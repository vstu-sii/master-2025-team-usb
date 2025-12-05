import { API_BASE_URL } from "../constants";
import {
  AuthResponse,
  Meal,
  MealPlan,
  MealPlanCreate,
  MealReplaceRequest,
  ShoppingListResponse,
  User,
} from "../types";

const getHeaders = () => {
  const token = localStorage.getItem("token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

const handleResponse = async (response: Response) => {
  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ detail: "Unknown error" }));
    throw new Error(errorData.detail || "API request failed");
  }
  return response.json();
};

export const authService = {
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    return handleResponse(response);
  },
  register: async (
    email: string,
    password: string,
    name: string
  ): Promise<User> => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, name }),
    });
    return handleResponse(response);
  },
};

export const planService = {
  getAll: async (): Promise<MealPlan[]> => {
    const response = await fetch(`${API_BASE_URL}/plans`, {
      headers: getHeaders(),
    });
    return handleResponse(response);
  },
  getOne: async (id: number): Promise<MealPlan> => {
    const response = await fetch(`${API_BASE_URL}/plans/${id}`, {
      headers: getHeaders(),
    });
    return handleResponse(response);
  },
  create: async (data: MealPlanCreate): Promise<MealPlan> => {
    const response = await fetch(`${API_BASE_URL}/plans`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },
  delete: async (id: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/plans/${id}`, {
      method: "DELETE",
      headers: getHeaders(),
    });
    if (!response.ok) throw new Error("Failed to delete");
  },
  // NEW: проверка статуса
  getStatus: async (
    id: number
  ): Promise<{ status: string; is_generating: boolean }> => {
    const response = await fetch(`${API_BASE_URL}/plans/${id}/status`, {
      headers: getHeaders(),
    });
    return handleResponse(response);
  },
  // NEW: перегенерация
  regenerate: async (id: number): Promise<MealPlan> => {
    const response = await fetch(`${API_BASE_URL}/plans/${id}/regenerate`, {
      method: "POST",
      headers: getHeaders(),
    });
    return handleResponse(response);
  },
};

export const mealService = {
  replace: async (
    planId: number,
    data: MealReplaceRequest
  ): Promise<Meal[]> => {
    const response = await fetch(`${API_BASE_URL}/meals/${planId}/replace`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  update: async (mealId: number, data: Partial<Meal>): Promise<Meal> => {
    const response = await fetch(`${API_BASE_URL}/meals/${mealId}`, {
      method: "PATCH",
      headers: getHeaders(),
      body: JSON.stringify({
        dish_name: data.dish_name,
        calories: data.calories,
        recipe: data.recipe,
        // protein, fat, carbs можно добавить, если ИИ их генерирует
      }),
    });
    return handleResponse(response);
  },
  // UPDATED: возвращает статус
  getShoppingList: async (planId: number): Promise<ShoppingListResponse> => {
    const response = await fetch(
      `${API_BASE_URL}/meals/${planId}/shopping-list`,
      {
        headers: getHeaders(),
      }
    );
    return handleResponse(response);
  },
  // NEW: генерация списка покупок
  generateShoppingList: async (
    planId: number
  ): Promise<ShoppingListResponse> => {
    const response = await fetch(
      `${API_BASE_URL}/meals/${planId}/shopping-list/generate`,
      {
        method: "POST",
        headers: getHeaders(),
      }
    );
    return handleResponse(response);
  },
};
