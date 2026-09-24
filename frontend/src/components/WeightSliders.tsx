import React from 'react';
import { Sliders, RotateCcw, HelpCircle } from 'lucide-react';

interface WeightSlidersProps {
  weights: {
    w_content: number;
    w_rating: number;
    w_popularity: number;
    w_collab: number;
  };
  onChange: (weights: {
    w_content: number;
    w_rating: number;
    w_popularity: number;
    w_collab: number;
  }) => void;
  onReset: () => void;
}

export const WeightSliders: React.FC<WeightSlidersProps> = ({
  weights,
  onChange,
  onReset,
}) => {
  const handleChange = (key: keyof typeof weights, value: number) => {
    onChange({
      ...weights,
      [key]: value,
    });
  };

  const total = Number((weights.w_content + weights.w_rating + weights.w_popularity + weights.w_collab).toFixed(2));

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 md:p-5 shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Sliders size={16} className="text-amber-400" />
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Model Ranking Formula Tuning
          </h4>
        </div>
        <button
          onClick={onReset}
          className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-amber-400 transition"
          title="Reset to default baseline weights"
        >
          <RotateCcw size={12} />
          Reset Defaults
        </button>
      </div>

      <p className="text-[11px] text-slate-400 mb-4 leading-relaxed">
        Adjust how CineSenseAI balances feature similarity, Bayesian ratings, popularity bias, and collaborative taste:
      </p>

      {/* Sliders Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
        {/* Content Similarity */}
        <div className="space-y-1.5 bg-slate-950/50 p-2.5 rounded-lg border border-slate-800/80">
          <div className="flex justify-between items-center text-slate-300">
            <span className="font-medium text-amber-400">Content Similarity</span>
            <span className="font-mono font-semibold">{(weights.w_content * 100).toFixed(0)}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={weights.w_content}
            onChange={(e) => handleChange('w_content', parseFloat(e.target.value))}
            className="w-full accent-amber-500 cursor-pointer"
          />
          <div className="text-[10px] text-slate-500">TF-IDF metadata match (genres, plot, cast)</div>
        </div>

        {/* Bayesian Prior Rating */}
        <div className="space-y-1.5 bg-slate-950/50 p-2.5 rounded-lg border border-slate-800/80">
          <div className="flex justify-between items-center text-slate-300">
            <span className="font-medium text-emerald-400">Bayesian Rating</span>
            <span className="font-mono font-semibold">{(weights.w_rating * 100).toFixed(0)}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={weights.w_rating}
            onChange={(e) => handleChange('w_rating', parseFloat(e.target.value))}
            className="w-full accent-emerald-500 cursor-pointer"
          />
          <div className="text-[10px] text-slate-500">Weighted audience score prior ($m=10$)</div>
        </div>

        {/* Popularity Bias */}
        <div className="space-y-1.5 bg-slate-950/50 p-2.5 rounded-lg border border-slate-800/80">
          <div className="flex justify-between items-center text-slate-300">
            <span className="font-medium text-purple-400">Popularity Volume</span>
            <span className="font-mono font-semibold">{(weights.w_popularity * 100).toFixed(0)}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={weights.w_popularity}
            onChange={(e) => handleChange('w_popularity', parseFloat(e.target.value))}
            className="w-full accent-purple-500 cursor-pointer"
          />
          <div className="text-[10px] text-slate-500">Log-normalized rating count</div>
        </div>

        {/* Collaborative Taste */}
        <div className="space-y-1.5 bg-slate-950/50 p-2.5 rounded-lg border border-slate-800/80">
          <div className="flex justify-between items-center text-slate-300">
            <span className="font-medium text-sky-400">Collaborative Affinity</span>
            <span className="font-mono font-semibold">{(weights.w_collab * 100).toFixed(0)}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={weights.w_collab}
            onChange={(e) => handleChange('w_collab', parseFloat(e.target.value))}
            className="w-full accent-sky-500 cursor-pointer"
          />
          <div className="text-[10px] text-slate-500">Item-item user co-rating correlation</div>
        </div>
      </div>

      {/* Formula Readout */}
      <div className="mt-3 pt-2 border-t border-slate-800/60 flex flex-wrap items-center justify-between text-[11px] text-slate-400">
        <div className="flex items-center gap-1 font-mono text-slate-300">
          <span>Score = </span>
          <span className="text-amber-400">{weights.w_content}·S_c</span>
          <span> + </span>
          <span className="text-emerald-400">{weights.w_rating}·R_bay</span>
          <span> + </span>
          <span className="text-purple-400">{weights.w_popularity}·P_pop</span>
          <span> + </span>
          <span className="text-sky-400">{weights.w_collab}·C_collab</span>
        </div>
        <div className="text-slate-500 flex items-center gap-1">
          <HelpCircle size={11} />
          Total Weight Sum: <span className={total > 1.2 ? 'text-amber-400 font-bold' : 'text-slate-300'}>{total}</span>
        </div>
      </div>
    </div>
  );
};
