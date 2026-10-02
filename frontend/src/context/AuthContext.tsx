import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { authApi, profileApi } from '../api/client';

interface User { id: number; email: string; full_name?: string; }
interface AuthCtx {
  user: User | null;
  profile: any | null;
  loading: boolean;
  login: (email: string, pw: string) => Promise<void>;
  register: (email: string, pw: string, name: string) => Promise<void>;
  logout: () => void;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthCtx>({} as AuthCtx);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  async function loadProfile() {
    try {
      const p = await profileApi.get();
      setProfile(p);
    } catch { setProfile(null); }
  }

  useEffect(() => {
    (async () => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        try {
          const me = await authApi.me();
          setUser(me);
          await loadProfile();
        } catch { localStorage.removeItem('auth_token'); }
      }
      setLoading(false);
    })();
  }, []);

  async function login(email: string, password: string) {
    const data = await authApi.login({ email, password });
    localStorage.setItem('auth_token', data.access_token);
    setUser(data.user);
    await loadProfile();
  }

  async function register(email: string, password: string, full_name: string) {
    const data = await authApi.register({ email, password, full_name });
    localStorage.setItem('auth_token', data.access_token);
    setUser(data.user);
  }

  function logout() {
    localStorage.removeItem('auth_token');
    setUser(null);
    setProfile(null);
  }

  async function refreshProfile() {
    await loadProfile();
  }

  return (
    <AuthContext.Provider value={{ user, profile, loading, login, register, logout, refreshProfile }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
