export interface Explanation {
  summary: string;
  reasons: string[];
  common_genres: string[];
  shared_tags: string[];
  content_similarity_pct: number;
  collaborative_affinity_pct: number;
}

export interface Movie {
  movieId: number;
  title: string;
  original_title?: string;
  release_year?: number | null;
  genres: string[];
  tags: string[];
  rating_count: number;
  rating_mean: number;
  bayesian_rating: number;
  popularity_score: number;
  overview?: string | null;
  director?: string | null;
  actors?: string | null;
  runtime?: string | null;
  rated?: string | null;
  poster_url?: string | null;
  imdb_code?: string | null;
  recommendation_score?: number;
  content_similarity?: number;
  explanation?: Explanation;
}

export interface PaginatedMovies {
  items: Movie[];
  total: number;
  offset: number;
  limit: number;
}

export interface RecommendationRequest {
  liked_movie_ids: number[];
  preferred_genres: string[];
  top_k?: number;
  w_content?: number;
  w_rating?: number;
  w_popularity?: number;
  w_collab?: number;
}

export interface RatingDistributionItem {
  rating: number;
  count: number;
}

export interface GenreDistributionItem {
  genre: string;
  movie_count: number;
  avg_rating: number;
}

export interface DecadeDistributionItem {
  decade: number;
  count: number;
  avg_rating: number;
}

export interface AnalyticsSummary {
  dataset_name: string;
  total_movies: number;
  total_ratings: number;
  total_users: number;
  total_tags: number;
  avg_rating: number;
  min_rating: number;
  max_rating: number;
  rating_density_pct: number;
  rating_distribution: RatingDistributionItem[];
  genre_distribution: GenreDistributionItem[];
  most_rated_movies: Movie[];
  highest_rated_movies: Movie[];
  hidden_gems: Movie[];
  decade_distribution: DecadeDistributionItem[];
  user_activity_distribution: { range: string; count: number }[];
}

export interface ModelEvaluationModel {
  name: string;
  precision_at_5: number;
  precision_at_10: number;
  recall_at_10: number;
  hit_rate_at_10: number;
  catalog_coverage_pct: number;
  intra_list_diversity: number;
  unique_items_recommended: number;
}

export interface ModelInfo {
  model_name: string;
  architecture: string;
  total_movies: number;
  feature_count: number;
  similarity_metric: string;
  default_weights: {
    content_similarity: number;
    bayesian_rating: number;
    popularity_score: number;
    collaborative_affinity: number;
  };
  evaluation_metrics: {
    evaluation_info: {
      users_evaluated: number;
      catalog_size: number;
      protocol: string;
    };
    models: ModelEvaluationModel[];
  };
  last_trained: string;
}
