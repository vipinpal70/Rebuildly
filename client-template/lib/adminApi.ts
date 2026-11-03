'use client';

// Thin client for the FastAPI admin backend. Token is kept in a cookie (so the
// Next middleware can gate the dashboard) and mirrored to localStorage.
export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8009';
const TOKEN_KEY = 'admin_token';

export function setToken(token: string) {
  if (typeof document !== 'undefined') {
    document.cookie = `${TOKEN_KEY}=${token}; path=/; max-age=${60 * 60 * 12}; samesite=lax`;
    localStorage.setItem(TOKEN_KEY, token);
  }
}

export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY) ||
    (document.cookie.match(/(?:^|; )admin_token=([^;]+)/)?.[1] ?? null);
}

export function clearToken() {
  if (typeof document !== 'undefined') {
    document.cookie = `${TOKEN_KEY}=; path=/; max-age=0`;
    localStorage.removeItem(TOKEN_KEY);
  }
}

async function req(path: string, options: RequestInit = {}): Promise<any> {
  const token = getToken();
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });
  if (res.status === 401) {
    clearToken();
    if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) {
      window.location.href = '/login';
    }
    throw new Error('Unauthorized');
  }
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || `Request failed (${res.status})`);
  return res.json();
}

export const adminApi = {
  login: (username: string, password: string) =>
    req('/api/v1/admin/login', { method: 'POST', body: JSON.stringify({ username, password }) }),
  stats: () => req('/api/v1/admin/stats'),
  leads: (params: {
    page?: number;
    limit?: number;
    category?: string;
    city?: string;
    tier?: string;
    has_gaps?: string;
    has_site?: string;
    min_score?: number;
    search?: string;
    sort_by?: string;
    order?: string;
  } = {}) => {
    const q = new URLSearchParams();
    if (params.page) q.set('page', String(params.page));
    if (params.limit) q.set('limit', String(params.limit));
    if (params.category) q.set('category', params.category);
    if (params.city) q.set('city', params.city);
    if (params.tier) q.set('tier', params.tier);
    if (params.has_gaps) q.set('has_gaps', params.has_gaps);
    if (params.has_site) q.set('has_site', params.has_site);
    if (params.min_score !== undefined) q.set('min_score', String(params.min_score));
    if (params.search) q.set('search', params.search);
    if (params.sort_by) q.set('sort_by', params.sort_by);
    if (params.order) q.set('order', params.order);
    return req(`/api/v1/admin/leads?${q.toString()}`);
  },
  leadDetail: (id: string) => req(`/api/v1/admin/leads/${id}`),
  generateLeads: (body: { categories: string[]; countries: string[]; cities?: string[]; max_per_city: number; min_buying_power?: number }) =>
    req('/api/v1/admin/leads/generate', { method: 'POST', body: JSON.stringify(body) }),
  jobStatus: (id: string) => req(`/api/v1/admin/jobs/${id}`),
  enrich: (id: string) => req(`/api/v1/admin/leads/${id}/enrich`, { method: 'POST' }),
  saveAdditionalUrls: (id: string, urls: { url: string; label: string }[]) =>
    req(`/api/v1/admin/leads/${id}/urls`, { method: 'PUT', body: JSON.stringify({ urls }) }),
  generateSite: (id: string) => req(`/api/v1/admin/leads/${id}/generate-site`, { method: 'POST' }),
  sites: () => req('/api/v1/admin/sites'),
  siteVersions: (slug: string) => req(`/api/v1/admin/sites/${slug}/versions`),
  regenerateSite: (slug: string, feedback?: string) =>
    req(`/api/v1/admin/sites/${slug}/regenerate`, { method: 'POST', body: JSON.stringify({ feedback: feedback || null }) }),
  deleteSite: (slug: string) => req(`/api/v1/admin/sites/${slug}`, { method: 'DELETE' }),
  crmDrafts: (id: string) => req(`/admin/crm/leads/${id}/drafts`),
  generateAiSalesCopy: (id: string) => req(`/admin/crm/leads/${id}/generate-ai-copy`, { method: 'POST' }),
  saveCrmDrafts: (id: string, body: any) => req(`/admin/crm/leads/${id}/drafts`, { method: 'POST', body: JSON.stringify(body) }),
  sendCrmEmail: (id: string, body: any) => req(`/admin/crm/leads/${id}/send-email`, { method: 'POST', body: JSON.stringify(body) }),
  updateCrmStatus: (id: string, body: any) => req(`/admin/crm/leads/${id}/status`, { method: 'POST', body: JSON.stringify(body) }),
  getLlmSettings: () => req('/api/v1/admin/settings/llm'),
  saveLlmSettings: (body: { provider: string; api_key?: string | null; model?: string | null }) =>
    req('/api/v1/admin/settings/llm', { method: 'PUT', body: JSON.stringify(body) }),
  testLlmSettings: () => req('/api/v1/admin/settings/llm/test', { method: 'POST' }),
  changePassword: (body: { current_password: string; new_password: string }) =>
    req('/api/v1/admin/change-password', { method: 'POST', body: JSON.stringify(body) }),
};
