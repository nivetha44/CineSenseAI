import type {
  Movie,
  PaginatedMovies,
  RecommendationRequest,
  AnalyticsSummary,
  ModelInfo
} from '../types';

const BASE_URL = import.meta.env.VITE_API_URL || '/api';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    let errorMsg = `HTTP Error ${res.status}: ${res.statusText}`;
    try {
      const errData = await res.json();
      if (errData.detail) errorMsg = errData.detail;
      else if (errData.message) errorMsg = errData.message;
    } catch {
      // fallback to statusText
    }
    throw new Error(errorMsg);
  }

  return res.json();
}

export const api = {
  // Health
  getHealth: () => fetchJson<{ status: string; catalog_size: number; engine_ready: boolean }>('/health'),

  // Catalog & Search
  getMovies: (offset = 0, limit = 24, genre?: string, sortBy = 'relevance') => {
    const params = new URLSearchParams({
      offset: String(offset),
      limit: String(limit),
      sort_by: sortBy,
    });
    if (genre && genre !== 'All') params.append('genre', genre);
    return fetchJson<PaginatedMovies>(`/movies?${params.toString()}`);
  },

  getMovieById: (movieId: number) => fetchJson<Movie>(`/movies/${movieId}`),

  searchMovies: (params: {
    q?: string;
    genre?: string;
    minRating?: number;
    minYear?: number;
    maxYear?: number;
    sortBy?: string;
    limit?: number;
    offset?: number;
  }) => {
    const qParams = new URLSearchParams();
    if (params.q) qParams.append('q', params.q);
    if (params.genre && params.genre !== 'All') qParams.append('genre', params.genre);
    if (params.minRating && params.minRating > 0) qParams.append('min_rating', String(params.minRating));
    if (params.minYear) qParams.append('min_year', String(params.minYear));
    if (params.maxYear) qParams.append('max_year', String(params.maxYear));
    if (params.sortBy) qParams.append('sort_by', params.sortBy);
    if (params.limit) qParams.append('limit', String(params.limit));
    if (params.offset) qParams.append('offset', String(params.offset));

    return fetchJson<PaginatedMovies>(`/search?${qParams.toString()}`);
  },

  getGenres: () => fetchJson<string[]>('/genres'),

  // Curated sections
  getCurated: (sectionType: 'popular' | 'highly_rated' | 'hidden_gems' | 'genre', genre?: string, limit = 12) => {
    const params = new URLSearchParams({ limit: String(limit) });
    if (genre) params.append('genre', genre);
    return fetchJson<Movie[]>(`/curated/${sectionType}?${params.toString()}`);
  },

  // Recommendations
  getMovieRecommendations: (
    movieId: number,
    weights?: { w_content?: number; w_rating?: number; w_popularity?: number; w_collab?: number; top_k?: number }
  ) => {
    const params = new URLSearchParams();
    if (weights?.top_k) params.append('top_k', String(weights.top_k));
    if (weights?.w_content !== undefined) params.append('w_content', String(weights.w_content));
    if (weights?.w_rating !== undefined) params.append('w_rating', String(weights.w_rating));
    if (weights?.w_popularity !== undefined) params.append('w_popularity', String(weights.w_popularity));
    if (weights?.w_collab !== undefined) params.append('w_collab', String(weights.w_collab));

    return fetchJson<Movie[]>(`/recommendations/${movieId}?${params.toString()}`);
  },

  getUserRecommendations: (req: RecommendationRequest) =>
    fetchJson<Movie[]>('/recommendations', {
      method: 'POST',
      body: JSON.stringify(req),
    }),

  // Analytics
  getAnalyticsOverview: () => fetchJson<AnalyticsSummary>('/analytics/overview'),

  getModelInfo: () => fetchJson<ModelInfo>('/model/info'),
};
