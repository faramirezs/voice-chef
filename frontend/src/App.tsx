import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';

import { DbModelsCard } from '@/components/debug/DbModelsCard';

/**
 * A simplified App component for this branch.
 * It renders only the DbModelsCard on the root page.
 */
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route 
            path="/" 
            element={
              <div className="flex items-center justify-center min-h-screen bg-background">
                <DbModelsCard />
              </div>
            } 
          />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
