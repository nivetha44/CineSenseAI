"""
API route integration tests for CineSenseAI
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["catalog_size"] == 9742
    assert data["engine_ready"] is True


def test_genres_endpoint(client):
    res = client.get("/api/genres")
    assert res.status_code == 200
    genres = res.json()
    assert isinstance(genres, list)
    assert len(genres) >= 15
    assert "Action" in genres
    assert "Sci-Fi" in genres


def test_movies_pagination(client):
    res = client.get("/api/movies?offset=0&limit=10")
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 10
    assert data["total"] == 9742
    assert data["offset"] == 0
    assert data["limit"] == 10


def test_movie_details_valid(client):
    res = client.get("/api/movies/1")
    assert res.status_code == 200
    movie = res.json()
    assert movie["movieId"] == 1
    assert "Toy Story" in movie["title"]


def test_movie_details_invalid(client):
    res = client.get("/api/movies/999999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_search_endpoint(client):
    res = client.get("/api/search?q=Matrix")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    titles = [m["title"] for m in data["items"]]
    assert any("Matrix" in t for t in titles)


def test_recommendations_for_movie(client):
    res = client.get("/api/recommendations/1?top_k=4")
    assert res.status_code == 200
    recs = res.json()
    assert len(recs) == 4
    for r in recs:
        assert "recommendation_score" in r
        assert "explanation" in r
        assert len(r["explanation"]["reasons"]) > 0


def test_recommendations_user_profile(client):
    payload = {
        "liked_movie_ids": [1],
        "preferred_genres": ["Animation", "Comedy"],
        "top_k": 5,
        "w_content": 0.6,
        "w_rating": 0.2,
        "w_popularity": 0.1,
        "w_collab": 0.1
    }
    res = client.post("/api/recommendations", json=payload)
    assert res.status_code == 200
    recs = res.json()
    assert len(recs) == 5


def test_analytics_overview(client):
    res = client.get("/api/analytics/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["total_movies"] == 9742
    assert data["total_ratings"] == 100836
    assert data["total_users"] == 610
    assert data["avg_rating"] == 3.5
    assert len(data["rating_distribution"]) == 10


def test_model_info(client):
    res = client.get("/api/model/info")
    assert res.status_code == 200
    data = res.json()
    assert "Hybrid" in data["model_name"]
    assert data["feature_count"] > 1000
    assert "evaluation_metrics" in data
