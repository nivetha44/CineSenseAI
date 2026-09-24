"""
Unit tests for CineSenseAI RecommendationEngine
"""

import pytest
from backend.app.ml.recommender import RecommendationEngine


@pytest.fixture(scope="module")
def rec_engine():
    engine = RecommendationEngine(data_dir="data/processed")
    engine.initialize()
    return engine


def test_engine_initialization(rec_engine):
    assert rec_engine.is_ready is True
    assert len(rec_engine.movies_df) == 9742
    assert rec_engine.tfidf_matrix is not None
    assert rec_engine.tfidf_matrix.shape[0] == 9742


def test_get_movie_by_id(rec_engine):
    movie = rec_engine.get_movie_by_id(1)
    assert movie is not None
    assert movie["movieId"] == 1
    assert "Toy Story" in movie["title"]
    assert "Adventure" in movie["genres"]
    assert "Animation" in movie["genres"]
    assert movie["rating_mean"] > 3.0


def test_get_invalid_movie_id(rec_engine):
    movie = rec_engine.get_movie_by_id(999999)
    assert movie is None


def test_recommend_for_movie(rec_engine):
    recs = rec_engine.recommend_for_movie(1, top_k=5)
    assert len(recs) == 5
    # The top recommendations for Toy Story should be other animated / adventure titles like Toy Story 2 or 3
    rec_titles = [r["title"] for r in recs]
    assert any("Toy Story" in t for t in rec_titles)
    
    # Check explainability payload
    for r in recs:
        assert "explanation" in r
        assert "reasons" in r["explanation"]
        assert len(r["explanation"]["reasons"]) > 0
        assert r["recommendation_score"] > 0.0


def test_recommend_for_invalid_movie(rec_engine):
    recs = rec_engine.recommend_for_movie(999999, top_k=5)
    assert recs == []


def test_custom_scoring_weights(rec_engine):
    # Pure content vs pure rating weight
    recs_content = rec_engine.recommend_for_movie(1, top_k=5, w_content=1.0, w_rating=0.0, w_popularity=0.0, w_collab=0.0)
    recs_rating = rec_engine.recommend_for_movie(1, top_k=5, w_content=0.0, w_rating=1.0, w_popularity=0.0, w_collab=0.0)
    
    assert len(recs_content) == 5
    assert len(recs_rating) == 5
    # The lists should not be identical when weighting differs drastically
    content_ids = [m["movieId"] for m in recs_content]
    rating_ids = [m["movieId"] for m in recs_rating]
    assert content_ids != rating_ids


def test_user_profile_recommendations(rec_engine):
    recs = rec_engine.recommend_for_user_profile(
        liked_movie_ids=[1], # Toy Story
        preferred_genres=["Animation", "Adventure"],
        top_k=6
    )
    assert len(recs) == 6
    # Seed movie should be excluded from recommendations
    assert not any(m["movieId"] == 1 for m in recs)


def test_search_and_filter(rec_engine):
    # Search title
    results, total = rec_engine.search_movies(query="Godfather", limit=5)
    assert total >= 2
    assert any("Godfather" in m["title"] for m in results)

    # Search with genre filter
    results_sci_fi, total_sci_fi = rec_engine.search_movies(genre="Sci-Fi", limit=10)
    assert total_sci_fi > 100
    for m in results_sci_fi:
        assert "Sci-Fi" in m["genres"]

    # Search with min rating
    results_rated, _ = rec_engine.search_movies(min_rating=4.5, limit=10)
    for m in results_rated:
        assert m["rating_mean"] >= 4.5
