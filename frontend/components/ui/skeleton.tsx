import { cn } from "@/lib/utils"

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-md bg-gradient-to-r from-gray-800 via-gray-700 to-gray-800 bg-[length:200%_100%]",
        className
      )}
      {...props}
    />
  )
}

// Enhanced skeleton with shimmer effect for better loading UX
function ShimmerSkeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-md bg-gray-800",
        className
      )}
      {...props}
    >
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-gray-600/40 to-transparent animate-shimmer" />
    </div>
  )
}

// Progressive skeleton that starts with shimmer then transitions to pulse
function ProgressiveSkeleton({
  className,
  delay = 0,
  ...props
}: React.HTMLAttributes<HTMLDivElement> & { delay?: number }) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-md bg-gray-800",
        className
      )}
      style={{ animationDelay: `${delay}ms` }}
      {...props}
    >
      {/* Initial shimmer effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-gray-600/30 to-transparent animate-shimmer" />
      
      {/* Secondary pulse effect with delay */}
      <div 
        className="absolute inset-0 bg-gradient-to-r from-gray-800 via-gray-700 to-gray-800 animate-pulse opacity-0 animate-fade-in-delayed"
        style={{ animationDelay: `${delay + 800}ms` }}
      />
    </div>
  )
}

// Skeleton with smooth transitions for better perceived performance
function SmoothSkeleton({
  className,
  isLoading = true,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement> & { 
  isLoading?: boolean
  children?: React.ReactNode 
}) {
  return (
    <div className={cn("relative", className)} {...props}>
      {/* Skeleton overlay */}
      <div
        className={cn(
          "absolute inset-0 rounded-md bg-gray-800 transition-opacity duration-500 ease-out",
          isLoading ? "opacity-100" : "opacity-0 pointer-events-none"
        )}
      >
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-gray-600/30 to-transparent animate-shimmer" />
      </div>
      
      {/* Content */}
      <div
        className={cn(
          "transition-opacity duration-500 ease-out",
          isLoading ? "opacity-0" : "opacity-100"
        )}
      >
        {children}
      </div>
    </div>
  )
}

export { Skeleton, ShimmerSkeleton, ProgressiveSkeleton, SmoothSkeleton }