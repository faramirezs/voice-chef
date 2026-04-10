import { BrowserRouter, Routes, Route } from 'react-router-dom';

import { AppLayout } from '@/components/layout/AppLayout';
import { DebugPage } from '@/pages/DebugPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          {/* The root path will now show your DebugPage */}
          <Route path="/" element={<DebugPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
