import React from 'react';
import {
  Cpu,
  Layers,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  GitBranch,
  ShieldCheck,
  Sliders,
  Award
} from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="space-y-12 pb-20 max-w-5xl mx-auto">
      {/* Header */}
      <div className="border-b border-slate-800 pb-6 text-center space-y-3">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
          <Cpu size={13} />
          <span>System Architecture & Mathematical Methodology</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          How CineSenseAI Works
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 max-w-2xl mx-auto leading-relaxed">
          From raw sparse audience interactions to explainable vector similarity recommendations:
          a complete, reproducible data science and machine learning pipeline.
        </p>
      </div>

      {/* Visual Pipeline Diagram (Flow) */}
      <section className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-6">
        <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
          <Layers size={18} className="text-amber-400" />
          End-to-End Machine Learning Pipeline
        </h2>

        {/* Step-by-Step Flow Cards */}
        <div className="grid grid-cols-1 md:grid-cols-6 gap-3 text-xs">
          {/* Step 1 */}
          <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 flex flex-col justify-between space-y-2">
            <div>
              <span className="font-mono text-amber-400 font-bold text-[10px]">STEP 01</span>
              <h4 className="font-semibold text-slate-200 mt-1">MovieLens Data</h4>
              <p className="text-[11px] text-slate-400 mt-1">
                9,742 movies, 100,836 ratings, 3,683 tags, 610 users.
              </p>
            </div>
            <div className="text-[10px] text-slate-500 font-mono">Raw GroupLens</div>
          </div>

          {/* Step 2 */}
          <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 flex flex-col justify-between space-y-2">
            <div>
              <span className="font-mono text-amber-400 font-bold text-[10px]">STEP 02</span>
              <h4 className="font-semibold text-slate-200 mt-1">Data Cleaning</h4>
              <p className="text-[11px] text-slate-400 mt-1">
                Title normalization, release year extraction, genre cleaning, tag grouping.
              </p>
            </div>
            <div className="text-[10px] text-slate-500 font-mono">Regex & Pandas</div>
          </div>

          {/* Step 3 */}
          <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 flex flex-col justify-between space-y-2">
            <div>
              <span className="font-mono text-amber-400 font-bold text-[10px]">STEP 03</span>
              <h4 className="font-semibold text-slate-200 mt-1">Feature Soup</h4>
              <p className="text-[11px] text-slate-400 mt-1">
                Combining genres, synopsis, director, actors, user tags, and release era.
              </p>
            </div>
            <div className="text-[10px] text-slate-500 font-mono">Multi-modal Soup</div>
          </div>

          {/* Step 4 */}
          <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 flex flex-col justify-between space-y-2">
            <div>
              <span className="font-mono text-amber-400 font-bold text-[10px]">STEP 04</span>
              <h4 className="font-semibold text-slate-200 mt-1">TF-IDF & Collab</h4>
              <p className="text-[11px] text-slate-400 mt-1">
                12,000 bi-gram TF-IDF vectors + item-item rating co-occurrence matrix.
              </p>
            </div>
            <div className="text-[10px] text-slate-500 font-mono">Scikit-Learn Sparse</div>
          </div>

          {/* Step 5 */}
          <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 flex flex-col justify-between space-y-2">
            <div>
              <span className="font-mono text-amber-400 font-bold text-[10px]">STEP 05</span>
              <h4 className="font-semibold text-slate-200 mt-1">Hybrid Ranking</h4>
              <p className="text-[11px] text-slate-400 mt-1">
                Multi-objective transparent scoring: similarity, Bayesian rating, popularity.
              </p>
            </div>
            <div className="text-[10px] text-slate-500 font-mono">Weighted Formula</div>
          </div>

          {/* Step 6 */}
          <div className="bg-slate-950/80 p-4 rounded-xl border border-amber-500/40 bg-amber-500/5 flex flex-col justify-between space-y-2">
            <div>
              <span className="font-mono text-amber-400 font-bold text-[10px]">STEP 06</span>
              <h4 className="font-semibold text-amber-300 mt-1">Explainable UX</h4>
              <p className="text-[11px] text-slate-300 mt-1">
                Recommendations with concrete, data-backed reasons & similarity breakdowns.
              </p>
            </div>
            <div className="text-[10px] text-amber-400 font-mono">XAI Badges</div>
          </div>
        </div>
      </section>

      {/* Core Methodology Deep-Dive */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
        {/* Content-Based Filtering */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-3">
          <div className="flex items-center gap-2">
            <Sparkles size={16} className="text-amber-400" />
            <h3 className="text-sm font-bold text-white">
              1. Content-Based Filtering (TF-IDF + Cosine)
            </h3>
          </div>
          <p className="text-slate-300 leading-relaxed">
            Content-Based Filtering represents each movie as a multi-dimensional vector in a semantic
            space. We vectorize each movie's metadata (genre tokens boosted 2x, director tokens, top cast,
            community tags, and plot overview) using <strong>Term Frequency-Inverse Document Frequency (TF-IDF)</strong> with unigrams and bigrams.
          </p>
          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 font-mono text-[11px] text-amber-300">
            cosine_similarity(u, v) = (u · v) / (||u|| * ||v||)
          </div>
          <p className="text-slate-400 leading-relaxed text-[11px]">
            Because our TF-IDF vectors are L2-normalized upon creation, cosine similarity simplifies to the
            matrix dot product, computing similarities across all 9,742 catalog movies in under 4 milliseconds.
          </p>
        </div>

        {/* Bayesian Prior Weighting */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-3">
          <div className="flex items-center gap-2">
            <Award size={16} className="text-emerald-400" />
            <h3 className="text-sm font-bold text-white">
              2. Bayesian Prior Rating (IMDb Weighted Score)
            </h3>
          </div>
          <p className="text-slate-300 leading-relaxed">
            Raw average rating is prone to false positives: a movie with a single 5.0-star rating should
            never outrank a cinema masterpiece with 300 reviews averaging 4.4 stars.
          </p>
          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 font-mono text-[11px] text-emerald-300">
            WR = (v / (v + m)) * R + (m / (v + m)) * C
          </div>
          <p className="text-slate-400 leading-relaxed text-[11px]">
            Where <strong>v</strong> is movie review count, <strong>m=10</strong> is minimum threshold,
            <strong>R</strong> is the movie's average rating, and <strong>C=3.50</strong> is the global dataset mean.
          </p>
        </div>

        {/* Item-Item Collaborative Filtering */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-3">
          <div className="flex items-center gap-2">
            <Sliders size={16} className="text-sky-400" />
            <h3 className="text-sm font-bold text-white">
              3. Item-Item Collaborative Filtering Correlation
            </h3>
          </div>
          <p className="text-slate-300 leading-relaxed">
            In addition to metadata semantics, we construct a normalized user-item rating interaction matrix.
            For movies with ≥10 ratings, we center ratings by subtracting each user's mean rating, then
            compute pairwise cosine distance between item rating vectors.
          </p>
          <p className="text-slate-400 leading-relaxed text-[11px]">
            This captures emergent audience taste: movies that users loved together even if their metadata keywords differed.
          </p>
        </div>

        {/* Transparent Ranking Formula */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-3">
          <div className="flex items-center gap-2">
            <ShieldCheck size={16} className="text-purple-400" />
            <h3 className="text-sm font-bold text-white">
              4. The Transparent Scoring System
            </h3>
          </div>
          <p className="text-slate-300 leading-relaxed">
            Rather than relying on an opaque black-box algorithm, CineSenseAI ranks candidates through an
            explicit, customizable multi-objective formula:
          </p>
          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 font-mono text-[11px] text-purple-300">
            Score = w_c·S_content + w_r·R_bayesian + w_p·P_pop + w_collab·S_collab
          </div>
          <p className="text-slate-400 leading-relaxed text-[11px]">
            Defaults: Content (55%), Bayesian Rating (25%), Popularity (10%), Collaborative (10%). Users
            can adjust these weights dynamically in the Recommendations interface.
          </p>
        </div>
      </section>

      {/* Explainable AI (XAI) Philosophy */}
      <section className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-4">
        <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
          <CheckCircle2 size={18} className="text-emerald-400" />
          Explainable AI (XAI) & No-Fake-AI Policy
        </h2>
        <p className="text-xs text-slate-300 leading-relaxed">
          Traditional recommendation platforms present black-box recommendations without context.
          CineSenseAI enforces rigorous explainability: every recommendation card generates
          verifiable matching reasons derived from the underlying dataset:
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs pt-2">
          <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800">
            <span className="font-semibold text-amber-400">Common Genre Intersections</span>
            <p className="text-slate-400 text-[11px] mt-1">
              Exact set intersection between the seed/profile genres and the target movie.
            </p>
          </div>
          <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800">
            <span className="font-semibold text-sky-400">Directorial & Cast Match</span>
            <p className="text-slate-400 text-[11px] mt-1">
              Verifies shared directors (e.g. David Fincher, Christopher Nolan) or lead actors.
            </p>
          </div>
          <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800">
            <span className="font-semibold text-emerald-400">Audience Co-Rating Patterns</span>
            <p className="text-slate-400 text-[11px] mt-1">
              Reflects high item-item correlation from 100,000+ real user interactions.
            </p>
          </div>
        </div>
      </section>

      {/* Limitations & Real-World Challenges */}
      <section className="bg-slate-900/40 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-4">
        <div className="flex items-center gap-2">
          <AlertTriangle size={18} className="text-amber-400" />
          <h2 className="text-base font-bold text-white tracking-tight">
            Documented System Limitations & Trade-Offs
          </h2>
        </div>
        <p className="text-xs text-slate-400 leading-relaxed">
          A serious engineering portfolio project acknowledges real data constraints rather than hiding them:
        </p>
        <ul className="space-y-2 text-xs text-slate-300 list-disc list-inside">
          <li>
            <strong>Extreme Matrix Sparsity (98.3% empty):</strong> With 610 users and 9,742 movies, users have rated less than 1.7% of all potential pairs, necessitating Content-Based feature fallback.
          </li>
          <li>
            <strong>Popularity Bias:</strong> Mainstream blockbusters (e.g. Forrest Gump, Shawshank Redemption) receive thousands of reviews, creating an evaluation bias where popular baselines achieve high hit rates while failing catalog diversity.
          </li>
          <li>
            <strong>Cold-Start Problem:</strong> For brand new users with no history, CineSenseAI requires an onboarding genre/seed selection flow to construct an initial synthesized preference vector.
          </li>
          <li>
            <strong>Static Dataset:</strong> MovieLens 100k reflects a historical snapshot; real-time streaming services continuously ingest implicit watch-time and click-stream signals.
          </li>
        </ul>
      </section>

      {/* Project & Portfolio Submission Info */}
      <section className="bg-slate-950/90 border border-slate-800 rounded-2xl p-6 text-center space-y-2">
        <h3 className="text-sm font-bold text-white">CineSenseAI Portfolio Project</h3>
        <p className="text-xs text-slate-400">
          Source code, reproducible data science notebooks, model evaluation protocols, and FastAPI routes:
        </p>
        <div className="pt-2">
          <a
            href="https://github.com/nivetha44/CineSenseAI"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-amber-400 border border-slate-700 transition"
          >
            <GitBranch size={14} />
            github.com/nivetha44/CineSenseAI
          </a>
        </div>
      </section>
    </div>
  );
};
