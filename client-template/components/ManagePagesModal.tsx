"use client";

import React, { useEffect, useState } from "react";
import { X, Plus, Trash2, Link2, Loader2, Save } from "lucide-react";
import { adminApi } from "../lib/adminApi";

interface PageEntry {
  url: string;
  label: string;
}

interface ManagePagesModalProps {
  businessId: string | null;
  businessName?: string;
  initialUrls: PageEntry[];
  onClose: () => void;
  onSaved?: (urls: PageEntry[]) => void;
}

const SUGGESTED_LABELS = ["Team Page", "Contact Us", "About Us", "Custom"];
const MAX_URLS = 5;

/** Lets the admin attach extra pages (team, contact-us, about-us, or any URL) to a
 * lead — enrich_lead always scrapes these on top of whatever it auto-discovers, and
 * a page labeled "Team Page" overrides the automatic team-page guess entirely. */
export default function ManagePagesModal({ businessId, businessName, initialUrls, onClose, onSaved }: ManagePagesModalProps) {
  const [rows, setRows] = useState<PageEntry[]>(initialUrls.length ? initialUrls : []);
  const [newUrl, setNewUrl] = useState("");
  const [newLabel, setNewLabel] = useState("Team Page");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setRows(initialUrls.length ? initialUrls : []);
  }, [businessId]); // eslint-disable-line react-hooks/exhaustive-deps

  if (!businessId) return null;

  const addRow = () => {
    const url = newUrl.trim();
    setError("");
    if (!url) return;
    if (!/^https?:\/\//i.test(url)) {
      setError("URL must start with http:// or https://");
      return;
    }
    if (rows.length >= MAX_URLS) {
      setError(`Maximum ${MAX_URLS} additional pages per lead.`);
      return;
    }
    if (rows.some((r) => r.url.toLowerCase() === url.toLowerCase())) {
      setError("That URL is already in the list.");
      return;
    }
    setRows([...rows, { url, label: newLabel.trim() || "Custom" }]);
    setNewUrl("");
  };

  const removeRow = (idx: number) => setRows(rows.filter((_, i) => i !== idx));

  const save = async () => {
    setSaving(true);
    setError("");
    try {
      const res = await adminApi.saveAdditionalUrls(businessId, rows);
      onSaved?.(res.additional_urls || rows);
      onClose();
    } catch (e: any) {
      setError(e.message || "Failed to save pages.");
    }
    setSaving(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4">
      <div className="relative w-full max-w-lg bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
        <div className="flex items-center justify-between px-5 py-4 bg-slate-950/80 border-b border-slate-800">
          <div>
            <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              <Link2 className="w-4 h-4 text-cyan-400" /> Additional Pages
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              {businessName ? `For ${businessName} — ` : ""}always scraped on Enrich, on top of auto-discovery.
            </p>
          </div>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-5 space-y-4 overflow-y-auto">
          {rows.length === 0 && (
            <p className="text-xs text-slate-500">
              No extra pages added yet. Add a team page, contact-us, about-us, or any URL you want the enrichment to read.
            </p>
          )}

          <div className="space-y-2">
            {rows.map((r, i) => (
              <div key={i} className="flex items-center gap-2 bg-slate-950 border border-slate-800 rounded-xl px-3 py-2">
                <span className="shrink-0 text-[10px] font-bold uppercase tracking-wide px-2 py-1 rounded-md bg-cyan-500/15 text-cyan-300 border border-cyan-500/20">
                  {r.label}
                </span>
                <span className="flex-1 text-xs text-slate-300 truncate" title={r.url}>{r.url}</span>
                <button
                  onClick={() => removeRow(i)}
                  className="shrink-0 p-1 text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 rounded transition"
                  aria-label={`Remove ${r.url}`}
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>

          {rows.length < MAX_URLS && (
            <div className="pt-3 border-t border-slate-800 space-y-2">
              <div className="flex flex-wrap gap-1.5">
                {SUGGESTED_LABELS.map((l) => (
                  <button
                    key={l}
                    type="button"
                    onClick={() => setNewLabel(l)}
                    className={`px-2.5 py-1 text-[11px] font-semibold rounded-lg border transition ${
                      newLabel === l
                        ? "bg-cyan-600/20 text-cyan-300 border-cyan-600/40"
                        : "bg-slate-800/60 text-slate-400 border-slate-700 hover:text-slate-200"
                    }`}
                  >
                    {l}
                  </button>
                ))}
              </div>
              <div className="flex gap-2">
                <input
                  value={newUrl}
                  onChange={(e) => setNewUrl(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && addRow()}
                  placeholder="https://theirsite.com/team"
                  className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 outline-none focus:ring-2 focus:ring-cyan-500/40"
                />
                <button
                  onClick={addRow}
                  className="shrink-0 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold inline-flex items-center gap-1.5 transition"
                >
                  <Plus className="w-3.5 h-3.5" /> Add
                </button>
              </div>
              {newLabel === "Custom" || !SUGGESTED_LABELS.includes(newLabel) ? (
                <input
                  value={newLabel}
                  onChange={(e) => setNewLabel(e.target.value)}
                  placeholder="Custom label (e.g. Pricing Page)"
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-[11px] text-slate-300 outline-none focus:ring-2 focus:ring-cyan-500/40"
                />
              ) : null}
            </div>
          )}

          {error && <p className="text-xs text-rose-400">{error}</p>}
        </div>

        <div className="flex items-center justify-between px-5 py-4 border-t border-slate-800 bg-slate-950/40">
          <span className="text-[11px] text-slate-500">{rows.length}/{MAX_URLS} pages</span>
          <button
            onClick={save}
            disabled={saving}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-bold rounded-xl transition flex items-center gap-2 shadow-lg shadow-indigo-500/20"
          >
            {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
            Save Pages
          </button>
        </div>
      </div>
    </div>
  );
}
