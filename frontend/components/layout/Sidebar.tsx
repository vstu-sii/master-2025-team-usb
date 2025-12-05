import React from 'react';

interface SidebarProps {
  isOpen: boolean;
  activePath: string;
  onNavigate: (path: string) => void;
}

const MENU_ITEMS = [
  { label: 'Дашборд', path: '/' },
  { label: 'Мои планы', path: '/plans' },
  { label: 'Создать план', path: '/create' },
];

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, activePath, onNavigate }) => {
  return (
    <aside
      className={`fixed inset-y-0 left-0 z-40 w-64 transform bg-slate-900 text-white transition-transform duration-200 ease-in-out lg:static lg:translate-x-0 ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}
    >
      <div className="flex h-16 items-center justify-center border-b border-slate-800 font-bold text-xl">
        Меню
      </div>
      <nav className="p-4 space-y-2">
        {MENU_ITEMS.map((item) => (
          <button
            key={item.path}
            onClick={() => onNavigate(item.path)}
            className={`w-full rounded-md px-4 py-2 text-left text-sm font-medium transition-colors ${
              activePath === item.path
                ? 'bg-primary text-white'
                : 'text-slate-400 hover:bg-slate-800 hover:text-white'
            }`}
          >
            {item.label}
          </button>
        ))}
      </nav>
    </aside>
  );
};