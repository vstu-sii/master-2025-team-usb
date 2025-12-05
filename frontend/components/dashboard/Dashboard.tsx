import React, { useEffect, useState } from 'react';
import { Button } from '../ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { MealPlan } from '../../types';
import { planService } from '../../services/api';

interface DashboardProps {
  onNavigate: (path: string) => void;
  onViewPlan: (id: number) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onNavigate, onViewPlan }) => {
  const [recentPlan, setRecentPlan] = useState<MealPlan | null>(null);

  useEffect(() => {
    planService.getAll().then(plans => {
      if (plans.length > 0) setRecentPlan(plans[0]);
    }).catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-primary to-emerald-600 rounded-2xl p-8 text-white shadow-lg">
        <h1 className="text-3xl font-bold mb-2">Добро пожаловать в AI Meal Planner!</h1>
        <p className="opacity-90 max-w-xl mb-6">
          Генерируйте сбалансированные планы питания с учетом ваших целей, бюджета и вкусовых предпочтений за считанные секунды.
        </p>
        <Button variant="secondary" size="lg" onClick={() => onNavigate('/create')} className="shadow-lg bg-white text-primary hover:bg-slate-100 border-none">
          ✨ Создать новый план
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Последний активный план</CardTitle>
          </CardHeader>
          <CardContent>
            {recentPlan ? (
              <div className="flex flex-col sm:flex-row justify-between items-center gap-4 bg-slate-50 p-4 rounded-lg border">
                <div>
                  <h3 className="font-bold text-lg">{recentPlan.goal}</h3>
                  <div className="flex gap-3 text-sm text-slate-600 mt-1">
                     <span>🔥 {recentPlan.calories} ккал</span>
                     <span>💰 {recentPlan.budget} руб</span>
                  </div>
                </div>
                <Button onClick={() => onViewPlan(recentPlan.id)}>Открыть план</Button>
              </div>
            ) : (
               <div className="text-center py-6 text-slate-500">
                 Нет активных планов. Создайте первый!
               </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
             <CardTitle>Быстрые пресеты</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
             <Button variant="outline" className="w-full justify-start" onClick={() => onNavigate('/create')}>🥗 Похудение</Button>
             <Button variant="outline" className="w-full justify-start" onClick={() => onNavigate('/create')}>💪 Набор массы</Button>
             <Button variant="outline" className="w-full justify-start" onClick={() => onNavigate('/create')}>🥑 Кето диета</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};