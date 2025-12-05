import React, { useState, useEffect } from "react";
import { AuthForm } from "./components/auth/AuthForm";
import { Sidebar } from "./components/layout/Sidebar";
import { Header } from "./components/layout/Header";
import { Dashboard } from "./components/dashboard/Dashboard";
import { CreatePlanForm } from "./components/plans/CreatePlanForm";
import { PlanList } from "./components/plans/PlanList";
import { PlanDetail } from "./components/plans/PlanDetail";

// Simple Router implementation since standard routing libraries can be complex to setup in single file response
const App: React.FC = () => {
  const [token, setToken] = useState<string | null>(
    localStorage.getItem("token")
  );
  const [currentPath, setCurrentPath] = useState(
    window.location.hash.replace("#", "") || "/"
  );
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Parse dynamic ID from route, e.g., /plans/123
  const planIdMatch = currentPath.match(/^\/plans\/(\d+)$/);
  const currentPlanId = planIdMatch ? parseInt(planIdMatch[1]) : null;

  useEffect(() => {
    const handleHashChange = () => {
      setCurrentPath(window.location.hash.replace("#", "") || "/");
    };
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  const navigate = (path: string) => {
    window.location.hash = path;
    // Close sidebar on mobile on navigation
    setSidebarOpen(false);
  };

  const handleLogin = (newToken: string) => {
    localStorage.setItem("token", newToken);
    setToken(newToken);
    navigate("/");
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
    navigate("/");
  };

  if (!token) {
    return <AuthForm onSuccess={handleLogin} />;
  }

  const renderContent = () => {
    if (currentPlanId) {
      return <PlanDetail planId={currentPlanId} />;
    }

    switch (currentPath) {
      case "/":
        return (
          <Dashboard
            onNavigate={navigate}
            onViewPlan={(id) => navigate(`/plans/${id}`)}
          />
        );
      case "/create":
        return <CreatePlanForm onSuccess={(id) => navigate(`/plans/${id}`)} />;
      case "/plans":
        return (
          <PlanList
            onSelectPlan={(id) => navigate(`/plans/${id}`)}
            onCreateNew={() => navigate("/create")}
          />
        );
      default:
        return <div>404 Not Found</div>;
    }
  };

  return (
    // ИЗМЕНЕНИЕ 1: h-screen вместо min-h-screen и overflow-hidden
    // Это фиксирует высоту приложения по высоте окна браузера
    <div className="flex h-screen overflow-hidden bg-slate-50">
      {/* Sidebar теперь будет занимать всю высоту, и если меню длинное — скролл будет внутри него */}
      <Sidebar
        isOpen={sidebarOpen}
        activePath={
          currentPath.split("/")[1] ? `/${currentPath.split("/")[1]}` : "/"
        }
        onNavigate={navigate}
      />

      {/* Затемнение для мобильных */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* ИЗМЕНЕНИЕ 2: flex-1 flex flex-col h-full */}
      {/* Правая часть занимает всё оставшееся место и высоту */}
      <div className="flex-1 flex flex-col min-w-0 h-full">
        <Header
          onLogout={handleLogout}
          toggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          userName="User"
        />

        {/* ИЗМЕНЕНИЕ 3: flex-1 overflow-y-auto */}
        {/* Скролл теперь находится ТОЛЬКО в этом контейнере (main), а не на всей странице */}
        <main className="flex-1 p-4 md:p-8 overflow-y-auto scroll-smooth">
          <div className="max-w-7xl mx-auto w-full">{renderContent()}</div>
        </main>
      </div>
    </div>
  );
};

export default App;
