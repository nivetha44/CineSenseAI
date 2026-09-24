"""
Pydantic schemas for CineSenseAI API
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ExplanationSchema(BaseModel):
    summary: str
    reasons: List[str] = []
    common_genres: List[str] = []
    shared_tags: List[str] = []
    content_similarity_pct: int = 0
    collaborative_affinity_pct: int = 0


class MovieSchema(BaseModel):
    movieId: int
    title: str
    original_title: Optional[str] = None
    release_year: Optional[int] = None
    genres: List[str] = []
    tags: List[str] = []
    rating_count: int = 0
    rating_mean: float = 0.0
    bayesian_rating: float = 0.0
    popularity_score: float = 0.0
    overview: Optional[str] = None
    director: Optional[str] = None
    actors: Optional[str] = None
    runtime: Optional[str] = None
    poster_url: Optional[str] = None
    imdb_code: Optional[str] = None


class RecommendedMovieSchema(MovieSchema):
    recommendation_score: float
    content_similarity: float
    explanation: ExplanationSchema


class PaginatedMoviesSchema(BaseModel):
    items: List[MovieSchema]
    total: int
    offset: int
    limit: int


class RecommendationRequestSchema(BaseModel):
    liked_movie_ids: List[int] = Field(default_factory=list, description="IDs of movies user has watched and liked")
    preferred_genres: List[str] = Field(default_factory=list, description="User's selected favorite genres")
    top_k: int = Field(default=12, ge=1, le=50)
    w_content: float = Field(default=0.55, ge=0.0, le=1.0)
    w_rating: float = Field(default=0.25, ge=0.0, le=1.0)
    w_popularity: float = Field(default=0.10, ge=0.0, le=1.0)
    w_collab: float = Field(default=0.10, ge=0.0, le=1.0)


class RatingDistributionItem(BaseModel):
    rating: float
    count: int


class GenreDistributionItem(BaseModel):
    genre: str
    movie_count: int
    avg_rating: float


class DecadeDistributionItem(BaseModel):
    decade: int
    count: int
    avg_rating: float


class AnalyticsOverviewSchema(BaseModel):
    dataset_name: str
    total_movies: int
    total_ratings: int
    total_users: int
    total_tags: int
    avg_rating: float
    min_rating: float
    max_rating: float
    rating_density_pct: float
    rating_distribution: List[RatingDistributionItem]
    genre_distribution: List[GenreDistributionItem]
    most_rated_movies: List[Dict[str, Any]]
    highest_rated_movies: List[Dict[str, Any]]
    hidden_gems: List[Dict[str, Any]]
    decade_distribution: List[DecadeDistributionItem]
    user_activity_distribution: List[Dict[str, Any]]


class ModelInfoSchema(BaseModel):
    model_name: str
    architecture: str
    feature_count: int
    similarity_metric: str
    default_weights: Dict[str, float]
    evaluation_metrics: Dict[str, Any]
    last_trained: str
