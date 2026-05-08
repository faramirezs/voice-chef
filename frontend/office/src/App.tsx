import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import type { ReactNode } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { RecipesPage } from '@/pages/RecipesPage';
import { RecipeDetailPage } from '@/pages/RecipeDetailPage';
import { CreateRecipePage } from '@/pages/CreateRecipePage';
import { MenuPlannerPage } from '@/pages/MenuPlannerPage';
import { NotesPage } from '@/pages/NotesPage';
import { TasksPage } from '@/pages/TasksPage';
import { CalculatorPage } from '@/pages/CalculatorPage';
import { StartingPage } from '@/pages/StartingPage';
import { SettingsGeneralPage } from '@/pages/SettingsGeneral';
import { IngredientsPage } from '@/pages/IngredientsPage';
import { AnalyticsPage } from '@/pages/AnalyticsPage';
import { TimersPage } from '@/pages/TimersPage';
import { ProfilePage } from '@/pages/ProfilePage';
import { FilesPage } from '@/pages/FilesPage';

import { LoginPage } from '@/pages/LoginPage';
import { SignupPage } from '@/pages/SignupPage';
import { TermsOfServicePage } from '@/pages/TermsOfServicePage';
import { PrivacyPolicyPage } from '@/pages/PrivacyPolicyPage';

function PublicOnlyRoute({ children }: { children: ReactNode }) {
  const isLoggedIn = Boolean(localStorage.getItem('token'));
  return isLoggedIn ? <Navigate to="/" replace /> : children;
}

function ProtectedRoute({ children }: { children: ReactNode }) {
  const isLoggedIn = Boolean(localStorage.getItem('token'));
  return isLoggedIn ? children : <Navigate to="/login" replace />;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
          <Route
            path="login"
            element={
              <PublicOnlyRoute>
                <LoginPage />
              </PublicOnlyRoute>
            }
          />
          <Route
            path="signup"
            element={
              <PublicOnlyRoute>
                <SignupPage />
              </PublicOnlyRoute>
            }
          />
          <Route path="terms" element={<TermsOfServicePage />} />
          <Route path="privacy" element={<PrivacyPolicyPage />} />

        <Route
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
        
          <Route index element={<StartingPage />} />

          <Route path="recipes" element={<RecipesPage />} />
          <Route path="recipes/new" element={<CreateRecipePage />} />
          <Route path="recipes/:id" element={<RecipeDetailPage />} />
          
          <Route path="menu-planner" element={<MenuPlannerPage />} />
          <Route path="tasks" element={<TasksPage />} />
          <Route path="calculator" element={<CalculatorPage />} />
          <Route path="timers" element={<TimersPage />} />
          <Route path="notes" element={<NotesPage />} />

          <Route path="ingredients" element={<IngredientsPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="files" element={<FilesPage />} />

          <Route path="settings/*" element={<SettingsGeneralPage />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
