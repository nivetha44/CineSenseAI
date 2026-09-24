import React from 'react';
import { Film, Sparkles, Search, Bookmark, type LucideIcon } from 'lucide-react';

interface EmptyStateProps {
  type?: 'recommendations' | 'search' | 'watchlist' | 'generic';
  title?: string;
  description?: string;
  actionText?: string;
  onAction?: () => void;
  icon?: LucideIcon;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  type = 'generic',
  title,
  description,
  actionText,
  onAction,
  icon: CustomIcon,
}) => {
  let defaultIcon = Film;
  let defaultTitle = 'No movies to display';
  let defaultDesc = 'Try adjusting your filters or explore other cinematic categories.';

  if (type === 'recommendations') {
    defaultIcon = Sparkles;
    defaultTitle = 'No recommendations generated yet.';
    defaultDesc =
      'Choose a few movies you love and CineSenseAI will analyze their narrative, genre, and audience patterns to build your personalized discovery profile.';
  } else if (type === 'search') {
    defaultIcon = Search;
    defaultTitle = 'No movies matched your search query.';
    defaultDesc =
      'We could not find any titles matching those exact keywords. Try searching for a director (e.g. Christopher Nolan), actor, or broader genre.';
  } else if (type === 'watchlist') {
    defaultIcon = Bookmark;
    defaultTitle = 'Your Watchlist is empty.';
    defaultDesc =
      'Save movies while exploring to build your personal queue and help CineSenseAI understand your long-term cinematic taste.';
  }

  const Icon = CustomIcon || defaultIcon;
  const finalTitle = title || defaultTitle;
  const finalDesc = description || defaultDesc;

  return (
    <div className="flex flex-col items-center justify-center p-8 md:p-12 text-center max-w-lg mx-auto bg-slate-900/40 border border-slate-800/80 rounded-2xl my-8">
      <div className="w-14 h-14 rounded-2xl bg-slate-800/80 border border-slate-700/80 flex items-center justify-center text-amber-400 mb-4 shadow-inner">
        <Icon size={26} />
      </div>
      <h3 className="text-base md:text-lg font-bold text-slate-100 mb-2">
        {finalTitle}
      </h3>
      <p className="text-xs md:text-sm text-slate-400 leading-relaxed mb-6">
        {finalDesc}
      </p>
      {actionText && onAction && (
        <button
          onClick={onAction}
          className="px-5 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold text-xs transition shadow-lg shadow-amber-500/10"
        >
          {actionText}
        </button>
      )}
    </div>
  );
};
