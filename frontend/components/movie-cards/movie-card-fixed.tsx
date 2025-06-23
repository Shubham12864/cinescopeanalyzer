"use client"

import React from "react"
import { Star, Calendar, Play, Info } from "lucide-react"
import { useRouter } from "next/navigation"
import { useMovieContext } from "@/contexts/movie-context"
import { Button } from "@/components/ui/button"
import { MovieImage } from "@/components/ui/movie-image"
import { formatRating } from "@/lib/api"
import { type Movie } from "@/types/movie"

interface MovieCardProps {
  movie: Movie
}

export function MovieCard({ movie }: MovieCardProps) {
  const router = useRouter()
  const { setSelectedMovie, analyzeMovie, isBackendConnected } = useMovieContext()
  
  const getImageSrc = () => {
    console.log(`🎬 [${movie.title}] Checking image sources...`, {
      poster: movie.poster,
      omdbPoster: movie.omdbPoster,
      scrapedPoster: movie.scrapedPoster,
      imdbPoster: movie.imdbPoster
    })

    // Priority 1: Backend poster field (this is what the API returns)
    if (movie.poster && movie.poster !== "N/A" && !movie.poster.includes('tmdb')) {
      console.log(`🎬 [${movie.title}] Using backend poster:`, movie.poster)
      return movie.poster
    }

    // Priority 2: OMDB poster (for mock data)
    if (movie.omdbPoster && movie.omdbPoster !== "N/A") {
      console.log(`🎬 [${movie.title}] Using OMDB poster:`, movie.omdbPoster)
      return movie.omdbPoster
    }
    
    // Priority 3: Scraped poster 
    if (movie.scrapedPoster && movie.scrapedPoster !== "N/A") {
      console.log(`🎬 [${movie.title}] Using scraped poster:`, movie.scrapedPoster)
      return movie.scrapedPoster
    }
    
    // Priority 4: IMDB poster
    if (movie.imdbPoster && movie.imdbPoster !== "N/A") {
      console.log(`🎬 [${movie.title}] Using IMDB poster:`, movie.imdbPoster)
      return movie.imdbPoster
    }

    // Skip TMDB URLs and any other cases - use fallback
    console.log(`🎬 [${movie.title}] No valid poster found, using fallback`)
    return null
  }

  const handleViewDetails = () => {
    setSelectedMovie(movie)
    router.push(`/movies/${movie.id}`)
  }

  const handleAnalyze = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (isBackendConnected) {
      analyzeMovie(movie.id)
      router.push(`/movies/${movie.id}/analysis`)
    } else {
      router.push(`/movies/${movie.id}/analysis`)
    }
  }

  return (
    <div
      className="bg-gray-900/80 backdrop-blur-sm rounded-2xl overflow-hidden cursor-pointer group relative border border-gray-800 hover:border-red-500/50 transition-all duration-300 hover:scale-105 hover:-translate-y-2"
      onClick={handleViewDetails}
    >
      <div className="relative aspect-[3/4] overflow-hidden">
        <MovieImage
          src={getImageSrc()}
          alt={movie.title}
          fill
          className="object-cover transition-transform duration-500 group-hover:scale-110"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        
        {/* Action Buttons Overlay */}
        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-300">
          <div className="flex gap-2">
            <Button size="sm" variant="secondary" className="bg-white/20 text-white border-white/30 hover:bg-white/30">
              <Play className="w-4 h-4 mr-1" />
              Watch
            </Button>
            <Button size="sm" variant="secondary" className="bg-white/20 text-white border-white/30 hover:bg-white/30" onClick={handleAnalyze}>
              <Info className="w-4 h-4 mr-1" />
              Analyze
            </Button>
          </div>
        </div>

        {/* Rating Badge */}
        <div className="absolute top-2 right-2 bg-black/70 backdrop-blur-sm rounded-full px-2 py-1 flex items-center gap-1">
          <Star className="w-3 h-3 text-yellow-400 fill-current" />
          <span className="text-white text-xs font-medium">
            {formatRating(movie.rating || 0)}
          </span>
        </div>
      </div>

      <div className="p-4">
        <h3 className="font-semibold text-white text-lg mb-2 line-clamp-2 group-hover:text-red-400 transition-colors">
          {movie.title}
        </h3>
        
        <div className="flex items-center gap-3 mb-3 text-sm text-gray-400">
          <div className="flex items-center gap-1">
            <Calendar className="w-4 h-4" />
            <span>{movie.year}</span>
          </div>
          <div className="flex items-center gap-1">
            <Star className="w-4 h-4 text-yellow-400" />
            <span>{formatRating(movie.rating || 0)}</span>
          </div>
        </div>
        
        <div className="flex flex-wrap gap-1 mb-3">
          {movie.genre?.slice(0, 2).map((genre) => (
            <span
              key={genre}
              className="bg-red-600/20 text-red-300 px-2 py-1 rounded-full text-xs border border-red-600/30"
            >
              {genre}
            </span>
          ))}
          {movie.genre && movie.genre.length > 2 && (
            <span className="bg-gray-600/20 text-gray-300 px-2 py-1 rounded-full text-xs border border-gray-600/30">
              +{movie.genre.length - 2}
            </span>
          )}
        </div>
          <p className="text-gray-300 text-sm leading-relaxed mb-4 text-justify">
          {(() => {
            const plot = movie.plot || '';
            if (!plot || plot === 'No plot available.' || plot === 'N/A') {
              return `Discover the story of ${movie.title}, a captivating ${movie.genre?.[0]?.toLowerCase() || 'movie'} from ${movie.year}.`;
            }
            
            // Smart truncation that doesn't cut words
            if (plot.length > 120) {
              const truncated = plot.slice(0, 120);
              const lastSpace = truncated.lastIndexOf(' ');
              return lastSpace > 90 ? `${truncated.slice(0, lastSpace)}...` : `${truncated}...`;
            }
            
            return plot;
          })()}
        </p>

        <div className="flex gap-2">
          <Button size="sm" className="flex-1 bg-red-600 hover:bg-red-700 text-white" onClick={handleViewDetails}>
            <Info className="w-4 h-4 mr-1" />
            Details
          </Button>
          <Button size="sm" variant="outline" className="border-gray-600 text-gray-300 hover:bg-gray-800" onClick={handleAnalyze}>
            <Play className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
