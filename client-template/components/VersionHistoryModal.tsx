"use client";

import React, { useEffect, useState } from "react";
import { X, History, ExternalLink, Loader2, Sparkles } from "lucide-react";
import { adminApi } from "../lib/adminApi";

interface VersionEntry {
  version_number: number;
  is_current: boolean;
  archetype: string | null;
  created_at: string | null;
  feedback_snapshot: { text: string; created_at: string }[];
  preview_url: string;
}

interface VersionHistoryModalProps {
  slug: string;
  siteName: string;
  onClose: () => void;
}

export default function VersionHistoryModal({ slug, siteName, onClose }: VersionHistoryModalProps) {
  const [versions, setVersions] = useState<VersionEntry[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    adminApi
      .siteVersions(slug)
      .then((r) => setVersions(r.versions))
      .catch((e) => setError(e.message || "Failed to load version history."));
  }, [slug]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4">
      <div className="relative w-full max-w-xl bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
        <div className="flex items-center justify-between px-5 py-4 bg-slate-950/80 border-b border-slate-800">
          <div>
            <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              <History className="w-4 h-4 text-indigo-400" /> Version History: {siteName}
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Every past design is kept — share any link below with the client to let them compare.
            </p>
          </div>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-5 space-y-2.5 overflow-y-auto">
          {error && <p className="text-xs text-rose-400">{error}</p>}
          {!versions && !error && (
            <div className="flex items-center justify-center py-10 text-slate-500 text-xs gap-2">
              <Loader2 className="w-4 h-4 animate-spin" /> Loading versions…
            </div>
          )}
          {versions?.map((v) => (
            <div
              key={v.version_number}
              className={`rounded-xl border p-3.5 ${
                v.is_current ? "bg-indigo-500/10 border-indigo-500/30" : "bg-slate-950/60 border-slate-800"
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-white">Version {v.version_number}</span>
                    {v.is_current && (
                      <span className="inline-flex items-center gap-1 text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                        <Sparkles className="w-2.5 h-2.5" /> Current
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    {v.created_at ? new Date(v.created_at).toLocaleString() : "—"} · {v.archetype || "—"}
                  </p>
                </div>
                <a
                  href={v.preview_url}
                  target="_blank"
                  rel="noreferrer"
                  className="shrink-0 text-[11px] font-bold px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 flex items-center gap-1.5 transition"
                >
                  <ExternalLink className="w-3 h-3" /> View
                </a>
              </div>
              {v.feedback_snapshot.length > 0 && (
                <ul className="mt-2.5 pt-2.5 border-t border-slate-800/80 space-y-1">
                  {v.feedback_snapshot.map((f, i) => (
                    <li key={i} className="text-[11px] text-slate-400 leading-relaxed">
                      <span className="text-slate-600">{new Date(f.created_at).toLocaleDateString()}:</span> {f.text}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))}
          {versions?.length === 1 && (
            <p className="text-xs text-slate-500 text-center py-2">
              No past versions yet — they'll appear here after the first regeneration.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
