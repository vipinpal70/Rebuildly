'use client';

import React, { useEffect, useState, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ShieldCheck, LogOut, Users, Gauge, Star, Sparkles, Globe, MapPin, Loader2,
  Play, RefreshCw, Wand2, ExternalLink, ChevronDown, Check, X, Search, Rocket, TrendingUp,
  Layers, RotateCw, Trash2, Filter, Activity, LayoutDashboard, Send, Eye, CheckCircle2,
  AlertTriangle, PhoneCall, MessageSquare, Mail, Terminal, ChevronRight, ChevronLeft, Settings,
  Zap, Award, BarChart3, Building2, MousePointerClick, Sun, Moon, Lock, Key, EyeOff, Save,
  CheckCircle, AlertCircle, ArrowUpDown, ArrowDown, ArrowUp, Link2, History
} from 'lucide-react';
import OutreachStudioModal from '@/components/OutreachStudioModal';
import ManagePagesModal from '@/components/ManagePagesModal';
import RegenerateFeedbackModal from '@/components/RegenerateFeedbackModal';
import VersionHistoryModal from '@/components/VersionHistoryModal';
import MultiSelectCombo from '@/components/MultiSelectCombo';
import { adminApi, clearToken, getToken } from '../lib/adminApi';

/* ------------------- Discovery Launcher: predefined option sets -------------------
 * Curated from leads-improve-plan.md's category priority table and country expansion
 * strategy — a starting point the admin can pick from, not a hard limit (custom text
 * is always accepted too). Cities are scoped per selected country so picking "USA"
 * doesn't leave UK cities suggested (or vice versa). */
const CATEGORY_OPTIONS = [
  'Dentist', 'Orthodontist', 'Chiropractor', 'Med Spa', 'Physiotherapist',
  'Solicitor', 'Attorney', 'Immigration Lawyer', 'Family Law Attorney', 'Estate Planning Attorney',
  'Accountant', 'CPA', 'Financial Advisor', 'Mortgage Broker',
  'Plumber', 'Electrician', 'HVAC Contractor', 'Roofing Contractor', 'Pest Control',
  'Boutique Gym', 'Yoga Studio',
];
// UK/Ireland use "Solicitor"; the USA uses "Attorney"/"Lawyer" — flag the mismatch
// inline rather than let a "Solicitor in Austin" query silently return nothing useful.
const CATEGORY_HINTS: Record<string, string> = {
  Solicitor: 'UK / Ireland term',
  Attorney: 'USA term',
};

const CITY_OPTIONS_BY_COUNTRY: Record<string, string[]> = {
  UK: ['Manchester', 'Leeds', 'Bristol', 'Birmingham', 'London', 'Sheffield', 'Liverpool', 'Newcastle', 'Nottingham', 'Edinburgh', 'Glasgow'],
  Ireland: ['Dublin', 'Cork', 'Galway', 'Limerick'],
  USA: ['Austin', 'Nashville', 'Charlotte', 'Raleigh', 'Columbus', 'Tampa', 'San Antonio', 'Denver', 'Indianapolis', 'Phoenix'],
  Australia: ['Brisbane', 'Perth', 'Adelaide', 'Sydney', 'Melbourne'],
  Germany: ['Berlin', 'Munich', 'Hamburg'],
  Canada: ['Toronto', 'Calgary', 'Ottawa'],
};
const COUNTRY_OPTIONS = Object.keys(CITY_OPTIONS_BY_COUNTRY);
// Both have soft opt-in / lower-risk cold email rules; the rest need a caution flag
// so the choice to include them is deliberate, not accidental — see
// leads-improve-plan.md Section 5 for the full compliance rationale per country.
const COUNTRY_HINTS: Record<string, string> = {
  Germany: '⚠ email restricted — LinkedIn/phone only',
  Canada: '⚠ CASL — opt-in only',
  Australia: '⚠ consent-based — LinkedIn-first',
};

/* --------------------------------- Compact Stat Card --------------------------------- */
function StatCard({ icon, label, value, subtext, accent, onClick, isLight }: {
  icon: React.ReactNode;
  label: string;
  value: React.ReactNode;
  subtext?: string;
  accent: string;
  onClick?: () => void;
  isLight?: boolean;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      onClick={onClick}
      className={`rounded-xl border p-3 flex items-center justify-between transition-all duration-200 ${
        onClick ? 'cursor-pointer hover:border-indigo-500/40 shadow-md' : ''
      } ${
        isLight ? 'bg-white border-slate-200/90 hover:bg-slate-50' : 'bg-slate-900/60 border-slate-800/80 hover:bg-slate-900/90'
      }`}
    >
      <div className="space-y-0.5">
        <div className={`text-[10px] font-bold uppercase tracking-wider ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>{label}</div>
        <div className={`text-xl font-bold font-mono tracking-tight ${isLight ? 'text-slate-900' : 'text-white'}`}>{value}</div>
        {subtext && <div className={`text-[10px] font-medium ${isLight ? 'text-slate-400' : 'text-slate-500'}`}>{subtext}</div>}
      </div>
      <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 shadow-md" style={{ background: accent }}>
        {icon}
      </div>
    </motion.div>
  );
}

function ScoreBadge({ score }: { score: number | null }) {
  if (score == null) return <span className="text-slate-400 text-[11px]">—</span>;
  const color = score >= 80 ? '#f43f5e' : score >= 60 ? '#f59e0b' : score >= 40 ? '#0284c7' : '#64748b';
  return (
    <span
      className="inline-flex items-center justify-center w-7 h-7 rounded-lg font-bold font-mono text-[11px] shadow-sm"
      style={{ color, backgroundColor: `${color}15`, border: `1px solid ${color}35` }}
    >
      {score}
    </span>
  );
}

function Toast({ msg, type = 'info', onClose }: { msg: string; type?: 'info' | 'success' | 'error'; onClose: () => void }) {
  useEffect(() => { const t = setTimeout(onClose, 3500); return () => clearTimeout(t); }, [onClose]);
  return (
    <motion.div
      initial={{ opacity: 0, y: 12, scale: 0.96 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 12, scale: 0.96 }}
      className={`fixed bottom-4 right-4 z-50 rounded-xl px-4 py-2.5 text-xs font-semibold shadow-2xl flex items-center gap-2 border ${
        type === 'success' ? 'bg-emerald-950 text-emerald-200 border-emerald-500/40' :
        type === 'error' ? 'bg-rose-950 text-rose-200 border-rose-500/40' :
        'bg-slate-900 text-slate-200 border-indigo-500/30'
      }`}
    >
      {type === 'success' ? <CheckCircle className="w-3.5 h-3.5 text-emerald-400" /> :
       type === 'error' ? <AlertCircle className="w-3.5 h-3.5 text-rose-400" /> :
       <Sparkles className="w-3.5 h-3.5 text-cyan-400" />}
      <span>{msg}</span>
    </motion.div>
  );
}

/* ------------------------------- Dense Lead Row ------------------------------- */
function LeadRow({
  lead,
  onAction,
  onOpenOutreach,
  onManagePages,
  busy,
  isLight
}: {
  lead: any;
  onAction: (id: string, act: 'enrich' | 'site') => void;
  onOpenOutreach: (id: string) => void;
  onManagePages: (lead: any) => void;
  busy: string;
  isLight: boolean;
}) {
  const [open, setOpen] = useState(false);
  const outreach = lead.outreach || {};

  const getOutreachPill = () => {
    if (outreach.preview_clicked || outreach.status === 'VIEWED') {
      return (
        <span className="px-1.5 py-0.5 text-[9px] font-bold rounded bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/25 flex items-center gap-1">
          <Eye className="w-2.5 h-2.5" /> Viewed ({outreach.click_count || 1}x)
        </span>
      );
    }
    switch (outreach.status) {
      case 'EMAIL_SENT':
        return <span className="px-1.5 py-0.5 text-[9px] font-semibold rounded bg-indigo-500/15 text-indigo-600 dark:text-indigo-300 border border-indigo-500/25 flex items-center gap-1"><Mail className="w-2.5 h-2.5" /> Email Sent</span>;
      case 'LINKEDIN_SENT':
        return <span className="px-1.5 py-0.5 text-[9px] font-semibold rounded bg-blue-500/15 text-blue-600 dark:text-blue-300 border border-blue-500/25 flex items-center gap-1"><Send className="w-2.5 h-2.5" /> LinkedIn</span>;
      case 'WA_SENT':
        return <span className="px-1.5 py-0.5 text-[9px] font-semibold rounded bg-emerald-500/15 text-emerald-600 dark:text-emerald-300 border border-emerald-500/25 flex items-center gap-1"><MessageSquare className="w-2.5 h-2.5" /> WA Sent</span>;
      case 'CALLED':
        return <span className="px-1.5 py-0.5 text-[9px] font-semibold rounded bg-amber-500/15 text-amber-600 dark:text-amber-300 border border-amber-500/25 flex items-center gap-1"><PhoneCall className="w-2.5 h-2.5" /> Called</span>;
      case 'CONVERTED':
        return <span className="px-1.5 py-0.5 text-[9px] font-bold rounded bg-purple-500/15 text-purple-600 dark:text-purple-300 border border-purple-500/25 flex items-center gap-1"><Award className="w-2.5 h-2.5" /> Converted</span>;
      default:
        return null;
    }
  };

  return (
    <>
      <tr className={`border-t transition-colors ${isLight ? 'border-slate-200/80 hover:bg-slate-50' : 'border-white/5 hover:bg-white/[0.02]'}`}>
        <td className="py-2 px-3"><ScoreBadge score={lead.score} /></td>
        <td className="py-2 px-3">
          <div className={`font-semibold text-xs flex items-center gap-2 ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
            {lead.name}
            {getOutreachPill()}
          </div>
          <div className={`text-[10px] flex items-center gap-1 mt-0.5 ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
            <MapPin className="w-2.5 h-2.5 text-slate-400" />{lead.city} · <Building2 className="w-2.5 h-2.5 text-slate-400 ml-0.5" />{lead.category}
          </div>
        </td>
        <td className="py-2 px-3 hidden md:table-cell">
          {lead.tier && (
            <span className={`text-[8px] font-semibold uppercase tracking-wide px-1.5 py-0.5 rounded border ${isLight ? 'bg-slate-100 border-slate-300 text-slate-600' : 'bg-slate-900 border-slate-700/80 text-slate-400'}`}>
              {lead.tier.replace(/_/g, ' ')}
            </span>
          )}
        </td>
        <td className="py-2 px-3 hidden lg:table-cell text-[11px] text-slate-400">
          {lead.missing_count != null ? (
            <span className="text-amber-500 font-semibold flex items-center gap-1">
              <AlertTriangle className="w-3 h-3" /> {lead.missing_count} gaps
            </span>
          ) : '—'}
        </td>
        <td className="py-2 px-3 hidden lg:table-cell">
          <div className="flex items-center gap-1.5">
            {lead.website && (
              <a href={lead.website} target="_blank" rel="noreferrer" title="Original Website" className={`p-1 rounded transition-colors ${isLight ? 'text-slate-500 hover:text-slate-900 hover:bg-slate-100' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}>
                <Globe className="w-3.5 h-3.5" />
              </a>
            )}
            {lead.google_maps_url && (
              <a href={lead.google_maps_url} target="_blank" rel="noreferrer" title="Google Maps" className={`p-1 rounded transition-colors ${isLight ? 'text-slate-500 hover:text-slate-900 hover:bg-slate-100' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}>
                <MapPin className="w-3.5 h-3.5" />
              </a>
            )}
          </div>
        </td>
        <td className="py-2 px-3">
          <div className="flex items-center justify-end gap-1.5">
            <button
              onClick={() => onOpenOutreach(lead.id)}
              className="text-[11px] font-bold px-2.5 py-1 rounded-lg inline-flex items-center gap-1 text-white shadow-md hover:opacity-90 cursor-pointer transition-all border border-indigo-400/30"
              style={{ background: 'linear-gradient(135deg, #4338ca, #6d28d9)' }}
              title="Launch Claude AI Sales Copywriter"
            >
              <Zap className="w-3 h-3 text-cyan-300" /> AI Sales Copy
            </button>
            <button
              onClick={() => onManagePages(lead)}
              title="Add team page, contact-us, about-us, or any URL for Enrich to read"
              className={`relative text-[11px] font-medium px-2.5 py-1 rounded-lg border inline-flex items-center gap-1 cursor-pointer ${isLight ? 'border-slate-300 text-slate-700 hover:bg-slate-100' : 'border-white/10 text-slate-300 hover:bg-white/5'}`}
            >
              <Link2 className="w-3 h-3 text-slate-400" /> Pages
              {!!lead.additional_urls?.length && (
                <span className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full bg-cyan-500 text-white text-[9px] font-bold flex items-center justify-center">
                  {lead.additional_urls.length}
                </span>
              )}
            </button>
            <button
              onClick={() => onAction(lead.id, 'enrich')}
              disabled={!!busy}
              className={`text-[11px] font-medium px-2.5 py-1 rounded-lg border inline-flex items-center gap-1 disabled:opacity-40 cursor-pointer ${isLight ? 'border-slate-300 text-slate-700 hover:bg-slate-100' : 'border-white/10 text-slate-300 hover:bg-white/5'}`}
            >
              {busy === lead.id + ':enrich' ? <Loader2 className="w-3 h-3 animate-spin" /> : <Search className="w-3 h-3 text-slate-400" />} Enrich
            </button>
            {lead.site ? (
              <a
                href={lead.site.preview_url}
                target="_blank"
                rel="noreferrer"
                className="text-[11px] font-bold px-2.5 py-1 rounded-lg inline-flex items-center gap-1 text-white shadow-sm hover:opacity-90"
                style={{ background: 'linear-gradient(135deg, #047857, #059669)' }}
              >
                <ExternalLink className="w-3 h-3" /> View
              </a>
            ) : (
              <button
                onClick={() => onAction(lead.id, 'site')}
                disabled={!!busy}
                className="text-[11px] font-bold px-2.5 py-1 rounded-lg inline-flex items-center gap-1 text-white disabled:opacity-40 shadow-sm hover:opacity-90 cursor-pointer"
                style={{ background: 'linear-gradient(135deg, #1d4ed8, #2563eb)' }}
              >
                {busy === lead.id + ':site' ? <Loader2 className="w-3 h-3 animate-spin" /> : <Wand2 className="w-3 h-3" />} Generate
              </button>
            )}
            <button onClick={() => setOpen(!open)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-0.5 cursor-pointer">
              <ChevronDown className={`w-3.5 h-3.5 transition-transform ${open ? 'rotate-180' : ''}`} />
            </button>
          </div>
        </td>
      </tr>
      <AnimatePresence>
        {open && (
          <tr>
            <td colSpan={6} className="p-0">
              <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
                <div className={`px-4 py-3 grid sm:grid-cols-2 lg:grid-cols-5 gap-2 border-b ${isLight ? 'bg-slate-100/70 border-slate-200' : 'bg-black/30 border-white/5'}`}>
                  {(lead.findings || []).map((f: any, i: number) => (
                    <div key={i} className={`flex items-center gap-1.5 text-[11px] p-1.5 rounded border ${isLight ? 'bg-white border-slate-200' : 'bg-slate-900/80 border-white/5'}`}>
                      {f.ok ? <Check className="w-3 h-3 text-emerald-500 shrink-0" /> : <X className="w-3 h-3 text-rose-500 shrink-0" />}
                      <span className={f.ok ? (isLight ? 'text-slate-800 font-medium' : 'text-slate-300 font-medium') : 'text-slate-400'}>{f.label}</span>
                    </div>
                  ))}
                </div>
              </motion.div>
            </td>
          </tr>
        )}
      </AnimatePresence>
    </>
  );
}

/* ------------------------------- Main Dashboard ------------------------------- */
export default function Dashboard() {
  // Client component — can't export Next.js `metadata` (that's server-only), and the
  // root layout's default title is a neutral placeholder shared with prospect-facing
  // /preview/[slug] links, so it's deliberately left alone rather than branded here.
  useEffect(() => { document.title = 'Rebuildly | Admin Dashboard'; }, []);
  const [ready, setReady] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'leads' | 'crm' | 'sites' | 'audits' | 'settings'>('overview');
  
  // Theme State (Dark / Light)
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');

  // Backend Data
  const [stats, setStats] = useState<any>(null);
  const [sites, setSites] = useState<any[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  
  // Paginated Leads Data state
  const [leadsData, setLeadsData] = useState<{
    leads: any[];
    total: number;
    page: number;
    limit: number;
    total_pages: number;
  }>({
    leads: [],
    total: 0,
    page: 1,
    limit: 25,
    total_pages: 1
  });

  const [busy, setBusy] = useState('');
  const [toast, setToast] = useState<{ msg: string; type: 'info' | 'success' | 'error' } | null>(null);
  const [outreachLeadId, setOutreachLeadId] = useState<string | null>(null);
  const [managePagesLead, setManagePagesLead] = useState<any | null>(null);
  const [regenTarget, setRegenTarget] = useState<any | null>(null);
  const [historyTarget, setHistoryTarget] = useState<any | null>(null);

  // Filters for Lead Pipeline API Call
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(25);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [selectedCity, setSelectedCity] = useState('ALL');
  const [selectedTier, setSelectedTier] = useState('ALL');
  const [selectedHasGaps, setSelectedHasGaps] = useState('ALL');
  const [selectedHasSite, setSelectedHasSite] = useState('ALL');
  const [minScore, setMinScore] = useState(0);
  const [sortBy, setSortBy] = useState<'score' | 'date' | 'name'>('score');
  const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc');

  // Available categories & cities extracted from backend
  const [allCategories, setAllCategories] = useState<string[]>(['Dentist', 'Solicitor', 'Lawyer', 'Dental Practice', 'Immigration']);
  const [allCities, setAllCities] = useState<string[]>(['Manchester', 'Bristol', 'London', 'Birmingham']);

  // CRM Kanban Filter
  const [crmStatusFilter, setCrmStatusFilter] = useState('ALL');

  // Discovery Launcher inputs — each a multi-select so one job can run a full
  // category x city x country campaign matrix (see DiscoveryEngine.run_campaign).
  const [categoriesSelected, setCategoriesSelected] = useState<string[]>(['Dentist']);
  const [citiesSelected, setCitiesSelected] = useState<string[]>(['Manchester', 'Bristol']);
  const [countriesSelected, setCountriesSelected] = useState<string[]>(['UK']);
  const [minBuyingPower, setMinBuyingPower] = useState(0);
  const [maxPer, setMaxPer] = useState(15);
  const [job, setJob] = useState<{ id: string; status: string } | null>(null);

  // Category suggestions: curated list merged with whatever's actually in the DB.
  const categoryOptions = useMemo(
    () => Array.from(new Set([...CATEGORY_OPTIONS, ...allCategories])),
    [allCategories]
  );
  // City suggestions are scoped to the currently-selected countries (so picking "USA"
  // doesn't leave Manchester/Leeds suggested) — falls back to every curated city when
  // no country is picked yet, always merged with real cities already in the DB.
  const cityOptions = useMemo(() => {
    const fromCountries = countriesSelected.length
      ? countriesSelected.flatMap((c) => CITY_OPTIONS_BY_COUNTRY[c] || [])
      : Object.values(CITY_OPTIONS_BY_COUNTRY).flat();
    return Array.from(new Set([...fromCountries, ...allCities]));
  }, [countriesSelected, allCities]);

  // Settings State: Password Update
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [updatingPassword, setUpdatingPassword] = useState(false);

  // Theme Initializer
  useEffect(() => {
    const savedTheme = localStorage.getItem('admin_theme') as 'dark' | 'light';
    if (savedTheme) {
      setTheme(savedTheme);
    }
  }, []);

  const toggleTheme = () => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
    localStorage.setItem('admin_theme', nextTheme);
    setToast({ msg: `Theme changed to ${nextTheme.toUpperCase()} mode`, type: 'info' });
  };

  const load = useCallback(async () => {
    try {
      const [s, lRes, si] = await Promise.all([
        adminApi.stats(),
        adminApi.leads({
          page,
          limit,
          category: selectedCategory,
          city: selectedCity,
          tier: selectedTier,
          has_gaps: selectedHasGaps,
          has_site: selectedHasSite,
          min_score: minScore,
          search: searchQuery,
          sort_by: sortBy,
          order: sortOrder
        }),
        adminApi.sites()
      ]);
      setStats(s);
      setLeadsData(lRes);
      setSites(si.sites);

      // Extract unique categories & cities if available
      if (lRes.leads && lRes.leads.length > 0) {
        const cats = Array.from(new Set(lRes.leads.map((l: any) => l.category).filter(Boolean))) as string[];
        const cts = Array.from(new Set(lRes.leads.map((l: any) => l.city).filter(Boolean))) as string[];
        if (cats.length) setAllCategories(prev => Array.from(new Set([...prev, ...cats])));
        if (cts.length) setAllCities(prev => Array.from(new Set([...prev, ...cts])));
      }

      // Fetch logs
      const token = getToken();
      if (token) {
        const logRes = await fetch('http://localhost:8009/api/v1/admin/audit/logs?limit=50', {
          headers: { Authorization: `Bearer ${token}` }
        }).then(r => r.json()).catch(() => ({ logs: [] }));
        if (logRes && logRes.logs) setLogs(logRes.logs);
      }
    } catch (e) {
      console.error("Dashboard load error", e);
    }
  }, [page, limit, selectedCategory, selectedCity, selectedTier, selectedHasGaps, selectedHasSite, minScore, searchQuery, sortBy, sortOrder]);

  useEffect(() => {
    if (!getToken()) {
      window.location.href = '/login';
      return;
    }
    load().then(() => setReady(true)).catch(() => setReady(true));
  }, [load]);

  // Reset pagination to page 1 whenever filters change
  const handleFilterChange = (setter: (val: any) => void, val: any) => {
    setter(val);
    setPage(1);
  };

  // Filtered CRM Leads
  const crmLeads = useMemo(() => {
    if (crmStatusFilter === 'ALL') return leadsData.leads;
    return leadsData.leads.filter(l => (l.outreach?.status || 'NEW') === crmStatusFilter);
  }, [leadsData.leads, crmStatusFilter]);

  const action = async (id: string, act: 'enrich' | 'site') => {
    setBusy(id + ':' + act);
    try {
      if (act === 'enrich') {
        const r = await adminApi.enrich(id);
        setToast({ msg: `Enriched: ${r.counts.services} services · ${r.team.length} team · ${r.counts.gallery} photos`, type: 'success' });
      } else {
        const r = await adminApi.generateSite(id);
        setToast({ msg: `Site generated: ${r.slug} (${r.archetype})`, type: 'success' });
      }
      await load();
    } catch (e: any) {
      setToast({ msg: e.message || 'Action failed', type: 'error' });
    }
    setBusy('');
  };

  const removeSite = async (slug: string) => {
    if (!window.confirm(`Delete site "${slug}"?`)) return;
    setBusy(slug + ':del');
    try {
      await adminApi.deleteSite(slug);
      setToast({ msg: `Deleted ${slug}`, type: 'info' });
      await load();
    } catch (e: any) {
      setToast({ msg: e.message || 'Delete failed', type: 'error' });
    }
    setBusy('');
  };

  const runPipeline = async () => {
    const categories = categoriesSelected;
    const cities = citiesSelected;
    const countries = countriesSelected;
    if (!categories.length || !cities.length || !countries.length) {
      setToast({ msg: 'Enter at least one category, city, and country.', type: 'error' });
      return;
    }
    setBusy('pipeline');
    try {
      const r = await adminApi.generateLeads({
        categories,
        cities,
        countries,
        max_per_city: maxPer,
        min_buying_power: minBuyingPower,
      });
      setJob({ id: r.job_id, status: r.status });
      const combos = categories.length * cities.length * countries.length;
      setToast({ msg: `Discovery campaign launched: ${combos} quer${combos === 1 ? 'y' : 'ies'} across ${categories.length} categor${categories.length === 1 ? 'y' : 'ies'} × ${cities.length} cit${cities.length === 1 ? 'y' : 'ies'} × ${countries.length} countr${countries.length === 1 ? 'y' : 'ies'}...`, type: 'info' });
    } catch (e: any) {
      setToast({ msg: e.message || 'Failed to start lead discovery', type: 'error' });
    }
    setBusy('');
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentPassword || !newPassword) {
      setToast({ msg: 'Please enter current and new password.', type: 'error' });
      return;
    }
    if (newPassword !== confirmPassword) {
      setToast({ msg: 'New passwords do not match.', type: 'error' });
      return;
    }
    if (newPassword.length < 5) {
      setToast({ msg: 'New password must be at least 5 characters long.', type: 'error' });
      return;
    }

    setUpdatingPassword(true);
    try {
      await adminApi.changePassword({ current_password: currentPassword, new_password: newPassword });
      setToast({ msg: '🔒 Password successfully updated!', type: 'success' });
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      setToast({ msg: err.message || 'Failed to update password.', type: 'error' });
    } finally {
      setUpdatingPassword(false);
    }
  };

  useEffect(() => {
    if (!job || job.status === 'completed' || job.status === 'failed') return;
    const t = setInterval(async () => {
      try {
        const s = await adminApi.jobStatus(job.id);
        setJob({ id: job.id, status: s.status });
        if (s.status === 'completed') {
          setToast({ msg: 'Lead discovery complete!', type: 'success' });
          load();
        }
        if (s.status === 'failed') setToast({ msg: 'Pipeline failed: ' + (s.message || ''), type: 'error' });
      } catch {}
    }, 3000);
    return () => clearInterval(t);
  }, [job, load]);

  const logout = () => {
    clearToken();
    window.location.href = '/login';
  };

  const isLight = theme === 'light';

  if (!ready) {
    return (
      <main className={`min-h-screen flex items-center justify-center ${isLight ? 'bg-slate-100 text-slate-600' : 'bg-[#050811] text-slate-400'}`}>
        <div className="flex flex-col items-center gap-2">
          <Loader2 className="w-6 h-6 animate-spin text-cyan-400" />
          <p className="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Loading Dashboard...</p>
        </div>
      </main>
    );
  }

  return (
    <div className={`min-h-screen flex selection:bg-cyan-500 selection:text-white ${
      isLight ? 'bg-slate-100 text-slate-800' : 'bg-[#050811] text-slate-200'
    }`}>
      
      {/* ==================================== SIDEBAR MENU ==================================== */}
      <aside className={`w-56 flex flex-col justify-between shrink-0 sticky top-0 h-screen z-30 border-r backdrop-blur-xl ${
        isLight ? 'bg-white border-slate-200/90' : 'bg-[#0b1120] border-slate-800/80'
      }`}>
        <div>
          {/* Logo Brand */}
          <div className={`p-3.5 border-b flex items-center gap-2.5 ${isLight ? 'border-slate-200' : 'border-slate-800/80'}`}>
            <div className="w-8 h-8 rounded-xl flex items-center justify-center shadow-md" style={{ background: 'linear-gradient(135deg, #2563eb, #38bdf8)' }}>
              <ShieldCheck className="w-4.5 h-4.5 text-white" />
            </div>
            <div>
              <div className={`font-extrabold text-xs tracking-tight leading-none ${isLight ? 'text-slate-900' : 'text-white'}`}>Rebuildly</div>
              <div className="text-[9px] font-bold text-cyan-500 uppercase tracking-wider mt-0.5">Enterprise CRM</div>
            </div>
          </div>

          {/* Navigation Group */}
          <nav className="p-2 space-y-1">
            <p className={`text-[9px] font-extrabold uppercase tracking-widest px-2.5 py-1.5 ${isLight ? 'text-slate-400' : 'text-slate-500'}`}>Workspaces</p>

            <button
              onClick={() => setActiveTab('overview')}
              className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs font-semibold transition flex items-center justify-between cursor-pointer ${
                activeTab === 'overview'
                  ? isLight ? 'bg-indigo-50 text-indigo-700 border border-indigo-200 font-bold' : 'bg-indigo-600/15 text-indigo-300 border border-indigo-500/30'
                  : isLight ? 'text-slate-600 hover:bg-slate-100 hover:text-slate-900' : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
              }`}
            >
              <div className="flex items-center gap-2">
                <LayoutDashboard className="w-3.5 h-3.5" />
                <span>Executive Overview</span>
              </div>
              <ChevronRight className={`w-3 h-3 transition-transform ${activeTab === 'overview' ? 'rotate-90 text-indigo-500' : 'text-slate-400'}`} />
            </button>

            <button
              onClick={() => setActiveTab('leads')}
              className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs font-semibold transition flex items-center justify-between cursor-pointer ${
                activeTab === 'leads'
                  ? isLight ? 'bg-indigo-50 text-indigo-700 border border-indigo-200 font-bold' : 'bg-indigo-600/15 text-indigo-300 border border-indigo-500/30'
                  : isLight ? 'text-slate-600 hover:bg-slate-100 hover:text-slate-900' : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
              }`}
            >
              <div className="flex items-center gap-2">
                <Gauge className="w-3.5 h-3.5" />
                <span>Lead Pipeline</span>
              </div>
              <span className={`px-1.5 py-0.5 text-[9px] font-bold rounded ${isLight ? 'bg-slate-200 text-slate-700' : 'bg-slate-800 text-slate-300 border border-slate-700'}`}>
                {leadsData.total}
              </span>
            </button>

            <button
              onClick={() => setActiveTab('crm')}
              className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs font-semibold transition flex items-center justify-between cursor-pointer ${
                activeTab === 'crm'
                  ? isLight ? 'bg-indigo-50 text-indigo-700 border border-indigo-200 font-bold' : 'bg-indigo-600/15 text-indigo-300 border border-indigo-500/30'
                  : isLight ? 'text-slate-600 hover:bg-slate-100 hover:text-slate-900' : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
              }`}
            >
              <div className="flex items-center gap-2">
                <Rocket className="w-3.5 h-3.5 text-indigo-500" />
                <span>Sales CRM Studio</span>
              </div>
              <span className="px-1.5 py-0.5 text-[9px] font-bold rounded bg-indigo-500/20 text-indigo-600 dark:text-indigo-300 border border-indigo-500/30">
                Outreach
              </span>
            </button>

            <button
              onClick={() => setActiveTab('sites')}
              className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs font-semibold transition flex items-center justify-between cursor-pointer ${
                activeTab === 'sites'
                  ? isLight ? 'bg-indigo-50 text-indigo-700 border border-indigo-200 font-bold' : 'bg-indigo-600/15 text-indigo-300 border border-indigo-500/30'
                  : isLight ? 'text-slate-600 hover:bg-slate-100 hover:text-slate-900' : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
              }`}
            >
              <div className="flex items-center gap-2">
                <Layers className="w-3.5 h-3.5 text-emerald-500" />
                <span>Generated Live Sites</span>
              </div>
              <span className={`px-1.5 py-0.5 text-[9px] font-bold rounded ${isLight ? 'bg-slate-200 text-slate-700' : 'bg-slate-800 text-slate-300 border border-slate-700'}`}>
                {sites.length}
              </span>
            </button>

            <button
              onClick={() => setActiveTab('audits')}
              className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs font-semibold transition flex items-center justify-between cursor-pointer ${
                activeTab === 'audits'
                  ? isLight ? 'bg-indigo-50 text-indigo-700 border border-indigo-200 font-bold' : 'bg-indigo-600/15 text-indigo-300 border border-indigo-500/30'
                  : isLight ? 'text-slate-600 hover:bg-slate-100 hover:text-slate-900' : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
              }`}
            >
              <div className="flex items-center gap-2">
                <Terminal className="w-3.5 h-3.5 text-amber-500" />
                <span>Audit Console</span>
              </div>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            </button>

            <button
              onClick={() => setActiveTab('settings')}
              className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs font-semibold transition flex items-center justify-between cursor-pointer ${
                activeTab === 'settings'
                  ? isLight ? 'bg-indigo-50 text-indigo-700 border border-indigo-200 font-bold' : 'bg-indigo-600/15 text-indigo-300 border border-indigo-500/30'
                  : isLight ? 'text-slate-600 hover:bg-slate-100 hover:text-slate-900' : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
              }`}
            >
              <div className="flex items-center gap-2">
                <Settings className="w-3.5 h-3.5 text-cyan-500" />
                <span>Settings & Security</span>
              </div>
            </button>
          </nav>
        </div>

        {/* Sidebar Footer */}
        <div className={`p-3 border-t space-y-2 ${isLight ? 'border-slate-200' : 'border-slate-800/80'}`}>
          <div className={`p-2 rounded-lg border flex items-center justify-between ${isLight ? 'bg-slate-50 border-slate-200' : 'bg-slate-900 border-slate-800/80'}`}>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></div>
              <div className={`text-[10px] font-medium ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>PostgreSQL + Claude</div>
            </div>
            <button onClick={toggleTheme} className="p-1 rounded hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-500 transition-colors" title={`Switch to ${isLight ? 'Dark' : 'Light'} Mode`}>
              {isLight ? <Moon className="w-3.5 h-3.5 text-indigo-600" /> : <Sun className="w-3.5 h-3.5 text-amber-400" />}
            </button>
          </div>

          <button
            onClick={logout}
            className={`w-full text-[11px] font-semibold py-1.5 rounded-lg border transition-colors flex items-center justify-center gap-1.5 cursor-pointer ${
              isLight ? 'border-slate-300 text-slate-600 hover:bg-rose-50 hover:text-rose-600 hover:border-rose-200' : 'border-slate-800 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10'
            }`}
          >
            <LogOut className="w-3 h-3" /> Logout Admin
          </button>
        </div>
      </aside>

      {/* ==================================== MAIN WORKSPACE CONTENT ==================================== */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        
        {/* Top Header */}
        <header className={`sticky top-0 z-20 backdrop-blur-md border-b px-5 py-2.5 flex items-center justify-between ${
          isLight ? 'bg-white/90 border-slate-200' : 'bg-[#070b14]/90 border-slate-800/80'
        }`}>
          <div className="flex items-center gap-2 text-xs font-medium text-slate-400">
            <span>Admin</span> / <span className={`font-bold capitalize ${isLight ? 'text-slate-900' : 'text-slate-200'}`}>{activeTab}</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={toggleTheme}
              className={`p-1.5 rounded-lg border transition cursor-pointer flex items-center gap-1.5 text-xs font-semibold ${
                isLight ? 'border-slate-300 bg-slate-50 text-slate-700 hover:bg-slate-100' : 'border-slate-800 bg-slate-900 text-slate-300 hover:bg-slate-800'
              }`}
              title="Toggle Theme"
            >
              {isLight ? <Moon className="w-3.5 h-3.5 text-indigo-600" /> : <Sun className="w-3.5 h-3.5 text-amber-400" />}
              <span className="capitalize">{theme} Theme</span>
            </button>

            <button
              onClick={() => load()}
              className={`p-1.5 rounded-lg border transition cursor-pointer ${
                isLight ? 'border-slate-300 text-slate-600 hover:bg-slate-100' : 'border-slate-800 text-slate-400 hover:text-white hover:bg-slate-900'
              }`}
              title="Refresh Data"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>

            <button
              onClick={() => setActiveTab('crm')}
              className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-lg transition flex items-center gap-1.5 shadow-sm cursor-pointer"
            >
              <Zap className="w-3 h-3 text-cyan-300" /> Sales CRM Studio
            </button>
          </div>
        </header>

        <main className="p-4 sm:p-5 space-y-5 max-w-7xl w-full mx-auto">
          
          {/* ==================== WORKSPACE 1: EXECUTIVE OVERVIEW ==================== */}
          {activeTab === 'overview' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-5">
              {/* Stat Cards Row */}
              <section className="grid grid-cols-2 lg:grid-cols-5 gap-3">
                <StatCard
                  icon={<Users className="w-4 h-4 text-white" />}
                  label="Total Leads"
                  value={stats?.total_leads ?? '—'}
                  subtext="Discovered Businesses"
                  accent="linear-gradient(135deg,#1d4ed8,#38bdf8)"
                  onClick={() => setActiveTab('leads')}
                  isLight={isLight}
                />
                <StatCard
                  icon={<Gauge className="w-4 h-4 text-white" />}
                  label="Avg Score"
                  value={stats?.avg_score ?? '—'}
                  subtext="Opportunity Index"
                  accent="linear-gradient(135deg,#0e7490,#22d3ee)"
                  isLight={isLight}
                />
                <StatCard
                  icon={<TrendingUp className="w-4 h-4 text-white" />}
                  label="Top Score"
                  value={stats?.top_score ?? '—'}
                  subtext="Highest Gap Score"
                  accent="linear-gradient(135deg,#be185d,#f43f5e)"
                  isLight={isLight}
                />
                <StatCard
                  icon={<Star className="w-4 h-4 text-white" />}
                  label="Priority (80+)"
                  value={stats?.priority_leads ?? '—'}
                  subtext="High Potential"
                  accent="linear-gradient(135deg,#b45309,#f59e0b)"
                  onClick={() => { setSelectedTier('ALL'); setMinScore(80); setPage(1); setActiveTab('leads'); }}
                  isLight={isLight}
                />
                <StatCard
                  icon={<Sparkles className="w-4 h-4 text-white" />}
                  label="Sites Built"
                  value={stats?.generated_sites ?? '—'}
                  subtext="Live Subdomains"
                  accent="linear-gradient(135deg,#047857,#10b981)"
                  onClick={() => setActiveTab('sites')}
                  isLight={isLight}
                />
              </section>

              {/* Lead Discovery Launcher */}
              <section className={`rounded-xl border p-4 shadow-md ${isLight ? 'bg-white border-slate-200' : 'bg-slate-900/60 border-slate-800/80'}`}>
                <div className="flex items-center gap-2 mb-3">
                  <Rocket className="w-4 h-4 text-cyan-500" />
                  <h2 className={`font-bold text-sm ${isLight ? 'text-slate-900' : 'text-white'}`}>Lead Discovery Engine & Technical Auditor</h2>
                </div>
                <div className="grid sm:grid-cols-3 gap-2.5">
                  <MultiSelectCombo
                    label="Categories"
                    options={categoryOptions}
                    value={categoriesSelected}
                    onChange={setCategoriesSelected}
                    placeholder="Select or type a category..."
                    isLight={isLight}
                    hints={CATEGORY_HINTS}
                  />
                  <MultiSelectCombo
                    label="Cities"
                    options={cityOptions}
                    value={citiesSelected}
                    onChange={setCitiesSelected}
                    placeholder="Select or type a city..."
                    isLight={isLight}
                  />
                  <MultiSelectCombo
                    label="Countries"
                    options={COUNTRY_OPTIONS}
                    value={countriesSelected}
                    onChange={setCountriesSelected}
                    placeholder="Select or type a country..."
                    isLight={isLight}
                    hints={COUNTRY_HINTS}
                  />
                </div>
                <div className="flex items-center gap-2.5 mt-2.5">
                  <label className={`text-[11px] whitespace-nowrap ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                    Max leads / query:
                  </label>
                  <input
                    type="number"
                    min={1}
                    value={maxPer}
                    onChange={(e) => setMaxPer(+e.target.value)}
                    className={`w-20 px-3 py-1 rounded-lg border text-xs outline-none focus:border-indigo-500/50 ${
                      isLight ? 'bg-slate-50 border-slate-300 text-slate-900' : 'bg-slate-950 border-slate-800 text-white'
                    }`}
                  />
                </div>
                <div className="flex items-center gap-2 mt-2.5">
                  <label className={`text-[11px] whitespace-nowrap ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                    Min. buying power (skip low-value leads before auditing):
                  </label>
                  <input
                    type="range"
                    min={0}
                    max={100}
                    step={5}
                    value={minBuyingPower}
                    onChange={(e) => setMinBuyingPower(+e.target.value)}
                    className="flex-1 accent-indigo-600"
                  />
                  <span className={`text-[11px] font-mono w-8 text-right ${isLight ? 'text-slate-700' : 'text-slate-300'}`}>{minBuyingPower}</span>
                </div>
                {(() => {
                  const nCat = categoriesSelected.length;
                  const nCity = citiesSelected.length;
                  const nCountry = countriesSelected.length;
                  const combos = nCat * nCity * nCountry;
                  return combos > 0 ? (
                    <p className={`text-[11px] mt-1.5 ${isLight ? 'text-slate-500' : 'text-slate-500'}`}>
                      This will run <span className="font-semibold text-indigo-500">{combos}</span> quer{combos === 1 ? 'y' : 'ies'}
                      {combos > 1 ? ` (${nCat} × ${nCity} × ${nCountry})` : ''}
                      {maxPer ? <> — up to <span className="font-semibold text-indigo-500">{combos * maxPer}</span> leads.</> : '.'}
                    </p>
                  ) : (
                    <p className={`text-[11px] mt-1.5 ${isLight ? 'text-amber-600' : 'text-amber-500'}`}>
                      Select at least one category, city, and country to run a campaign.
                    </p>
                  );
                })()}
                <div className={`flex items-center justify-between mt-3 pt-2.5 border-t ${isLight ? 'border-slate-200' : 'border-slate-800/80'}`}>
                  <button
                    onClick={runPipeline}
                    disabled={busy === 'pipeline' || job?.status === 'running'}
                    className="text-xs font-bold px-4 py-2 rounded-lg inline-flex items-center gap-1.5 text-white disabled:opacity-50 shadow-md cursor-pointer hover:opacity-90 transition-all bg-indigo-600"
                  >
                    {busy === 'pipeline' || job?.status === 'running' ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
                    {job?.status === 'running' ? 'Discovering & auditing...' : 'Discover Leads Now'}
                  </button>
                  {job && (
                    <span className="text-[11px] text-slate-400">
                      Job ID: <span className="font-mono">{job.id.slice(0, 8)}</span> • Status: <span className="font-bold text-cyan-500 uppercase">{job.status}</span>
                    </span>
                  )}
                </div>
              </section>

              {/* High Intent Outreach Opportunity Spotlight */}
              <section className={`rounded-xl border p-4 shadow-md space-y-3 ${isLight ? 'bg-white border-slate-200' : 'bg-slate-900/60 border-slate-800/80'}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Zap className="w-4 h-4 text-amber-500" />
                    <h2 className={`font-bold text-sm ${isLight ? 'text-slate-900' : 'text-white'}`}>Top Outreach Opportunities (Score 80+)</h2>
                  </div>
                  <button onClick={() => { setSelectedTier('ALL'); setMinScore(80); setPage(1); setActiveTab('leads'); }} className="text-xs font-semibold text-indigo-500 hover:underline">
                    View All ({stats?.priority_leads ?? 0}) →
                  </button>
                </div>

                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {leadsData.leads.filter(l => (l.score || 0) >= 80).slice(0, 6).map((l) => (
                    <div key={l.id} className={`p-3 rounded-lg border flex flex-col justify-between gap-2.5 ${isLight ? 'bg-slate-50 border-slate-200' : 'bg-slate-950/60 border-slate-800'}`}>
                      <div>
                        <div className="flex items-center justify-between">
                          <ScoreBadge score={l.score} />
                          <span className="text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-rose-500/10 text-rose-500 border border-rose-500/20">
                            High Priority
                          </span>
                        </div>
                        <h3 className={`font-bold text-xs mt-2 ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>{l.name}</h3>
                        <p className={`text-[11px] ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>{l.city} • {l.category}</p>
                      </div>

                      <button
                        onClick={() => setOutreachLeadId(l.id)}
                        className="w-full text-xs font-bold py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white flex items-center justify-center gap-1.5 shadow-sm cursor-pointer"
                      >
                        <Zap className="w-3.5 h-3.5 text-cyan-300" /> Start AI Outreach
                      </button>
                    </div>
                  ))}
                </div>
              </section>
            </motion.div>
          )}

          {/* ==================== WORKSPACE 2: LEAD PIPELINE ==================== */}
          {activeTab === 'leads' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
              <section className={`rounded-xl border overflow-hidden shadow-md ${isLight ? 'bg-white border-slate-200' : 'bg-slate-900/60 border-slate-800/80'}`}>
                
                {/* Search & Filter Header */}
                <div className={`p-4 border-b space-y-3 ${isLight ? 'border-slate-200' : 'border-slate-800/80'}`}>
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <h2 className={`font-bold text-sm flex items-center gap-2 ${isLight ? 'text-slate-900' : 'text-white'}`}>
                      <Gauge className="w-4 h-4 text-cyan-500" /> Lead Intelligence Pipeline
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-500 border border-cyan-500/20">
                        {leadsData.total} Total Leads (Page {leadsData.page} of {leadsData.total_pages})
                      </span>
                    </h2>

                    {/* Sorting & Order Controls */}
                    <div className="flex items-center gap-2">
                      <div className="flex items-center gap-1 text-xs font-semibold text-slate-400">
                        <ArrowUpDown className="w-3.5 h-3.5" />
                        <span>Sort by:</span>
                      </div>

                      <select
                        value={sortBy}
                        onChange={(e) => handleFilterChange(setSortBy, e.target.value)}
                        className={`text-xs px-2.5 py-1.5 rounded-lg border outline-none cursor-pointer font-semibold ${
                          isLight ? 'bg-slate-50 border-slate-300 text-slate-800' : 'bg-slate-950 border-slate-800 text-slate-200'
                        }`}
                      >
                        <option value="score" style={{ color: '#000' }}>Opportunity Score</option>
                        <option value="date" style={{ color: '#000' }}>Date Discovered</option>
                        <option value="name" style={{ color: '#000' }}>Business Name</option>
                      </select>

                      <button
                        onClick={() => handleFilterChange(setSortOrder, sortOrder === 'desc' ? 'asc' : 'desc')}
                        className={`px-2.5 py-1.5 text-xs font-bold rounded-lg border transition flex items-center gap-1 cursor-pointer ${
                          isLight ? 'bg-slate-50 border-slate-300 text-slate-700 hover:bg-slate-100' : 'bg-slate-950 border-slate-800 text-slate-300 hover:bg-slate-900'
                        }`}
                        title="Toggle Sort Order"
                      >
                        {sortOrder === 'desc' ? <ArrowDown className="w-3 h-3 text-cyan-500" /> : <ArrowUp className="w-3 h-3 text-cyan-500" />}
                        <span className="uppercase">{sortOrder}</span>
                      </button>
                    </div>
                  </div>

                  {/* Filter Dropdowns Grid */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7 gap-2">
                    <div className="relative">
                      <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
                      <input
                        type="text"
                        placeholder="Search lead/city..."
                        value={searchQuery}
                        onChange={(e) => handleFilterChange(setSearchQuery, e.target.value)}
                        className={`w-full pl-8 pr-2 py-1.5 text-xs rounded-lg border outline-none focus:border-indigo-500/50 ${
                          isLight ? 'bg-slate-50 border-slate-300 text-slate-900' : 'bg-slate-950 border-slate-800 text-white'
                        }`}
                      />
                    </div>

                    {/* Category Selector */}
                    <select
                      value={selectedCategory}
                      onChange={(e) => handleFilterChange(setSelectedCategory, e.target.value)}
                      className={`text-xs px-2 py-1.5 rounded-lg border outline-none cursor-pointer ${
                        isLight ? 'bg-slate-50 border-slate-300 text-slate-800' : 'bg-slate-950 border-slate-800 text-slate-200'
                      }`}
                    >
                      <option value="ALL" style={{ color: '#000' }}>All Categories</option>
                      {allCategories.map(cat => <option key={cat} value={cat} style={{ color: '#000' }}>{cat}</option>)}
                    </select>

                    {/* City Selector */}
                    <select
                      value={selectedCity}
                      onChange={(e) => handleFilterChange(setSelectedCity, e.target.value)}
                      className={`text-xs px-2 py-1.5 rounded-lg border outline-none cursor-pointer ${
                        isLight ? 'bg-slate-50 border-slate-300 text-slate-800' : 'bg-slate-950 border-slate-800 text-slate-200'
                      }`}
                    >
                      <option value="ALL" style={{ color: '#000' }}>All Cities</option>
                      {allCities.map(c => <option key={c} value={c} style={{ color: '#000' }}>{c}</option>)}
                    </select>

                    {/* Priority Tier Selector */}
                    <select
                      value={selectedTier}
                      onChange={(e) => handleFilterChange(setSelectedTier, e.target.value)}
                      className={`text-xs px-2 py-1.5 rounded-lg border outline-none cursor-pointer ${
                        isLight ? 'bg-slate-50 border-slate-300 text-slate-800' : 'bg-slate-950 border-slate-800 text-slate-200'
                      }`}
                    >
                      <option value="ALL" style={{ color: '#000' }}>All Priority Tiers</option>
                      <option value="TIER_1_PRIORITY" style={{ color: '#000' }}>Tier 1 Priority (80+)</option>
                      <option value="TIER_2_STANDARD" style={{ color: '#000' }}>Tier 2 Standard (60+)</option>
                      <option value="TIER_3_LOW" style={{ color: '#000' }}>Tier 3 Low (40+)</option>
                      <option value="SKIP" style={{ color: '#000' }}>Skip / Unscored (&lt;40)</option>
                    </select>

                    {/* Audit Gaps Selector */}
                    <select
                      value={selectedHasGaps}
                      onChange={(e) => handleFilterChange(setSelectedHasGaps, e.target.value)}
                      className={`text-xs px-2 py-1.5 rounded-lg border outline-none cursor-pointer ${
                        isLight ? 'bg-slate-50 border-slate-300 text-slate-800' : 'bg-slate-950 border-slate-800 text-slate-200'
                      }`}
                    >
                      <option value="ALL" style={{ color: '#000' }}>All Audit Statuses</option>
                      <option value="HAS_GAPS" style={{ color: '#000' }}>Has Audit Gaps (&gt;0)</option>
                      <option value="HIGH_GAPS" style={{ color: '#000' }}>High Gaps (3+)</option>
                      <option value="NO_GAPS" style={{ color: '#000' }}>Clean Audit (0 Gaps)</option>
                    </select>

                    {/* Site Generated Selector */}
                    <select
                      value={selectedHasSite}
                      onChange={(e) => handleFilterChange(setSelectedHasSite, e.target.value)}
                      className={`text-xs px-2 py-1.5 rounded-lg border outline-none cursor-pointer ${
                        isLight ? 'bg-slate-50 border-slate-300 text-slate-800' : 'bg-slate-950 border-slate-800 text-slate-200'
                      }`}
                    >
                      <option value="ALL" style={{ color: '#000' }}>All Sites Status</option>
                      <option value="YES" style={{ color: '#000' }}>Site Generated (Live)</option>
                      <option value="NO" style={{ color: '#000' }}>No Site Generated Yet</option>
                    </select>

                    {/* Minimum Score Selector */}
                    <select
                      value={minScore}
                      onChange={(e) => handleFilterChange(setMinScore, +e.target.value)}
                      className={`text-xs px-2 py-1.5 rounded-lg border outline-none cursor-pointer ${
                        isLight ? 'bg-slate-50 border-slate-300 text-slate-800' : 'bg-slate-950 border-slate-800 text-slate-200'
                      }`}
                    >
                      <option value={0} style={{ color: '#000' }}>All Scores (0+)</option>
                      <option value={40} style={{ color: '#000' }}>Score 40+</option>
                      <option value={60} style={{ color: '#000' }}>Score 60+</option>
                      <option value={80} style={{ color: '#000' }}>Priority Score 80+</option>
                    </select>
                  </div>
                </div>

                {/* Table */}
                <div className="max-h-[540px] overflow-y-auto overflow-x-auto relative">
                  <table className="w-full text-left border-collapse">
                    <thead className={`sticky top-0 z-20 border-b ${isLight ? 'bg-slate-100 border-slate-200' : 'bg-slate-950 border-slate-800/80'}`}>
                      <tr className={`text-[9px] uppercase tracking-widest font-bold ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                        <th className="py-2.5 px-3">Score</th>
                        <th className="py-2.5 px-3">Business Lead</th>
                        <th className="py-2.5 px-3 hidden md:table-cell">Tier</th>
                        <th className="py-2.5 px-3 hidden lg:table-cell">Audit Gaps</th>
                        <th className="py-2.5 px-3 hidden lg:table-cell">Links</th>
                        <th className="py-2.5 px-3 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {leadsData.leads.map((l) => (
                        <LeadRow key={l.id} lead={l} onAction={action} onOpenOutreach={setOutreachLeadId} onManagePages={setManagePagesLead} busy={busy} isLight={isLight} />
                      ))}
                    </tbody>
                  </table>
                  {!leadsData.leads.length && (
                    <div className="p-10 text-center text-xs text-slate-500">
                      No leads match the selected category, score, or filter criteria.
                    </div>
                  )}
                </div>

                {/* Pagination Controls Footer */}
                <div className={`p-3 border-t flex flex-wrap items-center justify-between gap-3 text-xs ${isLight ? 'bg-slate-50 border-slate-200 text-slate-600' : 'bg-slate-950 border-slate-800/80 text-slate-400'}`}>
                  <div className="flex items-center gap-2">
                    <span>Per page:</span>
                    <select
                      value={limit}
                      onChange={(e) => { setLimit(+e.target.value); setPage(1); }}
                      className={`text-xs px-2 py-1 rounded border outline-none cursor-pointer ${
                        isLight ? 'bg-white border-slate-300 text-slate-800' : 'bg-slate-900 border-slate-700 text-slate-200'
                      }`}
                    >
                      <option value={15} style={{ color: '#000' }}>15 leads</option>
                      <option value={25} style={{ color: '#000' }}>25 leads</option>
                      <option value={50} style={{ color: '#000' }}>50 leads</option>
                      <option value={100} style={{ color: '#000' }}>100 leads</option>
                    </select>
                    <span className="text-[11px] text-slate-400 ml-2">
                      Showing {leadsData.leads.length ? (page - 1) * limit + 1 : 0} - {Math.min(page * limit, leadsData.total)} of {leadsData.total}
                    </span>
                  </div>

                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={() => setPage(p => Math.max(1, p - 1))}
                      disabled={page <= 1}
                      className={`px-3 py-1.5 rounded-lg border text-xs font-bold transition flex items-center gap-1 disabled:opacity-40 cursor-pointer ${
                        isLight ? 'bg-white border-slate-300 hover:bg-slate-100 text-slate-800' : 'bg-slate-900 border-slate-700 hover:bg-slate-800 text-slate-200'
                      }`}
                    >
                      <ChevronLeft className="w-3.5 h-3.5" /> Previous
                    </button>

                    <span className="px-3 py-1 text-xs font-mono font-bold">
                      Page {leadsData.page} / {leadsData.total_pages}
                    </span>

                    <button
                      onClick={() => setPage(p => Math.min(leadsData.total_pages, p + 1))}
                      disabled={page >= leadsData.total_pages}
                      className={`px-3 py-1.5 rounded-lg border text-xs font-bold transition flex items-center gap-1 disabled:opacity-40 cursor-pointer ${
                        isLight ? 'bg-white border-slate-300 hover:bg-slate-100 text-slate-800' : 'bg-slate-900 border-slate-700 hover:bg-slate-800 text-slate-200'
                      }`}
                    >
                      Next <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

              </section>
            </motion.div>
          )}

          {/* ==================== WORKSPACE 3: SALES CRM STUDIO ==================== */}
          {activeTab === 'crm' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
              {/* Filter Tabs */}
              <div className={`flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-xl border ${isLight ? 'bg-white border-slate-200' : 'bg-slate-900/60 border-slate-800/80'}`}>
                <div className="flex items-center gap-2">
                  <Rocket className="w-4 h-4 text-indigo-500" />
                  <h2 className={`font-bold text-sm ${isLight ? 'text-slate-900' : 'text-white'}`}>Sales Outreach Stage Pipeline</h2>
                </div>

                <div className="flex flex-wrap items-center gap-1.5">
                  {[
                    { key: 'ALL', label: 'All' },
                    { key: 'NEW', label: 'New' },
                    { key: 'LINKEDIN_SENT', label: 'LinkedIn' },
                    { key: 'EMAIL_SENT', label: 'Email' },
                    { key: 'WA_SENT', label: 'WhatsApp' },
                    { key: 'CALLED', label: 'Called' },
                    { key: 'CONVERTED', label: 'Converted' },
                  ].map((tab) => (
                    <button
                      key={tab.key}
                      onClick={() => setCrmStatusFilter(tab.key)}
                      className={`px-2.5 py-1 text-[11px] font-semibold rounded-lg transition cursor-pointer ${
                        crmStatusFilter === tab.key
                          ? 'bg-indigo-600 text-white shadow-sm'
                          : isLight ? 'bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200' : 'bg-slate-950 text-slate-400 hover:text-white border border-slate-800'
                      }`}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Leads Grid in CRM */}
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {crmLeads.map((l) => (
                  <div key={l.id} className={`p-4 rounded-xl border flex flex-col justify-between gap-3 ${isLight ? 'bg-white border-slate-200 shadow-sm' : 'bg-slate-900/60 border-slate-800/80'}`}>
                    <div>
                      <div className="flex items-center justify-between">
                        <ScoreBadge score={l.score} />
                        <span className="px-2 py-0.5 text-[9px] font-bold rounded bg-indigo-500/10 text-indigo-600 dark:text-indigo-300 border border-indigo-500/20 uppercase">
                          {l.outreach?.status || 'NEW'}
                        </span>
                      </div>
                      <h3 className={`font-bold text-xs mt-2.5 ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>{l.name}</h3>
                      <p className={`text-[11px] ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>{l.city} • {l.category}</p>
                    </div>

                    <div className={`space-y-1.5 pt-2 border-t text-[11px] ${isLight ? 'border-slate-200' : 'border-slate-800/80'}`}>
                      <div className={`flex items-center justify-between ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
                        <span>Preview Subdomain:</span>
                        <a href={l.preview_url} target="_blank" rel="noreferrer" className="text-cyan-500 font-mono hover:underline">
                          /sites/{l.slug}
                        </a>
                      </div>

                      {l.outreach?.click_count > 0 && (
                        <div className="p-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-300 font-semibold flex items-center justify-between text-[11px]">
                          <span className="flex items-center gap-1"><MousePointerClick className="w-3.5 h-3.5 text-emerald-500" /> Prospect Clicks</span>
                          <span className="font-bold">{l.outreach.click_count} Link Clicks!</span>
                        </div>
                      )}
                    </div>

                    <button
                      onClick={() => setOutreachLeadId(l.id)}
                      className="w-full text-xs font-bold py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white flex items-center justify-center gap-1.5 shadow-sm cursor-pointer"
                    >
                      <Zap className="w-3.5 h-3.5 text-cyan-300" /> Open AI Sales Studio
                    </button>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* ==================== WORKSPACE 4: GENERATED SITES SHOWCASE ==================== */}
          {activeTab === 'sites' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
              <section className={`rounded-xl border overflow-hidden p-4 shadow-md ${isLight ? 'bg-white border-slate-200' : 'bg-slate-900/60 border-slate-800/80'}`}>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Layers className="w-4 h-4 text-emerald-500" />
                    <h2 className={`font-bold text-sm ${isLight ? 'text-slate-900' : 'text-white'}`}>Generated Modernized Preview Sites</h2>
                  </div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                    {sites.length} Active Subdomains
                  </span>
                </div>

                {!sites.length ? (
                  <div className="p-10 text-center text-xs text-slate-500">
                    No client sites generated yet. Go to the Lead Pipeline and click "Generate" on any business lead.
                  </div>
                ) : (
                  <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {sites.map((s) => (
                      <div key={s.slug} className={`p-3.5 rounded-xl border flex flex-col justify-between gap-2.5 ${isLight ? 'bg-slate-50 border-slate-200' : 'bg-slate-950/60 border-slate-800'}`}>
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <h3 className={`font-bold text-xs ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>{s.name}</h3>
                            <p className={`text-[10px] flex items-center gap-1 mt-0.5 ${isLight ? 'text-slate-500' : 'text-slate-400'}`}><MapPin className="w-2.5 h-2.5 text-slate-400" /> {s.city || '—'}</p>
                          </div>
                          <span className="text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 shrink-0">
                            {s.status}
                          </span>
                        </div>

                        <div className="flex flex-wrap items-center gap-1.5">
                          <div className={`text-[10px] font-mono px-2 py-0.5 rounded border ${isLight ? 'bg-white border-slate-200 text-slate-600' : 'bg-slate-900 border-slate-800 text-slate-400'}`}>
                            Archetype: {s.archetype}
                          </div>
                          {!!s.regeneration_count && (
                            <div className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20" title="Regenerations with feedback applied">
                              {s.regeneration_count}x regenerated
                            </div>
                          )}
                        </div>

                        <div className={`flex items-center gap-1.5 pt-2 border-t ${isLight ? 'border-slate-200' : 'border-slate-800'}`}>
                          <button
                            onClick={() => setOutreachLeadId(s.business_id)}
                            className="w-full text-[11px] font-bold px-2.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white flex items-center justify-center gap-1 shadow-sm cursor-pointer"
                          >
                            <Zap className="w-3 h-3 text-cyan-300" /> Outreach
                          </button>
                          <a
                            href={s.preview_url}
                            target="_blank"
                            rel="noreferrer"
                            className="flex-1 text-[11px] font-bold px-2.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white flex items-center justify-center gap-1 shadow-sm"
                          >
                            <ExternalLink className="w-3 h-3" /> View
                          </a>
                          <button
                            onClick={() => setRegenTarget(s)}
                            disabled={!!busy}
                            className={`p-1.5 rounded-lg border disabled:opacity-40 cursor-pointer ${isLight ? 'border-slate-300 text-slate-600 hover:bg-slate-200' : 'border-slate-800 text-slate-300 hover:bg-slate-900'}`}
                            title="Regenerate Site"
                          >
                            <RotateCw className="w-3 h-3" />
                          </button>
                          <button
                            onClick={() => setHistoryTarget(s)}
                            disabled={!!busy}
                            className={`p-1.5 rounded-lg border disabled:opacity-40 cursor-pointer ${isLight ? 'border-slate-300 text-slate-600 hover:bg-slate-200' : 'border-slate-800 text-slate-300 hover:bg-slate-900'}`}
                            title="Version History"
                          >
                            <History className="w-3 h-3" />
                          </button>
                          <button
                            onClick={() => removeSite(s.slug)}
                            disabled={!!busy}
                            className="p-1.5 rounded-lg border border-rose-500/30 hover:bg-rose-500/10 text-rose-500 disabled:opacity-40 cursor-pointer"
                            title="Delete Site"
                          >
                            <Trash2 className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            </motion.div>
          )}

          {/* ==================== WORKSPACE 5: REAL-TIME AUDIT LOGS ==================== */}
          {activeTab === 'audits' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
              <section className={`rounded-xl border overflow-hidden shadow-md ${isLight ? 'bg-white border-slate-200' : 'bg-slate-900/60 border-slate-800/80'}`}>
                <div className={`p-3.5 border-b flex items-center justify-between ${isLight ? 'bg-slate-100 border-slate-200' : 'bg-slate-950 border-slate-800'}`}>
                  <div className="flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-amber-500" />
                    <h2 className={`font-bold text-xs font-mono uppercase tracking-wider ${isLight ? 'text-slate-900' : 'text-white'}`}>Technical Audit Log Console ({logs.length} events)</h2>
                  </div>
                </div>

                <div className={`h-[520px] overflow-y-auto p-3 font-mono text-[11px] space-y-1.5 ${isLight ? 'bg-slate-50' : 'bg-[#040711]'}`}>
                  {logs.map((log) => (
                    <div key={log.id} className={`flex items-start gap-2.5 p-1.5 rounded border-b ${isLight ? 'border-slate-200/60 hover:bg-slate-200/50' : 'border-white/[0.02] hover:bg-white/[0.02]'}`}>
                      <span className="text-slate-400 shrink-0 text-[10px] pt-0.5">{log.timestamp.slice(11, 19)}</span>
                      <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold border ${
                        log.level === 'SUCCESS' ? 'bg-emerald-500/15 text-emerald-500 border-emerald-500/25' :
                        log.level === 'WARNING' ? 'bg-amber-500/15 text-amber-500 border-amber-500/25' :
                        log.level === 'ERROR' ? 'bg-rose-500/15 text-rose-500 border-rose-500/25' :
                        'bg-cyan-500/15 text-cyan-500 border-cyan-500/25'
                      }`}>
                        {log.level}
                      </span>
                      <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold border shrink-0 ${isLight ? 'bg-slate-200 text-slate-700 border-slate-300' : 'bg-slate-800 text-slate-300 border-white/10'}`}>
                        {log.stage}
                      </span>
                      <span className="text-cyan-500 font-semibold shrink-0">{log.business_name}:</span>
                      <span className={`flex-1 leading-relaxed ${isLight ? 'text-slate-800' : 'text-slate-300'}`}>{log.message}</span>
                    </div>
                  ))}
                  {!logs.length && (
                    <div className="p-10 text-center text-slate-500 text-xs">No logs available in real-time stream.</div>
                  )}
                </div>
              </section>
            </motion.div>
          )}

          {/* ==================== WORKSPACE 6: SETTINGS & SECURITY ==================== */}
          {activeTab === 'settings' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-5 max-w-3xl">
              
              {/* Theme Settings Card */}
              <section className={`rounded-xl border p-5 shadow-md ${isLight ? 'bg-white border-slate-200' : 'bg-slate-900/60 border-slate-800/80'}`}>
                <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-200 dark:border-slate-800">
                  <Sun className="w-4 h-4 text-amber-500" />
                  <h2 className={`font-bold text-sm ${isLight ? 'text-slate-900' : 'text-white'}`}>Interface Theme Preferences</h2>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h3 className={`font-semibold text-xs ${isLight ? 'text-slate-900' : 'text-slate-200'}`}>Active Theme Mode</h3>
                    <p className={`text-[11px] mt-0.5 ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>Switch between Dark (Obsidian) and Light (Clean Slate) modes.</p>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => { setTheme('dark'); localStorage.setItem('admin_theme', 'dark'); }}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 cursor-pointer ${
                        theme === 'dark'
                          ? 'bg-indigo-600 text-white shadow-sm'
                          : isLight ? 'bg-slate-100 text-slate-600 hover:bg-slate-200' : 'bg-slate-950 text-slate-400 hover:bg-slate-800'
                      }`}
                    >
                      <Moon className="w-3.5 h-3.5" /> Dark Mode
                    </button>

                    <button
                      onClick={() => { setTheme('light'); localStorage.setItem('admin_theme', 'light'); }}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 cursor-pointer ${
                        theme === 'light'
                          ? 'bg-indigo-600 text-white shadow-sm'
                          : isLight ? 'bg-slate-100 text-slate-600 hover:bg-slate-200' : 'bg-slate-950 text-slate-400 hover:bg-slate-800'
                      }`}
                    >
                      <Sun className="w-3.5 h-3.5" /> Light Mode
                    </button>
                  </div>
                </div>
              </section>

              {/* Password Update Card */}
              <section className={`rounded-xl border p-5 shadow-md ${isLight ? 'bg-white border-slate-200' : 'bg-slate-900/60 border-slate-800/80'}`}>
                <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-200 dark:border-slate-800">
                  <Lock className="w-4 h-4 text-cyan-500" />
                  <h2 className={`font-bold text-sm ${isLight ? 'text-slate-900' : 'text-white'}`}>Update Admin Password</h2>
                </div>

                <form onSubmit={handleChangePassword} className="space-y-4">
                  <div>
                    <label className={`block text-xs font-semibold mb-1.5 ${isLight ? 'text-slate-700' : 'text-slate-300'}`}>
                      Current Password
                    </label>
                    <div className="relative">
                      <Key className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
                      <input
                        type={showPassword ? 'text' : 'password'}
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        placeholder="Enter current password"
                        required
                        className={`w-full pl-9 pr-10 py-2 text-xs rounded-lg border outline-none focus:border-indigo-500/50 ${
                          isLight ? 'bg-slate-50 border-slate-300 text-slate-900' : 'bg-slate-950 border-slate-800 text-white'
                        }`}
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-200 cursor-pointer"
                      >
                        {showPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                  </div>

                  <div className="grid sm:grid-cols-2 gap-3">
                    <div>
                      <label className={`block text-xs font-semibold mb-1.5 ${isLight ? 'text-slate-700' : 'text-slate-300'}`}>
                        New Password
                      </label>
                      <input
                        type={showPassword ? 'text' : 'password'}
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        placeholder="New password (min 5 chars)"
                        required
                        className={`w-full px-3 py-2 text-xs rounded-lg border outline-none focus:border-indigo-500/50 ${
                          isLight ? 'bg-slate-50 border-slate-300 text-slate-900' : 'bg-slate-950 border-slate-800 text-white'
                        }`}
                      />
                    </div>

                    <div>
                      <label className={`block text-xs font-semibold mb-1.5 ${isLight ? 'text-slate-700' : 'text-slate-300'}`}>
                        Confirm New Password
                      </label>
                      <input
                        type={showPassword ? 'text' : 'password'}
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="Confirm new password"
                        required
                        className={`w-full px-3 py-2 text-xs rounded-lg border outline-none focus:border-indigo-500/50 ${
                          isLight ? 'bg-slate-50 border-slate-300 text-slate-900' : 'bg-slate-950 border-slate-800 text-white'
                        }`}
                      />
                    </div>
                  </div>

                  <div className="pt-2 flex items-center justify-end gap-2">
                    <button
                      type="submit"
                      disabled={updatingPassword}
                      className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-lg shadow-md flex items-center gap-1.5 disabled:opacity-50 cursor-pointer"
                    >
                      {updatingPassword ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
                      <span>Save New Password</span>
                    </button>
                  </div>
                </form>
              </section>

              {/* System Configuration Status Card */}
              <section className={`rounded-xl border p-5 shadow-md ${isLight ? 'bg-white border-slate-200' : 'bg-slate-900/60 border-slate-800/80'}`}>
                <div className="flex items-center gap-2 mb-3 pb-3 border-b border-slate-200 dark:border-slate-800">
                  <ShieldCheck className="w-4 h-4 text-emerald-500" />
                  <h2 className={`font-bold text-sm ${isLight ? 'text-slate-900' : 'text-white'}`}>System Engine Status & Integrations</h2>
                </div>

                <div className="space-y-2 text-xs">
                  <div className={`p-2.5 rounded-lg border flex items-center justify-between ${isLight ? 'bg-slate-50 border-slate-200' : 'bg-slate-950 border-slate-800'}`}>
                    <span className="font-semibold text-slate-400">Claude AI Sales Intelligence</span>
                    <span className="text-emerald-500 font-bold flex items-center gap-1"><CheckCircle className="w-3.5 h-3.5" /> Anthropic Claude 3.5 Sonnet Active</span>
                  </div>

                  <div className={`p-2.5 rounded-lg border flex items-center justify-between ${isLight ? 'bg-slate-50 border-slate-200' : 'bg-slate-950 border-slate-800'}`}>
                    <span className="font-semibold text-slate-400">PostgreSQL Relational DB</span>
                    <span className="text-emerald-500 font-bold flex items-center gap-1"><CheckCircle className="w-3.5 h-3.5" /> Connected & Initialized</span>
                  </div>

                  <div className={`p-2.5 rounded-lg border flex items-center justify-between ${isLight ? 'bg-slate-50 border-slate-200' : 'bg-slate-950 border-slate-800'}`}>
                    <span className="font-semibold text-slate-400">Redis Cache & Queue</span>
                    <span className="text-emerald-500 font-bold flex items-center gap-1"><CheckCircle className="w-3.5 h-3.5" /> Fast Cache Operational</span>
                  </div>
                </div>
              </section>

            </motion.div>
          )}

        </main>
      </div>

      {/* ==================================== MODALS & OVERLAYS ==================================== */}
      {outreachLeadId && (
        <OutreachStudioModal
          businessId={outreachLeadId}
          onClose={() => setOutreachLeadId(null)}
          onStatusUpdated={load}
        />
      )}

      {managePagesLead && (
        <ManagePagesModal
          businessId={managePagesLead.id}
          businessName={managePagesLead.name}
          initialUrls={managePagesLead.additional_urls || []}
          onClose={() => setManagePagesLead(null)}
          onSaved={() => load()}
        />
      )}

      {regenTarget && (
        <RegenerateFeedbackModal
          slug={regenTarget.slug}
          siteName={regenTarget.name}
          currentArchetype={regenTarget.archetype}
          pastFeedback={regenTarget.regeneration_feedback || []}
          onClose={() => setRegenTarget(null)}
          onRegenerated={(r) => {
            setToast({ msg: `Regenerated ${r.slug} (${r.archetype})`, type: 'success' });
            load();
          }}
        />
      )}

      {historyTarget && (
        <VersionHistoryModal
          slug={historyTarget.slug}
          siteName={historyTarget.name}
          onClose={() => setHistoryTarget(null)}
        />
      )}

      <AnimatePresence>
        {toast && <Toast msg={toast.msg} type={toast.type} onClose={() => setToast(null)} />}
      </AnimatePresence>
    </div>
  );
}