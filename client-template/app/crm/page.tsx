"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import OutreachStudioModal from "@/components/OutreachStudioModal";

interface CRMLead {
  business_id: string;
  name: string;
  category: string;
  city: string;
  phone: string;
  website: string;
  google_rating: number;
  review_count: number;
  modernization_score: number;
  tier: string;
  preview_url: string;
  slug: string;
  outreach_status: string;
  contact_email: string;
  preview_clicked: boolean;
  click_count: number;
}

export default function CRMPage() {
  const [leads, setLeads] = useState<CRMLead[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedStatus, setSelectedStatus] = useState<string>("ALL");
  const [selectedLeadId, setSelectedLeadId] = useState<string | null>(null);

  useEffect(() => {
    fetchLeads();
  }, [selectedStatus]);

  const fetchLeads = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("token") || "";
      const res = await fetch(`http://localhost:8000/admin/crm/leads?status=${selectedStatus}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setLeads(data.leads || []);
      }
    } catch (err) {
      console.error("Failed to load CRM leads", err);
    } finally {
      setLoading(false);
    }
  };

  // Metrics
  const totalLeads = leads.length;
  const emailsSent = leads.filter(l => l.outreach_status === "EMAIL_SENT" || l.outreach_status === "VIEWED").length;
  const totalClicks = leads.reduce((sum, l) => sum + (l.click_count || 0), 0);
  const convertedCount = leads.filter(l => l.outreach_status === "CONVERTED").length;

  const getStatusBadge = (status: string, previewClicked: boolean) => {
    if (previewClicked || status === "VIEWED") {
      return <span className="px-2.5 py-1 text-xs font-bold rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">👁️ PREVIEW VIEWED</span>;
    }
    switch (status) {
      case "EMAIL_SENT":
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">📧 EMAIL SENT</span>;
      case "LINKEDIN_SENT":
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30">🔗 LINKEDIN TOUCH</span>;
      case "WA_SENT":
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">💬 WA SENT</span>;
      case "CALLED":
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30">📞 CALLED</span>;
      case "CONVERTED":
        return <span className="px-2.5 py-1 text-xs font-bold rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">🎉 CONVERTED</span>;
      default:
        return <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-slate-800 text-slate-400 border border-slate-700">NEW LEAD</span>;
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      
      {/* Header Navigation */}
      <header className="sticky top-0 z-30 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/20">
            OF
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight">Sales & Outreach Command Studio</h1>
            <p className="text-xs text-slate-400">Admin-Controlled Omnichannel Sales Pipeline</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="px-4 py-2 text-xs font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-xl transition"
          >
            ← Main Dashboard
          </Link>
          <Link
            href="/audit"
            className="px-4 py-2 text-xs font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-xl transition"
          >
            Live Logs Console
          </Link>
        </div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">

        {/* Metrics Overview */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
            <p className="text-xs font-semibold text-slate-400">Discovered Leads</p>
            <h3 className="text-2xl font-bold text-white mt-1">{totalLeads}</h3>
            <span className="text-[11px] text-slate-500 mt-1 block">Tier 1 & Tier 2 Leads</span>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
            <p className="text-xs font-semibold text-slate-400">Outreach Emails Sent</p>
            <h3 className="text-2xl font-bold text-indigo-400 mt-1">{emailsSent}</h3>
            <span className="text-[11px] text-slate-500 mt-1 block">Plain-text verified emails</span>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
            <p className="text-xs font-semibold text-slate-400">Preview Link Engagement</p>
            <h3 className="text-2xl font-bold text-emerald-400 mt-1">{totalClicks} Clicks</h3>
            <span className="text-[11px] text-slate-500 mt-1 block">Tracked via Real-time Telegram Alert</span>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
            <p className="text-xs font-semibold text-slate-400">Conversions</p>
            <h3 className="text-2xl font-bold text-purple-400 mt-1">{convertedCount}</h3>
            <span className="text-[11px] text-slate-500 mt-1 block">Closed Web Modernization Clients</span>
          </div>
        </div>

        {/* Filters & Pipeline Controls */}
        <div className="flex items-center justify-between flex-wrap gap-3 bg-slate-900/50 p-4 rounded-2xl border border-slate-800">
          <div className="flex items-center gap-2 overflow-x-auto">
            {["ALL", "NEW", "LINKEDIN_SENT", "EMAIL_SENT", "WA_SENT", "CALLED", "CONVERTED"].map((status) => (
              <button
                key={status}
                onClick={() => setSelectedStatus(status)}
                className={`px-3 py-1.5 text-xs font-medium rounded-xl transition ${
                  selectedStatus === status
                    ? "bg-indigo-600 text-white shadow-md shadow-indigo-500/20"
                    : "bg-slate-800/80 text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                }`}
              >
                {status.replace("_", " ")}
              </button>
            ))}
          </div>

          <button
            onClick={fetchLeads}
            className="px-3.5 py-1.5 text-xs font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 rounded-xl transition flex items-center gap-1.5"
          >
            🔄 Refresh Leads
          </button>
        </div>

        {/* Lead Table */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
          {loading ? (
            <div className="p-12 text-center text-slate-400 animate-pulse">
              Loading CRM lead pipeline data...
            </div>
          ) : leads.length === 0 ? (
            <div className="p-12 text-center text-slate-500">
              No leads match the selected status filter.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-950/80 text-xs font-semibold text-slate-400 uppercase border-b border-slate-800">
                  <tr>
                    <th className="px-6 py-4">Business & City</th>
                    <th className="px-4 py-4">Google Score</th>
                    <th className="px-4 py-4">Audit Score</th>
                    <th className="px-4 py-4">Outreach Status</th>
                    <th className="px-4 py-4">Preview Clicks</th>
                    <th className="px-6 py-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {leads.map((lead) => (
                    <tr key={lead.business_id} className="hover:bg-slate-800/40 transition">
                      <td className="px-6 py-4">
                        <div className="font-semibold text-white">{lead.name}</div>
                        <div className="text-xs text-slate-400">{lead.category} • {lead.city}</div>
                      </td>

                      <td className="px-4 py-4">
                        <span className="font-semibold text-amber-400">⭐ {lead.google_rating || "4.8"}</span>
                        <div className="text-xs text-slate-500">{lead.review_count} reviews</div>
                      </td>

                      <td className="px-4 py-4">
                        <span className={`px-2.5 py-1 text-xs font-bold rounded-lg ${
                          lead.modernization_score >= 80 
                            ? "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                            : "bg-amber-500/10 text-amber-400 border border-amber-500/30"
                        }`}>
                          {lead.modernization_score}/100
                        </span>
                      </td>

                      <td className="px-4 py-4">
                        {getStatusBadge(lead.outreach_status, lead.preview_clicked)}
                      </td>

                      <td className="px-4 py-4 font-mono text-xs">
                        {lead.click_count > 0 ? (
                          <span className="text-emerald-400 font-bold">👁️ {lead.click_count} clicks</span>
                        ) : (
                          <span className="text-slate-500">0 clicks</span>
                        )}
                      </td>

                      <td className="px-6 py-4 text-right space-x-2">
                        <button
                          onClick={() => setSelectedLeadId(lead.business_id)}
                          className="px-3 py-1.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl transition shadow-md shadow-indigo-500/20"
                        >
                          ⚡ Outreach Studio
                        </button>
                        <a
                          href={lead.preview_url}
                          target="_blank"
                          rel="noreferrer"
                          className="px-3 py-1.5 text-xs font-semibold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-xl transition inline-block"
                        >
                          🌐 Preview Site
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

      </main>

      {/* Outreach Studio Modal Drawer */}
      {selectedLeadId && (
        <OutreachStudioModal
          businessId={selectedLeadId}
          onClose={() => setSelectedLeadId(null)}
          onStatusUpdated={fetchLeads}
        />
      )}

    </div>
  );
}
