"""
Recommendation Routes for CineSenseAI
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from backend.app.models.schemas import (
    RecommendedMovieSchema,
    MovieSchema,
    RecommendationRequestSchema
)
from backend.app.services.recommendation_service import RecommendationService
from backend.app.services.movie_service import MovieService

router = APIRouter(prefix="", tags=["recommendations"])


@router.get("/recommendations/{movie_id}", response_model=List[RecommendedMovieSchema])
def get_recommendations_for_movie(
    movie_id: int,
    top_k: int = Query(default=10, ge=1, le=50),
    w_content: float = Query(default=0.55, ge=0.0, le=1.0),
    w_rating: float = Query(default=0.25, ge=0.0, le=1.0),
    w_popularity: float = Query(default=0.10, ge=0.0, le=1.0),
    w_collab: float = Query(default=0.10, ge=0.0, le=1.0)
):
    """
    Generate explainable hybrid recommendations for a seed movie.
    Returns matching features, similarity scores, and explainable rationale.
    """
    seed_movie = MovieService.get_movie_by_id(movie_id)
    if not seed_movie:
        raise HTTPException(
            status_code=404,
            detail=f"Seed movie with ID {movie_id} does not exist in the catalog."
        )

    recommendations = RecommendationService.get_movie_recommendations(
        movie_id=movie_id,
        top_k=top_k,
        w_content=w_content,
        w_rating=w_rating,
        w_popularity=w_popularity,
        w_collab=w_collab
    )
    return recommendations


@router.post("/recommendations", response_model=List[RecommendedMovieSchema])
def get_user_profile_recommendations(request: RecommendationRequestSchema):
    """
    Generate personalized recommendations based on user preferences:
    selected genres, liked movies, and customizable scoring weights.
    """
    return RecommendationService.get_user_profile_recommendations(request)


@router.get("/curated/{section_type}", response_model=List[MovieSchema])
def get_curated_section(
    section_type: str,
    genre: Optional[str] = Query(default=None),
    limit: int = Query(default=12, ge=1, le=50)
):
    """
    Curated discovery sections:
    - 'popular': Blockbusters with most user ratings
    - 'highly_rated': Highest Bayesian rating with significant review volume
    - 'hidden_gems': High average rating (>= 4.0) with moderate rating count
    - 'genre': Top movies in a given genre
    """
    valid_types = ["popular", "highly_rated", "hidden_gems", "genre"]
    if section_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid section type '{section_type}'. Valid types: {valid_types}"
        )
    return RecommendationService.get_curated_section(
        section_type=section_type,
        genre=genre,
        limit=limit
    )
