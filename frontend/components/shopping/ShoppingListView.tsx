import React, { useEffect, useState, useRef, useCallback } from "react";
import { ShoppingItem, ShoppingListResponse } from "../../types";
import { mealService } from "../../services/api";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/Card";
import { Button } from "../ui/Button";

interface ShoppingListViewProps {
  planId: number;
  budget?: number;
}

export const ShoppingListView: React.FC<ShoppingListViewProps> = ({
  planId,
  budget,
}) => {
  const [data, setData] = useState<ShoppingListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [checkedItems, setCheckedItems] = useState<Set<number>>(new Set());
  const [error, setError] = useState<string | null>(null);

  const isGeneratingRef = useRef(false);

  const loadList = useCallback(async () => {
    try {
      const response = await mealService.getShoppingList(planId);
      setData(response);
      return response;
    } catch (err: any) {
      setError(err.message);
      return null;
    }
  }, [planId]);

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      await loadList();
      setLoading(false);
    };
    init();
  }, [loadList]);

  const handleGenerate = async () => {
    if (isGeneratingRef.current || generating) return;
    isGeneratingRef.current = true;
    setGenerating(true);
    setError(null);
    try {
      const response = await mealService.generateShoppingList(planId);
      setData(response);
    } catch (err: any) {
      if (err.message.includes("already in progress")) {
        setError("Список уже генерируется. Пожалуйста, подождите.");
      } else {
        setError(err.message || "Ошибка генерации списка");
      }
    } finally {
      setGenerating(false);
      isGeneratingRef.current = false;
    }
  };

  const toggleCheck = (idx: number) => {
    const next = new Set(checkedItems);
    if (next.has(idx)) next.delete(idx);
    else next.add(idx);
    setCheckedItems(next);
  };

  const formatPrice = (price: number | null | undefined): string => {
    if (price === null || price === undefined) return "—";
    return `${price.toFixed(0)} ₽`;
  };

  // --- НОВАЯ ЛОГИКА ЭКСПОРТА ---
  const handleExportTxt = () => {
    if (!data?.items) return;

    const itemsToBuy = data.items.filter((item) => {
      const globalIdx = data.items.indexOf(item);
      // Экспортируем только те, что НЕ отмечены галочкой
      return !checkedItems.has(globalIdx);
    });

    if (itemsToBuy.length === 0) {
      alert("Все товары уже куплены! Нечего экспортировать.");
      return;
    }

    // Группируем для красоты в файле
    const grouped = itemsToBuy.reduce((acc, item) => {
      const cat = item.category || "Разное";
      if (!acc[cat]) acc[cat] = [];
      acc[cat].push(item);
      return acc;
    }, {} as Record<string, ShoppingItem[]>);

    let textContent = `СПИСОК ПОКУПОК (AI Meal Planner)\n`;
    textContent += `================================\n\n`;

    let totalEstimate = 0;

    Object.entries(grouped).forEach(([category, items]) => {
      textContent += `[ ${category} ]\n`;
      items.forEach((item) => {
        const priceStr = item.estimated_price
          ? `${item.estimated_price} руб.`
          : "цена неизв.";
        textContent += `- ${item.item_name} (${item.quantity}) ~ ${priceStr}\n`;
        totalEstimate += item.estimated_price || 0;
      });
      textContent += `\n`;
    });

    textContent += `================================\n`;
    textContent += `Примерная сумма: ${totalEstimate.toFixed(0)} руб.\n`;

    // Создаем файл и ссылку для скачивания
    const blob = new Blob([textContent], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `shopping_list_${planId}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  // -----------------------------

  if (loading) {
    return (
      <div className="flex justify-center p-8">
        <div className="animate-spin text-2xl">🛒</div>
      </div>
    );
  }

  if (!data || data.status === "pending") {
    return (
      <Card className="max-w-3xl mx-auto">
        <CardHeader>
          <CardTitle>🛒 Список покупок</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 space-y-4">
            <div className="text-4xl">📝</div>
            <p className="text-slate-500">Список покупок ещё не создан.</p>
            {error && (
              <div className="text-red-500 text-sm bg-red-50 p-3 rounded-lg">
                {error}
              </div>
            )}
            <Button
              onClick={handleGenerate}
              isLoading={generating}
              disabled={generating}
            >
              {generating ? "Генерируем..." : "Сгенерировать список"}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (data.status === "generating" || generating) {
    return (
      <Card className="max-w-3xl mx-auto">
        <CardHeader>
          <CardTitle>🛒 Список покупок</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 space-y-4">
            <div className="animate-spin text-4xl">🤖</div>
            <p className="text-slate-500">ИИ составляет список покупок...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const items = data.items;
  const groupedItems = items.reduce((acc, item) => {
    const cat = item.category || "Разное";
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(item);
    return acc;
  }, {} as Record<string, ShoppingItem[]>);

  const totalPrice = items.reduce(
    (sum, item) => sum + (item.estimated_price || 0),
    0
  );
  const checkedPrice = items
    .filter((_, idx) => checkedItems.has(idx))
    .reduce((sum, item) => sum + (item.estimated_price || 0), 0);

  // Сумма того, что осталось купить
  const remainingPrice = totalPrice - checkedPrice;

  return (
    <div className="space-y-6 max-w-3xl mx-auto pb-8">
      {" "}
      {/* pb-8 добавлен для отступа снизу */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <CardTitle>🛒 Список покупок</CardTitle>
            <div className="text-right">
              <div className="text-2xl font-bold text-primary">
                {formatPrice(totalPrice)}
              </div>
              {budget && (
                <div
                  className={`text-sm ${
                    totalPrice > budget ? "text-red-500" : "text-green-600"
                  }`}
                >
                  {totalPrice > budget
                    ? "⚠️ Превышает бюджет"
                    : "✓ В рамках бюджета"}{" "}
                  ({budget} ₽)
                </div>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {Object.keys(groupedItems).length === 0 ? (
            <p className="text-slate-500 text-center">Список пуст</p>
          ) : (
            <div className="space-y-6">
              {Object.entries(groupedItems).map(([category, catItems]) => (
                <div key={category}>
                  <h4 className="font-semibold text-primary mb-2 border-b pb-1 flex justify-between">
                    <span>{category}</span>
                  </h4>
                  <ul className="space-y-2">
                    {catItems.map((item, itemIdx) => {
                      const globalIdx = items.indexOf(item);
                      const isChecked = checkedItems.has(globalIdx);
                      return (
                        <li
                          key={globalIdx}
                          className="flex items-center gap-3 py-1 group hover:bg-slate-50 rounded px-2 transition-colors"
                        >
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={() => toggleCheck(globalIdx)}
                            className="h-5 w-5 rounded border-slate-300 text-primary focus:ring-primary cursor-pointer"
                          />
                          <div
                            className={`flex-1 flex justify-between text-sm ${
                              isChecked ? "line-through text-slate-400" : ""
                            }`}
                          >
                            <span className="flex-1">{item.item_name}</span>
                            <span className="text-slate-500 mx-2">
                              {item.quantity}
                            </span>
                            <span className="font-medium text-slate-700 min-w-[60px] text-right">
                              {formatPrice(item.estimated_price)}
                            </span>
                          </div>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              ))}
            </div>
          )}

          <div className="mt-6 pt-4 border-t space-y-4">
            <div className="flex justify-between text-sm text-slate-600">
              <span>Уже куплено: {checkedItems.size} тов.</span>
              <span>Потрачено: {formatPrice(checkedPrice)}</span>
            </div>
            <div className="flex justify-between text-sm font-bold text-slate-800">
              <span>Осталось купить:</span>
              <span>{formatPrice(remainingPrice)}</span>
            </div>
          </div>
        </CardContent>
      </Card>
      {/* Кнопка экспорта внизу */}
      <div className="flex justify-end">
        <Button
          onClick={handleExportTxt}
          variant="secondary"
          className="shadow-lg"
          disabled={items.length === 0 || items.length === checkedItems.size}
        >
          📥 Скачать список (TXT)
        </Button>
      </div>
    </div>
  );
};
