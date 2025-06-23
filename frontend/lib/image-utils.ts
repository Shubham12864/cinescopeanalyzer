/**
 * Image utilities for handling movie posters
 * Prioritizes OMDB and scraped sources over TMDB
 */

import type { Movie } from '@/types/movie'

export function getBestPosterUrl(movie: Movie): string {
  console.log('🖼️ Getting poster for:', movie.title, {
    omdbPoster: movie.omdbPoster,
    scrapedPoster: movie.scrapedPoster,
    imdbPoster: movie.imdbPoster,
    poster: movie.poster
  })

  // Priority 1: OMDB poster (highest quality, most reliable)
  if (movie.omdbPoster && movie.omdbPoster !== "N/A") {
    console.log('✅ Using OMDB poster for:', movie.title)
    return movie.omdbPoster
  }
  
  // Priority 2: Scraped poster (from IMDb, Rotten Tomatoes, etc.)
  if (movie.scrapedPoster && movie.scrapedPoster !== "N/A") {
    console.log('✅ Using scraped poster for:', movie.title)
    return movie.scrapedPoster
  }
  
  // Priority 3: IMDB poster
  if (movie.imdbPoster && movie.imdbPoster !== "N/A") {
    console.log('✅ Using IMDB poster for:', movie.title)
    return movie.imdbPoster
  }

  // Priority 4: Direct HTTP/HTTPS URLs (but skip TMDB)
  if (movie.poster && movie.poster !== "N/A" && movie.poster.startsWith("http")) {
    // Skip TMDB URLs in favor of fallback
    if (movie.poster.includes("tmdb")) {
      console.log('⚠️ Skipping TMDB poster for:', movie.title)
      return generateFallbackPoster(movie.title)
    }
    console.log('✅ Using direct poster URL for:', movie.title)
    return movie.poster
  }
  
  // Priority 5: OMDB-style poster URLs from main poster field
  if (movie.poster && (movie.poster.includes("media-amazon") || movie.poster.includes("imdb-api"))) {
    console.log('✅ Using OMDB-style poster for:', movie.title)
    return movie.poster
  }
  
  // Final fallback with movie title
  console.log('🔄 Using fallback poster for:', movie.title)
  return generateFallbackPoster(movie.title)
}

export function generateFallbackPoster(title: string, width = 500, height = 750): string {
  const encodedTitle = encodeURIComponent(title.slice(0, 20))
  return `https://via.placeholder.com/${width}x${height}/1a1a1a/ffffff?text=${encodedTitle}`
}

export function isValidImageUrl(url: string | null | undefined): boolean {
  if (!url || url === "N/A") return false
  if (url.includes("placeholder")) return false
  if (url.includes("tmdb")) return false // Avoid TMDB per requirements
  return url.startsWith("http")
}

export function getPosterSourceType(url: string): 'omdb' | 'scraped' | 'imdb' | 'tmdb' | 'fallback' | 'unknown' {
  if (!url || url === "N/A") return 'fallback'
  if (url.includes("placeholder")) return 'fallback'
  if (url.includes("tmdb")) return 'tmdb'
  if (url.includes("media-amazon") || url.includes("imdb-api")) return 'omdb'
  if (url.includes("imdb")) return 'imdb'
  if (url.startsWith("http")) return 'scraped'
  return 'unknown'
}
