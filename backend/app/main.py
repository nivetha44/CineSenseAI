"""
CineSenseAI FastAPI Application Entry Point
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.ml.recommender import engine
from backend.app.api.routes.movies import router as movies_router
from backend.app.api.routes.recommendations import router as recs_router
from backend.app.api.routes.analytics import router as analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load dataset and fit TF-IDF vectorizer / collaborative matrix
    print("Starting CineSenseAI backend server...")
    if not engine.is_ready:
        engine.initialize()
    print(f"CineSenseAI Engine ready with {len(engine.movies_df)} movies.")
    yield
    # Shutdown
    print("Shutting down CineSenseAI backend server...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Data-driven, explainable Movie Recommendation System powered by TF-IDF, Cosine Similarity, and Item-Item Collaborative Filtering.",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["system"])
def health_check():
    """Health check endpoint confirming engine readiness and dataset size."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "catalog_size": len(engine.movies_df),
        "engine_ready": engine.is_ready
    }


# Include Routers with /api prefix
app.include_router(movies_router, prefix=settings.API_PREFIX)
app.include_router(recs_router, prefix=settings.API_PREFIX)
app.include_router(analytics_router, prefix=settings.API_PREFIX)

# Mount frontend production build if available
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.isdir(frontend_dist):
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Graceful JSON error handler that prevents exposing internal stack traces."""
    print(f"Unhandled server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred while processing your request. Please try again later.",
            "path": str(request.url.path)
        }
    )
