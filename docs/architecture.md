# CineSenseAI — System Architecture

## Overview
CineSenseAI is built as a modular, decoupled full-stack machine learning system comprising an offline batch preprocessing pipeline, an in-memory sparse vector inference engine, a high-performance FastAPI REST backend, and a modern React (Vite + TypeScript + Tailwind CSS) client.

---

## Architectural Diagram

```
+---------------------------------------------------------------------------------+
|                                 CLIENT TIER                                     |
|  React 18 + Vite + TypeScript + Tailwind CSS + Lucide Icons + Recharts          |
|  - Discover Page (Curated Rows, Bayesian Top-Picks, Hidden Gems)               |
|  - Recommendations Page (Neural Preference Profiler + Scoring Weight Tuning)    |
|  - Explore Catalog (Full multi-attribute search, genre, rating & era filters)   |
|  - Analytics Dashboard (Interactive EDA charts + Recommender Evaluation Suite)  |
|  - Explainability Modals & LocalStorage Watchlist                               |
+----------------------------------------+----------------------------------------+
                                         | JSON over HTTP / REST
                                         v
+---------------------------------------------------------------------------------+
|                                 BACKEND API                                     |
|  FastAPI (Python 3.11+) + Uvicorn ASGI Server                                   |
|  - Lifespan Startup: Pre-fits TF-IDF and loads collaborative matrix into memory |
|  - Route Controllers:                                                           |
|      /api/movies, /api/movies/{id}, /api/search, /api/genres                    |
|      /api/recommendations/{id}, /api/recommendations (POST User Profile)       |
|      /api/analytics/overview, /api/analytics/genres, /api/analytics/ratings    |
|      /api/model/info, /api/health                                               |
|  - Pydantic Validation & Robust Error Serialization                             |
+----------------------------------------+----------------------------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
|                        RECOMMENDATION & ML LAYER                                |
|  - TF-IDF Vectorizer (1-2 ngrams, stop words, min_df=2, 12,000 max features)    |
|  - Cosine Similarity Engine (Vectorized Dot Product in <4ms)                    |
|  - Item-Item Normalized Collaborative Affinity Matrix                           |
|  - Transparent Ranking Model:                                                   |
|      Score = w_c * S_content + w_r * R_bayesian + w_p * P_pop + w_collab * S_collab|
|  - Explainable AI Engine (Extracts shared genres, directors, cast, tags)        |
+----------------------------------------+----------------------------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
|                               DATA PIPELINE                                     |
|  - GroupLens MovieLens 100k (9,742 movies, 100,836 ratings, 610 users)          |
|  - Title Normalization & Regex Year Extraction                                  |
|  - Multi-modal Feature Soup Construction                                        |
|  - Cached Enriched Metadata (Director, Cast, HD Posters)                        |
|  - Processed Artifacts: movies_cleaned.csv/json, analytics_summary.json         |
+---------------------------------------------------------------------------------+
```

---

## Component Deep Dive

### 1. Data Pipeline (`scripts/prepare_data.py`)
- Reads raw files (`movies.csv`, `ratings.csv`, `tags.csv`, `links.csv`).
- Cleans movie titles (extracts release years, strips trailing grammar articles).
- Computes Bayesian Weighted Ratings using IMDb's formula:
  $$WR = \frac{v}{v+m} \cdot R + \frac{m}{v+m} \cdot C$$
  where $v$ is review count, $m=10$ is threshold, $R$ is average rating, and $C=3.50$ is dataset mean.
- Enriches metadata for top movies (directors, cast, high-res posters).
- Computes empirical statistics for the Analytics Dashboard and exports to `data/processed/analytics_summary.json`.

### 2. Machine Learning Engine (`backend/app/ml/recommender.py`)
- **Content-Based Model**: Constructs a rich feature soup (genre tokens weighted 2x, director tokens, top cast members, community user tags, and synopsis). Fits a Scikit-Learn `TfidfVectorizer` (unigrams + bigrams).
- **Collaborative Filtering**: Computes mean-centered item-item cosine similarity on active user interaction matrices.
- **Fast Inference**: Stores L2-normalized sparse CSR matrices. Pairwise cosine similarity evaluates in ~3-4ms per query.

### 3. FastAPI Service (`backend/app/`)
- Adheres to clean separation of concerns:
  - `api/routes/`: Route handlers and parameter parsing.
  - `services/`: Business logic.
  - `models/schemas.py`: Pydantic input/output validation.
  - `ml/`: Recommendation algorithms.
- Configured with non-blocking async lifecycle management.

### 4. Client Application (`frontend/`)
- Single Page Application built with Vite and React 18.
- Styled using Tailwind CSS v4 and Google Fonts (`Outfit` for display headings, `Inter` for body).
- Visual charts rendered with Recharts.
- Complete state persistence for Watchlist and Onboarding selections via browser `localStorage`.
