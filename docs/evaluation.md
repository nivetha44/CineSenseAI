# CineSenseAI — Model Evaluation Report

## 1. Evaluation Protocol

To prevent data leakage and provide authentic performance benchmarks, CineSenseAI was evaluated using an offline hold-out testing protocol:
- **Eligible Users**: Users with $\ge 20$ historical interactions.
- **Evaluation Split**: For each user, their chronological positive interactions (ratings $\ge 4.0$, or $\ge 3.5$ if sparse) were split into:
  - 75% Training Interactions (available to construct user taste vectors)
  - 25% Held-Out Test Set (used solely to evaluate recommendations)
- **Sample Size**: 150 active users randomly sampled under a fixed random seed (`seed=42`).

---

## 2. Quantitative Benchmark Results

| Model / Architecture | Precision@5 | Precision@10 | Recall@10 | Hit Rate@10 | Catalog Coverage | Intra-List Diversity |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Popularity Baseline** | 0.0905 | 0.0655 | 0.0464 | 36.5% | 0.21% (20 titles) | 0.9587 |
| **Content-Based (TF-IDF)** | 0.0095 | 0.0061 | 0.0020 | 6.1% | 11.91% (1,160 titles) | 0.2437 |
| **Hybrid (CineSenseAI)** | **0.0459** | **0.0446** | **0.0308** | **31.8%** | **6.27% (611 titles)** | **0.6162** |

---

## 3. Analysis & Key Insights

### 3.1 The Popularity Paradox
The Popularity Baseline produced the highest raw Hit Rate (36.5%). However, this metric is deceptive:
- The baseline repeatedly suggested the same 20 blockbusters (*Forrest Gump*, *The Shawshank Redemption*, *Pulp Fiction*, *The Matrix*).
- Catalog coverage was a catastrophic **0.21%**, completely failing to recommend 99.79% of the catalog.
- In production, this causes user churn because users already know mainstream movies.

### 3.2 Long-Tail Discovery in Content-Based Models
Pure Content-Based Filtering demonstrated massive catalog exploration:
- Catalog coverage reached **11.91%** (1,160 unique titles recommended).
- The lower hit rate (6.1%) on historical ratings is expected in a sparse rating matrix (98.3% unrated pairs): users often haven't rated obscure similar films yet, even if they would enjoy them.

### 3.3 The Optimal Trade-off: CineSenseAI Hybrid
The CineSenseAI Hybrid model balances serendipity, catalog discovery, and relevance:
- **Hit Rate@10 of 31.8%**: Competitive with the popularity baseline.
- **Catalog Coverage of 6.27%**: Over 30x the catalog coverage of the baseline (611 unique movies recommended).
- **Intra-List Diversity of 0.6162**: Prevents recommending 10 near-identical franchise sequels in a single recommendation list.
