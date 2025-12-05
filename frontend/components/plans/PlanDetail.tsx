import React, { useEffect, useState, useRef, useCallback } from "react";
import { Meal, MealPlan } from "../../types";
import { planService, mealService } from "../../services/api";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/Card";
import { Button } from "../ui/Button";
import { Modal } from "../ui/Modal";
import { ShoppingListView } from "../shopping/ShoppingListView";
import { DAYS_OF_WEEK } from "../../constants";

interface PlanDetailProps {
  planId: number;
}

export const PlanDetail: React.FC<PlanDetailProps> = ({ planId }) => {
  const [plan, setPlan] = useState<MealPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeDay, setActiveDay] = useState<string>("Понедельник");

  // Состояния для замены блюда
  const [replaceModalOpen, setReplaceModalOpen] = useState(false);
  const [selectedMeal, setSelectedMeal] = useState<Meal | null>(null);
  const [alternatives, setAlternatives] = useState<Meal[]>([]);
  const [replacing, setReplacing] = useState(false);

  // Состояние для списка покупок
  const [showShoppingList, setShowShoppingList] = useState(false);

  // NEW: Состояние для просмотра полного рецепта
  const [viewRecipeMeal, setViewRecipeMeal] = useState<Meal | null>(null);

  const isReplacingRef = useRef(false);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  const fetchPlan = useCallback(async () => {
    try {
      const data = await planService.getOne(planId);
      setPlan(data);
      // Если при первой загрузке выбранный день пустой, ищем первый день с едой
      if (data.meals && data.meals.length > 0) {
        // Логика: если текущего activeDay нет в списке блюд, переключаем на первый доступный
        const hasMealsForCurrentDay = data.meals.some(
          (m) => m.day_of_week === activeDay
        );
        if (!hasMealsForCurrentDay) {
          setActiveDay(data.meals[0].day_of_week);
        }
      }
      return data;
    } catch (error) {
      console.error(error);
      return null;
    }
  }, [planId, activeDay]); // activeDay в зависимости, чтобы не сбрасывался при поллинге

  // Polling (как было раньше)
  useEffect(() => {
    const startPolling = async () => {
      setLoading(true);
      const data = await fetchPlan();
      setLoading(false);

      if (data && (data.status === "pending" || data.status === "generating")) {
        pollingRef.current = setInterval(async () => {
          const updated = await fetchPlan();
          if (updated && updated.status === "ready") {
            if (pollingRef.current) {
              clearInterval(pollingRef.current);
              pollingRef.current = null;
            }
          }
        }, 2000);
      }
    };
    startPolling();
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [planId, fetchPlan]);

  // Логика замены (как было раньше)
  const handleOpenReplace = (meal: Meal) => {
    if (isReplacingRef.current) return;
    setSelectedMeal(meal);
    setAlternatives([]);
    setReplaceModalOpen(true);
    fetchAlternatives(meal.dish_name);
  };

  const fetchAlternatives = async (dishName: string) => {
    if (!plan || isReplacingRef.current) return;
    isReplacingRef.current = true;
    setReplacing(true);
    try {
      const alts = await mealService.replace(plan.id, {
        dish_name: dishName,
        reason: "Хочу что-то другое",
      });
      setAlternatives(alts);
    } catch (error: any) {
      if (!error.message.includes("already in progress")) console.error(error);
    } finally {
      setReplacing(false);
      isReplacingRef.current = false;
    }
  };

  const handleSelectAlternative = async (alternative: Meal) => {
    if (!selectedMeal || !selectedMeal.id) return;
    setReplacing(true);
    try {
      await mealService.update(selectedMeal.id, alternative);
      await fetchPlan();
      setReplaceModalOpen(false);
    } catch (error) {
      console.error(error);
      alert("Не удалось обновить блюдо");
    } finally {
      setReplacing(false);
    }
  };

  if (loading)
    return (
      <div className="flex justify-center p-12">
        <div className="animate-spin text-4xl">🥘</div>
      </div>
    );
  if (!plan) return <div>План не найден</div>;
  if (plan.status === "pending" || plan.status === "generating") {
    return (
      <div className="flex flex-col items-center justify-center p-12 space-y-6">
        <div className="animate-spin text-6xl">🤖</div>
        <div className="text-center">
          <h2 className="text-xl font-bold text-slate-800 mb-2">
            Генерируем план...
          </h2>
          <p className="text-slate-500">Пожалуйста, подождите 10-30 секунд.</p>
        </div>
      </div>
    );
  }

  if (showShoppingList) {
    return (
      <div className="space-y-4">
        <Button variant="outline" onClick={() => setShowShoppingList(false)}>
          ← Вернуться к плану
        </Button>
        <ShoppingListView planId={plan.id} budget={plan.budget} />
      </div>
    );
  }

  const mealsForDay =
    plan.meals?.filter((m) => m.day_of_week === activeDay) || [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold">{plan.goal}</h1>
          <p className="text-slate-500 text-sm">
            {plan.calories} ккал/день • Бюджет: {plan.budget}₽
          </p>
        </div>
        <Button variant="secondary" onClick={() => setShowShoppingList(true)}>
          🛒 Список покупок
        </Button>
      </div>

      <div className="flex overflow-x-auto pb-2 gap-2 scrollbar-hide">
        {DAYS_OF_WEEK.map((day) => (
          <button
            key={day}
            onClick={() => setActiveDay(day)}
            className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
              activeDay === day
                ? "bg-primary text-white shadow-md"
                : "bg-white text-slate-600 hover:bg-slate-100"
            }`}
          >
            {day}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {mealsForDay.map((meal) => (
          <Card
            key={meal.id}
            className="flex flex-col h-full hover:shadow-md transition-shadow"
          >
            <CardHeader className="pb-3">
              <div className="text-xs font-bold uppercase text-primary tracking-wide">
                {meal.meal_type}
              </div>
              <CardTitle className="text-lg leading-tight">
                {meal.dish_name}
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 space-y-3 text-sm text-slate-600">
              <div className="flex justify-between border-b pb-2">
                <span>Калории</span>
                <span className="font-semibold">{meal.calories}</span>
              </div>
              <div className="grid grid-cols-3 gap-1 text-xs text-center">
                <div className="bg-slate-50 p-1 rounded">
                  Б: {meal.protein}г
                </div>
                <div className="bg-slate-50 p-1 rounded">Ж: {meal.fat}г</div>
                <div className="bg-slate-50 p-1 rounded">У: {meal.carbs}г</div>
              </div>

              {/* UPDATED: Секция рецепта */}
              {meal.recipe && (
                <div
                  className="bg-yellow-50 p-2 rounded border border-yellow-100 cursor-pointer hover:bg-yellow-100 transition-colors group"
                  onClick={() => setViewRecipeMeal(meal)}
                  title="Нажмите, чтобы прочитать полный рецепт"
                >
                  <p className="text-xs italic text-slate-700 line-clamp-3 mb-1">
                    {meal.recipe}
                  </p>
                  <div className="text-[10px] text-primary font-medium text-right group-hover:underline">
                    Читать рецепт полностью →
                  </div>
                </div>
              )}
            </CardContent>
            <div className="p-4 pt-0 mt-auto">
              <Button
                variant="outline"
                size="sm"
                className="w-full text-xs"
                onClick={() => handleOpenReplace(meal)}
                disabled={replacing}
              >
                🔄 Заменить
              </Button>
            </div>
          </Card>
        ))}
        {mealsForDay.length === 0 && (
          <div className="col-span-full text-center py-12 text-slate-400">
            Нет блюд для этого дня
          </div>
        )}
      </div>

      {/* Модалка замены (как была) */}
      <Modal
        isOpen={replaceModalOpen}
        onClose={() => {
          if (!replacing) setReplaceModalOpen(false);
        }}
        title={`Замена: ${selectedMeal?.dish_name}`}
      >
        <div className="space-y-4">
          {/* ... содержимое модалки замены ... */}
          {replacing ? (
            <div className="text-center p-4">Ищем варианты...</div>
          ) : (
            <div className="space-y-2">
              {alternatives.map((alt, i) => (
                <div
                  key={i}
                  className="border p-3 rounded flex justify-between items-center hover:bg-slate-50 cursor-pointer"
                  onClick={() => handleSelectAlternative(alt)}
                >
                  <div>
                    <div className="font-medium">{alt.dish_name}</div>
                    <div className="text-xs text-slate-500">
                      {alt.calories} ккал
                    </div>
                  </div>
                  <Button size="sm" variant="ghost">
                    Выбрать
                  </Button>
                </div>
              ))}
              {alternatives.length === 0 && (
                <div className="text-center text-red-500">Нет вариантов</div>
              )}
            </div>
          )}
        </div>
      </Modal>
      {/* NEW: Модалка просмотра рецепта (Обновленный дизайн) */}
      <Modal
        isOpen={!!viewRecipeMeal}
        onClose={() => setViewRecipeMeal(null)}
        title="" // Убираем заголовок из пропса, сделаем кастомный внутри для красоты
      >
        {viewRecipeMeal && (
          <div className="space-y-6">
            {/* Заголовок блюда */}
            <div className="text-center border-b pb-4">
              <h3 className="text-2xl font-bold text-slate-800 leading-tight">
                {viewRecipeMeal.dish_name}
              </h3>
              <p className="text-slate-400 text-sm mt-1 uppercase tracking-wider font-medium">
                {viewRecipeMeal.meal_type}
              </p>
            </div>

            {/* Карточки КБЖУ */}
            <div className="grid grid-cols-4 gap-2">
              <div className="flex flex-col items-center bg-orange-50 p-2 rounded-xl border border-orange-100">
                <span className="text-xl">🔥</span>
                <span className="font-bold text-orange-700 text-lg">
                  {viewRecipeMeal.calories}
                </span>
                <span className="text-[10px] text-orange-600 uppercase font-bold">
                  Ккал
                </span>
              </div>
              <div className="flex flex-col items-center bg-blue-50 p-2 rounded-xl border border-blue-100">
                <span className="text-xl">🥩</span>
                <span className="font-bold text-blue-700 text-lg">
                  {viewRecipeMeal.protein}
                </span>
                <span className="text-[10px] text-blue-600 uppercase font-bold">
                  Белки
                </span>
              </div>
              <div className="flex flex-col items-center bg-yellow-50 p-2 rounded-xl border border-yellow-100">
                <span className="text-xl">🥑</span>
                <span className="font-bold text-yellow-700 text-lg">
                  {viewRecipeMeal.fat}
                </span>
                <span className="text-[10px] text-yellow-600 uppercase font-bold">
                  Жиры
                </span>
              </div>
              <div className="flex flex-col items-center bg-green-50 p-2 rounded-xl border border-green-100">
                <span className="text-xl">🌾</span>
                <span className="font-bold text-green-700 text-lg">
                  {viewRecipeMeal.carbs}
                </span>
                <span className="text-[10px] text-green-600 uppercase font-bold">
                  Углев.
                </span>
              </div>
            </div>

            {/* Блок рецепта */}
            <div>
              <h4 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
                📖 Способ приготовления:
              </h4>
              <div className="bg-slate-50 p-5 rounded-2xl border border-slate-100 text-slate-700 text-base leading-7 whitespace-pre-wrap shadow-sm">
                {viewRecipeMeal.recipe || "Рецепт отсутствует"}
              </div>
            </div>

            {/* Кнопка закрытия */}
            <div className="pt-2">
              <Button
                onClick={() => setViewRecipeMeal(null)}
                className="w-full py-6 text-lg rounded-xl shadow-lg shadow-primary/20"
              >
                Отлично, понятно!
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
