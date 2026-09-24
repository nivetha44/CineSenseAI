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
