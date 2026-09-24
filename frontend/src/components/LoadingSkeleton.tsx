import React from 'react';

interface LoadingSkeletonProps {
  count?: number;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({ count = 8 }) => {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
      {[...Array(count)].map((_, i) => (
        <div
          key={i}
          className="flex flex-col bg-slate-900/40 rounded-xl overflow-hidden border border-slate-800 animate-pulse"
        >
          <div className="aspect-[2/3] w-full bg-slate-800/60" />
          <div className="p-3 space-y-2">
            <div className="h-3.5 bg-slate-800 rounded w-4/5" />
            <div className="flex gap-1">
              <div className="h-3 bg-slate-800/80 rounded w-1/3" />
              <div className="h-3 bg-slate-800/80 rounded w-1/4" />
            </div>
            <div className="h-3 bg-slate-800/60 rounded w-1/2 pt-1" />
          </div>
        </div>
      ))}
    </div>
  );
};
