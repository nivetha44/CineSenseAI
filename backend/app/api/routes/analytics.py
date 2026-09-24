"""
Analytics and Model Evaluation Routes
"""

from typing import List, Dict, Any
from fastapi import APIRouter
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="", tags=["analytics"])


@router.get("/analytics/overview")
def get_analytics_overview() -> Dict[str, Any]:
    """Retrieve complete overview of real MovieLens statistics, density, and ratings."""
    return AnalyticsService.get_summary()


@router.get("/analytics/genres")
def get_genre_analytics() -> List[Dict[str, Any]]:
    """Retrieve genre frequencies and average ratings."""
    return AnalyticsService.get_genre_analytics()


@router.get("/analytics/ratings")
def get_rating_distribution() -> List[Dict[str, Any]]:
    """Retrieve exact rating count distribution on the 0.5 - 5.0 scale."""
    return AnalyticsService.get_rating_distribution()


@router.get("/analytics/decades")
def get_decade_distribution() -> List[Dict[str, Any]]:
    """Retrieve movie counts and average ratings across release decades."""
    return AnalyticsService.get_decade_distribution()


@router.get("/model/info")
def get_model_info() -> Dict[str, Any]:
    """Retrieve ML architecture, TF-IDF feature vocabulary size, and offline evaluation metrics."""
    return AnalyticsService.get_model_info()
