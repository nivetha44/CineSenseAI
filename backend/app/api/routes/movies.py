"""
Movie Catalog and Search Routes
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from backend.app.models.schemas import MovieSchema, PaginatedMoviesSchema
from backend.app.services.movie_service import MovieService

router = APIRouter(prefix="", tags=["movies"])


@router.get("/movies", response_model=PaginatedMoviesSchema)
def list_movies(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=24, ge=1, le=100),
    genre: Optional[str] = Query(default=None),
    sort_by: str = Query(default="relevance", pattern="^(relevance|rating|count|popularity|year|bayesian)$")
):
    """Retrieve paginated movies with optional genre filter and sorting."""
    items, total = MovieService.get_movies(
        offset=offset,
        limit=limit,
        genre=genre,
        sort_by=sort_by
    )
    return {
        "items": items,
        "total": total,
        "offset": offset,
        "limit": limit
    }


@router.get("/movies/{movie_id}", response_model=MovieSchema)
def get_movie_details(movie_id: int):
    """Retrieve detailed metadata for a specific movie by its ID."""
    movie = MovieService.get_movie_by_id(movie_id)
    if not movie:
        raise HTTPException(
            status_code=404,
            detail=f"Movie with ID {movie_id} was not found in the CineSenseAI catalog."
        )
    return movie


@router.get("/search", response_model=PaginatedMoviesSchema)
def search_movies(
    q: str = Query(default="", description="Search query matching title, director, actors, or themes"),
    genre: Optional[str] = Query(default=None),
    min_rating: float = Query(default=0.0, ge=0.0, le=5.0),
    min_year: Optional[int] = Query(default=None, ge=1900),
    max_year: Optional[int] = Query(default=None, le=2030),
    sort_by: str = Query(default="relevance"),
    limit: int = Query(default=24, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """Multi-attribute search across title, cast, directors, genres, and community tags."""
    items, total = MovieService.search_movies(
        query=q,
        genre=genre,
        min_rating=min_rating,
        min_year=min_year,
        max_year=max_year,
        sort_by=sort_by,
        limit=limit,
        offset=offset
    )
    return {
        "items": items,
        "total": total,
        "offset": offset,
        "limit": limit
    }


@router.get("/genres")
def get_genres():
    """Retrieve all available genres in the dataset."""
    return MovieService.get_all_genres()
