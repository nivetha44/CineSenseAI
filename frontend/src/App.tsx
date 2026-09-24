import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { MovieDetailsModal } from './components/MovieDetailsModal';
import { DiscoverPage } from './pages/DiscoverPage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { ExplorePage } from './pages/ExplorePage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { AboutPage } from './pages/AboutPage';
import { WatchlistPage } from './pages/WatchlistPage';
import type { Movie } from './types';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { api } from './services/api';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('discover');
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);
  const [watchlist, setWatchlist] = useState<Movie[]>(() => {
    try {
      const saved = localStorage.getItem('cinesense_watchlist');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [backendHealthy, setBackendHealthy] = useState<boolean>(true);

  // Check backend health on mount
  useEffect(() => {
    api
      .getHealth()
      .then((data) => {
        setBackendHealthy(data.engine_ready);
      })
      .catch((err) => {
        console.warn('Backend not responding yet:', err);
        setBackendHealthy(false);
      });
  }, []);

  // Save watchlist to localStorage
  useEffect(() => {
    try {
      localStorage.setItem('cinesense_watchlist', JSON.stringify(watchlist));
    } catch (err) {
      console.error('Failed to save watchlist to localStorage:', err);
    }
  }, [watchlist]);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 2800);
  };

  const handleToggleBookmark = (movie: Movie) => {
    const exists = watchlist.some((m) => m.movieId === movie.movieId);
    if (exists) {
      setWatchlist(watchlist.filter((m) => m.movieId !== movie.movieId));
      showToast(`Removed "${movie.title}" from My List`);
    } else {
      setWatchlist([...watchlist, movie]);
      showToast(`Saved "${movie.title}" to My List`);
    }
  };

  const handleClearWatchlist = () => {
    if (window.confirm('Are you sure you want to clear your saved watchlist?')) {
      setWatchlist([]);
      showToast('Watchlist cleared');
    }
  };

  const isBookmarked = (movieId: number) => watchlist.some((m) => m.movieId === movieId);

  return (
    <div className="min-h-screen bg-[#0B0F17] text-slate-100 flex flex-col font-sans">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-slate-900 border border-amber-500/40 text-amber-300 px-4 py-2.5 rounded-xl shadow-2xl text-xs font-semibold flex items-center gap-2 animate-in slide-in-from-bottom-4 duration-200">
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Navigation Bar */}
      <Navbar
        currentTab={currentTab}
        onTabChange={setCurrentTab}
        watchlistCount={watchlist.length}
        onOpenSearch={() => setCurrentTab('explore')}
      />

      {/* Backend connection warning if API is down */}
      {!backendHealthy && (
        <div className="bg-amber-500/10 border-b border-amber-500/20 text-amber-300 px-4 py-2 text-xs flex items-center justify-between">
          <div className="max-w-7xl mx-auto w-full flex items-center justify-between">
            <span className="flex items-center gap-2">
              <AlertCircle size={14} className="text-amber-400" />
              <span>Connecting to CineSenseAI Recommendation Engine backend server...</span>
            </span>
            <button
              onClick={() => {
                api
                  .getHealth()
                  .then(() => setBackendHealthy(true))
                  .catch(() => {});
              }}
              className="flex items-center gap-1 text-[11px] underline hover:text-white"
            >
              <RefreshCw size={11} />
              Retry Connection
            </button>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        {currentTab === 'discover' && (
          <DiscoverPage
            onSelectMovie={setSelectedMovie}
            onNavigateTab={setCurrentTab}
            watchlist={watchlist}
            onToggleBookmark={handleToggleBookmark}
          />
        )}

        {currentTab === 'recommendations' && (
          <RecommendationsPage
            onSelectMovie={setSelectedMovie}
            watchlist={watchlist}
            onToggleBookmark={handleToggleBookmark}
            onNavigateTab={setCurrentTab}
          />
        )}

        {currentTab === 'explore' && (
          <ExplorePage
            onSelectMovie={setSelectedMovie}
            watchlist={watchlist}
            onToggleBookmark={handleToggleBookmark}
          />
        )}

        {currentTab === 'analytics' && <AnalyticsPage />}

        {currentTab === 'about' && <AboutPage />}

        {currentTab === 'watchlist' && (
          <WatchlistPage
            watchlist={watchlist}
            onSelectMovie={setSelectedMovie}
            onToggleBookmark={handleToggleBookmark}
            onClearWatchlist={handleClearWatchlist}
            onNavigateTab={setCurrentTab}
          />
        )}
      </main>

      {/* Movie Details Modal */}
      {selectedMovie && (
        <MovieDetailsModal
          movie={selectedMovie}
          onClose={() => setSelectedMovie(null)}
          onSelectMovie={(movie) => setSelectedMovie(movie)}
          isBookmarked={isBookmarked(selectedMovie.movieId)}
          onToggleBookmark={handleToggleBookmark}
        />
      )}

      {/* Footer */}
      <Footer onTabChange={setCurrentTab} />
    </div>
  );
};

export default App;
