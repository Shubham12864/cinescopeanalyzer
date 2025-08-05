/**
 * Enhanced API Integration with Azure Cosmos DB Caching
 * High-performance frontend API client with intelligent caching
 */

// Base configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://cinescopeanalyzer-production.up.railway.app';
const API_V2_BASE = `${API_BASE_URL}/api/v2`;

// API client configuration
const defaultHeaders = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
};

// Response type definitions
export interface EnhancedAPIResponse<T> {
  data?: T;
  success: boolean;
  from_cache: boolean;
  response_time_ms: number;
  timestamp: string;
  enhanced: boolean;
  error?: string;
}

export interface MovieSearchResponse extends EnhancedAPIResponse<any> {
  results: Movie[];
  page: number;
  total_pages: number;
  total_results: number;
  query: string;
  limit: number;
}

export interface MovieDetailsResponse extends EnhancedAPIResponse<any> {
  movie: Movie;
}

export interface Movie {
  id: number;
  title: string;
  overview: string;
  release_date: string;
  release_year?: number;
  poster_path?: string;
  poster_url?: string;
  poster_url_high?: string;
  poster_url_low?: string;
  backdrop_path?: string;
  backdrop_url?: string;
  backdrop_url_high?: string;
  vote_average: number;
  vote_count: number;
  genre_ids?: number[];
  genres?: Genre[];
  genre_string?: string;
  runtime?: number;
  runtime_string?: string;
  adult: boolean;
  popularity: number;
  cached_at?: string;
  enhanced?: boolean;
}

export interface Genre {
  id: number;
  name: string;
}

export interface CacheStats {
  hit_rate_percent: number;
  total_hits: number;
  total_misses: number;
  total_writes: number;
  total_errors: number;
  cache_type: 'azure_cosmos' | 'memory_fallback';
  memory_fallback_active: boolean;
}

// Enhanced API client class
class EnhancedAPI {
  private baseUrl: string;
  private headers: Record<string, string>;

  constructor() {
    this.baseUrl = API_V2_BASE;
    this.headers = { ...defaultHeaders };
  }

  // Helper method for making requests
  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const config: RequestInit = {
      ...options,
      headers: {
        ...this.headers,
        ...options.headers,
      },
    };

    try {
      console.log(`🌐 API Request: ${config.method || 'GET'} ${url}`);
      const startTime = Date.now();
      
      const response = await fetch(url, config);
      
      const responseTime = Date.now() - startTime;
      console.log(`⏱️ Response time: ${responseTime}ms`);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Log cache performance
      if (data.from_cache !== undefined) {
        console.log(`${data.from_cache ? '🎯 Cache HIT' : '💾 Cache MISS'} - ${responseTime}ms`);
      }

      return data;
    } catch (error) {
      console.error(`❌ API Error for ${url}:`, error);
      throw error;
    }
  }

  // Enhanced movie search with caching
  async searchMovies(
    query: string,
    page: number = 1,
    limit: number = 20,
    forceRefresh: boolean = false
  ): Promise<MovieSearchResponse> {
    const params = new URLSearchParams({
      q: query,
      page: page.toString(),
      limit: limit.toString(),
      ...(forceRefresh && { force_refresh: 'true' }),
    });

    return this.makeRequest<MovieSearchResponse>(`/movies/search?${params}`);
  }

  // Enhanced movie details with caching
  async getMovieDetails(
    movieId: number,
    forceRefresh: boolean = false
  ): Promise<MovieDetailsResponse> {
    const params = forceRefresh ? '?force_refresh=true' : '';
    return this.makeRequest<MovieDetailsResponse>(`/movies/${movieId}${params}`);
  }

  // Enhanced popular movies with caching
  async getPopularMovies(
    page: number = 1,
    limit: number = 20,
    forceRefresh: boolean = false
  ): Promise<MovieSearchResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...(forceRefresh && { force_refresh: 'true' }),
    });

    return this.makeRequest<MovieSearchResponse>(`/movies/popular?${params}`);
  }

  // Enhanced image proxy with caching
  async getImageProxy(
    imageUrl: string,
    quality: 'low' | 'medium' | 'high' = 'medium',
    format: 'base64' | 'binary' = 'base64'
  ): Promise<{
    success: boolean;
    image_data?: string;
    content_type?: string;
    size?: number;
    quality: string;
    from_cache: boolean;
    response_time_ms: number;
    timestamp: string;
    enhanced: boolean;
    error?: string;
  }> {
    const params = new URLSearchParams({
      url: imageUrl,
      quality,
      format,
    });

    return this.makeRequest(`/images/proxy?${params}`);
  }

  // Get comprehensive cache statistics
  async getCacheStats(): Promise<{
    cache_service: CacheStats;
    image_service: {
      image_service_stats: {
        total_requests: number;
        cache_hits: number;
        downloads: number;
        processed: number;
        errors: number;
        cache_hit_rate_percent: number;
      };
      cache_stats: CacheStats;
      performance: {
        avg_cache_hit_rate: number;
        download_reduction_percent: number;
      };
    };
    system: {
      timestamp: string;
      status: string;
      azure_cosmos_enabled: boolean;
    };
  }> {
    return this.makeRequest('/cache/stats');
  }

  // Clear all caches (admin function)
  async clearAllCaches(): Promise<{
    success: boolean;
    message: string;
    timestamp: string;
  }> {
    return this.makeRequest('/cache/clear', { method: 'POST' });
  }

  // Utility: Check if Azure Cosmos DB is enabled
  async isAzureCosmosEnabled(): Promise<boolean> {
    try {
      const stats = await this.getCacheStats();
      return stats.system.azure_cosmos_enabled;
    } catch (error) {
      console.warn('Could not check Azure Cosmos DB status:', error);
      return false;
    }
  }

  // Utility: Get performance metrics
  async getPerformanceMetrics(): Promise<{
    overall_cache_hit_rate: number;
    movie_cache_hit_rate: number;
    image_cache_hit_rate: number;
    azure_enabled: boolean;
    total_requests: number;
    avg_response_time: number;
  }> {
    try {
      const stats = await this.getCacheStats();
      
      const movieCacheHitRate = stats.cache_service.hit_rate_percent;
      const imageCacheHitRate = stats.image_service.image_service_stats.cache_hit_rate_percent;
      const overallHitRate = (movieCacheHitRate + imageCacheHitRate) / 2;

      return {
        overall_cache_hit_rate: Math.round(overallHitRate * 100) / 100,
        movie_cache_hit_rate: movieCacheHitRate,
        image_cache_hit_rate: imageCacheHitRate,
        azure_enabled: stats.system.azure_cosmos_enabled,
        total_requests: stats.cache_service.total_hits + stats.cache_service.total_misses,
        avg_response_time: 0 // This would need to be tracked separately
      };
    } catch (error) {
      console.error('Error getting performance metrics:', error);
      return {
        overall_cache_hit_rate: 0,
        movie_cache_hit_rate: 0,
        image_cache_hit_rate: 0,
        azure_enabled: false,
        total_requests: 0,
        avg_response_time: 0
      };
    }
  }
}

// Create singleton instance
export const enhancedAPI = new EnhancedAPI();

// Backward compatibility with existing API
export const api = {
  searchMovies: enhancedAPI.searchMovies.bind(enhancedAPI),
  getMovieDetails: enhancedAPI.getMovieDetails.bind(enhancedAPI),
  getPopularMovies: enhancedAPI.getPopularMovies.bind(enhancedAPI),
  
  // Legacy methods that now use enhanced API
  async searchMoviesByTitle(title: string, page: number = 1) {
    const result = await enhancedAPI.searchMovies(title, page);
    return result.results || [];
  },

  async getMovieById(id: number) {
    const result = await enhancedAPI.getMovieDetails(id);
    return result.movie || null;
  },

  async getPopular(page: number = 1) {
    const result = await enhancedAPI.getPopularMovies(page);
    return result.results || [];
  }
};

// Enhanced utilities
export const cacheUtils = {
  // Force refresh all data
  async forceRefreshMovieData(movieId: number) {
    return Promise.all([
      enhancedAPI.getMovieDetails(movieId, true),
      // Could add more refresh operations here
    ]);
  },

  // Preload popular movies for better UX
  async preloadPopularMovies() {
    console.log('📦 Preloading popular movies...');
    try {
      await enhancedAPI.getPopularMovies(1, 20);
      console.log('✅ Popular movies preloaded');
    } catch (error) {
      console.warn('⚠️ Failed to preload popular movies:', error);
    }
  },

  // Performance monitoring
  async logPerformanceMetrics() {
    try {
      const metrics = await enhancedAPI.getPerformanceMetrics();
      console.log('📊 Performance Metrics:', {
        'Overall Cache Hit Rate': `${metrics.overall_cache_hit_rate}%`,
        'Movie Cache Hit Rate': `${metrics.movie_cache_hit_rate}%`,
        'Image Cache Hit Rate': `${metrics.image_cache_hit_rate}%`,
        'Azure Cosmos DB': metrics.azure_enabled ? 'Enabled' : 'Disabled',
        'Total Requests': metrics.total_requests
      });
    } catch (error) {
      console.warn('Could not log performance metrics:', error);
    }
  }
};

export default enhancedAPI;
