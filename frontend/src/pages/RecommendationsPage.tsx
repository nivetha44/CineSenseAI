import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Sliders,
  Check,
  Search,
  Plus,
  X,
  Film,
  Zap
} from 'lucide-react';
import type { Movie, RecommendationRequest } from '../types';
import { MovieCard } from '../components/MovieCard';
import { WeightSliders } from '../components/WeightSliders';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { EmptyState } from '../components/EmptyState';
import { api } from '../services/api';

interface RecommendationsPageProps {
  onSelectMovie: (movie: Movie) => void;
  watchlist: Movie[];
  onToggleBookmark: (movie: Movie) => void;
  onNavigateTab: (tab: string) => void;
}

export const RecommendationsPage: React.FC<RecommendationsPageProps> = ({
  onSelectMovie,
  watchlist,
  onToggleBookmark,
  onNavigateTab,
}) => {
  // Taste Profile State
  const [selectedGenres, setSelectedGenres] = useState<string[]>(['Sci-Fi', 'Drama', 'Thriller']);
  const [likedMovies, setLikedMovies] = useState<Movie[]>([]);
  const [allGenres, setAllGenres] = useState<string[]>([]);
  
  // Movie Search for Seed Picker
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Movie[]>([]);
  const [searching, setSearching] = useState(false);
  const [showSearchModal, setShowSearchModal] = useState(false);

  // Model Weights State
  const defaultWeights = {
    w_content: 0.55,
    w_rating: 0.25,
    w_popularity: 0.10,
    w_collab: 0.10,
  };
  const [weights, setWeights] = useState(defaultWeights);
  const [showSliders, setShowSliders] = useState(false);

  // Recommendations Results
  const [recommendations, setRecommendations] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(false);

  // Load genres on mount
  useEffect(() => {
    api.getGenres().then((genres) => setAllGenres(genres)).catch(() => {});
    
    // Seed initial liked movie if available (e.g. Inception or Shawshank)
    api.searchMovies({ q: 'Inception', limit: 1 }).then((res) => {
      if (res.items.length > 0) {
        setLikedMovies([res.items[0]]);
      }
    }).catch(() => {});
  }, []);

  // Fetch recommendations whenever profile or weights change
  useEffect(() => {
    if (selectedGenres.length === 0 && likedMovies.length === 0) return;

    setLoading(true);
    const req: RecommendationRequest = {
      liked_movie_ids: likedMovies.map((m) => m.movieId),
      preferred_genres: selectedGenres,
      top_k: 12,
      w_content: weights.w_content,
      w_rating: weights.w_rating,
      w_popularity: weights.w_popularity,
      w_collab: weights.w_collab,
    };

    api
      .getUserRecommendations(req)
      .then((res) => setRecommendations(res))
      .catch((err) => {
        console.error('Failed to fetch recommendations:', err);
        setRecommendations([]);
      })
      .finally(() => setLoading(false));
  }, [selectedGenres, likedMovies, weights]);

  // Handle movie search inside seed picker
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }
    const timer = setTimeout(() => {
      setSearching(true);
      api
        .searchMovies({ q: searchQuery, limit: 6 })
        .then((res) => setSearchResults(res.items))
        .catch(() => setSearchResults([]))
        .finally(() => setSearching(false));
    }, 250);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const toggleGenre = (genre: string) => {
    if (selectedGenres.includes(genre)) {
      setSelectedGenres(selectedGenres.filter((g) => g !== genre));
    } else {
      setSelectedGenres([...selectedGenres, genre]);
    }
  };

  const addLikedMovie = (movie: Movie) => {
    if (!likedMovies.some((m) => m.movieId === movie.movieId)) {
      setLikedMovies([...likedMovies, movie]);
    }
    setShowSearchModal(false);
    setSearchQuery('');
  };

  const removeLikedMovie = (movieId: number) => {
    setLikedMovies(likedMovies.filter((m) => m.movieId !== movieId));
  };

  const isBookmarked = (id: number) => watchlist.some((m) => m.movieId === id);

  return (
    <div className="space-y-8 pb-16">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30 mb-2">
            <Zap size={13} />
            <span>Interactive Neural-Vector Preference Profiling</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            Recommended For You
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            Personalized movie recommendations synthesized from your chosen genres, favorite films,
            and mathematical similarity rankings.
          </p>
        </div>

        {/* Action Toggle for Scoring Weights */}
        <button
          onClick={() => setShowSliders(!showSliders)}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold border transition ${
            showSliders
              ? 'bg-amber-500 text-slate-950 border-amber-400'
              : 'bg-slate-900 text-slate-300 hover:text-white border-slate-700'
          }`}
        >
          <Sliders size={14} />
          <span>{showSliders ? 'Hide Scoring Weights' : 'Adjust ML Model Weights'}</span>
        </button>
      </div>

      {/* Model Weights Tuner Drawer */}
      {showSliders && (
        <WeightSliders
          weights={weights}
          onChange={setWeights}
          onReset={() => setWeights(defaultWeights)}
        />
      )}

      {/* Taste Profile Customization Panel */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 md:p-6 space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Sparkles size={16} className="text-amber-400" />
            Your Taste Profile Settings
          </h3>
          <span className="text-xs text-slate-500">
            Changes immediately update your live recommendations
          </span>
        </div>

        {/* 1. Genres Multi-select */}
        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Preferred Genres ({selectedGenres.length} selected)
          </label>
          <div className="flex flex-wrap gap-2">
            {(allGenres.length > 0 ? allGenres : ['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Drama', 'Fantasy', 'Horror', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller']).map((genre) => {
              const isSelected = selectedGenres.includes(genre);
              return (
                <button
                  key={genre}
                  onClick={() => toggleGenre(genre)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                    isSelected
                      ? 'bg-amber-500 text-slate-950 font-bold shadow-md shadow-amber-950/40'
                      : 'bg-slate-950/80 text-slate-400 hover:text-slate-200 border border-slate-800 hover:border-slate-700'
                  }`}
                >
                  {isSelected && <Check size={12} strokeWidth={3} />}
                  <span>{genre}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* 2. Liked Seed Movies */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Favorite Seed Movies ({likedMovies.length})
            </label>
            <button
              onClick={() => setShowSearchModal(true)}
              className="flex items-center gap-1 text-xs text-amber-400 hover:text-amber-300 font-semibold"
            >
              <Plus size={14} />
              <span>Add Favorite Movie</span>
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            {likedMovies.map((movie) => (
              <div
                key={movie.movieId}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-slate-200 text-xs shadow-sm"
              >
                <Film size={13} className="text-amber-400" />
                <span className="font-medium">{movie.title}</span>
                {movie.release_year && (
                  <span className="text-[10px] text-slate-500">({movie.release_year})</span>
                )}
                <button
                  onClick={() => removeLikedMovie(movie.movieId)}
                  className="text-slate-500 hover:text-rose-400 transition"
                  title="Remove seed movie"
                >
                  <X size={13} />
                </button>
              </div>
            ))}

            {likedMovies.length === 0 && (
              <button
                onClick={() => setShowSearchModal(true)}
                className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg border border-dashed border-slate-700 text-xs text-slate-400 hover:text-slate-200 hover:border-slate-600 transition"
              >
                <Plus size={13} />
                <span>Select a movie you love to seed recommendations...</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Seed Movie Picker Modal */}
      {showSearchModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in">
          <div className="relative w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Search size={16} className="text-amber-400" />
                Add Movie to Taste Profile
              </h3>
              <button
                onClick={() => setShowSearchModal(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X size={16} />
              </button>
            </div>

            <div className="relative">
              <Search size={16} className="absolute left-3.5 top-3 text-slate-500" />
              <input
                type="text"
                autoFocus
                placeholder="Type movie title (e.g. Interstellar, Fight Club, Toy Story)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500"
              />
            </div>

            {/* Results list */}
            <div className="max-h-64 overflow-y-auto space-y-1.5 pr-1">
              {searching ? (
                <div className="p-4 text-center text-xs text-slate-500">Searching catalog...</div>
              ) : searchResults.length > 0 ? (
                searchResults.map((m) => (
                  <div
                    key={m.movieId}
                    onClick={() => addLikedMovie(m)}
                    className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950/60 hover:bg-slate-800 border border-slate-800/80 cursor-pointer transition"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-10 rounded bg-slate-800 overflow-hidden shrink-0 flex items-center justify-center">
                        {m.poster_url ? (
                          <img src={m.poster_url} alt="" className="w-full h-full object-cover" />
                        ) : (
                          <Film size={14} className="text-slate-600" />
                        )}
                      </div>
                      <div>
                        <h4 className="text-xs font-semibold text-slate-200">{m.title}</h4>
                        <div className="text-[10px] text-slate-500">
                          {m.release_year} • {m.genres.slice(0, 2).join(', ')}
                        </div>
                      </div>
                    </div>
                    <button className="px-2.5 py-1 rounded-md text-[11px] font-semibold bg-amber-500/10 text-amber-400 hover:bg-amber-500 hover:text-slate-950 transition">
                      Select
                    </button>
                  </div>
                ))
              ) : searchQuery ? (
                <div className="p-4 text-center text-xs text-slate-500">No movies found matching "{searchQuery}"</div>
              ) : (
                <div className="p-4 text-center text-xs text-slate-500">Search above to pick a movie.</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Recommendations Results Section */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              <Sparkles size={18} className="text-amber-400" />
              Tailored Selection
            </h2>
            <p className="text-xs text-slate-400">
              Ranked by model score using your chosen taste weights
            </p>
          </div>

          <span className="text-xs text-slate-400 font-mono">
            {recommendations.length} Results
          </span>
        </div>

        {loading ? (
          <LoadingSkeleton count={12} />
        ) : recommendations.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {recommendations.map((movie) => (
              <MovieCard
                key={movie.movieId}
                movie={movie}
                onSelect={onSelectMovie}
                isBookmarked={isBookmarked(movie.movieId)}
                onToggleBookmark={onToggleBookmark}
                showMatchScore={true}
              />
            ))}
          </div>
        ) : (
          <EmptyState
            type="recommendations"
            actionText="Explore Popular Movies"
            onAction={() => onNavigateTab('explore')}
          />
        )}
      </section>
    </div>
  );
};
