import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  Outlet,
} from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useStore } from '@/store/useStore';
import { Header } from '@/components/Header';
import { LoadingOverlay } from '@/components/ui/loading';
import { Dashboard } from '@/pages/Dashboard';
import { NewTrade } from '@/pages/NewTrade';
import { TradeDetail } from '@/pages/TradeDetail';
import { TradesList } from '@/pages/TradesList';
import { Analytics } from '@/pages/Analytics';
import { Onboarding } from '@/pages/Onboarding';

// Protected route wrapper
function ProtectedLayout() {
  const { isAuthenticated, apiKey, fetchProfile } = useStore();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      if (apiKey) {
        try {
          await fetchProfile();
        } catch {
          // Profile fetch failed, redirect will happen
        }
      }
      setIsChecking(false);
    };

    checkAuth();
  }, [apiKey, fetchProfile]);

  if (isChecking) {
    return <LoadingOverlay />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/onboarding" replace />;
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/onboarding" element={<Onboarding />} />

        {/* Protected routes */}
        <Route element={<ProtectedLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/trade/new" element={<NewTrade />} />
          <Route path="/trade/:id" element={<TradeDetail />} />
          <Route path="/trades" element={<TradesList />} />
          <Route path="/analytics" element={<Analytics />} />
        </Route>

        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
