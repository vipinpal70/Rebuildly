"use client";

import React, { useState } from "react";
import { X, RotateCw, Loader2, MessageSquareText, History } from "lucide-react";
import { adminApi } from "../lib/adminApi";

interface FeedbackEntry {
  text: string;
  created_at: string;
}

interface RegenerateFeedbackModalProps {
  slug: string;
  siteName: string;
  currentArchetype?: string;
  pastFeedback?: FeedbackEntry[];
  onClose: () => void;
  onRegenerated: (result: { slug: string; archetype: string }) => void;
}

// Quick-start prompts covering the categories explicitly worth calling out — the
// admin can click one to drop a starter phrase into the textarea, then finish the
// thought in their own words. Doesn't restrict input to just these topics.
const QUICK_TAGS = [
  { label: "Colors / Theme", starter: "The colors/theme feel " },
  { label: "Font", starter: "The font/typography " },
  { label: "Layout", starter: "The layout " },
  { label: "Animation", starter: "The animation/motion " },
  { label: "Content", starter: "For the content, please " },
];

export default function RegenerateFeedbackModal({
  slug, siteName, currentArchetype, pastFeedback = [], onClose, onRegenerated,
}: RegenerateFeedbackModalProps) {
  const [feedback, setFeedback] = useState("");
  const [busy, setBusy] = useState<"feedback" | "skip" | "">("");
  const [error, setError] = useState("");

  const addTag = (starter: string) => {
    setFeedback((prev) => (prev && !prev.endsWith(" ") && !prev.endsWith("\n") ? prev + "\n" : prev) + starter);
  };

  const run = async (mode: "feedback" | "skip") => {
    setBusy(mode);
    setError("");
    try {
      const text = mode === "feedback" ? feedback.trim() : undefined;
      const result = await adminApi.regenerateSite(slug, text);
      onRegenerated(result);
      onClose();
    } catch (e: any) {
      setError(e.message || "Regenerate failed.");
    }
    setBusy("");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4">
      <div className="relative w-full max-w-lg bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
        <div className="flex items-center justify-between px-5 py-4 bg-slate-950/80 border-b border-slate-800">
          <div>
            <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              <MessageSquareText className="w-4 h-4 text-indigo-400" /> Regenerate: {siteName}
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              {currentArchetype ? `Current design: ${currentArchetype} — ` : ""}tell us what to change and the next version will address it.
            </p>
          </div>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-5 space-y-4 overflow-y-auto">
          {pastFeedback.length > 0 && (
            <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-400 mb-2">
                <History className="w-3.5 h-3.5" /> Previous feedback (still applied every regeneration)
              </div>
              <ul className="space-y-1.5">
                {pastFeedback.map((f, i) => (
                  <li key={i} className="text-xs text-slate-300 leading-relaxed">
                    <span className="text-slate-600">{new Date(f.created_at).toLocaleDateString()}:</span> {f.text}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div>
            <div className="flex flex-wrap gap-1.5 mb-2">
              {QUICK_TAGS.map((t) => (
                <button
                  key={t.label}
                  type="button"
                  onClick={() => addTag(t.starter)}
                  className="px-2.5 py-1 text-[11px] font-semibold rounded-lg border bg-slate-800/60 text-slate-300 border-slate-700 hover:bg-slate-800 hover:text-white transition"
                >
                  + {t.label}
                </button>
              ))}
            </div>
            <textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              rows={6}
              placeholder="e.g. The colors feel too flashy/neon — I want something more professional and clean. The FAQ section feels cluttered. Please add a section for opening hours."
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-slate-200 outline-none focus:ring-2 focus:ring-indigo-500/40 resize-none"
            />
          </div>

          {error && <p className="text-xs text-rose-400">{error}</p>}
        </div>

        <div className="flex items-center justify-between gap-3 px-5 py-4 border-t border-slate-800 bg-slate-950/40">
          <button
            onClick={() => run("skip")}
            disabled={!!busy}
            className="text-xs font-semibold text-slate-400 hover:text-slate-200 disabled:opacity-40 transition flex items-center gap-1.5"
          >
            {busy === "skip" ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RotateCw className="w-3.5 h-3.5" />}
            Just regenerate (no feedback)
          </button>
          <button
            onClick={() => run("feedback")}
            disabled={!!busy || !feedback.trim()}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white text-xs font-bold rounded-xl transition flex items-center gap-2 shadow-lg shadow-indigo-500/20"
          >
            {busy === "feedback" ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RotateCw className="w-3.5 h-3.5" />}
            Regenerate with Feedback
          </button>
        </div>
      </div>
    </div>
  );
}
