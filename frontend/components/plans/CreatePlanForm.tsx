import React, { useState, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/Card";
import { Input } from "../ui/Input";
import { Button } from "../ui/Button";
import { planService } from "../../services/api";
import { PRESET_GOALS } from "../../constants";

interface CreatePlanFormProps {
  onSuccess: (planId: number) => void;
}

export const CreatePlanForm: React.FC<CreatePlanFormProps> = ({
  onSuccess,
}) => {
  const [goal, setGoal] = useState("");
  const [calories, setCalories] = useState(2000);
  const [budget, setBudget] = useState(5000);
  const [allergies, setAllergies] = useState("");
  const [preferences, setPreferences] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Ref для предотвращения повторных запросов
  const isSubmittingRef = useRef(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Защита от повторных кликов
    if (isSubmittingRef.current || loading) {
      return;
    }

    isSubmittingRef.current = true;
    setLoading(true);
    setError(null);

    try {
      const plan = await planService.create({
        goal,
        calories,
        budget,
        allergies,
        preferences,
      });
      onSuccess(plan.id);
    } catch (err: any) {
      // Обработка ошибки конфликта (уже генерируется)
      if (err.message.includes("already in progress")) {
        setError("План уже создаётся. Пожалуйста, подождите.");
      } else {
        setError(err.message || "Ошибка создания плана");
      }
    } finally {
      setLoading(false);
      isSubmittingRef.current = false;
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Создать новый план питания</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Цель питания
            </label>
            <div className="flex flex-wrap gap-2 mb-2">
              {PRESET_GOALS.map((g) => (
                <button
                  key={g}
                  type="button"
                  onClick={() => setGoal(g)}
                  disabled={loading}
                  className={`px-3 py-1 text-xs rounded-full border transition-colors ${
                    goal === g
                      ? "bg-primary text-white border-primary"
                      : "bg-white text-slate-600 border-slate-300 hover:bg-slate-50"
                  } ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
                >
                  {g}
                </button>
              ))}
            </div>
            <Input
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="Например: Похудеть к лету"
              required
              disabled={loading}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              type="number"
              label="Калории (ккал/день)"
              value={calories}
              onChange={(e) => setCalories(Number(e.target.value))}
              min={1000}
              max={6000}
              required
              disabled={loading}
            />
            <Input
              type="number"
              label="Бюджет (руб)"
              value={budget}
              onChange={(e) => setBudget(Number(e.target.value))}
              min={0}
              required
              disabled={loading}
            />
          </div>

          <Input
            label="Аллергии / Исключения"
            value={allergies}
            onChange={(e) => setAllergies(e.target.value)}
            placeholder="Например: Арахис, Молоко"
            disabled={loading}
          />

          <Input
            label="Предпочтения"
            value={preferences}
            onChange={(e) => setPreferences(e.target.value)}
            placeholder="Например: Люблю рыбу, не люблю грибы"
            disabled={loading}
          />

          {error && (
            <div className="text-red-500 text-sm p-3 bg-red-50 rounded-lg">
              {error}
            </div>
          )}

          <div className="bg-blue-50 p-4 rounded-lg text-sm text-blue-700">
            💡 <strong>AI Генерация:</strong> План создастся мгновенно, а блюда
            будут сгенерированы в фоне. Вы можете следить за прогрессом на
            странице плана.
          </div>

          <Button
            type="submit"
            className="w-full"
            size="lg"
            isLoading={loading}
            disabled={loading || !goal.trim()}
          >
            {loading ? "Создаём план..." : "Создать план"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};
