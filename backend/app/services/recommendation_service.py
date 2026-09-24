"""
Recommendation Service interfaces with RecommendationEngine for item-to-item,
user-preference profile recommendations, and curated discovery sections.
"""

from typing import List, Dict, Any, Optional
from backend.app.ml.recommender import engine
from backend.app.models.schemas import RecommendationRequestSchema


class RecommendationService:
    @staticmethod
    def get_movie_recommendations(
        movie_id: int,
        top_k: int = 10,
        w_content: float = 0.55,
        w_rating: float = 0.25,
        w_popularity: float = 0.10,
        w_collab: float = 0.10
    ) -> List[Dict[str, Any]]:
        return engine.recommend_for_movie(
            movie_id=movie_id,
            top_k=top_k,
            w_content=w_content,
            w_rating=w_rating,
            w_popularity=w_popularity,
            w_collab=w_collab
        )

    @staticmethod
    def get_user_profile_recommendations(req: RecommendationRequestSchema) -> List[Dict[str, Any]]:
        return engine.recommend_for_user_profile(
            liked_movie_ids=req.liked_movie_ids,
            preferred_genres=req.preferred_genres,
            top_k=req.top_k,
            w_content=req.w_content,
            w_rating=req.w_rating,
            w_popularity=req.w_popularity,
            w_collab=req.w_collab
        )

    @staticmethod
    def get_curated_section(section_type: str, genre: Optional[str] = None, limit: int = 12) -> List[Dict[str, Any]]:
        return engine.get_curated_section(section_type=section_type, genre=genre, limit=limit)
