import React, { useState, useEffect } from 'react';
import {
  Search,
  X,
  RotateCcw,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import type { Movie } from '../types';
import { MovieCard } from '../components/MovieCard';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { EmptyState } from '../components/EmptyState';
import { api } from '../services/api';

interface ExplorePageProps {
  onSelectMovie: (movie: Movie) => void;
  watchlist: Movie[];
  onToggleBookmark: (movie: Movie) => void;
  initialQuery?: string;
}

export const ExplorePage: React.FC<ExplorePageProps> = ({
  onSelectMovie,
  watchlist,
  onToggleBookmark,
  initialQuery = '',
}) => {
  const [query, setQuery] = useState(initialQuery);
  const [selectedGenre, setSelectedGenre] = useState<string>('All');
  const [minRating, setMinRating] = useState<number>(0.0);
  const [minYear, setMinYear] = useState<number>(1930);
  const [maxYear, setMaxYear] = useState<number>(2024);
  const [sortBy, setSortBy] = useState<string>('relevance');
  const [genresList, setGenresList] = useState<string[]>([]);

  // Pagination state
  const [offset, setOffset] = useState<number>(0);
  const limit = 24;
  const [movies, setMovies] = useState<Movie[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [loading, setLoading] = useState(true);

  // Load genres
  useEffect(() => {
    api.getGenres().then((genres) => setGenresList(genres)).catch(() => {});
  }, []);

  // Fetch movies with filters
  useEffect(() => {
    setLoading(true);
    const timer = setTimeout(() => {
      api
        .searchMovies({
          q: query,
          genre: selectedGenre !== 'All' ? selectedGenre : undefined,
          minRating: minRating > 0 ? minRating : undefined,
          minYear: minYear > 1930 ? minYear : undefined,
          maxYear: maxYear < 2024 ? maxYear : undefined,
          sortBy,
          limit,
          offset,
        })
        .then((res) => {
          setMovies(res.items);
          setTotalCount(res.total);
        })
        .catch((err) => {
          console.error('Error fetching catalog:', err);
          setMovies([]);
          setTotalCount(0);
        })
        .finally(() => setLoading(false));
    }, 200);

    return () => clearTimeout(timer);
  }, [query, selectedGenre, minRating, minYear, maxYear, sortBy, offset]);

  // Reset pagination when search or filters change
  const handleQueryChange = (val: string) => {
    setQuery(val);
    setOffset(0);
  };

  const handleGenreChange = (g: string) => {
    setSelectedGenre(g);
    setOffset(0);
  };

  const handleSortChange = (s: string) => {
    setSortBy(s);
    setOffset(0);
  };

  const handleResetFilters = () => {
    setQuery('');
    setSelectedGenre('All');
    setMinRating(0.0);
    setMinYear(1930);
    setMaxYear(2024);
    setSortBy('relevance');
    setOffset(0);
  };

  const currentPage = Math.floor(offset / limit) + 1;
  const totalPages = Math.ceil(totalCount / limit) || 1;
  const isBookmarked = (id: number) => watchlist.some((m) => m.movieId === id);

  return (
    <div className="space-y-6 pb-16">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Explore Movie Catalog
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Search across 9,742 verified movies, filter by genre, ratings, release era, and popularity.
        </p>
      </div>

      {/* Search & Filter Toolbar */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 md:p-5 space-y-4">
        {/* Search Bar Input */}
        <div className="relative">
          <Search size={18} className="absolute left-3.5 top-3.5 text-slate-500" />
          <input
            type="text"
            placeholder="Search by title, director, actors, or themes..."
            value={query}
            onChange={(e) => handleQueryChange(e.target.value)}
            className="w-full pl-11 pr-10 py-3 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 transition shadow-inner"
          />
          {query && (
            <button
              onClick={() => handleQueryChange('')}
              className="absolute right-3.5 top-3.5 text-slate-500 hover:text-white"
            >
              <X size={16} />
            </button>
          )}
        </div>

        {/* Filter Controls Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          {/* Genre Dropdown */}
          <div className="space-y-1">
            <label className="text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
              Genre
            </label>
            <select
              value={selectedGenre}
              onChange={(e) => handleGenreChange(e.target.value)}
              className="w-full py-2 px-3 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-amber-500"
            >
              <option value="All">All Genres ({totalCount})</option>
              {genresList.map((g) => (
                <option key={g} value={g}>
                  {g}
                </option>
              ))}
            </select>
          </div>

          {/* Min Rating Slider */}
          <div className="space-y-1">
            <div className="flex justify-between items-center text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
              <span>Min Rating</span>
              <span className="text-amber-400 font-mono">{minRating > 0 ? `${minRating.toFixed(1)}★` : 'Any'}</span>
            </div>
            <input
              type="range"
              min="0"
              max="4.5"
              step="0.5"
              value={minRating}
              onChange={(e) => {
                setMinRating(parseFloat(e.target.value));
                setOffset(0);
              }}
              className="w-full accent-amber-500 cursor-pointer h-8"
            />
          </div>

          {/* Sort By */}
          <div className="space-y-1">
            <label className="text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
              Sort By
            </label>
            <select
              value={sortBy}
              onChange={(e) => handleSortChange(e.target.value)}
              className="w-full py-2 px-3 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-amber-500"
            >
              <option value="relevance">Relevance (Bayesian Prior)</option>
              <option value="rating">Highest Average Rating</option>
              <option value="popularity">Most Reviewed (Popularity)</option>
              <option value="year">Newest Release Year</option>
            </select>
          </div>

          {/* Reset Filters */}
          <div className="flex items-end">
            <button
              onClick={handleResetFilters}
              className="w-full py-2 px-3 rounded-lg bg-slate-950 border border-slate-800 text-slate-400 hover:text-amber-400 hover:border-slate-700 flex items-center justify-center gap-1.5 transition"
            >
              <RotateCcw size={13} />
              <span>Reset Filters</span>
            </button>
          </div>
        </div>
      </div>

      {/* Catalog Results Header */}
      <div className="flex items-center justify-between text-xs text-slate-400 border-b border-slate-800/80 pb-3">
        <span>
          Showing <strong className="text-white">{movies.length > 0 ? offset + 1 : 0}</strong> -{' '}
          <strong className="text-white">{Math.min(offset + limit, totalCount)}</strong> of{' '}
          <strong className="text-white">{totalCount.toLocaleString()}</strong> movies
        </span>

        {/* Top Pagination Buttons */}
        <div className="flex items-center gap-2">
          <button
            disabled={offset === 0}
            onClick={() => setOffset(Math.max(0, offset - limit))}
            className="p-1 rounded bg-slate-900 border border-slate-800 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800 text-slate-300"
          >
            <ChevronLeft size={16} />
          </button>
          <span className="font-mono text-[11px]">
            Page {currentPage} / {totalPages}
          </span>
          <button
            disabled={offset + limit >= totalCount}
            onClick={() => setOffset(offset + limit)}
            className="p-1 rounded bg-slate-900 border border-slate-800 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800 text-slate-300"
          >
            <ChevronRight size={16} />
          </button>
        </div>
      </div>

      {/* Movies Grid */}
      {loading ? (
        <LoadingSkeleton count={limit} />
      ) : movies.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {movies.map((movie) => (
            <MovieCard
              key={movie.movieId}
              movie={movie}
              onSelect={onSelectMovie}
              isBookmarked={isBookmarked(movie.movieId)}
              onToggleBookmark={onToggleBookmark}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          type="search"
          actionText="Clear All Filters"
          onAction={handleResetFilters}
        />
      )}

      {/* Bottom Pagination */}
      {totalCount > limit && (
        <div className="flex items-center justify-center gap-3 pt-6 border-t border-slate-800/80">
          <button
            disabled={offset === 0}
            onClick={() => {
              setOffset(Math.max(0, offset - limit));
              window.scrollTo({ top: 0, behavior: 'smooth' });
            }}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition"
          >
            <ChevronLeft size={14} />
            <span>Previous</span>
          </button>

          <span className="text-xs text-slate-400 font-mono px-3">
            Page {currentPage} of {totalPages}
          </span>

          <button
            disabled={offset + limit >= totalCount}
            onClick={() => {
              setOffset(offset + limit);
              window.scrollTo({ top: 0, behavior: 'smooth' });
            }}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition"
          >
            <span>Next</span>
            <ChevronRight size={14} />
          </button>
        </div>
      )}
    </div>
  );
};
