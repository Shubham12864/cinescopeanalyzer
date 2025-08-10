import { Skeleton, ShimmerSkeleton, ProgressiveSkeleton } from "@/components/ui/skeleton"

export function MovieCardSkeleton({ delay = 0 }: { delay?: number }) {
  return (
    <div 
      className="bg-gray-800/50 rounded-lg overflow-hidden border border-gray-700/50 transition-all duration-300 hover:border-gray-600/50"
      style={{ animationDelay: `${delay}ms` }}
    >
      {/* Image skeleton with progressive loading */}
      <div className="aspect-[2/3] bg-gray-700/50 relative">
        <ProgressiveSkeleton className="w-full h-full" delay={delay} />
        
        {/* Rating badge skeleton */}
        <div className="absolute top-2 right-2">
          <ProgressiveSkeleton className="w-12 h-6 rounded-full" delay={delay + 100} />
        </div>
        
        {/* Play button overlay skeleton */}
        <div className="absolute inset-0 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity duration-300">
          <ProgressiveSkeleton className="w-12 h-12 rounded-full" delay={delay + 200} />
        </div>
      </div>
      
      {/* Content skeleton with staggered animations */}
      <div className="p-4 space-y-3">
        {/* Title skeleton */}
        <ProgressiveSkeleton className="h-6 w-3/4" delay={delay + 150} />
        
        {/* Year and genre skeleton */}
        <div className="flex items-center gap-2">
          <ProgressiveSkeleton className="h-4 w-12" delay={delay + 200} />
          <ProgressiveSkeleton className="h-4 w-1 rounded-full" delay={delay + 250} />
          <ProgressiveSkeleton className="h-4 w-16" delay={delay + 300} />
        </div>
        
        {/* Plot skeleton with varying widths for realism */}
        <div className="space-y-2">
          <ProgressiveSkeleton className="h-4 w-full" delay={delay + 350} />
          <ProgressiveSkeleton className="h-4 w-4/5" delay={delay + 400} />
          <ProgressiveSkeleton className="h-4 w-3/5" delay={delay + 450} />
        </div>
        
        {/* Cast skeleton */}
        <div className="space-y-2">
          <ProgressiveSkeleton className="h-4 w-16" delay={delay + 500} />
          <div className="flex flex-wrap gap-1">
            <ProgressiveSkeleton className="h-6 w-20 rounded-full" delay={delay + 550} />
            <ProgressiveSkeleton className="h-6 w-24 rounded-full" delay={delay + 600} />
            <ProgressiveSkeleton className="h-6 w-18 rounded-full" delay={delay + 650} />
          </div>
        </div>
        
        {/* Action buttons skeleton */}
        <div className="flex gap-2 pt-2">
          <ProgressiveSkeleton className="h-9 flex-1 rounded-md" delay={delay + 700} />
          <ProgressiveSkeleton className="h-9 w-9 rounded-md" delay={delay + 750} />
        </div>
      </div>
    </div>
  )
}

export function MovieGridSkeleton({ count = 12 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-6">
      {Array.from({ length: count }).map((_, index) => (
        <MovieCardSkeleton 
          key={index} 
          delay={index * 50} // Stagger animations for smooth appearance
        />
      ))}
    </div>
  )
}

// Enhanced skeleton for search results with different layout
export function SearchResultsSkeleton({ count = 8 }: { count?: number }) {
  return (
    <div className="space-y-8">
      {/* Search header skeleton */}
      <div className="px-4 lg:px-8">
        <div className="flex items-center gap-3 mb-6">
          <ShimmerSkeleton className="w-6 h-6 rounded-full" />
          <ShimmerSkeleton className="h-8 w-64" />
        </div>
      </div>
      
      {/* Grid skeleton */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-6 gap-8 px-6 lg:px-12 max-w-screen-2xl mx-auto">
        {Array.from({ length: count }).map((_, index) => (
          <MovieCardSkeleton 
            key={index} 
            delay={index * 75} // Slightly longer delay for search results
          />
        ))}
      </div>
    </div>
  )
}

// Row skeleton for home page sections
export function MovieRowSkeleton({ title, count = 15 }: { title: string; count?: number }) {
  return (
    <div className="space-y-4">
      {/* Row title skeleton */}
      <div className="px-4 lg:px-8">
        <ShimmerSkeleton className="h-8 w-48" />
      </div>
      
      {/* Horizontal scrolling skeleton */}
      <div className="flex gap-4 px-4 lg:px-8 overflow-hidden">
        {Array.from({ length: count }).map((_, index) => (
          <div key={index} className="flex-shrink-0 w-48">
            <MovieCardSkeleton delay={index * 30} />
          </div>
        ))}
      </div>
    </div>
  )
}