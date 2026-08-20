import React from 'react';
import { Star, Quote, CheckCircle2, MessageSquare } from 'lucide-react';
import { BusinessData } from '../types/business';

interface ReviewCarouselProps {
  business: BusinessData;
}

export const ReviewCarousel: React.FC<ReviewCarouselProps> = ({ business }) => {
  const reviews = business.reviews || [];

  return (
    <section id="reviews" className="py-24 px-4 sm:px-8 bg-[#050b17] relative overflow-hidden border-t border-white/10">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-16">
          <div>
            <div className="inline-flex items-center gap-2 text-xs font-bold tracking-widest uppercase text-cyan-400 mb-3 bg-cyan-950/50 border border-cyan-400/30 px-4 py-1.5 rounded-full">
              <MessageSquare className="w-4 h-4 text-cyan-400" />
              <span>PATIENT REVIEWS & STORIES</span>
            </div>
            <h2 className="font-serif-title text-3xl sm:text-5xl font-bold text-white tracking-tight">
              Loved by Patients in <em className="italic text-cyan-300 font-normal">{business.city}</em>
            </h2>
          </div>

          {/* Rating Summary Box */}
          <div className="glass-card px-6 py-4 rounded-2xl flex items-center gap-4 border border-white/10">
            <div className="font-serif-title text-3xl font-extrabold text-white">
              {business.google_rating}
            </div>
            <div>
              <div className="flex text-amber-400 gap-0.5 mb-1">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-3.5 h-3.5 fill-amber-400" />
                ))}
              </div>
              <div className="text-[11px] text-slate-400 font-semibold">
                Based on {business.review_count} Verified Google Reviews
              </div>
            </div>
          </div>
        </div>

        {/* Reviews Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {reviews.map((rev, idx) => (
            <div
              key={idx}
              className="glass-card p-8 rounded-3xl border border-white/10 hover:border-cyan-400/40 transition-all flex flex-col justify-between group relative"
            >
              <div>
                {/* Result Badge */}
                {rev.resultBadge && (
                  <div className="inline-flex items-center gap-1.5 text-[10px] font-bold tracking-wider uppercase text-cyan-300 bg-cyan-950/70 border border-cyan-500/30 px-3 py-1 rounded-full mb-6">
                    <CheckCircle2 className="w-3 h-3 text-cyan-400" />
                    <span>{rev.resultBadge}</span>
                  </div>
                )}

                {/* Star Rating */}
                <div className="flex text-amber-400 gap-1 mb-4">
                  {[...Array(rev.rating || 5)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 fill-amber-400" />
                  ))}
                </div>

                {/* Review Text */}
                <p className="text-slate-300 text-xs sm:text-sm leading-relaxed italic mb-8">
                  "{rev.text}"
                </p>
              </div>

              {/* Author Details */}
              <div className="flex items-center gap-3 pt-4 border-t border-white/10">
                <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-white font-bold text-sm shadow-md">
                  {rev.avatarLetter || rev.author.charAt(0)}
                </div>
                <div>
                  <div className="text-xs font-bold text-white group-hover:text-cyan-300 transition-colors">
                    {rev.author}
                  </div>
                  <div className="text-[11px] text-slate-400">
                    Verified Google Review • {rev.relativeTime}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
