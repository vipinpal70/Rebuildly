'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Lock, User, LogIn, ShieldCheck, Loader2 } from 'lucide-react';
import { adminApi, setToken } from '../../lib/adminApi';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await adminApi.login(username.trim(), password);
      setToken(res.token);
      window.location.href = '/';
    } catch (err: any) {
      setError(err.message || 'Login failed');
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center px-4 relative overflow-hidden"
      style={{ background: 'radial-gradient(70% 60% at 50% 0%, #0f1b3d 0%, #070b16 55%, #05070f 100%)', color: '#e2e8f0' }}>
      <div aria-hidden className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[400px] rounded-full blur-[160px]" style={{ background: 'rgba(56,189,248,0.18)' }} />

      <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
        className="w-full max-w-md relative z-10">
        <div className="rounded-3xl border p-8 sm:p-10 backdrop-blur-xl"
          style={{ backgroundColor: 'rgba(15,23,42,0.6)', borderColor: 'rgba(255,255,255,0.1)', boxShadow: '0 30px 80px rgba(0,0,0,0.5)' }}>
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 rounded-2xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg,#1e56d9,#38bdf8)' }}>
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Opportunity Finder</h1>
              <p className="text-xs text-slate-400">Admin Control Center</p>
            </div>
          </div>

          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">Username or Email</label>
              <div className="mt-2 flex items-center gap-3 px-4 py-3 rounded-xl border" style={{ borderColor: 'rgba(255,255,255,0.12)', backgroundColor: 'rgba(255,255,255,0.04)' }}>
                <User className="w-4 h-4 text-slate-400" />
                <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="vipinpal7060" autoFocus
                  className="flex-1 bg-transparent outline-none text-sm text-white placeholder:text-slate-500" />
              </div>
            </div>

            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">Password</label>
              <div className="mt-2 flex items-center gap-3 px-4 py-3 rounded-xl border" style={{ borderColor: 'rgba(255,255,255,0.12)', backgroundColor: 'rgba(255,255,255,0.04)' }}>
                <Lock className="w-4 h-4 text-slate-400" />
                <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" placeholder="••••••••"
                  className="flex-1 bg-transparent outline-none text-sm text-white placeholder:text-slate-500" />
              </div>
            </div>

            {error && <div className="text-sm rounded-lg px-4 py-2.5" style={{ backgroundColor: 'rgba(239,68,68,0.12)', color: '#fca5a5' }}>{error}</div>}

            <button type="submit" disabled={loading}
              className="w-full py-3.5 rounded-xl text-sm font-bold text-white uppercase tracking-wider inline-flex items-center justify-center gap-2 disabled:opacity-60 transition-opacity"
              style={{ background: 'linear-gradient(135deg,#1e56d9,#2d6af5)', boxShadow: '0 12px 30px rgba(30,86,217,0.4)' }}>
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <LogIn className="w-4 h-4" />}
              {loading ? 'Signing in…' : 'Sign In'}
            </button>
          </form>

          <p className="text-center text-xs text-slate-500 mt-6">Authorized administrators only · No sign-up</p>
        </div>
      </motion.div>
    </main>
  );
}
