import React, { useEffect, useState } from 'react';
import {
  X,
  Bookmark,
  Sparkles,
  Calendar,
  Clock,
  User,
  Users,
  ExternalLink,
  Film,
  CheckCircle2,
  Cpu
} from 'lucide-react';
import type { Movie } from '../types';
import { RatingBadge } from './RatingBadge';
import { api } from '../services/api';

interface MovieDetailsModalProps {
  movie: Movie | null;
  onClose: () => void;
  onSelectMovie: (movie: Movie) => void;
  isBookmarked: boolean;
  onToggleBookmark: (movie: Movie) => void;
}

export const MovieDetailsModal: React.FC<MovieDetailsModalProps> = ({
  movie,
  onClose,
  onSelectMovie,
  isBookmarked,
  onToggleBookmark,
}) => {
  const [similarMovies, setSimilarMovies] = useState<Movie[]>([]);
  const [loadingSimilar, setLoadingSimilar] = useState(false);
  const [imgFailed, setImgFailed] = useState(false);

  useEffect(() => {
    if (!movie) return;
    setImgFailed(false);

    // Fetch similar movies live
    setLoadingSimilar(true);
    api
      .getMovieRecommendations(movie.movieId, { top_k: 5 })
      .then((res) => setSimilarMovies(res))
      .catch((err) => {
        console.error('Failed to load similar movies:', err);
        setSimilarMovies([]);
      })
      .finally(() => setLoadingSimilar(false));

    // Handle ESC key
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [movie, onClose]);

  if (!movie) return null;

  const explanation = movie.explanation;
  const matchPct = movie.recommendation_score
    ? Math.min(99, Math.max(60, Math.round(movie.recommendation_score * 160)))
    : null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 md:p-6 overflow-y-auto bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div
        className="relative w-full max-w-4xl max-h-[92vh] overflow-y-auto bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl text-slate-100 flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-20 p-2 rounded-full bg-slate-950/70 border border-slate-700 text-slate-400 hover:text-white hover:bg-slate-800 transition"
        >
          <X size={18} />
        </button>

        {/* Modal Header / Banner Hero */}
        <div className="relative p-6 md:p-8 flex flex-col md:flex-row gap-6 border-b border-slate-800 bg-gradient-to-b from-slate-800/40 via-slate-900 to-slate-900">
          {/* Poster */}
          <div className="w-36 md:w-52 shrink-0 aspect-[2/3] rounded-xl overflow-hidden bg-slate-950 border border-slate-800 shadow-xl relative self-center md:self-start">
            {!imgFailed && movie.poster_url ? (
              <img
                src={movie.poster_url}
                alt={movie.title}
                onError={() => setImgFailed(true)}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full p-4 flex flex-col justify-between items-center bg-gradient-to-br from-slate-900 to-indigo-950/60 text-center">
                <Film size={28} className="text-slate-600 mt-4" />
                <span className="font-semibold text-xs text-slate-300">{movie.title}</span>
                <span className="text-[10px] text-slate-500 font-mono">{movie.release_year}</span>
              </div>
            )}
          </div>

          {/* Details Content */}
          <div className="flex flex-col justify-between flex-1 gap-4">
            <div>
              {/* Title & Match Score */}
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-white">
                  {movie.title}
                </h2>
                {matchPct !== null && (
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500 text-slate-950 flex items-center gap-1 shadow-md shadow-amber-950/60">
                    <Sparkles size={12} className="fill-current" />
                    {matchPct}% Match
                  </span>
                )}
              </div>

              {/* Meta tags (Year, Runtime, Rated) */}
              <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400 mb-3">
                {movie.release_year && (
                  <span className="flex items-center gap-1">
                    <Calendar size={13} className="text-slate-500" />
                    {movie.release_year}
                  </span>
                )}
                {movie.runtime && (
                  <span className="flex items-center gap-1">
                    <Clock size={13} className="text-slate-500" />
                    {movie.runtime}
                  </span>
                )}
                {movie.rated && (
                  <span className="px-1.5 py-0.5 text-[10px] font-semibold border border-slate-700 rounded bg-slate-800 text-slate-300">
                    {movie.rated}
                  </span>
                )}
                <RatingBadge rating={movie.rating_mean} count={movie.rating_count} size="md" />
                {movie.bayesian_rating > 0 && (
                  <span className="text-slate-400 text-xs font-mono">
                    Weighted Prior: <strong className="text-amber-400">{movie.bayesian_rating.toFixed(2)}</strong>
                  </span>
                )}
              </div>

              {/* Genres */}
              <div className="flex flex-wrap gap-1.5 mb-4">
                {movie.genres.map((g) => (
                  <span
                    key={g}
                    className="text-xs px-2.5 py-0.5 rounded-md bg-slate-800 border border-slate-700 text-slate-300 font-medium"
                  >
                    {g}
                  </span>
                ))}
              </div>

              {/* Overview / Synopsis */}
              <div className="mb-4">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                  Plot Synopsis
                </h4>
                <p className="text-sm text-slate-300 leading-relaxed">
                  {movie.overview || 'No synopsis available for this title.'}
                </p>
              </div>

              {/* Director & Cast */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-slate-400">
                {movie.director && (
                  <div className="flex items-center gap-2">
                    <User size={13} className="text-amber-400 shrink-0" />
                    <span>
                      <strong className="text-slate-300">Director:</strong> {movie.director}
                    </span>
                  </div>
                )}
                {movie.actors && (
                  <div className="flex items-center gap-2">
                    <Users size={13} className="text-amber-400 shrink-0" />
                    <span className="truncate">
                      <strong className="text-slate-300">Starring:</strong> {movie.actors}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Actions Bar */}
            <div className="flex items-center gap-3 pt-3 border-t border-slate-800">
              <button
                onClick={() => onToggleBookmark(movie)}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition ${
                  isBookmarked
                    ? 'bg-amber-500 text-slate-950 hover:bg-amber-400'
                    : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700'
                }`}
              >
                <Bookmark size={14} className={isBookmarked ? 'fill-current' : ''} />
                {isBookmarked ? 'In Watchlist' : 'Add to Watchlist'}
              </button>

              {movie.imdb_code && (
                <a
                  href={`https://www.imdb.com/title/${movie.imdb_code}/`}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white bg-slate-950/60 border border-slate-800 hover:border-slate-700 transition"
                >
                  <ExternalLink size={13} />
                  IMDb Reference
                </a>
              )}
            </div>
          </div>
        </div>

        {/* Explainability Section: Why CineSenseAI Recommends This */}
        {explanation && (
          <div className="p-6 md:p-8 bg-slate-950/50 border-b border-slate-800">
            <div className="flex items-center gap-2 mb-3">
              <Cpu size={16} className="text-amber-400" />
              <h3 className="text-sm font-semibold uppercase tracking-wider text-amber-400">
                Why CineSenseAI Recommends This Movie
              </h3>
            </div>

            <p className="text-sm text-slate-300 mb-4 bg-slate-900/80 p-3 rounded-lg border border-slate-800/80">
              "{explanation.summary}"
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Evidence Pills */}
              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Algorithmic Matching Factors
                </h4>
                <div className="space-y-1.5">
                  {explanation.reasons.map((reason, i) => (
                    <div
                      key={i}
                      className="flex items-center gap-2 text-xs text-slate-300 bg-slate-900/60 px-3 py-2 rounded-lg border border-slate-800"
                    >
                      <CheckCircle2 size={13} className="text-emerald-400 shrink-0" />
                      <span>{reason}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Similarity Breakdown Meters */}
              <div className="space-y-3 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Mathematical Similarity Scores
                </h4>

                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400">Content TF-IDF Cosine Similarity</span>
                    <span className="font-mono text-amber-400 font-semibold">
                      {explanation.content_similarity_pct}%
                    </span>
                  </div>
                  <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-amber-500 rounded-full transition-all duration-500"
                      style={{ width: `${explanation.content_similarity_pct}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400">Collaborative Viewer Alignment</span>
                    <span className="font-mono text-sky-400 font-semibold">
                      {explanation.collaborative_affinity_pct}%
                    </span>
                  </div>
                  <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-sky-500 rounded-full transition-all duration-500"
                      style={{ width: `${Math.max(5, explanation.collaborative_affinity_pct)}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* More Like This (Live Model Inference) */}
        <div className="p-6 md:p-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-semibold text-white">
              More Like This
            </h3>
            <span className="text-xs text-slate-500">
              Live recommendations from CineSenseAI Model
            </span>
          </div>

          {loadingSimilar ? (
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="aspect-[2/3] rounded-lg bg-slate-800/60 animate-pulse" />
              ))}
            </div>
          ) : similarMovies.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
              {similarMovies.map((simMovie) => (
                <div
                  key={simMovie.movieId}
                  onClick={() => onSelectMovie(simMovie)}
                  className="group cursor-pointer flex flex-col bg-slate-950/60 rounded-lg overflow-hidden border border-slate-800 hover:border-amber-500/40 transition hover:-translate-y-0.5"
                >
                  <div className="aspect-[2/3] bg-slate-950 relative overflow-hidden flex items-center justify-center">
                    {simMovie.poster_url ? (
                      <img
                        src={simMovie.poster_url}
                        alt={simMovie.title}
                        loading="lazy"
                        className="w-full h-full object-cover group-hover:scale-105 transition"
                      />
                    ) : (
                      <div className="p-2 text-center text-[10px] text-slate-400">
                        {simMovie.title}
                      </div>
                    )}
                  </div>
                  <div className="p-2">
                    <h5 className="text-xs font-medium text-slate-200 line-clamp-1 group-hover:text-amber-400">
                      {simMovie.title}
                    </h5>
                    <div className="flex justify-between items-center mt-1">
                      <span className="text-[10px] text-slate-500">{simMovie.release_year}</span>
                      <RatingBadge rating={simMovie.rating_mean} size="sm" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500">No additional similar movies found.</p>
          )}
        </div>
      </div>
    </div>
  );
};
