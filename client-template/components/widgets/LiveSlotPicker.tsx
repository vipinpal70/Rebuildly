'use client';

import React, { useState } from 'react';
import { Calendar, Clock, CheckCircle2, ChevronRight } from 'lucide-react';

interface LiveSlotPickerProps {
  cityName?: string;
  onSlotSelected?: (slot: string) => void;
  accentColor?: string;
}

export function LiveSlotPicker({
  cityName = "Manchester",
  onSlotSelected,
  accentColor = "#00b4d8"
}: LiveSlotPickerProps) {
  const [selectedSlot, setSelectedSlot] = useState<string | null>("Today • 3:30 PM");

  const availableSlots = [
    { day: "Today", time: "2:00 PM", badge: "URGENT SLOT" },
    { day: "Today", time: "3:30 PM", badge: "POPULAR" },
    { day: "Tomorrow", time: "10:00 AM", badge: "MORNING" },
    { day: "Tomorrow", time: "11:30 AM", badge: "MORNING" },
    { day: "Tomorrow", time: "2:30 PM", badge: "AFTERNOON" },
    { day: "Friday", time: "09:00 AM", badge: "EARLY" }
  ];

  const handleSelect = (slotStr: string) => {
    setSelectedSlot(slotStr);
    if (onSlotSelected) onSlotSelected(slotStr);
  };

  return (
    <div className="w-full p-6 sm:p-8 rounded-3xl border border-white/10 bg-slate-900/90 backdrop-blur-2xl shadow-2xl">
      <div className="flex items-center justify-between gap-4 mb-6 pb-4 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>LIVE APPOINTMENT DESK</span>
          </div>
          <h4 className="text-lg font-bold mt-1">Select Available Time Slot in {cityName}</h4>
        </div>
        <Calendar className="w-6 h-6 text-cyan-400 hidden sm:block" />
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
        {availableSlots.map((s, idx) => {
          const slotStr = `${s.day} • ${s.time}`;
          const isSelected = selectedSlot === slotStr;
          return (
            <button
              key={idx}
              onClick={() => handleSelect(slotStr)}
              className={`p-3.5 rounded-2xl border text-left transition-all cursor-pointer flex flex-col justify-between ${
                isSelected
                  ? 'border-cyan-400 bg-cyan-500/15 shadow-[0_0_20px_rgba(0,180,216,0.25)]'
                  : 'border-white/10 bg-white/5 hover:border-white/20'
              }`}
            >
              <div className="text-[10px] font-bold tracking-wider text-cyan-400 uppercase">{s.badge}</div>
              <div className="font-bold text-xs mt-1">{s.day}</div>
              <div className="text-sm font-semibold text-slate-300 flex items-center gap-1 mt-0.5">
                <Clock className="w-3 h-3 text-slate-400" />
                <span>{s.time}</span>
              </div>
            </button>
          );
        })}
      </div>

      {selectedSlot && (
        <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-between gap-4">
          <div className="flex items-center gap-2.5 text-xs">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>Selected: <strong>{selectedSlot}</strong> (Reserved for 10 mins)</span>
          </div>
          <button
            onClick={() => onSlotSelected && onSlotSelected(selectedSlot)}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-emerald-500 text-slate-950 uppercase tracking-wider hover:bg-emerald-400 transition-all flex items-center gap-1 cursor-pointer"
          >
            <span>Confirm Slot</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}
    </div>
  );
}
