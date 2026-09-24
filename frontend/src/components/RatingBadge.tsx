import React from 'react';
import { Star } from 'lucide-react';

interface RatingBadgeProps {
  rating: number;
  count?: number;
  size?: 'sm' | 'md' | 'lg';
}

export const RatingBadge: React.FC<RatingBadgeProps> = ({ rating, count, size = 'sm' }) => {
  const isHigh = rating >= 4.0;
  const isMid = rating >= 3.0 && rating < 4.0;

  const colorClass = isHigh
    ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
    : isMid
    ? 'bg-sky-500/10 text-sky-400 border-sky-500/30'
    : 'bg-slate-800 text-slate-400 border-slate-700';

  const sizeClass = size === 'lg' ? 'px-3 py-1 text-sm' : size === 'md' ? 'px-2.5 py-0.5 text-xs' : 'px-2 py-0.5 text-[11px]';
  const iconSize = size === 'lg' ? 14 : size === 'md' ? 12 : 10;

  return (
    <div className={`inline-flex items-center gap-1 font-medium rounded-full border ${colorClass} ${sizeClass}`}>
      <Star size={iconSize} className="fill-current" />
      <span>{rating > 0 ? rating.toFixed(1) : '—'}</span>
      {count !== undefined && count > 0 && (
        <span className="text-slate-500 text-[10px] font-normal">({count})</span>
      )}
    </div>
  );
};
