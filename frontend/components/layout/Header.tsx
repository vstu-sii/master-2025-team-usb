import React from 'react';
import { Button } from '../ui/Button';

interface HeaderProps {
  onLogout: () => void;
  toggleSidebar: () => void;
  userName?: string;
}

export const Header: React.FC<HeaderProps> = ({ onLogout, toggleSidebar, userName }) => {
  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center gap-4 border-b bg-white px-6 shadow-sm">
      <Button variant="ghost" size="sm" className="lg:hidden" onClick={toggleSidebar}>
        <span className="text-xl">☰</span>
      </Button>
      <div className="flex items-center gap-2 font-bold text-xl text-primary">
        <span className="text-2xl">🥗</span> AI Meal Planner
      </div>
      <div className="flex-1"></div>
      <div className="flex items-center gap-4">
        {userName && <span className="text-sm font-medium text-slate-600 hidden md:inline">Привет, {userName}</span>}
        <Button variant="outline" size="sm" onClick={onLogout}>Выйти</Button>
      </div>
    </header>
  );
};