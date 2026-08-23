'use client';

import React, { useEffect, useState, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ShieldCheck, ArrowLeft, RefreshCw, Terminal, Search, Filter,
  CheckCircle2, AlertTriangle, XCircle, Info, Shield, Smartphone,
  Code, Calendar, MessageSquare, Gauge, Globe, ExternalLink, ChevronDown, Check, X,
  Activity, Play, Sparkles
} from 'lucide-react';
import { adminApi, getToken } from '../../lib/adminApi';

/* --------------------------------- Gauge Card --------------------------------- */
function HealthCard({ title, pct, icon, accent }: { title: string; pct: number | string; icon: React.ReactNode; accent: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl border p-5 flex items-center justify-between"
      style={{ borderColor: 'rgba(255,255,255,0.1)', backgroundColor: 'rgba(15,23,42,0.5)' }}
    >
      <div>
        <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">{title}</div>
        <div className="text-3xl font-extrabold text-white font-mono">{pct}{typeof pct === 'number' ? '%' : ''}</div>
      </div>
      <div className="w-12 h-12 rounded-xl flex items-center justify-center shadow-lg" style={{ background: accent }}>
        {icon}
      </div>
    </motion.div>
  );
}

/* --------------------------------- Audit Log Console Component --------------------------------- */
export default function AuditDashboard() {
  useEffect(() => { document.title = 'Rebuildly | Live Logs Console'; }, []);
  const [ready, setReady] = useState(false);
  const [summary, setSummary] = useState<any>(null);
  const [logs, setLogs] = useState<any[]>([]);
  const [leads, setLeads] = useState<any[]>([]);
  const [selectedLead, setSelectedLead] = useState<any | null>(null);

  // Filter States
  const [logLevel, setLogLevel] = useState('ALL');
  const [logStage, setLogStage] = useState('ALL');
  const [logSearch, setLogSearch] = useState('');
  const [autoScroll, setAutoScroll] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const consoleEndRef = useRef<HTMLDivElement>(null);

  const fetchAuditData = useCallback(async () => {
    setIsRefreshing(true);
    try {
      const token = getToken();
      if (!token) {
        window.location.href = '/login';
        return;
      }
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch Live Audit Summary, Audit Logs, and Leads List
      const [sumRes, logsRes, leadsRes] = await Promise.all([
        fetch('http://localhost:8009/api/v1/admin/audit/summary', { headers }).then(r => r.json()).catch(() => null),
        fetch(`http://localhost:8009/api/v1/admin/audit/logs?limit=200&level=${logLevel}&stage=${logStage}&search=${encodeURIComponent(logSearch)}`, { headers }).then(r => r.json()).catch(() => ({ logs: [] })),
        adminApi.leads({ limit: 100 }).catch(() => ({ leads: [] }))
      ]);

      if (sumRes) setSummary(sumRes);
      if (logsRes && logsRes.logs) setLogs(logsRes.logs);
      if (leadsRes && leadsRes.leads) setLeads(leadsRes.leads);
    } catch (e) {
      console.error('Audit fetch error:', e);
    } finally {
      setIsRefreshing(false);
      setReady(true);
    }
  }, [logLevel, logStage, logSearch]);

  useEffect(() => {
    fetchAuditData();
    const interval = setInterval(fetchAuditData, 4000); // 4-second live poll
    return () => clearInterval(interval);
  }, [fetchAuditData]);

  useEffect(() => {
    if (autoScroll && consoleEndRef.current) {
      consoleEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  const getLevelBadge = (level: string) => {
    switch (level) {
      case 'SUCCESS':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1"><CheckCircle2 className="w-3 h-3" /> SUCCESS</span>;
      case 'WARNING':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center gap-1"><AlertTriangle className="w-3 h-3" /> WARN</span>;
      case 'ERROR':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30 flex items-center gap-1"><XCircle className="w-3 h-3" /> ERROR</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 flex items-center gap-1"><Info className="w-3 h-3" /> INFO</span>;
    }
  };

  if (!ready) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-400">
        <Activity className="w-6 h-6 animate-spin text-cyan-400" />
      </main>
    );
  }

  return (
    <main className="min-h-screen selection:bg-cyan-500 selection:text-white" style={{ background: 'radial-gradient(80% 50% at 50% 0%, #0d1730 0%, #070b16 60%)', color: '#e2e8f0' }}>
      {/* Header */}
      <header className="sticky top-0 z-40 backdrop-blur-xl border-b" style={{ borderColor: 'rgba(255,255,255,0.08)', backgroundColor: 'rgba(7,11,22,0.85)' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <a href="/" className="p-2 rounded-xl border border-white/10 hover:bg-white/5 text-slate-400 hover:text-white transition-colors" title="Back to Dashboard">
              <ArrowLeft className="w-4 h-4" />
            </a>
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl flex items-center justify-center shadow-lg" style={{ background: 'linear-gradient(135deg,#0284c7,#38bdf8)' }}>
                <Terminal className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="font-bold text-white leading-none">Live Audit & Pipeline Logs</div>
                <div className="text-[11px] text-slate-400">Real-Time Lead Scraping & Technical Intelligence</div>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>Live Engine Connected</span>
            </div>
            <button onClick={fetchAuditData} className="p-2.5 rounded-xl border border-white/10 text-slate-400 hover:text-white hover:bg-white/5 cursor-pointer" title="Refresh Now">
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-8">
        {/* Technical Audit Summary Stats */}
        <section className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <HealthCard title="SSL / HTTPS Adoption" pct={summary?.ssl_rate ?? 0} icon={<Shield className="w-5 h-5 text-white" />} accent="linear-gradient(135deg,#059669,#10b981)" />
          <HealthCard title="Mobile Viewport Ready" pct={summary?.mobile_rate ?? 0} icon={<Smartphone className="w-5 h-5 text-white" />} accent="linear-gradient(135deg,#0284c7,#38bdf8)" />
          <HealthCard title="Structured Schema.org" pct={summary?.schema_rate ?? 0} icon={<Code className="w-5 h-5 text-white" />} accent="linear-gradient(135deg,#7c3aed,#8b5cf6)" />
          <HealthCard title="Avg PageSpeed Score" pct={summary?.avg_pagespeed ?? 0} icon={<Gauge className="w-5 h-5 text-white" />} accent="linear-gradient(135deg,#d97706,#f59e0b)" />
        </section>

        {/* Real-Time Live Audit Console Log Stream */}
        <section className="rounded-2xl border overflow-hidden shadow-2xl" style={{ borderColor: 'rgba(255,255,255,0.1)', backgroundColor: 'rgba(9,13,22,0.95)' }}>
          {/* Console Header Bar */}
          <div className="p-4 border-b flex flex-wrap items-center justify-between gap-4" style={{ borderColor: 'rgba(255,255,255,0.08)', backgroundColor: '#060a13' }}>
            <div className="flex items-center gap-3">
              <div className="flex gap-1.5">
                <span className="w-3 h-3 rounded-full bg-rose-500/80 inline-block"></span>
                <span className="w-3 h-3 rounded-full bg-amber-500/80 inline-block"></span>
                <span className="w-3 h-3 rounded-full bg-emerald-500/80 inline-block"></span>
              </div>
              <h3 className="font-mono font-bold text-xs text-slate-300 uppercase tracking-widest flex items-center gap-2">
                <Terminal className="w-4 h-4 text-cyan-400" /> Real-Time Audit Log Terminal ({logs.length} events)
              </h3>
            </div>

            {/* Filter controls */}
            <div className="flex flex-wrap items-center gap-2">
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
                <input
                  type="text"
                  placeholder="Filter logs..."
                  value={logSearch}
                  onChange={(e) => setLogSearch(e.target.value)}
                  className="pl-8 pr-3 py-1.5 text-xs rounded-lg border bg-slate-900 text-white outline-none focus:border-cyan-500"
                  style={{ borderColor: 'rgba(255,255,255,0.15)' }}
                />
              </div>

              <select
                value={logLevel}
                onChange={(e) => setLogLevel(e.target.value)}
                className="text-xs px-2.5 py-1.5 rounded-lg border bg-slate-900 text-slate-300 outline-none cursor-pointer"
                style={{ borderColor: 'rgba(255,255,255,0.15)' }}
              >
                <option value="ALL" style={{ color: '#000' }}>All Levels</option>
                <option value="INFO" style={{ color: '#000' }}>INFO</option>
                <option value="SUCCESS" style={{ color: '#000' }}>SUCCESS</option>
                <option value="WARNING" style={{ color: '#000' }}>WARN</option>
                <option value="ERROR" style={{ color: '#000' }}>ERROR</option>
              </select>

              <select
                value={logStage}
                onChange={(e) => setLogStage(e.target.value)}
                className="text-xs px-2.5 py-1.5 rounded-lg border bg-slate-900 text-slate-300 outline-none cursor-pointer"
                style={{ borderColor: 'rgba(255,255,255,0.15)' }}
              >
                <option value="ALL" style={{ color: '#000' }}>All Stages</option>
                <option value="DISCOVERY" style={{ color: '#000' }}>Discovery</option>
                <option value="CRAWLER" style={{ color: '#000' }}>Crawler</option>
                <option value="AUDITOR" style={{ color: '#000' }}>Auditor</option>
                <option value="GENERATOR" style={{ color: '#000' }}>Generator</option>
                <option value="SYSTEM" style={{ color: '#000' }}>System</option>
              </select>

              <button
                onClick={() => setAutoScroll(!autoScroll)}
                className={`text-xs px-3 py-1.5 rounded-lg border font-semibold cursor-pointer transition-colors ${
                  autoScroll ? 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30' : 'bg-slate-900 text-slate-400 border-white/10'
                }`}
              >
                {autoScroll ? '⚡ Auto-Scroll ON' : '⏸ Auto-Scroll OFF'}
              </button>
            </div>
          </div>

          {/* Console Log Terminal Window */}
          <div className="h-[420px] overflow-y-auto p-4 font-mono text-xs space-y-2 select-text bg-[#070b14]">
            {logs.map((log) => (
              <div key={log.id} className="flex items-start gap-3 p-2 rounded hover:bg-white/[0.03] transition-colors border-b border-white/[0.02]">
                <span className="text-slate-500 shrink-0 text-[10px] pt-0.5">{log.timestamp.slice(11, 19)}</span>
                <div className="shrink-0">{getLevelBadge(log.level)}</div>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300 border border-white/10 shrink-0">
                  {log.stage}
                </span>
                <span className="text-cyan-400 font-semibold shrink-0">{log.business_name}:</span>
                <span className="text-slate-300 flex-1 leading-relaxed">{log.message}</span>
              </div>
            ))}
            {!logs.length && (
              <div className="p-12 text-center text-slate-500">No logs found matching current filters.</div>
            )}
            <div ref={consoleEndRef} />
          </div>
        </section>

        {/* Deep Lead Technical Audit Inspection Table */}
        <section className="rounded-2xl border overflow-hidden shadow-2xl" style={{ borderColor: 'rgba(255,255,255,0.1)', backgroundColor: 'rgba(15,23,42,0.4)' }}>
          <div className="p-5 border-b flex items-center justify-between" style={{ borderColor: 'rgba(255,255,255,0.08)' }}>
            <h3 className="font-bold text-white text-base flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-cyan-400" /> Deep Technical Audit Breakdown per Lead
            </h3>
            <span className="text-xs text-slate-400">{leads.length} Audited Businesses</span>
          </div>

          <div className="max-h-[500px] overflow-y-auto overflow-x-auto relative">
            <table className="w-full text-left border-collapse">
              <thead className="sticky top-0 z-20 backdrop-blur-xl border-b" style={{ backgroundColor: '#0c1527', borderColor: 'rgba(255,255,255,0.1)' }}>
                <tr className="text-[10px] uppercase tracking-widest text-slate-400">
                  <th className="p-3 font-semibold">Lead</th>
                  <th className="p-3 font-semibold">Score</th>
                  <th className="p-3 font-semibold">SSL</th>
                  <th className="p-3 font-semibold">Mobile</th>
                  <th className="p-3 font-semibold">Schema</th>
                  <th className="p-3 font-semibold">Booking</th>
                  <th className="p-3 font-semibold">Chatbot</th>
                  <th className="p-3 font-semibold text-right">Audit Detail</th>
                </tr>
              </thead>
              <tbody>
                {leads.map((l) => (
                  <tr key={l.id} className="border-t hover:bg-white/[0.02] transition-colors" style={{ borderColor: 'rgba(255,255,255,0.06)' }}>
                    <td className="p-3">
                      <div className="font-semibold text-white text-sm">{l.name}</div>
                      <div className="text-xs text-slate-400">{l.city} · {l.category}</div>
                    </td>
                    <td className="p-3">
                      <span className="font-extrabold text-sm text-cyan-400">{l.score ?? '—'}</span>
                    </td>
                    <td className="p-3">
                      {l.findings?.find((f: any) => f.label.includes('SSL'))?.ok ? (
                        <Check className="w-4 h-4 text-emerald-400" />
                      ) : (
                        <X className="w-4 h-4 text-rose-400" />
                      )}
                    </td>
                    <td className="p-3">
                      {l.findings?.find((f: any) => f.label.includes('Mobile'))?.ok ? (
                        <Check className="w-4 h-4 text-emerald-400" />
                      ) : (
                        <X className="w-4 h-4 text-rose-400" />
                      )}
                    </td>
                    <td className="p-3">
                      {l.findings?.find((f: any) => f.label.includes('Schema'))?.ok ? (
                        <Check className="w-4 h-4 text-emerald-400" />
                      ) : (
                        <X className="w-4 h-4 text-rose-400" />
                      )}
                    </td>
                    <td className="p-3">
                      {l.findings?.find((f: any) => f.label.includes('booking'))?.ok ? (
                        <Check className="w-4 h-4 text-emerald-400" />
                      ) : (
                        <X className="w-4 h-4 text-rose-400" />
                      )}
                    </td>
                    <td className="p-3">
                      {l.findings?.find((f: any) => f.label.includes('chatbot'))?.ok ? (
                        <Check className="w-4 h-4 text-emerald-400" />
                      ) : (
                        <X className="w-4 h-4 text-rose-400" />
                      )}
                    </td>
                    <td className="p-3 text-right">
                      <button
                        onClick={() => setSelectedLead(l)}
                        className="text-xs font-semibold px-3 py-1.5 rounded-lg border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10 cursor-pointer"
                      >
                        Inspect Audit
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>

      {/* Audit Inspection Modal Popup */}
      <AnimatePresence>
        {selectedLead && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="w-full max-w-2xl rounded-3xl border border-white/10 bg-slate-900 p-6 sm:p-8 shadow-2xl space-y-6"
            >
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-xs font-bold text-cyan-400 uppercase tracking-widest">TECHNICAL AUDIT REPORT</span>
                  <h3 className="text-2xl font-bold text-white mt-1">{selectedLead.name}</h3>
                  <p className="text-xs text-slate-400">{selectedLead.address || selectedLead.city} · Rating: {selectedLead.google_rating ?? 'N/A'}</p>
                </div>
                <button onClick={() => setSelectedLead(null)} className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/10 cursor-pointer">
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="grid grid-cols-2 gap-3 p-4 rounded-2xl bg-white/5 border border-white/10">
                <div>
                  <div className="text-xs text-slate-400">Opportunity Score</div>
                  <div className="text-3xl font-extrabold text-cyan-400 font-mono mt-0.5">{selectedLead.score}/100</div>
                </div>
                <div>
                  <div className="text-xs text-slate-400">Priority Tier</div>
                  <div className="text-sm font-bold text-amber-400 mt-1">{selectedLead.tier || 'STANDARD'}</div>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase text-slate-400 tracking-wider">Audit Findings Checklist</h4>
                <div className="grid grid-cols-2 gap-2">
                  {(selectedLead.findings || []).map((f: any, i: number) => (
                    <div key={i} className="p-3 rounded-xl border border-white/10 bg-slate-950/60 flex items-center justify-between text-xs">
                      <span className="text-slate-300">{f.label}</span>
                      {f.ok ? <Check className="w-4 h-4 text-emerald-400" /> : <X className="w-4 h-4 text-rose-400" />}
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-end pt-2">
                <button
                  onClick={() => setSelectedLead(null)}
                  className="px-6 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs uppercase tracking-wider cursor-pointer"
                >
                  Close Report
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </main>
  );
}
