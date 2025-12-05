import React, { useEffect, useState } from "react";
import { MealPlan } from "../../types";
import { planService } from "../../services/api";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardFooter,
} from "../ui/Card";
import { Button } from "../ui/Button";

interface PlanListProps {
  onSelectPlan: (id: number) => void;
  onCreateNew: () => void;
}

export const PlanList: React.FC<PlanListProps> = ({
  onSelectPlan,
  onCreateNew,
}) => {
  const [plans, setPlans] = useState<MealPlan[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    planService
      .getAll()
      .then(setPlans)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-center p-8">Загрузка планов...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-slate-800">Мои планы</h2>
        <Button onClick={onCreateNew}>+ Новый план</Button>
      </div>

      {plans.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-xl border border-dashed border-slate-300">
          <div className="text-4xl mb-4">🥗</div>
          <h3 className="text-lg font-medium text-slate-900">
            У вас пока нет планов питания
          </h3>
          <p className="text-slate-500 mb-6">
            Создайте свой первый план с помощью ИИ за пару кликов
          </p>
          <Button onClick={onCreateNew}>Создать план</Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {plans.map((plan) => (
            <Card
              key={plan.id}
              className="flex flex-col hover:shadow-lg transition-all group"
            >
              <div
                className="flex-grow cursor-pointer"
                onClick={() => onSelectPlan(plan.id)}
              >
                <CardHeader>
                  <CardTitle className="group-hover:text-primary transition-colors">
                    {plan.goal}
                  </CardTitle>
                  <div className="text-sm text-slate-500">
                    {new Date(plan.created_at).toLocaleDateString("ru-RU")}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex justify-between items-center text-sm mb-2">
                    <span className="text-slate-500">Калории:</span>
                    <span className="font-semibold bg-green-50 text-green-700 px-2 py-0.5 rounded">
                      {plan.calories}
                    </span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-slate-500">Бюджет:</span>
                    <span className="font-semibold bg-blue-50 text-blue-700 px-2 py-0.5 rounded">
                      {plan.budget} ₽
                    </span>
                  </div>
                </CardContent>
              </div>
              <CardFooter className="mt-auto pt-4 border-t border-slate-100 flex justify-between items-center">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onSelectPlan(plan.id)}
                >
                  Открыть →
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (
                      window.confirm(
                        `Вы уверены, что хотите удалить план "${plan.goal}"?`
                      )
                    ) {
                      planService
                        .delete(plan.id)
                        .then(() => {
                          setPlans((prevPlans) =>
                            prevPlans.filter((p) => p.id !== plan.id)
                          );
                        })
                        .catch((err) => {
                          console.error("Failed to delete plan:", err);
                          alert("Не удалось удалить план.");
                        });
                    }
                  }}
                >
                  Удалить
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
