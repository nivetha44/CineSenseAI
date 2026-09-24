import React from 'react';
import { Film, Code2, Database, Layers, Sparkles } from 'lucide-react';

interface FooterProps {
  onTabChange: (tab: string) => void;
}

export const Footer: React.FC<FooterProps> = ({ onTabChange }) => {
  return (
    <footer className="w-full border-t border-slate-800/80 bg-slate-950/90 text-slate-400 py-12 px-4 sm:px-6 lg:px-8 mt-20">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
        {/* Brand & Purpose */}
        <div className="space-y-3 md:col-span-2">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-amber-500 flex items-center justify-center text-slate-950">
              <Film size={16} />
            </div>
            <span className="text-base font-bold text-white tracking-tight">
              CineSense<span className="text-amber-400">AI</span>
            </span>
          </div>
          <p className="text-xs text-slate-400 max-w-sm leading-relaxed">
            "Discover your next favorite movie."
            <br />
            An AI-powered, explainable recommendation engine combining TF-IDF content similarity,
            item-item collaborative filtering, and Bayesian rating models on verified MovieLens data.
          </p>
          <div className="flex items-center gap-4 pt-2">
            <a
              href="https://github.com/nivetha44/CineSenseAI"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-amber-400 transition"
            >
              <Code2 size={14} />
              GitHub Repository
            </a>
            <span className="text-slate-700">•</span>
            <span className="inline-flex items-center gap-1.5 text-xs text-slate-500">
              <Database size={13} />
              GroupLens MovieLens 100k
            </span>
          </div>
        </div>

        {/* Quick Links */}
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-300 mb-3">
            Exploration
          </h4>
          <ul className="space-y-2 text-xs">
            <li>
              <button
                onClick={() => onTabChange('discover')}
                className="hover:text-amber-400 transition"
              >
                Curated Discoveries
              </button>
            </li>
            <li>
              <button
                onClick={() => onTabChange('recommendations')}
                className="hover:text-amber-400 transition"
              >
                Personalized Recommendations
              </button>
            </li>
            <li>
              <button
                onClick={() => onTabChange('explore')}
                className="hover:text-amber-400 transition"
              >
                Full Catalog & Search
              </button>
            </li>
            <li>
              <button
                onClick={() => onTabChange('watchlist')}
                className="hover:text-amber-400 transition"
              >
                My Saved Watchlist
              </button>
            </li>
          </ul>
        </div>

        {/* Technical Architecture */}
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-300 mb-3">
            Architecture
          </h4>
          <ul className="space-y-2 text-xs">
            <li>
              <button
                onClick={() => onTabChange('analytics')}
                className="hover:text-amber-400 transition"
              >
                Data Science EDA & Insights
              </button>
            </li>
            <li>
              <button
                onClick={() => onTabChange('about')}
                className="hover:text-amber-400 transition"
              >
                Methodology & Evaluation
              </button>
            </li>
            <li className="flex items-center gap-1.5 text-slate-500">
              <Layers size={13} />
              FastAPI + React + Vite
            </li>
            <li className="flex items-center gap-1.5 text-slate-500">
              <Sparkles size={13} />
              Scikit-Learn TF-IDF
            </li>
          </ul>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="max-w-7xl mx-auto pt-6 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-600 gap-2">
        <p>© {new Date().getFullYear()} CineSenseAI. Developed for Portfolio & Academic Evaluation.</p>
        <p className="flex items-center gap-2">
          <span>Clean Pipeline</span>
          <span>•</span>
          <span>Explainable ML</span>
          <span>•</span>
          <span>Zero Fabricated Statistics</span>
        </p>
      </div>
    </footer>
  );
};
