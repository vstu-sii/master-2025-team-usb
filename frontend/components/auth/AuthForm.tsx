import React, { useState } from 'react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { authService } from '../../services/api';

interface AuthFormProps {
  onSuccess: (token: string) => void;
}

export const AuthForm: React.FC<AuthFormProps> = ({ onSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isLogin) {
        const res = await authService.login(email, password);
        onSuccess(res.access_token);
      } else {
        await authService.register(email, password, name);
        // Auto login after register
        const res = await authService.login(email, password);
        onSuccess(res.access_token);
      }
    } catch (err: any) {
      setError(err.message || 'Ошибка аутентификации');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-center text-2xl font-bold text-primary">
            {isLogin ? 'Вход' : 'Регистрация'}
          </CardTitle>
          <p className="text-center text-sm text-slate-500">
            {isLogin ? 'Добро пожаловать обратно' : 'Создайте аккаунт для старта'}
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <Input
                label="Имя"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            )}
            <Input
              type="email"
              label="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Input
              type="password"
              label="Пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            {error && <div className="p-3 bg-red-50 text-red-600 rounded-md text-sm">{error}</div>}

            <Button type="submit" className="w-full" isLoading={loading}>
              {isLogin ? 'Войти' : 'Зарегистрироваться'}
            </Button>
          </form>

          <div className="mt-4 text-center text-sm">
            <span className="text-slate-600">{isLogin ? 'Нет аккаунта?' : 'Уже есть аккаунт?'}</span>
            <button
              type="button"
              className="ml-2 font-medium text-primary hover:underline"
              onClick={() => {
                setIsLogin(!isLogin);
                setError(null);
              }}
            >
              {isLogin ? 'Создать' : 'Войти'}
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};