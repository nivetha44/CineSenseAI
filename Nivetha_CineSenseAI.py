"""
CineSenseAI — Complete Machine Learning Pipeline (.py format)
Author: Nivetha
Repository: https://github.com/nivetha44/CineSenseAI
Live Demo: https://cinesense-ai.onrender.com
"""

# ======================================================================
# PART 1: DATA PREPARATION & ENRICHMENT
# ======================================================================
"""
CineSenseAI Data Preparation and Enrichment Pipeline
Extracts, cleans, enriches, and computes analytics from the MovieLens dataset.
"""

import os
import re
import json
import concurrent.futures
import pandas as pd
import numpy as np
import requests

RAW_DIR = "data/raw/ml-latest-small"
PROCESSED_DIR = "data/processed"
CACHE_FILE = os.path.join(PROCESSED_DIR, "omdb_cache.json")


def clean_title(title_raw: str):
    """
    Cleans movie title:
    e.g. 'Shawshank Redemption, The (1994)' -> 'The Shawshank Redemption', 1994
    """
    title = title_raw.strip()
    year = None
    
    # Extract year (e.g. (1994))
    match = re.search(r'\((\d{4})\)$', title)
    if match:
        try:
            year = int(match.group(1))
            title = title[:match.start()].strip()
        except ValueError:
            pass
            
    # Handle trailing articles: ', The', ', A', ', An'
    articles = [', The', ', A', ', An', ', Il', ', La', ', Le', ', L\'', ', Der', ', Die', ', Das']
    for article in articles:
        if title.endswith(article):
            prefix = article.replace(', ', '').strip()
            title = f"{prefix} {title[:-len(article)]}".strip()
            break
            
    return title, year


def fetch_omdb_metadata(imdb_id: str, title: str):
    """Fetch metadata from OMDB using open key."""
    if not imdb_id:
        return None
    url = f"http://www.omdbapi.com/?i={imdb_id}&apikey=trilogy"
    try:
        resp = requests.get(url, timeout=4)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("Response") == "True":
                poster = data.get("Poster")
                if poster == "N/A":
                    poster = None
                return {
                    "overview": data.get("Plot") if data.get("Plot") != "N/A" else None,
                    "director": data.get("Director") if data.get("Director") != "N/A" else None,
                    "actors": data.get("Actors") if data.get("Actors") != "N/A" else None,
                    "runtime": data.get("Runtime") if data.get("Runtime") != "N/A" else None,
                    "rated": data.get("Rated") if data.get("Rated") != "N/A" else None,
                    "poster_url": poster,
                    "imdb_rating": float(data.get("imdbRating")) if data.get("imdbRating") and data.get("imdbRating") != "N/A" else None
                }
    except Exception:
        pass
    return None


def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    print("Loading raw MovieLens files...")
    movies_df = pd.read_csv(os.path.join(RAW_DIR, "movies.csv"))
    ratings_df = pd.read_csv(os.path.join(RAW_DIR, "ratings.csv"))
    tags_df = pd.read_csv(os.path.join(RAW_DIR, "tags.csv"))
    links_df = pd.read_csv(os.path.join(RAW_DIR, "links.csv"))

    print(f"Loaded: {len(movies_df)} movies, {len(ratings_df)} ratings, {len(tags_df)} tags, {len(links_df)} links.")

    # 1. Clean Title and Extract Year
    print("Cleaning titles and extracting release years...")
    titles_years = [clean_title(t) for t in movies_df["title"]]
    movies_df["clean_title"] = [t[0] for t in titles_years]
    movies_df["release_year"] = [t[1] for t in titles_years]

    # Clean genres
    def parse_genres(g_str):
        if not isinstance(g_str, str) or g_str == "(no genres listed)":
            return []
        return [g.strip() for g in g_str.split("|") if g.strip()]

    movies_df["genre_list"] = movies_df["genres"].apply(parse_genres)

    # 2. Process Tags
    print("Aggregating user tags...")
    tags_clean = tags_df.dropna(subset=["tag"]).copy()
    tags_clean["tag"] = tags_clean["tag"].astype(str).str.lower().str.strip()
    tag_grouped = tags_clean.groupby("movieId")["tag"].apply(lambda s: list(pd.unique(s))).reset_index()
    tag_grouped.rename(columns={"tag": "tags_list"}, inplace=True)
    movies_df = movies_df.merge(tag_grouped, on="movieId", how="left")
    movies_df["tags_list"] = movies_df["tags_list"].apply(lambda x: x if isinstance(x, list) else [])

    # 3. Process Ratings & Statistics
    print("Computing rating distributions and statistics...")
    rating_stats = ratings_df.groupby("movieId").agg(
        rating_count=("rating", "count"),
        rating_mean=("rating", "mean"),
        rating_std=("rating", "std")
    ).reset_index()
    rating_stats["rating_mean"] = rating_stats["rating_mean"].round(2)
    rating_stats["rating_std"] = rating_stats["rating_std"].fillna(0).round(2)

    movies_df = movies_df.merge(rating_stats, on="movieId", how="left")
    movies_df["rating_count"] = movies_df["rating_count"].fillna(0).astype(int)
    movies_df["rating_mean"] = movies_df["rating_mean"].fillna(0.0)
    movies_df["rating_std"] = movies_df["rating_std"].fillna(0.0)

    # Global rating mean for IMDB Bayesian weighted rating
    C = float(ratings_df["rating"].mean())
    m = 10.0  # Minimum rating threshold
    v = movies_df["rating_count"]
    R = movies_df["rating_mean"]
    movies_df["bayesian_rating"] = ((v / (v + m)) * R + (m / (v + m)) * C).round(2)

    # Popularity score normalized 0.0 to 1.0 (log scale)
    max_log_count = np.log1p(movies_df["rating_count"].max())
    movies_df["popularity_score"] = (np.log1p(movies_df["rating_count"]) / max_log_count).round(3)

    # 4. Merge Links
    print("Merging IMDb/TMDb links...")
    links_df["imdb_code"] = links_df["imdbId"].apply(lambda x: f"tt{int(x):07d}" if pd.notnull(x) else None)
    movies_df = movies_df.merge(links_df[["movieId", "imdb_code", "tmdbId"]], on="movieId", how="left")

    # 5. Metadata Enrichment (OMDB Cache)
    cache = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cache = json.load(f)
            print(f"Loaded {len(cache)} existing cached movie metadata entries.")
        except Exception:
            cache = {}

    # Sort movies by rating_count to enrich the most popular/relevant movies first
    sorted_movies = movies_df.sort_values(by="rating_count", ascending=False)
    # We will enrich top 500 movies or any already cached
    to_fetch = []
    top_n = 450
    for idx, row in sorted_movies.head(top_n).iterrows():
        mid = str(row["movieId"])
        imdb = row["imdb_code"]
        if mid not in cache and imdb:
            to_fetch.append((mid, imdb, row["clean_title"]))

    print(f"Fetching OMDB metadata for {len(to_fetch)} movies (top rated)...")
    if to_fetch:
        def worker(item):
            mid, imdb, title = item
            meta = fetch_omdb_metadata(imdb, title)
            return mid, meta

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            results = executor.map(worker, to_fetch)
            count = 0
            for mid, meta in results:
                if meta:
                    cache[mid] = meta
                count += 1
                if count % 50 == 0:
                    print(f"Fetched {count}/{len(to_fetch)}...")

        # Save cache
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
        print(f"OMDB cache updated with total {len(cache)} entries.")

    # Apply cache to movies_df
    overviews, directors, actors_list, runtimes, rated_list, poster_urls = [], [], [], [], [], []
    for _, row in movies_df.iterrows():
        mid = str(row["movieId"])
        meta = cache.get(mid, {})
        overviews.append(meta.get("overview"))
        directors.append(meta.get("director"))
        actors_list.append(meta.get("actors"))
        runtimes.append(meta.get("runtime"))
        rated_list.append(meta.get("rated"))
        poster_urls.append(meta.get("poster_url"))

    movies_df["overview"] = overviews
    movies_df["director"] = directors
    movies_df["actors"] = actors_list
    movies_df["runtime"] = runtimes
    movies_df["rated"] = rated_list
    movies_df["poster_url"] = poster_urls

    # Fallback overviews for movies without external plot: descriptive genre/year text
    def make_fallback_overview(row):
        if row["overview"] and isinstance(row["overview"], str) and len(row["overview"]) > 10:
            return row["overview"]
        genres_str = ", ".join(row["genre_list"]) if row["genre_list"] else "Cinema"
        yr = f" released in {int(row['release_year'])}" if pd.notnull(row["release_year"]) else ""
        tags_str = f" Known for themes of {', '.join(row['tags_list'][:4])}." if row["tags_list"] else ""
        return f"A compelling {genres_str} feature{yr}.{tags_str}"

    movies_df["overview"] = movies_df.apply(make_fallback_overview, axis=1)

    # Save cleaned movies
    csv_path = os.path.join(PROCESSED_DIR, "movies_cleaned.csv")
    json_path = os.path.join(PROCESSED_DIR, "movies_cleaned.json")
    
    # Save CSV with string representations
    movies_df.to_csv(csv_path, index=False)
    
    # Save JSON with native types
    records = movies_df.to_dict(orient="records")
    with open(json_path, "w") as f:
        json.dump(records, f)
    print(f"Saved {len(movies_df)} movies to {csv_path} and {json_path}")

    # 6. Compute Comprehensive Analytics Summary
    print("Computing real EDA analytics...")
    rating_counts = ratings_df["rating"].value_counts().sort_index().to_dict()
    # Format keys as string
    rating_dist = [{"rating": float(k), "count": int(v)} for k, v in rating_counts.items()]

    # Genre analytics
    all_genres = []
    for g_list in movies_df["genre_list"]:
        all_genres.extend(g_list)
    genre_series = pd.Series(all_genres)
    genre_counts = genre_series.value_counts().to_dict()

    # Genre average rating
    genre_rating_map = {}
    # Explode movies by genre
    movies_exploded = movies_df.explode("genre_list")
    genre_ratings = movies_exploded.groupby("genre_list")["rating_mean"].mean().round(2).to_dict()

    genre_analytics = []
    for genre, count in genre_counts.items():
        if genre and genre != "(no genres listed)":
            genre_analytics.append({
                "genre": genre,
                "movie_count": int(count),
                "avg_rating": float(genre_ratings.get(genre, 0.0))
            })
    genre_analytics.sort(key=lambda x: x["movie_count"], reverse=True)

    # Top most rated movies
    top_most_rated = movies_df.sort_values(by="rating_count", ascending=False).head(15)[
        ["movieId", "clean_title", "release_year", "rating_count", "rating_mean", "poster_url"]
    ].to_dict(orient="records")

    # Top highest rated movies with at least 50 ratings
    top_highest_rated = movies_df[movies_df["rating_count"] >= 50].sort_values(
        by="rating_mean", ascending=False
    ).head(15)[
        ["movieId", "clean_title", "release_year", "rating_count", "rating_mean", "bayesian_rating", "poster_url"]
    ].to_dict(orient="records")

    # Hidden gems: rating >= 4.0, rating_count between 15 and 60
    hidden_gems = movies_df[(movies_df["rating_count"] >= 15) & (movies_df["rating_count"] <= 65) & (movies_df["rating_mean"] >= 4.0)].sort_values(
        by="rating_mean", ascending=False
    ).head(15)[
        ["movieId", "clean_title", "release_year", "rating_count", "rating_mean", "genres", "poster_url"]
    ].to_dict(orient="records")

    # Decades distribution
    valid_years = movies_df.dropna(subset=["release_year"]).copy()
    valid_years["decade"] = (valid_years["release_year"] // 10 * 10).astype(int)
    decade_counts = valid_years.groupby("decade").agg(
        count=("movieId", "count"),
        avg_rating=("rating_mean", "mean")
    ).reset_index()
    decade_counts["avg_rating"] = decade_counts["avg_rating"].round(2)
    decade_analytics = decade_counts[decade_counts["decade"] >= 1920].to_dict(orient="records")

    # User activity distribution (number of ratings per user)
    user_counts = ratings_df.groupby("userId").size()
    user_activity_bins = [
        {"range": "20-50", "count": int(((user_counts >= 20) & (user_counts <= 50)).sum())},
        {"range": "51-100", "count": int(((user_counts > 50) & (user_counts <= 100)).sum())},
        {"range": "101-250", "count": int(((user_counts > 100) & (user_counts <= 250)).sum())},
        {"range": "251-500", "count": int(((user_counts > 250) & (user_counts <= 500)).sum())},
        {"range": "500+", "count": int((user_counts > 500).sum())},
    ]

    # Overall dataset statistics
    dataset_summary = {
        "dataset_name": "MovieLens Latest Small (GroupLens Research)",
        "total_movies": int(len(movies_df)),
        "total_ratings": int(len(ratings_df)),
        "total_users": int(ratings_df["userId"].nunique()),
        "total_tags": int(len(tags_df)),
        "avg_rating": round(float(ratings_df["rating"].mean()), 2),
        "min_rating": float(ratings_df["rating"].min()),
        "max_rating": float(ratings_df["rating"].max()),
        "rating_density_pct": round(float(len(ratings_df)) / (len(movies_df) * ratings_df["userId"].nunique()) * 100, 2),
        "rating_distribution": rating_dist,
        "genre_distribution": genre_analytics,
        "most_rated_movies": top_most_rated,
        "highest_rated_movies": top_highest_rated,
        "hidden_gems": hidden_gems,
        "decade_distribution": decade_analytics,
        "user_activity_distribution": user_activity_bins
    }

    analytics_path = os.path.join(PROCESSED_DIR, "analytics_summary.json")
    with open(analytics_path, "w") as f:
        json.dump(dataset_summary, f, indent=2)
    print(f"Saved analytics summary to {analytics_path}")
    print("Data preparation complete!")


if __name__ == "__main__":
    main()


# ======================================================================
# PART 2: RECOMMENDATION ENGINE (TF-IDF + BAYESIAN + COLLABORATIVE)
# ======================================================================
"""
CineSenseAI Core Recommendation Engine
Implements:
1. TF-IDF + Cosine Similarity Content-Based Filtering on enriched metadata soup
2. Item-Item Collaborative Filtering based on user-rating patterns
3. Hybrid Transparent Scoring (Content + Rating + Popularity + Collaborative)
4. Dynamic User Profile Vector recommendations (multi-movie / multi-genre seeds)
5. Explainability Engine deriving real matching attributes (genres, director, cast, keywords)
"""

import os
import re
import json
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix


class RecommendationEngine:
    def __init__(self, data_dir: str = "data/processed"):
        self.data_dir = data_dir
        self.movies_df: pd.DataFrame = pd.DataFrame()
        self.ratings_df: Optional[pd.DataFrame] = None
        self.movie_id_to_idx: Dict[int, int] = {}
        self.idx_to_movie_id: Dict[int, int] = {}
        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.item_item_sim = None  # Collaborative item-item similarity
        self.collab_movie_to_idx: Dict[int, int] = {}
        self.is_ready = False

    def initialize(self):
        """Loads processed data, builds feature soups, fits vectorizer, and prepares collaborative matrix."""
        print("Initializing RecommendationEngine...")
        json_path = os.path.join(self.data_dir, "movies_cleaned.json")
        csv_path = os.path.join(self.data_dir, "movies_cleaned.csv")
        
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                records = json.load(f)
            self.movies_df = pd.DataFrame(records)
        elif os.path.exists(csv_path):
            self.movies_df = pd.read_csv(csv_path)
            # parse genre_list
            if "genre_list" in self.movies_df.columns:
                self.movies_df["genre_list"] = self.movies_df["genre_list"].apply(
                    lambda x: eval(x) if isinstance(x, str) and x.startswith("[") else []
                )
        else:
            raise FileNotFoundError(f"Cleaned movies file not found at {json_path} or {csv_path}")

        # Ensure movieId is int
        self.movies_df["movieId"] = self.movies_df["movieId"].astype(int)
        
        # Build index lookups
        for idx, mid in enumerate(self.movies_df["movieId"]):
            self.movie_id_to_idx[mid] = idx
            self.idx_to_movie_id[idx] = mid

        # 1. Build Content Feature Soups
        print("Constructing feature soups for TF-IDF...")
        soups = []
        for _, row in self.movies_df.iterrows():
            genres = " ".join([g.replace(" ", "") for g in (row.get("genre_list") or [])])
            # Boost genre significance by repeating
            genre_boosted = f"{genres} {genres}"
            tags = " ".join(row.get("tags_list") or [])
            overview = str(row.get("overview") or "")
            director = str(row.get("director") or "").replace(" ", "")
            director_boosted = f"{director} {director}" if director else ""
            actors = str(row.get("actors") or "").replace(",", " ")
            year = str(int(row["release_year"])) if pd.notnull(row.get("release_year")) else ""
            decade = f"{year[:3]}0s" if len(year) == 4 else ""

            soup = f"{genre_boosted} {director_boosted} {actors} {tags} {overview} {decade}".lower()
            soups.append(soup)

        self.movies_df["soup"] = soups

        # 2. Fit TF-IDF Vectorizer
        print("Fitting TF-IDF Vectorizer...")
        self.tfidf_vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            min_df=2,
            max_features=12000
        )
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(soups)
        print(f"TF-IDF Matrix shape: {self.tfidf_matrix.shape}")

        # 3. Collaborative Filtering (Item-Item Cosine Similarity on User-Rating Vectors)
        self._build_collaborative_matrix()

        self.is_ready = True
        print("RecommendationEngine ready!")

    def _build_collaborative_matrix(self):
        """Constructs collaborative item-item similarity for movies with >= 10 ratings."""
        ratings_raw_path = "data/raw/ml-latest-small/ratings.csv"
        if not os.path.exists(ratings_raw_path):
            print("Ratings file not found; skipping collaborative matrix.")
            return

        try:
            print("Building item-item collaborative similarity matrix...")
            ratings = pd.read_csv(ratings_raw_path)
            self.ratings_df = ratings
            
            # Filter movies with at least 10 ratings for stability
            counts = ratings.groupby("movieId").size()
            valid_mids = counts[counts >= 10].index.values

            filtered_ratings = ratings[ratings["movieId"].isin(valid_mids)]
            
            # Pivot user-item interaction matrix (mean-centered ratings)
            user_means = filtered_ratings.groupby("userId")["rating"].transform("mean")
            filtered_ratings = filtered_ratings.copy()
            filtered_ratings["norm_rating"] = filtered_ratings["rating"] - user_means

            # Create CSR sparse matrix
            user_cats = filtered_ratings["userId"].astype("category")
            movie_cats = filtered_ratings["movieId"].astype("category")
            
            row_idx = movie_cats.cat.codes.values
            col_idx = user_cats.cat.codes.values
            data = filtered_ratings["norm_rating"].values

            self.collab_movie_to_idx = {mid: code for code, mid in enumerate(movie_cats.cat.categories)}
            
            item_user_sparse = csr_matrix((data, (row_idx, col_idx)), shape=(len(movie_cats.cat.categories), len(user_cats.cat.categories)))
            
            # Compute cosine similarity between items
            self.item_item_sim = cosine_similarity(item_user_sparse, dense_output=False)
            print(f"Collaborative item matrix built for {len(self.collab_movie_to_idx)} items.")
        except Exception as e:
            print(f"Collaborative filtering build error: {e}. Using content-based only.")
            self.item_item_sim = None

    def get_movie_by_id(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve movie dictionary by movieId."""
        if movie_id not in self.movie_id_to_idx:
            return None
        idx = self.movie_id_to_idx[movie_id]
        row = self.movies_df.iloc[idx].to_dict()
        return self._format_movie_dict(row)

    def _format_movie_dict(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure clean types for API/JSON responses."""
        genres = row.get("genre_list", [])
        if isinstance(genres, str):
            try:
                genres = eval(genres)
            except Exception:
                genres = [g.strip() for g in genres.split("|") if g.strip()]
        
        tags = row.get("tags_list", [])
        if isinstance(tags, str):
            try:
                tags = eval(tags)
            except Exception:
                tags = []

        return {
            "movieId": int(row.get("movieId", 0)),
            "title": str(row.get("clean_title") or row.get("title", "")),
            "original_title": str(row.get("title", "")),
            "release_year": int(row["release_year"]) if pd.notnull(row.get("release_year")) else None,
            "genres": genres,
            "tags": tags[:6] if isinstance(tags, list) else [],
            "rating_count": int(row.get("rating_count", 0)),
            "rating_mean": float(round(row.get("rating_mean", 0.0), 2)),
            "bayesian_rating": float(round(row.get("bayesian_rating", 0.0), 2)),
            "popularity_score": float(round(row.get("popularity_score", 0.0), 3)),
            "overview": str(row.get("overview") or ""),
            "director": row.get("director") if pd.notnull(row.get("director")) else None,
            "actors": row.get("actors") if pd.notnull(row.get("actors")) else None,
            "runtime": row.get("runtime") if pd.notnull(row.get("runtime")) else None,
            "poster_url": row.get("poster_url") if pd.notnull(row.get("poster_url")) else None,
            "imdb_code": str(row.get("imdb_code")) if pd.notnull(row.get("imdb_code")) else None
        }

    def explain_recommendation(
        self,
        seed_movie: Dict[str, Any],
        rec_movie: Dict[str, Any],
        content_sim: float,
        collab_sim: float
    ) -> Dict[str, Any]:
        """
        Derives an authentic, explainable rationale based strictly on matching data:
        1. Common genres
        2. Common director
        3. Common cast members
        4. Matching tags/keywords
        5. Audience preference alignment
        """
        reasons = []
        tags_shared = []

        # 1. Shared genres
        seed_genres = set(seed_movie.get("genres", []))
        rec_genres = set(rec_movie.get("genres", []))
        common_genres = sorted(list(seed_genres.intersection(rec_genres)))
        
        if common_genres:
            if len(common_genres) == 1:
                reasons.append(f"Shares the {common_genres[0]} genre")
            else:
                reasons.append(f"Shares {', '.join(common_genres[:3])} genres")

        # 2. Shared Director
        seed_dir = seed_movie.get("director")
        rec_dir = rec_movie.get("director")
        if seed_dir and rec_dir and seed_dir != "N/A" and seed_dir == rec_dir:
            reasons.append(f"Both directed by {seed_dir}")

        # 3. Shared Actors
        seed_actors = set([a.strip() for a in str(seed_movie.get("actors") or "").split(",") if a.strip()])
        rec_actors = set([a.strip() for a in str(rec_movie.get("actors") or "").split(",") if a.strip()])
        common_actors = list(seed_actors.intersection(rec_actors))
        if common_actors:
            reasons.append(f"Features {', '.join(common_actors[:2])}")

        # 4. Shared Tags
        seed_tags = set([t.lower() for t in seed_movie.get("tags", [])])
        rec_tags = set([t.lower() for t in rec_movie.get("tags", [])])
        common_tags = list(seed_tags.intersection(rec_tags))
        if common_tags:
            tags_shared = common_tags[:3]
            reasons.append(f"Matching themes: {', '.join(common_tags[:2])}")

        # 5. Rating / Collaborative pattern
        if collab_sim > 0.25:
            reasons.append(f"Highly co-rated by viewers of {seed_movie['title']}")
        elif rec_movie.get("rating_mean", 0) >= 4.0:
            reasons.append(f"Critically acclaimed ({rec_movie['rating_mean']}/5.0 avg)")

        summary = f"Recommended because it shares {', '.join(common_genres[:2]) if common_genres else 'thematic'} qualities with {seed_movie['title']}."
        if not reasons:
            reasons.append("High thematic & narrative similarity")

        return {
            "summary": summary,
            "reasons": reasons,
            "common_genres": common_genres,
            "shared_tags": tags_shared,
            "content_similarity_pct": int(round(content_sim * 100)),
            "collaborative_affinity_pct": int(round(max(0.0, collab_sim) * 100)) if collab_sim > 0 else 0
        }

    def recommend_for_movie(
        self,
        movie_id: int,
        top_k: int = 10,
        w_content: float = 0.55,
        w_rating: float = 0.25,
        w_popularity: float = 0.10,
        w_collab: float = 0.10
    ) -> List[Dict[str, Any]]:
        """
        Recommends top_k movies similar to movie_id using the transparent hybrid ranking model.
        Formula:
        Score = w_content * S_content + w_rating * S_rating + w_pop * S_pop + w_collab * S_collab
        """
        if movie_id not in self.movie_id_to_idx:
            return []

        idx = self.movie_id_to_idx[movie_id]
        seed_movie = self.get_movie_by_id(movie_id)

        # 1. Content Cosine Similarity (1 x N)
        target_vec = self.tfidf_matrix[idx]
        content_sims = (self.tfidf_matrix @ target_vec.T).toarray().ravel()

        # 2. Collaborative Similarity (if available)
        collab_sims = np.zeros(len(self.movies_df))
        if self.item_item_sim is not None and movie_id in self.collab_movie_to_idx:
            c_idx = self.collab_movie_to_idx[movie_id]
            c_row = self.item_item_sim[c_idx].toarray().ravel()
            for rec_mid, r_c_idx in self.collab_movie_to_idx.items():
                if rec_mid in self.movie_id_to_idx:
                    collab_sims[self.movie_id_to_idx[rec_mid]] = c_row[r_c_idx]

        # 3. Rating & Popularity Normalized Components
        # Scale bayesian rating (usually 2.5 - 4.5) to [0, 1]
        rating_scores = (self.movies_df["bayesian_rating"] / 5.0).values
        pop_scores = self.movies_df["popularity_score"].values

        # 4. Hybrid Transparent Score
        final_scores = (
            w_content * content_sims +
            w_rating * rating_scores +
            w_popularity * pop_scores +
            w_collab * np.clip(collab_sims, 0, 1)
        )

        # Mask out the seed movie itself
        final_scores[idx] = -1.0

        # Select top candidates
        top_indices = np.argsort(final_scores)[::-1][:top_k]

        results = []
        for rec_idx in top_indices:
            rec_row = self.movies_df.iloc[rec_idx].to_dict()
            rec_movie = self._format_movie_dict(rec_row)
            c_sim = float(content_sims[rec_idx])
            col_sim = float(collab_sims[rec_idx])
            score = float(round(final_scores[rec_idx], 3))

            explanation = self.explain_recommendation(seed_movie, rec_movie, c_sim, col_sim)
            rec_movie["recommendation_score"] = score
            rec_movie["content_similarity"] = round(c_sim, 3)
            rec_movie["explanation"] = explanation
            results.append(rec_movie)

        return results

    def recommend_for_user_profile(
        self,
        liked_movie_ids: List[int],
        preferred_genres: List[str],
        top_k: int = 12,
        w_content: float = 0.55,
        w_rating: float = 0.25,
        w_popularity: float = 0.10,
        w_collab: float = 0.10
    ) -> List[Dict[str, Any]]:
        """
        Personalized discovery for onboarding/profile.
        Synthesizes a combined preference vector from liked movies + chosen genres.
        """
        if not liked_movie_ids and not preferred_genres:
            # Fallback to highest rated / popular movies
            return self.get_curated_section("highly_rated", limit=top_k)

        # 1. Synthesize profile vector
        vectors = []
        for mid in liked_movie_ids:
            if mid in self.movie_id_to_idx:
                vectors.append(self.tfidf_matrix[self.movie_id_to_idx[mid]])

        # If genres provided, synthesize genre pseudo-document vector
        if preferred_genres:
            genre_text = " ".join([g.lower().replace(" ", "") for g in preferred_genres] * 3)
            genre_vec = self.tfidf_vectorizer.transform([genre_text])
            vectors.append(genre_vec * 1.5)

        if not vectors:
            return self.get_curated_section("popular", limit=top_k)

        # Average vector
        from scipy.sparse import vstack
        combined_matrix = vstack(vectors)
        profile_vec = np.asarray(combined_matrix.mean(axis=0))

        # Content similarity
        content_sims = (self.tfidf_matrix @ profile_vec.T).ravel()

        # Collaborative component: average of liked movies' collab similarities
        collab_sims = np.zeros(len(self.movies_df))
        if self.item_item_sim is not None and liked_movie_ids:
            valid_c = [self.collab_movie_to_idx[m] for m in liked_movie_ids if m in self.collab_movie_to_idx]
            if valid_c:
                c_sub = self.item_item_sim[valid_c].toarray().mean(axis=0)
                for rec_mid, r_c_idx in self.collab_movie_to_idx.items():
                    if rec_mid in self.movie_id_to_idx:
                        collab_sims[self.movie_id_to_idx[rec_mid]] = c_sub[r_c_idx]

        rating_scores = (self.movies_df["bayesian_rating"] / 5.0).values
        pop_scores = self.movies_df["popularity_score"].values

        final_scores = (
            w_content * content_sims +
            w_rating * rating_scores +
            w_popularity * pop_scores +
            w_collab * np.clip(collab_sims, 0, 1)
        )

        # Mask out movies the user already liked
        for mid in liked_movie_ids:
            if mid in self.movie_id_to_idx:
                final_scores[self.movie_id_to_idx[mid]] = -1.0

        top_indices = np.argsort(final_scores)[::-1][:top_k]

        results = []
        for rec_idx in top_indices:
            rec_row = self.movies_df.iloc[rec_idx].to_dict()
            rec_movie = self._format_movie_dict(rec_row)
            c_sim = float(content_sims[rec_idx])
            col_sim = float(collab_sims[rec_idx])
            score = float(round(final_scores[rec_idx], 3))

            # Explain based on preferred genres and liked movies
            matching_genres = [g for g in rec_movie.get("genres", []) if g in preferred_genres]
            reasons = []
            if matching_genres:
                reasons.append(f"Matches your taste in {', '.join(matching_genres[:2])}")
            if col_sim > 0.2:
                reasons.append("Frequently enjoyed by users with similar watchlists")
            if rec_movie.get("bayesian_rating", 0) >= 3.8:
                reasons.append(f"Highly rated ({rec_movie['rating_mean']} avg)")

            if not reasons:
                reasons.append("Thematic alignment with your selected preferences")

            rec_movie["recommendation_score"] = score
            rec_movie["content_similarity"] = round(c_sim, 3)
            rec_movie["explanation"] = {
                "summary": f"Matches your interest in {', '.join(preferred_genres[:2]) if preferred_genres else 'cinema classics'}.",
                "reasons": reasons,
                "common_genres": matching_genres,
                "shared_tags": [],
                "content_similarity_pct": int(round(c_sim * 100)),
                "collaborative_affinity_pct": int(round(max(0.0, col_sim) * 100))
            }
            results.append(rec_movie)

        return results

    def get_curated_section(self, section_type: str, genre: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Curates thematic sections:
        - 'popular': Most rated movies
        - 'highly_rated': Highest Bayesian rating with threshold >= 40 ratings
        - 'hidden_gems': High rating (>= 4.0), moderate count (15-65 ratings)
        - 'genre': Top movies in a specific genre
        """
        df = self.movies_df.copy()

        if section_type == "popular":
            subset = df.sort_values(by="rating_count", ascending=False).head(limit)
        elif section_type == "highly_rated":
            subset = df[df["rating_count"] >= 35].sort_values(by="bayesian_rating", ascending=False).head(limit)
        elif section_type == "hidden_gems":
            subset = df[(df["rating_count"] >= 15) & (df["rating_count"] <= 65) & (df["rating_mean"] >= 4.0)].sort_values(
                by="rating_mean", ascending=False
            ).head(limit)
        elif section_type == "genre" and genre:
            # Filter by genre
            matches = df[df["genre_list"].apply(lambda g_list: genre.lower() in [g.lower() for g in (g_list or [])])]
            subset = matches.sort_values(by="bayesian_rating", ascending=False).head(limit)
        else:
            subset = df.sort_values(by="bayesian_rating", ascending=False).head(limit)

        results = []
        for _, row in subset.iterrows():
            movie = self._format_movie_dict(row.to_dict())
            results.append(movie)
        return results

    def search_movies(
        self,
        query: str = "",
        genre: Optional[str] = None,
        min_rating: float = 0.0,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        sort_by: str = "relevance",  # relevance, rating, count, year
        limit: int = 24,
        offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Rich search supporting title query, genre filter, rating threshold, release year, and sorting.
        """
        df = self.movies_df.copy()

        # Genre filter
        if genre and genre != "All":
            df = df[df["genre_list"].apply(lambda g_list: genre.lower() in [g.lower() for g in (g_list or [])])]

        # Minimum rating filter
        if min_rating > 0.0:
            df = df[df["rating_mean"] >= min_rating]

        # Year range filter
        if min_year is not None:
            df = df[df["release_year"].fillna(0) >= min_year]
        if max_year is not None:
            df = df[df["release_year"].fillna(9999) <= max_year]

        # Query search
        if query and query.strip():
            q = query.strip().lower()
            # Title match
            title_mask = df["clean_title"].str.lower().str.contains(q, na=False)
            # Director / Actor match
            dir_mask = df["director"].str.lower().str.contains(q, na=False)
            actor_mask = df["actors"].str.lower().str.contains(q, na=False)
            tag_mask = df["tags_list"].apply(lambda tags: any(q in t.lower() for t in (tags or [])))

            df = df[title_mask | dir_mask | actor_mask | tag_mask]

        total_count = len(df)

        # Sorting
        if sort_by == "rating":
            df = df.sort_values(by="rating_mean", ascending=False)
        elif sort_by == "bayesian":
            df = df.sort_values(by="bayesian_rating", ascending=False)
        elif sort_by == "count" or sort_by == "popularity":
            df = df.sort_values(by="rating_count", ascending=False)
        elif sort_by == "year":
            df = df.sort_values(by="release_year", ascending=False)
        else:
            # Default relevance: Bayesian rating weighted by popularity
            df = df.sort_values(by=["bayesian_rating", "rating_count"], ascending=[False, False])

        paginated = df.iloc[offset: offset + limit]
        results = [self._format_movie_dict(r.to_dict()) for _, r in paginated.iterrows()]

        return results, total_count


# Global recommender singleton
engine = RecommendationEngine()


# ======================================================================
# PART 3: OFFLINE MODEL EVALUATION BENCHMARK
# ======================================================================
"""
CineSenseAI Model Evaluation Protocol
Evaluates Popularity Baseline, Content-Based, and Hybrid models on held-out user interactions.
Computes: Precision@K, Recall@K, Hit Rate@K, Catalog Coverage, and Intra-List Diversity.
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any
from sklearn.metrics.pairwise import cosine_similarity
from backend.app.ml.recommender import RecommendationEngine


def run_evaluation(data_dir: str = "data/processed", sample_users: int = 150) -> Dict[str, Any]:
    print("Initializing recommender for evaluation...")
    engine = RecommendationEngine(data_dir=data_dir)
    engine.initialize()

    ratings_path = "data/raw/ml-latest-small/ratings.csv"
    ratings = pd.read_csv(ratings_path)

    # Filter to active users with at least 20 ratings
    user_counts = ratings.groupby("userId").size()
    eligible_users = user_counts[user_counts >= 20].index.values

    # Sample users for fast reproducible evaluation
    np.random.seed(42)
    eval_user_ids = np.random.choice(eligible_users, size=min(sample_users, len(eligible_users)), replace=False)

    print(f"Evaluating {len(eval_user_ids)} users with held-out preference sets...")

    # Data structures for metrics
    models = ["Popularity Baseline", "Content-Based", "Hybrid (CineSenseAI)"]
    metrics = {
        m: {
            "p5_list": [],
            "p10_list": [],
            "r10_list": [],
            "hit_list": [],
            "recommended_items": set(),
            "diversity_list": []
        }
        for m in models
    }

    # Precompute popular top-10 items for baseline
    top_popular_mids = [m["movieId"] for m in engine.get_curated_section("popular", limit=20)]

    for u_idx, uid in enumerate(eval_user_ids):
        u_ratings = ratings[ratings["userId"] == uid].sort_values("timestamp")
        
        # Positive interactions (rating >= 3.5 or >= 4.0)
        positives = u_ratings[u_ratings["rating"] >= 4.0]
        if len(positives) < 5:
            positives = u_ratings[u_ratings["rating"] >= 3.5]
        if len(positives) < 4:
            continue

        # Split 80% train, 20% test
        n_test = max(1, int(len(positives) * 0.25))
        train_pos = positives.iloc[:-n_test]
        test_pos = positives.iloc[-n_test:]
        
        test_mids = set(test_pos["movieId"].values)
        train_mids = list(train_pos["movieId"].values)

        if not test_mids or not train_mids:
            continue

        # 1. Popularity Baseline Recommendations (exclude train)
        pop_recs = [m for m in top_popular_mids if m not in train_mids][:10]
        
        # 2. Content-Based Recommendations (w_content=1.0, w_collab=0.0)
        cb_rec_objs = engine.recommend_for_user_profile(
            liked_movie_ids=train_mids[-5:],
            preferred_genres=[],
            top_k=10,
            w_content=1.0,
            w_rating=0.0,
            w_popularity=0.0,
            w_collab=0.0
        )
        cb_recs = [r["movieId"] for r in cb_rec_objs]

        # 3. Hybrid Recommendations (CineSenseAI balanced weights)
        hybrid_rec_objs = engine.recommend_for_user_profile(
            liked_movie_ids=train_mids[-5:],
            preferred_genres=[],
            top_k=10,
            w_content=0.55,
            w_rating=0.25,
            w_popularity=0.10,
            w_collab=0.10
        )
        hybrid_recs = [r["movieId"] for r in hybrid_rec_objs]

        rec_dict = {
            "Popularity Baseline": pop_recs,
            "Content-Based": cb_recs,
            "Hybrid (CineSenseAI)": hybrid_recs
        }

        # Calculate metrics for each model
        for m_name, rec_list in rec_dict.items():
            if not rec_list:
                continue

            # Update catalog coverage set
            metrics[m_name]["recommended_items"].update(rec_list)

            # Precision@5
            hits_5 = len(set(rec_list[:5]).intersection(test_mids))
            metrics[m_name]["p5_list"].append(hits_5 / 5.0)

            # Precision@10 & Recall@10
            hits_10 = len(set(rec_list[:10]).intersection(test_mids))
            metrics[m_name]["p10_list"].append(hits_10 / 10.0)
            metrics[m_name]["r10_list"].append(hits_10 / len(test_mids))
            metrics[m_name]["hit_list"].append(1.0 if hits_10 > 0 else 0.0)

            # Diversity (Mean Pairwise Cosine Distance of TF-IDF vectors)
            if len(rec_list) >= 2:
                valid_indices = [engine.movie_id_to_idx[mid] for mid in rec_list if mid in engine.movie_id_to_idx]
                if len(valid_indices) >= 2:
                    sub_matrix = engine.tfidf_matrix[valid_indices]
                    sim_mat = cosine_similarity(sub_matrix)
                    # Pairwise distance = 1 - sim
                    triu_indices = np.triu_indices(len(valid_indices), k=1)
                    pairwise_distances = 1.0 - sim_mat[triu_indices]
                    metrics[m_name]["diversity_list"].append(float(np.mean(pairwise_distances)))

    total_catalog_size = len(engine.movies_df)

    results = {
        "evaluation_info": {
            "users_evaluated": len(metrics["Hybrid (CineSenseAI)"]["p10_list"]),
            "catalog_size": total_catalog_size,
            "protocol": "Held-out test set (25% positive user ratings withheld, threshold >= 3.5-4.0)"
        },
        "models": []
    }

    for m_name in models:
        p5 = float(np.mean(metrics[m_name]["p5_list"])) if metrics[m_name]["p5_list"] else 0.0
        p10 = float(np.mean(metrics[m_name]["p10_list"])) if metrics[m_name]["p10_list"] else 0.0
        r10 = float(np.mean(metrics[m_name]["r10_list"])) if metrics[m_name]["r10_list"] else 0.0
        hit = float(np.mean(metrics[m_name]["hit_list"])) if metrics[m_name]["hit_list"] else 0.0
        cov = float(len(metrics[m_name]["recommended_items"]) / total_catalog_size * 100)
        div = float(np.mean(metrics[m_name]["diversity_list"])) if metrics[m_name]["diversity_list"] else 0.0

        model_entry = {
            "name": m_name,
            "precision_at_5": round(p5, 4),
            "precision_at_10": round(p10, 4),
            "recall_at_10": round(r10, 4),
            "hit_rate_at_10": round(hit, 4),
            "catalog_coverage_pct": round(cov, 2),
            "intra_list_diversity": round(div, 4),
            "unique_items_recommended": len(metrics[m_name]["recommended_items"])
        }
        results["models"].append(model_entry)
        print(f"\n[{m_name}]")
        print(f"  Precision@5:  {p5:.4f}")
        print(f"  Precision@10: {p10:.4f}")
        print(f"  Recall@10:    {r10:.4f}")
        print(f"  Hit Rate@10:  {hit * 100:.1f}%")
        print(f"  Coverage:     {cov:.2f}% ({len(metrics[m_name]['recommended_items'])} movies)")
        print(f"  Diversity:    {div:.4f}")

    eval_out_path = os.path.join(data_dir, "evaluation_results.json")
    with open(eval_out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved evaluation results to {eval_out_path}")
    return results


if __name__ == "__main__":
    run_evaluation()
