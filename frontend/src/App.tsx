import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';
import { RecipesPage } from '@/pages/RecipesPage';
import { RecipeDetailPage } from '@/pages/RecipeDetailPage';
import { MenuPlannerPage } from '@/pages/MenuPlannerPage';
import { NotesPage } from '@/pages/NotesPage';
import { TasksPage } from '@/pages/TasksPage';
import { CalculatorPage } from '@/pages/CalculatorPage';
import { StartingPage } from '@/pages/StartingPage';
import { LoginPage } from '@/pages/LoginPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
          <Route path="login" element={<LoginPage />} />

        <Route element={<AppLayout />}>
        
          <Route index element={<StartingPage />} />


          <Route path="recipes" element={<RecipesPage />} />
          <Route path="recipes/:id" element={<RecipeDetailPage />} />
          
          <Route path="menu-planner" element={<MenuPlannerPage />} />
          <Route path="tasks" element={<TasksPage />} />
          <Route path="calculator" element={<CalculatorPage />} />
          <Route path="notes" element={<NotesPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
