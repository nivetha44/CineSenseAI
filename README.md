# CineSenseAI 🎬

> **"Discover your next favorite movie."**  
> An explainable, data-driven movie recommendation and exploratory analysis platform built with Python, FastAPI, Scikit-Learn, React, Vite, TypeScript, and Tailwind CSS.

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6.svg)](https://www.typescriptlang.org/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-v4-38B2AC.svg)](https://tailwindcss.com/)
[![Dataset](https://img.shields.io/badge/Dataset-MovieLens%20100k-orange.svg)](https://grouplens.org/datasets/movielens/)
[![Tests](https://img.shields.io/badge/Tests-18%20Passed-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 Live Demo & Deployment
- **GitHub Repository**: [https://github.com/nivetha44/CineSenseAI](https://github.com/nivetha44/CineSenseAI)
- **Local Dev Server**: Frontend running at `http://localhost:5173`, Backend running at `http://localhost:8000`
- **Interactive OpenAPI Documentation**: `http://localhost:8000/docs`
- **Cloud Deployment Guide**: 1-Click deploy on Render, Railway, Vercel, or Docker container. See [docs/deployment.md](docs/deployment.md).

---

## 🎯 Project Overview & Philosophy

Most movie recommendation projects fall into two traps:
1. **Generic Netflix Clones**: Pretty user interfaces with hardcoded mock cards or random genre filters masquerading as "AI".
2. **Opaque Black Boxes**: Recommendation engines that output movie titles without explaining *why* they appeared, often repeating the exact same 15 blockbusters due to extreme popularity bias.

**CineSenseAI** is built to demonstrate the complete, reproducible **Data-to-Product Pipeline**:
```
MovieLens Dataset (9,742 titles, 100k ratings)
      ↓
Data Cleaning & Normalization (Regex year extraction, title standardization)
      ↓
Exploratory Data Analysis (Sparsity, power-law distribution, genre ratings)
      ↓
Feature Engineering (Weighted feature soup, 12,000 TF-IDF n-grams)
      ↓
Collaborative Correlation (Item-item mean-centered rating similarity)
      ↓
Transparent Multi-Objective Scoring (Content + Bayesian Prior + Popularity + Collab)
      ↓
Offline Model Evaluation (Precision@K, Recall@K, Hit Rate@K, Catalog Coverage, Diversity)
      ↓
FastAPI Backend Services (Validated REST endpoints with <4ms vector inference)
      ↓
Cinematic Interactive Web Client (Taste profiler, formula tuner, analytics charts)
```

---

## 📐 Quantitative Model Evaluation

To prevent data leakage, CineSenseAI was evaluated on a held-out test set of 150 active users (withholding 25% of their positive ratings, $\text{rating} \ge 4.0$):

| Model / Architecture | Precision@5 | Precision@10 | Recall@10 | Hit Rate@10 | Catalog Coverage | Intra-List Diversity |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Popularity Baseline** | 0.0905 | 0.0655 | 0.0464 | 36.5% | 0.21% (20 titles) | 0.9587 |
| **Content-Based (TF-IDF)** | 0.0095 | 0.0061 | 0.0020 | 6.1% | 11.91% (1,160 titles) | 0.2437 |
| **Hybrid (CineSenseAI)** | **0.0459** | **0.0446** | **0.0308** | **31.8%** | **6.27% (611 titles)** | **0.6162** |

### Key Academic Findings:
- **The Popularity Paradox**: Naive popularity baselines score high hit rates because everyone has watched *Forrest Gump* and *The Shawshank Redemption*, but catalog coverage is a catastrophic **0.21%** (ignoring 99.79% of the catalog).
- **The Long-Tail Discovery**: Pure Content-Based filtering achieves **11.91% coverage** (1,160 unique titles recommended), excelling at discovering niche cinematic gems.
- **The Balanced Hybrid**: CineSenseAI captures both worlds—retaining a **31.8% Hit Rate** while achieving **6.27% coverage** and balanced intra-list diversity.

---

## 🔬 Mathematical Methodology

### 1. Weighted Feature Soup & TF-IDF
$$\text{Soup}(m) = 2 \times \text{Genres} + 2 \times \text{Director} + \text{Cast} + \text{Tags} + \text{Overview} + \text{Decade}$$
Vectorized into $12,000$ unigrams and bigrams with sublinear TF scaling. Cosine similarity evaluates via matrix dot product in under 4ms across 9,742 movies.

### 2. Empirical Bayesian Prior (IMDb Weighted Rating)
Prevents titles with single 5.0-star reviews from outranking verified cinema masterpieces:
$$WR = \frac{v}{v+m} \cdot R + \frac{m}{v+m} \cdot C$$
- $v$: rating count
- $m = 10$: minimum rating threshold
- $R$: sample average rating
- $C = 3.50$: global dataset mean

### 3. Transparent Multi-Objective Ranking Formula
$$\text{Score}(i) = w_c \cdot S_{\text{content}}(i) + w_r \cdot \left(\frac{WR(i)}{5.0}\right) + w_p \cdot P_{\text{norm}}(i) + w_{\text{collab}} \cdot S_{\text{collab}}(i)$$
- **Default Production Weights**: Content ($55\%$), Bayesian Rating ($25\%$), Popularity ($10\%$), Collaborative ($10\%$).
- Evaluators can adjust these weights in real-time using the interactive sliders in the UI.

### 4. Explainable AI (XAI)
Every recommendation generates verifiable matching factors:
- Shared genre set intersections
- Shared directorial and lead cast credits
- Shared thematic community tags (e.g. *thought-provoking*, *pixar*, *twist ending*)
- Collaborative audience co-rating patterns

---

## 💻 Tech Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic, Scikit-Learn, Pandas, NumPy, SciPy
- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, Lucide React, Recharts
- **Dataset**: GroupLens MovieLens Latest Small (9,742 movies, 100,836 ratings, 610 users, 3,683 tags)
- **Testing**: Pytest, FastAPI TestClient, Httpx (18 automated tests passing)

---

## 📁 Repository Structure

```
CineSenseAI/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # Route controllers (movies, recommendations, analytics)
│   │   ├── services/            # Business logic layer
│   │   ├── models/schemas.py    # Pydantic schemas
│   │   ├── ml/                  # Recommendation engine & evaluation protocol
│   │   ├── config.py            # App settings
│   │   └── main.py              # FastAPI app with lifespan startup
│   └── requirements.txt         # Backend dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/          # MovieCard, MovieDetailsModal, WeightSliders, Navbar, etc.
│   │   ├── pages/               # Discover, Recommendations, Explore, Analytics, About, Watchlist
│   │   ├── services/api.ts      # Typed API client
│   │   ├── types/               # TypeScript interfaces
│   │   ├── App.tsx              # Root application with tab router & modal state
│   │   └── index.css            # Tailwind CSS v4 styling
│   ├── package.json
│   └── vite.config.ts
│
├── data/
│   ├── raw/ml-latest-small/     # Verified GroupLens MovieLens dataset
│   ├── processed/               # Cleaned CSV/JSON, analytics summary, evaluation benchmarks
│   └── README.md
│
├── notebooks/                   # Reproducible Jupyter Data Science Pipeline
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda.ipynb
│   ├── 04_feature_engineering.ipynb
│   ├── 05_recommendation_model.ipynb
│   └── 06_model_evaluation.ipynb
│
├── docs/                        # Academic & Portfolio Documentation
│   ├── architecture.md          # System architecture & data flow diagrams
│   ├── methodology.md           # Algorithm mathematics & TF-IDF formulation
│   ├── evaluation.md            # Benchmark comparison report
│   └── project_report.md        # Complete academic project report
│
├── scripts/
│   ├── prepare_data.py          # Data cleaning, metadata enrichment & analytics generation
│   └── generate_notebooks.py    # Generates all 6 Jupyter notebooks
│
├── tests/
│   ├── test_recommender.py      # Unit tests for recommendation algorithms
│   └── test_api.py              # FastAPI integration tests
│
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🚀 Quickstart & Running Locally

### 1. Clone the Repository
```bash
git clone https://github.com/nivetha44/CineSenseAI.git
cd CineSenseAI
```

### 2. Set Up Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

### 3. Run Data Pipeline (Optional — precomputed artifacts already included)
```bash
python scripts/prepare_data.py
python backend/app/ml/evaluation.py
```

### 4. Start the FastAPI Backend
```bash
PYTHONPATH=. uvicorn backend.app.main:app --reload --port 8000
```
Backend will be live at `http://localhost:8000` (API docs at `http://localhost:8000/docs`).

### 5. Start the React Frontend
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

### 6. Run the Test Suite
```bash
PYTHONPATH=. pytest tests/
```

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health check verifying engine readiness and catalog size |
| `GET` | `/api/movies` | Paginated movie catalog with genre and sort parameters |
| `GET` | `/api/movies/{id}` | Detailed movie metadata with director, cast, and Bayesian prior |
| `GET` | `/api/search` | Multi-attribute search (title, director, actor, community tag) |
| `GET` | `/api/genres` | Unique list of all 19 catalog genres |
| `GET` | `/api/curated/{type}` | Curated rows: `popular`, `highly_rated`, `hidden_gems`, `genre` |
| `GET` | `/api/recommendations/{id}` | Item-to-item hybrid recommendations with explainable factors |
| `POST`| `/api/recommendations` | Profile recommendations from liked movies & preferred genres |
| `GET` | `/api/analytics/overview` | Full dataset statistics, sparsity, and rating histograms |
| `GET` | `/api/analytics/genres` | Genre volume and average rating breakdown |
| `GET` | `/api/model/info` | Architecture specifications, feature vocabulary, and evaluation metrics |

---

## ⚠️ Documented Limitations

1. **Extreme Matrix Sparsity (98.3%)**: Users in the MovieLens 100k dataset have reviewed fewer than 1.7% of all potential movie pairs, necessitating Content-Based feature fallback for long-tail items.
2. **Cold-Start Requirement**: For new anonymous users, CineSenseAI requires an initial onboarding taste selection (preferred genres and 1-3 liked titles) to construct a synthesized preference vector.
3. **Static Historical Data**: GroupLens MovieLens captures historical ratings without real-time clickstream or watch-completion signals.

---

## 👤 Author
- **Nivetha** — [GitHub (@nivetha44)](https://github.com/nivetha44)
- Repository: [https://github.com/nivetha44/CineSenseAI](https://github.com/nivetha44/CineSenseAI)

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
The MovieLens dataset is provided by [GroupLens Research](https://grouplens.org/) for educational and research purposes.
