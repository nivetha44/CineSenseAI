import React, { useEffect, useState } from 'react';
import {
  Sparkles,
  Film,
  TrendingUp,
  Award,
  Gem,
  ArrowRight,
  Database,
  ChevronRight
} from 'lucide-react';
import type { Movie } from '../types';
import { MovieCard } from '../components/MovieCard';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { api } from '../services/api';

interface DiscoverPageProps {
  onSelectMovie: (movie: Movie) => void;
  onNavigateTab: (tab: string) => void;
  watchlist: Movie[];
  onToggleBookmark: (movie: Movie) => void;
}

export const DiscoverPage: React.FC<DiscoverPageProps> = ({
  onSelectMovie,
  onNavigateTab,
  watchlist,
  onToggleBookmark,
}) => {
  const [popular, setPopular] = useState<Movie[]>([]);
  const [highlyRated, setHighlyRated] = useState<Movie[]>([]);
  const [hiddenGems, setHiddenGems] = useState<Movie[]>([]);
  const [genreMovies, setGenreMovies] = useState<Movie[]>([]);
  const [selectedGenre, setSelectedGenre] = useState<string>('Sci-Fi');
  const [loading, setLoading] = useState(true);

  const curatedGenres = ['Sci-Fi', 'Action', 'Drama', 'Crime', 'Animation', 'Thriller', 'Comedy'];

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.getCurated('popular', undefined, 6),
      api.getCurated('highly_rated', undefined, 6),
      api.getCurated('hidden_gems', undefined, 6),
      api.getCurated('genre', selectedGenre, 6),
    ])
      .then(([popData, highData, gemsData, gData]) => {
        setPopular(popData);
        setHighlyRated(highData);
        setHiddenGems(gemsData);
        setGenreMovies(gData);
      })
      .catch((err) => console.error('Error loading curated rows:', err))
      .finally(() => setLoading(false));
  }, [selectedGenre]);

  const isBookmarked = (id: number) => watchlist.some((m) => m.movieId === id);

  return (
    <div className="space-y-12 pb-16">
      {/* Hero Banner */}
      <section className="relative rounded-3xl overflow-hidden border border-slate-800 bg-gradient-to-br from-slate-900 via-[#0B0F17] to-slate-950 p-6 sm:p-10 md:p-14 shadow-2xl">
        <div className="absolute top-0 right-0 -mr-20 -mt-20 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/3 -mb-20 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 border border-amber-500/30 text-amber-400">
            <Sparkles size={13} />
            <span>AI-Driven Explainable Recommender</span>
          </div>

          <h1 className="text-3xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-white leading-tight">
            Discover movies that feel <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-amber-200">made for you.</span>
          </h1>

          <p className="text-sm sm:text-base text-slate-300 leading-relaxed max-w-2xl font-normal">
            Data-driven recommendations powered by machine learning and movie intelligence.
            CineSenseAI analyzes plot semantics, genre matrices, and verified audience rating patterns
            to deliver relevant, explainable recommendations.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-wrap items-center gap-3 pt-3">
            <button
              onClick={() => onNavigateTab('recommendations')}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-sm transition shadow-lg shadow-amber-500/20 hover:scale-[1.02]"
            >
              <Sparkles size={16} className="fill-current" />
              <span>Get Recommendations</span>
              <ArrowRight size={16} />
            </button>

            <button
              onClick={() => onNavigateTab('explore')}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-slate-200 border border-slate-700/80 font-medium text-sm transition"
            >
              <Film size={16} className="text-slate-400" />
              <span>Explore Movies</span>
            </button>
          </div>

          {/* Key Facts Tagline */}
          <div className="pt-6 border-t border-slate-800/80 flex flex-wrap items-center gap-4 text-xs text-slate-400">
            <span className="flex items-center gap-1.5 font-mono">
              <Database size={13} className="text-amber-400" />
              9,742 Verified Titles
            </span>
            <span className="text-slate-700">•</span>
            <span className="font-mono">100,836 User Ratings</span>
            <span className="text-slate-700">•</span>
            <span className="font-mono">TF-IDF & Item-Item Collaborative Engine</span>
          </div>
        </div>
      </section>

      {/* Row 1: Popular Right Now */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400">
              <TrendingUp size={16} />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white tracking-tight">
                Popular Right Now
              </h2>
              <p className="text-xs text-slate-400">
                Mainstream cinema with the highest overall audience review volume
              </p>
            </div>
          </div>

          <button
            onClick={() => onNavigateTab('explore')}
            className="flex items-center gap-1 text-xs text-slate-400 hover:text-amber-400 font-medium transition"
          >
            <span>View All</span>
            <ChevronRight size={14} />
          </button>
        </div>

        {loading ? (
          <LoadingSkeleton count={6} />
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
            {popular.map((movie) => (
              <MovieCard
                key={movie.movieId}
                movie={movie}
                onSelect={onSelectMovie}
                isBookmarked={isBookmarked(movie.movieId)}
                onToggleBookmark={onToggleBookmark}
              />
            ))}
          </div>
        )}
      </section>

      {/* Row 2: Critically Acclaimed (Bayesian Prior) */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Award size={16} />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white tracking-tight">
                Critically Acclaimed
              </h2>
              <p className="text-xs text-slate-400">
                Highest Bayesian weighted rating (IMDb formula with m=10 threshold)
              </p>
            </div>
          </div>

          <button
            onClick={() => onNavigateTab('explore')}
            className="flex items-center gap-1 text-xs text-slate-400 hover:text-amber-400 font-medium transition"
          >
            <span>View All</span>
            <ChevronRight size={14} />
          </button>
        </div>

        {loading ? (
          <LoadingSkeleton count={6} />
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
            {highlyRated.map((movie) => (
              <MovieCard
                key={movie.movieId}
                movie={movie}
                onSelect={onSelectMovie}
                isBookmarked={isBookmarked(movie.movieId)}
                onToggleBookmark={onToggleBookmark}
              />
            ))}
          </div>
        )}
      </section>

      {/* Row 3: Hidden Gems */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <Gem size={16} />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white tracking-tight">
                Hidden Gems
              </h2>
              <p className="text-xs text-slate-400">
                Exceptional films (≥4.0 avg rating) that escape mainstream overexposure
              </p>
            </div>
          </div>

          <button
            onClick={() => onNavigateTab('explore')}
            className="flex items-center gap-1 text-xs text-slate-400 hover:text-amber-400 font-medium transition"
          >
            <span>View All</span>
            <ChevronRight size={14} />
          </button>
        </div>

        {loading ? (
          <LoadingSkeleton count={6} />
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
            {hiddenGems.map((movie) => (
              <MovieCard
                key={movie.movieId}
                movie={movie}
                onSelect={onSelectMovie}
                isBookmarked={isBookmarked(movie.movieId)}
                onToggleBookmark={onToggleBookmark}
              />
            ))}
          </div>
        )}
      </section>

      {/* Row 4: Explore by Genre Tabs */}
      <section className="space-y-4 pt-4 border-t border-slate-800/80">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight">
              Explore by Genre
            </h2>
            <p className="text-xs text-slate-400">
              Browse top-tier selections curated across core cinematic genres
            </p>
          </div>

          {/* Genre selector pills */}
          <div className="flex flex-wrap gap-1.5">
            {curatedGenres.map((g) => (
              <button
                key={g}
                onClick={() => setSelectedGenre(g)}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition ${
                  selectedGenre === g
                    ? 'bg-amber-500 text-slate-950 font-bold'
                    : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
                }`}
              >
                {g}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <LoadingSkeleton count={6} />
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
            {genreMovies.map((movie) => (
              <MovieCard
                key={movie.movieId}
                movie={movie}
                onSelect={onSelectMovie}
                isBookmarked={isBookmarked(movie.movieId)}
                onToggleBookmark={onToggleBookmark}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
};
