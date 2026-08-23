"use client";

import React, { useEffect, useRef, useState } from "react";
import { ChevronDown, X, Plus, Check } from "lucide-react";

interface MultiSelectComboProps {
  label: string;
  options: string[];
  value: string[];
  onChange: (values: string[]) => void;
  placeholder?: string;
  isLight?: boolean;
  /** Optional small inline hint badge per option, e.g. { Solicitor: "UK/Ireland term" } */
  hints?: Record<string, string>;
}

/** Predefined-options dropdown that also accepts free-text custom entries — pick from
 * the list, or type anything and press Enter / click "Add" to use a custom value. */
export default function MultiSelectCombo({
  label, options, value, onChange, placeholder, isLight, hints,
}: MultiSelectComboProps) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
        setQuery("");
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const lowerValue = value.map((v) => v.toLowerCase());
  const filtered = options.filter(
    (o) => o.toLowerCase().includes(query.trim().toLowerCase()) && !lowerValue.includes(o.toLowerCase())
  );
  const trimmedQuery = query.trim();
  const canAddCustom =
    trimmedQuery.length > 0 &&
    !lowerValue.includes(trimmedQuery.toLowerCase()) &&
    !options.some((o) => o.toLowerCase() === trimmedQuery.toLowerCase());

  const add = (item: string) => {
    if (!lowerValue.includes(item.toLowerCase())) onChange([...value, item]);
    setQuery("");
  };
  const remove = (item: string) => onChange(value.filter((v) => v !== item));
  const toggle = (item: string) => (lowerValue.includes(item.toLowerCase()) ? remove(item) : add(item));

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      if (filtered.length > 0 && trimmedQuery) add(filtered[0]);
      else if (canAddCustom) add(trimmedQuery);
    } else if (e.key === "Backspace" && !query && value.length > 0) {
      remove(value[value.length - 1]);
    } else if (e.key === "Escape") {
      setOpen(false);
      inputRef.current?.blur();
    }
  };

  return (
    <div className="relative" ref={containerRef}>
      <label className={`block text-[10px] font-semibold uppercase tracking-wide mb-1 ${isLight ? "text-slate-500" : "text-slate-500"}`}>
        {label}
      </label>
      <div
        onClick={() => { setOpen(true); inputRef.current?.focus(); }}
        className={`flex flex-wrap items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-xs cursor-text min-h-[34px] transition ${
          open ? "border-indigo-500/60 ring-2 ring-indigo-500/20" : isLight ? "border-slate-300" : "border-slate-800"
        } ${isLight ? "bg-slate-50" : "bg-slate-950"}`}
      >
        {value.map((item) => (
          <span
            key={item}
            className={`inline-flex items-center gap-1 pl-2 pr-1 py-0.5 rounded-md text-[11px] font-medium ${
              isLight ? "bg-indigo-100 text-indigo-700" : "bg-indigo-500/20 text-indigo-300"
            }`}
          >
            {item}
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); remove(item); }}
              className={`rounded-sm p-0.5 hover:bg-rose-500/20 hover:text-rose-400 transition`}
              aria-label={`Remove ${item}`}
            >
              <X className="w-2.5 h-2.5" />
            </button>
          </span>
        ))}
        <input
          ref={inputRef}
          value={query}
          onChange={(e) => { setQuery(e.target.value); setOpen(true); }}
          onFocus={() => setOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder={value.length === 0 ? placeholder : ""}
          className={`flex-1 min-w-[70px] bg-transparent outline-none text-xs ${
            isLight ? "text-slate-900 placeholder:text-slate-400" : "text-white placeholder:text-slate-600"
          }`}
        />
        <ChevronDown
          className={`w-3.5 h-3.5 shrink-0 transition-transform ${open ? "rotate-180" : ""} ${isLight ? "text-slate-400" : "text-slate-600"}`}
        />
      </div>

      {open && (
        <div
          className={`absolute z-30 mt-1 w-full max-h-56 overflow-y-auto rounded-lg border shadow-xl ${
            isLight ? "bg-white border-slate-200" : "bg-slate-900 border-slate-700"
          }`}
        >
          {filtered.length === 0 && !canAddCustom && (
            <div className={`px-3 py-2 text-[11px] ${isLight ? "text-slate-400" : "text-slate-600"}`}>
              {value.length > 0 && !trimmedQuery ? "All suggestions selected" : "No matches — keep typing to add a custom value"}
            </div>
          )}
          {filtered.map((opt) => (
            <button
              key={opt}
              type="button"
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => add(opt)}
              className={`w-full flex items-center justify-between gap-2 px-3 py-1.5 text-xs text-left transition ${
                isLight ? "text-slate-700 hover:bg-indigo-50" : "text-slate-300 hover:bg-slate-800"
              }`}
            >
              <span>{opt}</span>
              {hints?.[opt] && (
                <span className={`shrink-0 text-[9px] px-1.5 py-0.5 rounded ${isLight ? "bg-amber-100 text-amber-700" : "bg-amber-500/20 text-amber-400"}`}>
                  {hints[opt]}
                </span>
              )}
            </button>
          ))}
          {canAddCustom && (
            <button
              type="button"
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => add(trimmedQuery)}
              className={`w-full flex items-center gap-1.5 px-3 py-1.5 text-xs text-left border-t ${
                isLight ? "text-indigo-600 hover:bg-indigo-50 border-slate-100" : "text-indigo-400 hover:bg-slate-800 border-slate-800"
              }`}
            >
              <Plus className="w-3 h-3" /> Add "{trimmedQuery}"
            </button>
          )}
          {value.length > 0 && (
            <div className={`flex items-center gap-1 px-3 py-1.5 text-[10px] border-t ${isLight ? "text-slate-400 border-slate-100" : "text-slate-600 border-slate-800"}`}>
              <Check className="w-3 h-3" /> {value.length} selected
            </div>
          )}
        </div>
      )}
    </div>
  );
}
