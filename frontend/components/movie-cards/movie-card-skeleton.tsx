"use client"

export function MovieCardSkeleton() {
  return (
    <div className="glass rounded-2xl overflow-hidden">
      <div className="aspect-[3/4] skeleton" />
      <div className="p-6 space-y-4">
        <div className="flex justify-between items-start">
          <div className="skeleton h-6 w-3/4 rounded" />
          <div className="skeleton h-6 w-12 rounded-lg" />
        </div>
        <div className="skeleton h-4 w-20 rounded" />
        <div className="flex gap-2">
          <div className="skeleton h-6 w-16 rounded-full" />
          <div className="skeleton h-6 w-20 rounded-full" />
        </div>
        <div className="space-y-2">
          <div className="skeleton h-4 w-full rounded" />
          <div className="skeleton h-4 w-4/5 rounded" />
          <div className="skeleton h-4 w-3/5 rounded" />
        </div>
      </div>
    </div>
  )
}
