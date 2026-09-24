"""
Movie Service handles catalog queries, details retrieval, genre listing, and search.
"""

from typing import List, Optional, Tuple, Dict, Any
from backend.app.ml.recommender import engine


class MovieService:
    @staticmethod
    def get_movies(
        offset: int = 0,
        limit: int = 24,
        genre: Optional[str] = None,
        sort_by: str = "relevance"
    ) -> Tuple[List[Dict[str, Any]], int]:
        return engine.search_movies(
            query="",
            genre=genre,
            sort_by=sort_by,
            limit=limit,
            offset=offset
        )

    @staticmethod
    def get_movie_by_id(movie_id: int) -> Optional[Dict[str, Any]]:
        return engine.get_movie_by_id(movie_id)

    @staticmethod
    def search_movies(
        query: str,
        genre: Optional[str] = None,
        min_rating: float = 0.0,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        sort_by: str = "relevance",
        limit: int = 24,
        offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        return engine.search_movies(
            query=query,
            genre=genre,
            min_rating=min_rating,
            min_year=min_year,
            max_year=max_year,
            sort_by=sort_by,
            limit=limit,
            offset=offset
        )

    @staticmethod
    def get_all_genres() -> List[str]:
        """Returns unique list of genres present in the dataset."""
        genres = set()
        for g_list in engine.movies_df.get("genre_list", []):
            if isinstance(g_list, list):
                genres.update(g_list)
        return sorted([g for g in genres if g and g != "(no genres listed)"])
