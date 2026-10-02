import { useAuth } from './context/AuthContext'
import AuthPage from './pages/AuthPage'
import OnboardingPage from './pages/OnboardingPage'
import AppShell from './components/layout/AppShell'

export default function App() {
  const { user, profile, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ display:'flex', alignItems:'center', justifyContent:'center', height:'100dvh', gap:16 }}>
        <div className="spinner" style={{ width:32, height:32, borderWidth:3 }} />
        <span style={{ color:'var(--text-secondary)', fontFamily:'Inter,sans-serif' }}>Loading…</span>
      </div>
    );
  }

  if (!user) return <AuthPage />;
  if (!profile) return <OnboardingPage />;
  return <AppShell />;
}
