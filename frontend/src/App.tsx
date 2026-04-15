import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';
import { RecipesPage } from '@/pages/RecipesPage';
import { RecipeDetailPage } from '@/pages/RecipeDetailPage';
import { PlannerPage } from '@/pages/PlannerPage';
import { NotesPage } from '@/pages/NotesPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<RecipesPage />} />

          <Route path="recipes/:id" element={<RecipeDetailPage />} />
          
          <Route path="planner" element={<PlannerPage />} />
          <Route path="notes" element={<NotesPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
