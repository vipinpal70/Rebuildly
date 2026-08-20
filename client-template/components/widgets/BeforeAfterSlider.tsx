'use client';

import React, { useState, useRef, useCallback } from 'react';
import { Sparkles, CheckCircle2 } from 'lucide-react';

interface BeforeAfterSliderProps {
  beforeImage?: string;
  afterImage?: string;
  beforeLabel?: string;
  afterLabel?: string;
  title?: string;
  subtitle?: string;
  accentColor?: string;
}

export function BeforeAfterSlider({
  beforeImage = "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?auto=format&fit=crop&w=1200&q=80",
  afterImage = "https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=1200&q=80",
  beforeLabel = "INITIAL CONSULTATION",
  afterLabel = "AFTER TREATMENT",
  title = "Real Patient Transformation Result",
  subtitle = "Drag the slider to see the difference our precision treatments achieve.",
  accentColor = "#00b4d8"
}: BeforeAfterSliderProps) {
  const [sliderPosition, setSliderPosition] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMove = useCallback((clientX: number) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = clientX - rect.left;
    let percentage = (x / rect.width) * 100;
    if (percentage < 0) percentage = 0;
    if (percentage > 100) percentage = 100;
    setSliderPosition(percentage);
  }, []);

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    if (isDragging && e.touches[0]) {
      handleMove(e.touches[0].clientX);
    }
  }, [isDragging, handleMove]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (isDragging) {
      handleMove(e.clientX);
    }
  }, [isDragging, handleMove]);

  return (
    <div className="w-full my-12">
      <div className="text-center max-w-2xl mx-auto mb-8">
        <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest mb-2" style={{ color: accentColor }}>
          <Sparkles className="w-4 h-4" />
          <span>PROVEN RESULTS</span>
        </div>
        <h3 className="text-2xl sm:text-4xl font-bold mb-3">{title}</h3>
        <p className="text-xs sm:text-sm text-slate-400">{subtitle}</p>
      </div>

      <div
        ref={containerRef}
        className="relative w-full h-[420px] sm:h-[500px] rounded-3xl overflow-hidden shadow-2xl border border-white/10 select-none cursor-ew-resize touch-none"
        onMouseDown={() => setIsDragging(true)}
        onMouseUp={() => setIsDragging(false)}
        onMouseLeave={() => setIsDragging(false)}
        onMouseMove={handleMouseMove}
        onTouchStart={() => setIsDragging(true)}
        onTouchEnd={() => setIsDragging(false)}
        onTouchMove={handleTouchMove}
      >
        {/* After Image (Full Background) */}
        <img
          src={afterImage}
          alt={afterLabel}
          className="absolute inset-0 w-full h-full object-cover pointer-events-none"
        />

        {/* Before Image (Clipped) */}
        <div
          className="absolute top-0 bottom-0 left-0 overflow-hidden pointer-events-none"
          style={{ width: `${sliderPosition}%` }}
        >
          <img
            src={beforeImage}
            alt={beforeLabel}
            className="absolute top-0 left-0 max-w-none h-full object-cover"
            style={{ width: containerRef.current ? `${containerRef.current.clientWidth}px` : '100%' }}
          />
        </div>

        {/* Labels */}
        <div className="absolute top-6 left-6 bg-black/70 backdrop-blur-md px-4 py-2 rounded-full text-[11px] font-bold tracking-wider text-white border border-white/10 pointer-events-none">
          {beforeLabel}
        </div>
        <div className="absolute top-6 right-6 bg-black/70 backdrop-blur-md px-4 py-2 rounded-full text-[11px] font-bold tracking-wider text-white border border-white/10 pointer-events-none">
          {afterLabel}
        </div>

        {/* Divider Handle */}
        <div
          className="absolute top-0 bottom-0 w-1 bg-white shadow-[0_0_20px_rgba(255,255,255,0.8)] pointer-events-none"
          style={{ left: `${sliderPosition}%` }}
        >
          <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-10 h-10 rounded-full bg-white text-slate-950 shadow-2xl flex items-center justify-center font-bold text-xs border-2 border-cyan-500">
            ↔
          </div>
        </div>
      </div>
    </div>
  );
}
