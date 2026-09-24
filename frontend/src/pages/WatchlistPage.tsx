import { Bookmark, Sparkles, Trash2 } from 'lucide-react';
import type { Movie } from '../types';
import { MovieCard } from '../components/MovieCard';
import { EmptyState } from '../components/EmptyState';

interface WatchlistPageProps {
  watchlist: Movie[];
  onSelectMovie: (movie: Movie) => void;
  onToggleBookmark: (movie: Movie) => void;
  onClearWatchlist: () => void;
  onNavigateTab: (tab: string) => void;
}

export const WatchlistPage: React.FC<WatchlistPageProps> = ({
  watchlist,
  onSelectMovie,
  onToggleBookmark,
  onClearWatchlist,
  onNavigateTab,
}) => {
  return (
    <div className="space-y-6 pb-20">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <Bookmark size={24} className="text-amber-400 fill-amber-400" />
            My Saved Watchlist
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            {watchlist.length > 0
              ? `You have saved ${watchlist.length} movie${watchlist.length > 1 ? 's' : ''} to your personal watch queue.`
              : 'Save titles as you browse to create your personal queue.'}
          </p>
        </div>

        {watchlist.length > 0 && (
          <div className="flex items-center gap-2">
            <button
              onClick={() => onNavigateTab('recommendations')}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold text-xs transition shadow-md shadow-amber-500/10"
            >
              <Sparkles size={13} className="fill-current" />
              <span>Get Recommendations From Watchlist</span>
            </button>

            <button
              onClick={onClearWatchlist}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-rose-500/40 text-xs text-slate-400 hover:text-rose-400 transition"
              title="Clear entire watchlist"
            >
              <Trash2 size={13} />
              <span>Clear</span>
            </button>
          </div>
        )}
      </div>

      {/* Watchlist Grid */}
      {watchlist.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {watchlist.map((movie) => (
            <MovieCard
              key={movie.movieId}
              movie={movie}
              onSelect={onSelectMovie}
              isBookmarked={true}
              onToggleBookmark={onToggleBookmark}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          type="watchlist"
          actionText="Browse Popular Movies"
          onAction={() => onNavigateTab('discover')}
        />
      )}
    </div>
  );
};
