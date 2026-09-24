import React, { useState } from 'react';
import { Bookmark, Sparkles, Film, Info } from 'lucide-react';
import type { Movie } from '../types';
import { RatingBadge } from './RatingBadge';

interface MovieCardProps {
  movie: Movie;
  onSelect: (movie: Movie) => void;
  isBookmarked?: boolean;
  onToggleBookmark?: (movie: Movie) => void;
  showMatchScore?: boolean;
}

export const MovieCard: React.FC<MovieCardProps> = ({
  movie,
  onSelect,
  isBookmarked = false,
  onToggleBookmark,
  showMatchScore = false,
}) => {
  const [imgFailed, setImgFailed] = useState(!movie.poster_url);

  // Compute percentage match if recommendation score exists
  const matchPct = movie.recommendation_score
    ? Math.min(99, Math.max(60, Math.round(movie.recommendation_score * 160)))
    : null;

  const topReason = movie.explanation?.reasons?.[0];

  return (
    <div
      onClick={() => onSelect(movie)}
      className="group relative flex flex-col bg-slate-900/60 rounded-xl overflow-hidden border border-slate-800/80 hover:border-amber-500/40 transition-all duration-200 hover:-translate-y-1 hover:shadow-xl hover:shadow-black/60 cursor-pointer select-none"
    >
      {/* Poster Image / Fallback Container */}
      <div className="relative aspect-[2/3] w-full overflow-hidden bg-slate-950 flex items-center justify-center">
        {!imgFailed && movie.poster_url ? (
          <img
            src={movie.poster_url}
            alt={movie.title}
            onError={() => setImgFailed(true)}
            loading="lazy"
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
          />
        ) : (
          /* Subtle Fallback Poster */
          <div className="w-full h-full p-4 flex flex-col justify-between bg-gradient-to-br from-slate-900 via-slate-950 to-indigo-950/40 text-center relative border-b border-slate-800">
            <div className="w-full flex justify-between items-center opacity-40 text-slate-400">
              <Film size={18} />
              <span className="text-xs font-mono">{movie.release_year || 'Movie'}</span>
            </div>
            <div className="my-auto px-2">
              <h4 className="font-semibold text-sm line-clamp-3 text-slate-200 leading-snug">
                {movie.title}
              </h4>
              {movie.director && (
                <p className="text-[11px] text-slate-400 mt-1 line-clamp-1 italic">
                  dir. {movie.director}
                </p>
              )}
            </div>
            <div className="flex flex-wrap gap-1 justify-center opacity-60">
              {movie.genres.slice(0, 2).map((g) => (
                <span key={g} className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                  {g}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Gradient Overlay on hover */}
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/20 to-transparent opacity-60 group-hover:opacity-80 transition-opacity" />

        {/* Top Badges */}
        <div className="absolute top-2 left-2 right-2 flex justify-between items-start pointer-events-none">
          {/* Match Score */}
          {showMatchScore && matchPct !== null ? (
            <div className="bg-amber-500/90 text-slate-950 font-bold px-2 py-0.5 rounded-md text-[11px] flex items-center gap-1 shadow-md shadow-amber-950/50 backdrop-blur-sm">
              <Sparkles size={11} className="fill-current" />
              <span>{matchPct}% Match</span>
            </div>
          ) : (
            <div />
          )}

          {/* Bookmark Button */}
          {onToggleBookmark && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onToggleBookmark(movie);
              }}
              title={isBookmarked ? 'Remove from My List' : 'Save to My List'}
              className={`p-1.5 rounded-full pointer-events-auto transition-all ${
                isBookmarked
                  ? 'bg-amber-500 text-slate-950 hover:bg-amber-400 shadow-md'
                  : 'bg-slate-900/80 text-slate-300 hover:text-white hover:bg-slate-800 backdrop-blur-md'
              }`}
            >
              <Bookmark size={13} className={isBookmarked ? 'fill-current' : ''} />
            </button>
          )}
        </div>

        {/* Floating Reason Badge (if available) */}
        {topReason && (
          <div className="absolute bottom-2 left-2 right-2 pointer-events-none">
            <div className="bg-slate-900/90 border border-slate-700/80 text-amber-300 text-[10px] px-2 py-1 rounded backdrop-blur-md line-clamp-1 flex items-center gap-1">
              <Info size={10} className="shrink-0 text-amber-400" />
              <span className="truncate">{topReason}</span>
            </div>
          </div>
        )}
      </div>

      {/* Movie Information Footer */}
      <div className="p-3 flex flex-col flex-1 justify-between gap-2">
        <div>
          <div className="flex items-start justify-between gap-1 mb-1">
            <h3 className="font-semibold text-sm text-slate-100 line-clamp-1 group-hover:text-amber-400 transition-colors">
              {movie.title}
            </h3>
            {movie.release_year && (
              <span className="text-xs text-slate-500 shrink-0 font-mono">
                {movie.release_year}
              </span>
            )}
          </div>

          {/* Genres Tags */}
          <div className="flex flex-wrap gap-1 items-center">
            {movie.genres.slice(0, 2).map((genre) => (
              <span
                key={genre}
                className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800/80 text-slate-400 font-medium"
              >
                {genre}
              </span>
            ))}
            {movie.genres.length > 2 && (
              <span className="text-[10px] text-slate-500 font-medium">
                +{movie.genres.length - 2}
              </span>
            )}
          </div>
        </div>

        {/* Rating & Stats row */}
        <div className="flex items-center justify-between pt-1 border-t border-slate-800/60">
          <RatingBadge rating={movie.rating_mean} count={movie.rating_count} size="sm" />
          {movie.bayesian_rating > 0 && (
            <span className="text-[10px] text-slate-400" title="Bayesian Weighted Rating (IMDb formula)">
              WR: <span className="text-slate-300 font-medium">{movie.bayesian_rating.toFixed(1)}</span>
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
