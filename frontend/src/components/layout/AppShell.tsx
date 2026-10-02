import { useState, type ReactNode } from 'react';
import { useAuth } from '../../context/AuthContext';
import DashboardPage from '../../pages/DashboardPage';
import ChatPage from '../../pages/ChatPage';
import MealPlanPage from '../../pages/MealPlanPage';
import FoodLogPage from '../../pages/FoodLogPage';
import ProgressPage from '../../pages/ProgressPage';
import ProfilePage from '../../pages/ProfilePage';

type Route = 'dashboard' | 'chat' | 'meal-plan' | 'food-log' | 'progress' | 'profile';

const NAV_ITEMS: { id: Route; icon: string; label: string }[] = [
  { id: 'dashboard', icon: '📊', label: 'Dashboard' },
  { id: 'chat', icon: '🌱', label: 'AI Coach' },
  { id: 'meal-plan', icon: '🍽️', label: 'Meal Plan' },
  { id: 'food-log', icon: '📝', label: 'Food Log' },
  { id: 'progress', icon: '📈', label: 'Progress' },
  { id: 'profile', icon: '👤', label: 'Profile' },
];

export default function AppShell() {
  const { user, profile, logout } = useAuth();
  const [route, setRoute] = useState<Route>('dashboard');

  const firstName = profile?.full_name?.split(' ')[0] || user?.email?.split('@')[0] || 'User';

  const renderPage = (): ReactNode => {
    switch (route) {
      case 'dashboard':   return <DashboardPage />;
      case 'chat':        return <ChatPage />;
      case 'meal-plan':   return <MealPlanPage />;
      case 'food-log':    return <FoodLogPage />;
      case 'progress':    return <ProgressPage />;
      case 'profile':     return <ProfilePage />;
    }
  };

  return (
    <div style={{ display:'flex', height:'100dvh', overflow:'hidden', background:'var(--bg-base)' }}>
      {/* Sidebar - Nutrient Agent styling */}
      <aside style={{
        width: 250,
        minWidth: 250,
        background: 'var(--bg-sidebar)',
        borderRight: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        padding: '24px 16px',
        gap: 16,
      }}>
        {/* Brand Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '4px 6px' }}>
          <div style={{
            width: 38,
            height: 38,
            borderRadius: 12,
            background: 'var(--accent-terracotta)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ffffff',
            boxShadow: '0 2px 8px rgba(209, 100, 77, 0.25)',
            flexShrink: 0
          }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 22v-7"/>
              <path d="M12 15c-3.5 0-6-2.5-6-6 4 0 6 2 6 6Z"/>
              <path d="M12 15c3.5 0 6-2.5 6-6-4 0-6 2-6 6Z"/>
            </svg>
          </div>
          <div>
            <div style={{
              fontFamily: 'var(--font-serif)',
              fontSize: 17,
              fontWeight: 700,
              letterSpacing: '-0.02em',
              color: 'var(--text-primary)',
              lineHeight: 1.2
            }}>
              Nutrient Agent
            </div>
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 9,
              letterSpacing: '0.12em',
              color: 'var(--text-muted)',
              textTransform: 'uppercase',
              marginTop: 2
            }}>
              Everyday Food Support
            </div>
          </div>
        </div>

        {/* Start Fresh Action */}
        <button
          onClick={() => setRoute('chat')}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8,
            padding: '10px 16px',
            background: '#ffffff',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-full)',
            fontFamily: 'var(--font-sans)',
            fontSize: 13.5,
            fontWeight: 500,
            color: 'var(--text-primary)',
            cursor: 'pointer',
            transition: 'all 0.2s',
            boxShadow: '0 1px 3px rgba(31, 41, 34, 0.04)',
          }}
          onMouseEnter={e => {
            e.currentTarget.style.borderColor = 'var(--accent-terracotta)';
            e.currentTarget.style.color = 'var(--accent-terracotta)';
          }}
          onMouseLeave={e => {
            e.currentTarget.style.borderColor = 'var(--border)';
            e.currentTarget.style.color = 'var(--text-primary)';
          }}
        >
          <span style={{ fontSize: 16, color: 'var(--accent-terracotta)' }}>+</span>
          Start fresh
        </button>

        {/* Navigation Items */}
        <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 3, overflowY: 'auto' }}>
          {NAV_ITEMS.map(item => (
            <button
              key={item.id}
              id={`nav-${item.id}`}
              className={`nav-item ${route === item.id ? 'active' : ''}`}
              onClick={() => setRoute(item.id)}
            >
              <span style={{ fontSize: 15 }}>{item.icon}</span>
              <span>{item.label}</span>
              {item.id === 'chat' && (
                <span className="pulse-glow" style={{
                  marginLeft: 'auto',
                  width: 7,
                  height: 7,
                  borderRadius: '50%',
                  background: 'var(--accent-sage)',
                  flexShrink: 0
                }} />
              )}
            </button>
          ))}

          {/* Editorial Reminder Card */}
          <div style={{
            marginTop: 'auto',
            marginBottom: 8,
            background: '#ffffff',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-lg)',
            padding: '16px 14px',
            boxShadow: '0 2px 8px rgba(31, 41, 34, 0.03)',
            position: 'relative',
            overflow: 'hidden'
          }}>
            <div style={{
              position: 'absolute',
              top: -15,
              right: -15,
              width: 55,
              height: 55,
              borderRadius: '50%',
              border: '1px solid rgba(209, 100, 77, 0.15)',
              pointerEvents: 'none'
            }} />
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 9.5,
              letterSpacing: '0.08em',
              color: 'var(--accent-terracotta)',
              fontWeight: 600,
              textTransform: 'uppercase',
              marginBottom: 4
            }}>
              Keep It Human
            </div>
            <div style={{
              fontFamily: 'var(--font-serif)',
              fontSize: 14,
              fontWeight: 700,
              color: 'var(--text-primary)',
              lineHeight: 1.35,
              marginBottom: 4
            }}>
              Good food advice fits real life.
            </div>
            <div style={{
              fontSize: 11.5,
              color: 'var(--text-secondary)',
              lineHeight: 1.45
            }}>
              Flexible ideas, everyday ingredients, and room for what works for you.
            </div>
          </div>
        </nav>

        {/* User Footer & Status */}
        <div style={{
          borderTop: '1px solid var(--border)',
          paddingTop: 14,
          display: 'flex',
          flexDirection: 'column',
          gap: 10
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            padding: '6px 8px',
            borderRadius: 12,
            background: '#ffffff',
            border: '1px solid var(--border)'
          }}>
            <div style={{
              width: 32,
              height: 32,
              borderRadius: '50%',
              flexShrink: 0,
              background: 'var(--accent-terracotta)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 13,
              fontWeight: 700,
              color: '#ffffff'
            }}>
              {firstName[0]?.toUpperCase()}
            </div>
            <div style={{ minWidth: 0, flex: 1 }}>
              <div style={{
                fontSize: 12.5,
                fontWeight: 600,
                color: 'var(--text-primary)',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis'
              }}>
                {firstName}
              </div>
              <div style={{
                fontSize: 10.5,
                color: 'var(--text-muted)',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                textTransform: 'capitalize'
              }}>
                {profile?.goal?.replace('_', ' ') || 'healthy routine'}
              </div>
            </div>
            <button
              id="nav-logout"
              onClick={logout}
              title="Sign Out"
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                fontSize: 12,
                padding: '4px'
              }}
            >
              🚪
            </button>
          </div>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: 10.5,
            color: 'var(--text-muted)',
            padding: '0 4px',
            fontFamily: 'var(--font-mono)'
          }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--accent-sage)' }} />
              LOCAL PREVIEW
            </span>
            <span>v1.2</span>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100dvh', overflow: 'hidden' }}>
        {/* Top Header Bar */}
        <header style={{
          height: 48,
          borderBottom: '1px solid var(--border)',
          background: 'var(--bg-base)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 28px',
          flexShrink: 0
        }}>
          <div style={{ fontSize: 12.5, color: 'var(--text-secondary)' }}>
            <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Your food companion</span>
            <span style={{ margin: '0 8px', color: 'var(--accent-terracotta)' }}>•</span>
            Practical, personal, pressure-free
          </div>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
            background: 'var(--accent-sage-light)',
            color: 'var(--accent-sage-dark)',
            padding: '3px 10px',
            borderRadius: 'var(--radius-full)',
            fontSize: 11,
            fontWeight: 600,
            fontFamily: 'var(--font-mono)',
            border: '1px solid rgba(126, 146, 120, 0.25)'
          }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--accent-sage)' }} />
            LIVE AGENT
          </div>
        </header>

        {/* Page Content */}
        <main style={{ flex: 1, overflowY: 'auto', background: 'var(--bg-base)' }}>
          {renderPage()}
        </main>
      </div>
    </div>
  );
}
