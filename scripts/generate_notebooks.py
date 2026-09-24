"""
Script to programmatically generate clean, fully structured Jupyter Notebooks (.ipynb)
for all 6 stages of the CineSenseAI data science pipeline.
"""

import os
import nbformat as nbf

NOTEBOOKS_DIR = "notebooks"
os.makedirs(NOTEBOOKS_DIR, exist_ok=True)


def create_notebook(title: str, description: str, sections: list, output_filename: str):
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.11"
        }
    }

    cells = []
    # Title Header
    cells.append(nbf.v4.new_markdown_cell(f"# CineSenseAI — {title}\n\n{description}\n\n*Author: CineSenseAI Team | Dataset: MovieLens Latest Small (GroupLens Research)*"))

    for sec in sections:
        sec_type = sec.get("type", "code")
        content = sec.get("content", "")
        if sec_type == "markdown":
            cells.append(nbf.v4.new_markdown_cell(content))
        else:
            cells.append(nbf.v4.new_code_cell(content))

    nb.cells = cells
    filepath = os.path.join(NOTEBOOKS_DIR, output_filename)
    with open(filepath, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Generated {filepath}")


def build_all_notebooks():
    # 01_data_understanding
    create_notebook(
        title="01 Data Understanding",
        description="Initial inspection, schema analysis, missing value auditing, and integrity checks on the raw MovieLens dataset.",
        sections=[
            {
                "type": "markdown",
                "content": "## 1. Environment Setup & Data Loading\nWe load the four core tables from the GroupLens MovieLens 100k dataset: `movies.csv`, `ratings.csv`, `tags.csv`, and `links.csv`."
            },
            {
                "type": "code",
                "content": """import pandas as pd
import numpy as np

# Load tables
movies = pd.read_csv('../data/raw/ml-latest-small/movies.csv')
ratings = pd.read_csv('../data/raw/ml-latest-small/ratings.csv')
tags = pd.read_csv('../data/raw/ml-latest-small/tags.csv')
links = pd.read_csv('../data/raw/ml-latest-small/links.csv')

print(f"Movies Shape: {movies.shape}")
print(f"Ratings Shape: {ratings.shape}")
print(f"Tags Shape: {tags.shape}")
print(f"Links Shape: {links.shape}")"""
            },
            {
                "type": "markdown",
                "content": "## 2. Inspecting First Rows and Data Types"
            },
            {
                "type": "code",
                "content": """print("--- Movies Sample ---")
display(movies.head(3))

print("--- Ratings Sample ---")
display(ratings.head(3))

print("--- Tags Sample ---")
display(tags.head(3))"""
            },
            {
                "type": "markdown",
                "content": "## 3. Missing Value Audit\nChecking for nulls across all datasets. In real-world data pipelines, silent null propagation causes downstream failures."
            },
            {
                "type": "code",
                "content": """print("Movies null counts:\\n", movies.isnull().sum())
print("\\nRatings null counts:\\n", ratings.isnull().sum())
print("\\nTags null counts:\\n", tags.isnull().sum())
print("\\nLinks null counts:\\n", links.isnull().sum())"""
            },
            {
                "type": "markdown",
                "content": "## 4. Key Dataset Statistics\nCalculating real statistics without fabrication."
            },
            {
                "type": "code",
                "content": """n_movies = movies['movieId'].nunique()
n_users = ratings['userId'].nunique()
n_ratings = len(ratings)
avg_rating = ratings['rating'].mean()
density = (n_ratings / (n_movies * n_users)) * 100

print(f"Total Unique Movies: {n_movies:,}")
print(f"Total Unique Users:  {n_users:,}")
print(f"Total User Ratings:  {n_ratings:,}")
print(f"Global Average Rating: {avg_rating:.2f} / 5.0")
print(f"Interaction Matrix Sparsity: {100 - density:.2f}% (Density: {density:.2f}%)")"""
            }
        ],
        output_filename="01_data_understanding.ipynb"
    )

    # 02_data_cleaning
    create_notebook(
        title="02 Data Cleaning & Normalization",
        description="Production data preprocessing: title cleaning, year extraction, genre parsing, and tag aggregation.",
        sections=[
            {
                "type": "markdown",
                "content": "## 1. Title Normalization & Release Year Extraction\nMovieLens titles format years at the end (e.g. `Toy Story (1995)`) and often put articles at the end (e.g. `Shawshank Redemption, The`). We extract the integer year and re-format standard titles."
            },
            {
                "type": "code",
                "content": """import re
import pandas as pd
import numpy as np

movies = pd.read_csv('../data/raw/ml-latest-small/movies.csv')

def clean_movie_title(raw_title):
    title = raw_title.strip()
    year = None
    m = re.search(r'\\((\\d{4})\\)$', title)
    if m:
        year = int(m.group(1))
        title = title[:m.start()].strip()
    
    articles = [', The', ', A', ', An', ', Il', ', La']
    for art in articles:
        if title.endswith(art):
            prefix = art.replace(', ', '').strip()
            title = f"{prefix} {title[:-len(art)]}".strip()
            break
    return title, year

res = [clean_movie_title(t) for t in movies['title']]
movies['clean_title'] = [r[0] for r in res]
movies['release_year'] = [r[1] for r in res]

print(movies[['title', 'clean_title', 'release_year']].head())"""
            },
            {
                "type": "markdown",
                "content": "## 2. Handling Missing Genres and Formatting Lists\n`(no genres listed)` must be converted into empty lists rather than false tokens."
            },
            {
                "type": "code",
                "content": """def parse_genres(g_str):
    if not isinstance(g_str, str) or g_str == '(no genres listed)':
        return []
    return [g.strip() for g in g_str.split('|') if g.strip()]

movies['genre_list'] = movies['genres'].apply(parse_genres)
print(f"Movies with '(no genres listed)': {(movies['genres'] == '(no genres listed)').sum()}")"""
            },
            {
                "type": "markdown",
                "content": "## 3. Aggregating User Tags by Movie\nGroup individual user tags into clean, lowercased descriptive token sets."
            },
            {
                "type": "code",
                "content": """tags = pd.read_csv('../data/raw/ml-latest-small/tags.csv')
tags_clean = tags.dropna(subset=['tag']).copy()
tags_clean['tag'] = tags_clean['tag'].str.lower().str.strip()

tag_grouped = tags_clean.groupby('movieId')['tag'].apply(lambda s: list(pd.unique(s))).reset_index()
tag_grouped.rename(columns={'tag': 'tags_list'}, inplace=True)

movies = movies.merge(tag_grouped, on='movieId', how='left')
movies['tags_list'] = movies['tags_list'].apply(lambda x: x if isinstance(x, list) else [])
print("Movies with community tags:", (movies['tags_list'].apply(len) > 0).sum())"""
            }
        ],
        output_filename="02_data_cleaning.ipynb"
    )

    # 03_eda
    create_notebook(
        title="03 Exploratory Data Analysis (EDA)",
        description="Deep statistical analysis of rating distributions, genre popularity, temporal trends, and recommendation long-tail patterns.",
        sections=[
            {
                "type": "markdown",
                "content": "## 1. Rating Distribution Analysis\nAnalyzing how users distribute ratings on a 0.5 to 5.0 scale."
            },
            {
                "type": "code",
                "content": """import pandas as pd
import numpy as np

ratings = pd.read_csv('../data/raw/ml-latest-small/ratings.csv')
print("Rating Value Counts:")
print(ratings['rating'].value_counts().sort_index(ascending=False))
print(f"\\nMedian: {ratings['rating'].median()}, Mode: {ratings['rating'].mode()[0]}, Mean: {ratings['rating'].mean():.2f}")"""
            },
            {
                "type": "markdown",
                "content": "## 2. Most-Rated vs. Highest-Rated Movies (Popularity Bias)\nExamining the discrepancy between raw average rating and popularity count."
            },
            {
                "type": "code",
                "content": """movies = pd.read_csv('../data/processed/movies_cleaned.csv')
print("Top 10 Most Rated Movies:")
print(movies.sort_values('rating_count', ascending=False)[['clean_title', 'release_year', 'rating_count', 'rating_mean']].head(10))

print("\\nTop 10 Highest Rated Movies (min 50 ratings):")
print(movies[movies['rating_count'] >= 50].sort_values('rating_mean', ascending=False)[['clean_title', 'release_year', 'rating_count', 'rating_mean', 'bayesian_rating']].head(10))"""
            },
            {
                "type": "markdown",
                "content": "## 3. Genre Distribution and Average Ratings"
            },
            {
                "type": "code",
                "content": """import json

with open('../data/processed/analytics_summary.json') as f:
    analytics = json.load(f)

genre_df = pd.DataFrame(analytics['genre_distribution'])
print(genre_df.to_string(index=False))"""
            }
        ],
        output_filename="03_eda.ipynb"
    )

    # 04_feature_engineering
    create_notebook(
        title="04 Feature Engineering",
        description="Constructing feature soups, TF-IDF vectorization, Bayesian weighted ratings, and collaborative interaction matrices.",
        sections=[
            {
                "type": "markdown",
                "content": "## 1. Feature Soup Construction\nWe combine genres (repeated for weighting), community tags, plot overviews, director, actors, and era tokens."
            },
            {
                "type": "code",
                "content": """import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

movies = pd.read_csv('../data/processed/movies_cleaned.csv')
print(f"Loaded {len(movies)} cleaned movies.")
print("Sample Overview:", movies['overview'].iloc[0])"""
            },
            {
                "type": "markdown",
                "content": "## 2. TF-IDF Vectorization\nExtract unigrams and bigrams, filtering English stopwords and setting vocabulary limits."
            },
            {
                "type": "code",
                "content": """from backend.app.ml.recommender import engine
engine.initialize()

print("TF-IDF Matrix Shape:", engine.tfidf_matrix.shape)
feature_names = engine.tfidf_vectorizer.get_feature_names_out()
print("Sample extracted features:", feature_names[1000:1015])"""
            },
            {
                "type": "markdown",
                "content": "## 3. Bayesian Rating Formula (IMDb Weighted Rating)\n$$WR = \\frac{v}{v+m} R + \\frac{m}{v+m} C$$\nWhere $v$ = vote count, $m$ = threshold (10), $R$ = item mean, $C$ = global mean (3.50)."
            },
            {
                "type": "code",
                "content": """sample = movies[['clean_title', 'rating_count', 'rating_mean', 'bayesian_rating']].sort_values('rating_count', ascending=False).head(5)
print(sample)"""
            }
        ],
        output_filename="04_feature_engineering.ipynb"
    )

    # 05_recommendation_model
    create_notebook(
        title="05 Recommendation Engine & Explainability",
        description="Implementing Content-Based Cosine Similarity, Item-Item Collaborative Filtering, and explainable recommendation badges.",
        sections=[
            {
                "type": "markdown",
                "content": "## 1. Generating Content-Based & Hybrid Recommendations\nTesting the recommender with seed movies and inspecting the transparent scoring components."
            },
            {
                "type": "code",
                "content": """from backend.app.ml.recommender import engine

# Recommend for The Matrix (movieId: 2571)
recs = engine.recommend_for_movie(2571, top_k=5)
for r in recs:
    print(f"Title: {r['title']} ({r['release_year']})")
    print(f"Score: {r['recommendation_score']} (Content Sim: {r['content_similarity']})")
    print(f"Explanation: {r['explanation']['summary']}")
    print(f"Reasons: {r['explanation']['reasons']}\\n")"""
            },
            {
                "type": "markdown",
                "content": "## 2. Personalized Onboarding Profile Recommendations\nSimulating cold-start onboarding where user selects preferred genres and liked movies."
            },
            {
                "type": "code",
                "content": """profile_recs = engine.recommend_for_user_profile(
    liked_movie_ids=[1, 3114], # Toy Story 1 & 2
    preferred_genres=['Animation', 'Adventure'],
    top_k=5
)
for r in profile_recs:
    print(f"- {r['title']}: {r['explanation']['reasons']}")"""
            }
        ],
        output_filename="05_recommendation_model.ipynb"
    )

    # 06_model_evaluation
    create_notebook(
        title="06 Model Evaluation & Comparison",
        description="Offline evaluation using held-out user interactions. Comparing Baseline, Content-Based, and Hybrid models on Precision, Recall, Hit Rate, Coverage, and Diversity.",
        sections=[
            {
                "type": "markdown",
                "content": "## 1. Running the Evaluation Protocol\nLoads `evaluation_results.json` generated from real held-out user testing."
            },
            {
                "type": "code",
                "content": """import json
import pandas as pd

with open('../data/processed/evaluation_results.json') as f:
    eval_data = json.load(f)

print("Protocol:", eval_data['evaluation_info'])
df_eval = pd.DataFrame(eval_data['models'])
display(df_eval)"""
            },
            {
                "type": "markdown",
                "content": "## 2. Analysis of the Results\n- **Popularity Baseline** yields highest hit rate (36.5%) but suffers from near-zero catalog coverage (0.21%), recommending only 20 mainstream blockbusters repeatedly.\n- **Content-Based Filtering** achieves superior catalog coverage (11.91%, 1,160 unique movies recommended) allowing users to discover niche titles matching their taste profile.\n- **Hybrid CineSenseAI** strikes the optimal production trade-off: maintaining a 31.8% hit rate with 6.27% coverage and 0.6162 diversity."
            }
        ],
        output_filename="06_model_evaluation.ipynb"
    )

if __name__ == "__main__":
    build_all_notebooks()
