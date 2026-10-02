// API client for the Personal AI Nutrition Agent backend
const API_BASE = (import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL.replace(/\/$/, '') : '') + '/api';

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('auth_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const resp = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: resp.statusText }));
    throw new Error(err.detail || 'API error');
  }
  return resp.json();
}

// ── Auth ───────────────────────────────────────────────
export const authApi = {
  register: (data: { email: string; password: string; full_name?: string }) =>
    request<any>('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  login: (data: { email: string; password: string }) =>
    request<any>('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  me: () => request<any>('/auth/me'),
};

// ── Profile ────────────────────────────────────────────
export const profileApi = {
  get: () => request<any>('/profile'),
  create: (data: any) => request<any>('/profile', { method: 'POST', body: JSON.stringify(data) }),
  update: (data: any) => request<any>('/profile', { method: 'PUT', body: JSON.stringify(data) }),
};

// ── Nutrition ──────────────────────────────────────────
export const nutritionApi = {
  targets: () => request<any>('/nutrition/targets'),
  calculate: (data: any) => request<any>('/nutrition/calculate', { method: 'POST', body: JSON.stringify(data) }),
  goalFeasibility: (data: any) => request<any>('/nutrition/goal-feasibility', { method: 'POST', body: JSON.stringify(data) }),
};

// ── Dashboard ──────────────────────────────────────────
export const dashboardApi = {
  get: (date?: string) => request<any>(`/dashboard${date ? `?date=${date}` : ''}`),
};

// ── Foods ──────────────────────────────────────────────
export const foodsApi = {
  search: (q: string = '', category?: string, diet_type?: string) => {
    const params = new URLSearchParams({ query: q });
    if (category) params.set('category', category);
    if (diet_type) params.set('diet_type', diet_type);
    return request<any[]>(`/foods?${params}`);
  },
  getById: (id: number) => request<any>(`/foods/${id}`),
  create: (data: any) => request<any>('/foods', { method: 'POST', body: JSON.stringify(data) }),
  calculateServing: (data: any) =>
    request<any>('/foods/calculate-serving', { method: 'POST', body: JSON.stringify(data) }),
};

// ── Meals ──────────────────────────────────────────────
export const mealsApi = {
  today: () => request<any[]>('/meals/today'),
  byDate: (date: string) => request<any[]>(`/meals?date=${date}`),
  create: (data: any) => request<any>('/meals', { method: 'POST', body: JSON.stringify(data) }),
  delete: (id: number) => request<any>(`/meals/${id}`, { method: 'DELETE' }),
};

// ── Food Log ───────────────────────────────────────────
export const foodLogApi = {
  logNL: (text: string, date?: string) =>
    request<any>('/food-log', { method: 'POST', body: JSON.stringify({ text, date }) }),
  today: () => request<any>('/food-log/today'),
  logWater: (amount_ml: number, date?: string) =>
    request<any>('/food-log/water', { method: 'POST', body: JSON.stringify({ amount_ml, date }) }),
  logExercise: (data: any) =>
    request<any>('/food-log/exercise', { method: 'POST', body: JSON.stringify(data) }),
};

// ── Weight ─────────────────────────────────────────────
export const weightApi = {
  log: (weight_kg: number, note?: string, date?: string) =>
    request<any>('/weight', { method: 'POST', body: JSON.stringify({ weight_kg, note, date }) }),
  history: (days: number = 30) => request<any[]>(`/weight/history?days=${days}`),
};

// ── Meal Plan ──────────────────────────────────────────
export const mealPlanApi = {
  generate: (plan_date?: string) =>
    request<any>('/meal-plan/generate', { method: 'POST', body: JSON.stringify({ plan_date }) }),
  current: () => request<any>('/meal-plan/current'),
  getWeekly: (start_date?: string) =>
    request<any>(`/meal-plan/weekly${start_date ? `?start_date=${start_date}` : ''}`),
  generateWeekly: (plan_date?: string) =>
    request<any>('/meal-plan/weekly/generate', { method: 'POST', body: JSON.stringify({ plan_date }) }),
  getGroceryList: (start_date?: string) =>
    request<any>(`/meal-plan/grocery-list${start_date ? `?start_date=${start_date}` : ''}`),
  substitute: (food_name: string, target_calories?: number) =>
    request<any>('/meal-plan/substitute', { method: 'POST', body: JSON.stringify({ food_name, target_calories }) }),
  logSlot: (plan_id: number, slot_name: string) =>
    request<any>(`/meal-plan/log-slot-to-today/${plan_id}/${slot_name}`, { method: 'POST' }),
};

// ── Chat ───────────────────────────────────────────────
export const chatApi = {
  send: (message: string, session_id?: number) =>
    request<any>('/chat', { method: 'POST', body: JSON.stringify({ message, session_id }) }),
  history: (session_id?: number) =>
    request<any[]>(`/chat/history${session_id ? `?session_id=${session_id}` : ''}`),
  sessions: () => request<any[]>('/chat/sessions'),
  newSession: () => request<any>('/chat/sessions', { method: 'POST' }),
};

// ── Food Image ─────────────────────────────────────────
export const foodImageApi = {
  analyze: async (file: File) => {
    const token = localStorage.getItem('auth_token');
    const formData = new FormData();
    formData.append('file', file);
    const resp = await fetch(`${API_BASE}/food-image/analyze`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    });
    if (!resp.ok) throw new Error('Image analysis failed');
    return resp.json();
  },
  confirmLog: (data: any) =>
    request<any>('/food-image/confirm-log', { method: 'POST', body: JSON.stringify(data) }),
};

// ── Progress ───────────────────────────────────────────
export const progressApi = {
  weekly: () => request<any>('/progress/weekly'),
};

// ── RAG ────────────────────────────────────────────────
export const ragApi = {
  query: (query: string, top_k: number = 3) =>
    request<any>('/rag/query', { method: 'POST', body: JSON.stringify({ query, top_k }) }),
  documents: () => request<any[]>('/rag/documents'),
};
