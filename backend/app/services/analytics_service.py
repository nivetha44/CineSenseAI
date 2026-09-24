"""
Analytics Service provides real dataset statistics, genre distribution,
rating breakdowns, and offline model evaluation metrics.
"""

import os
import json
from typing import Dict, Any, List
from backend.app.ml.recommender import engine


class AnalyticsService:
    @staticmethod
    def get_summary() -> Dict[str, Any]:
        path = "data/processed/analytics_summary.json"
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {
            "error": "Analytics data not generated yet."
        }

    @staticmethod
    def get_genre_analytics() -> List[Dict[str, Any]]:
        summary = AnalyticsService.get_summary()
        return summary.get("genre_distribution", [])

    @staticmethod
    def get_rating_distribution() -> List[Dict[str, Any]]:
        summary = AnalyticsService.get_summary()
        return summary.get("rating_distribution", [])

    @staticmethod
    def get_decade_distribution() -> List[Dict[str, Any]]:
        summary = AnalyticsService.get_summary()
        return summary.get("decade_distribution", [])

    @staticmethod
    def get_model_info() -> Dict[str, Any]:
        eval_path = "data/processed/evaluation_results.json"
        eval_data = {}
        if os.path.exists(eval_path):
            with open(eval_path, "r") as f:
                eval_data = json.load(f)

        feature_count = engine.tfidf_matrix.shape[1] if engine.tfidf_matrix is not None else 0
        total_movies = len(engine.movies_df)

        return {
            "model_name": "CineSenseAI Hybrid Content-Collaborative Recommender",
            "architecture": "TF-IDF (1-2 ngrams) + Cosine Similarity + Item-Item Co-rating Affinity + Bayesian Prior Ranking",
            "total_movies": total_movies,
            "feature_count": feature_count,
            "similarity_metric": "Cosine Similarity (Vectorized L2 Dot Product)",
            "default_weights": {
                "content_similarity": 0.55,
                "bayesian_rating": 0.25,
                "popularity_score": 0.10,
                "collaborative_affinity": 0.10
            },
            "evaluation_metrics": eval_data,
            "last_trained": "Live In-Memory (MovieLens 100k Verified)"
        }
