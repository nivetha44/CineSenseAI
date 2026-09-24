# CineSenseAI Dataset Documentation

## Source
- **Dataset**: GroupLens MovieLens Latest Small (`ml-latest-small`)
- **Institution**: GroupLens Research, University of Minnesota
- **URL**: https://grouplens.org/datasets/movielens/latest/
- **License**: Non-commercial educational use

## Raw Structure (`data/raw/ml-latest-small/`)
- `movies.csv`: 9,742 records (`movieId`, `title`, `genres`)
- `ratings.csv`: 100,836 records (`userId`, `movieId`, `rating`, `timestamp`)
- `tags.csv`: 3,683 records (`userId`, `movieId`, `tag`, `timestamp`)
- `links.csv`: 9,742 records (`movieId`, `imdbId`, `tmdbId`)

## Processed Structure (`data/processed/`)
- `movies_cleaned.csv` / `movies_cleaned.json`: Cleaned titles, extracted release years, normalized genres, aggregated community tags, Bayesian weighted ratings, popularity scores, and enriched directors/cast/posters.
- `analytics_summary.json`: Precomputed EDA figures, rating distributions, genre counts, and decade trends for instant API delivery.
- `evaluation_results.json`: Offline model benchmark results across Popularity, Content-Based, and Hybrid models.
- `omdb_cache.json`: Cached plot summaries, directors, cast, and posters for top movies.

## Reproduction
Run the automated preparation script to rebuild processed artifacts:
```bash
python scripts/prepare_data.py
```
