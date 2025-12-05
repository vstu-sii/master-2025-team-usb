export interface User {
  id: number;
  email: string;
  name: string | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface Meal {
  id: number | null; // <--- БЫЛО: number. СТАЛО: number | null
  meal_plan_id: number;
  day_of_week: string;
  meal_type: string;
  dish_name: string;
  calories: number | null;
  protein: number | null;
  fat: number | null;
  carbs: number | null;
  recipe: string | null;
}

export interface ShoppingItem {
  id?: number;
  item_name: string;
  category: string;
  quantity: string;
  estimated_price?: number | null; // NEW
  checked?: boolean;
}

// NEW: Ответ списка покупок со статусом
export interface ShoppingListResponse {
  status: "pending" | "generating" | "ready" | "error";
  items: ShoppingItem[];
  total_price: number | null;
}

export interface MealPlan {
  id: number;
  user_id: number;
  goal: string;
  calories: number;
  budget: number;
  preferences: string | null;
  allergies: string | null;
  total_days: number;
  status: "pending" | "generating" | "ready" | "error"; // NEW
  created_at: string;
  meals?: Meal[];
  shopping_items?: ShoppingItem[];
}

export interface MealPlanCreate {
  goal: string;
  calories: number;
  budget: number;
  preferences?: string;
  allergies?: string;
}

export interface MealReplaceRequest {
  dish_name: string;
  reason?: string;
}

export interface ApiError {
  detail: string;
}
