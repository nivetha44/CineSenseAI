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
