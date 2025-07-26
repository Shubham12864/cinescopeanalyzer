"use client"

import type React from "react"

import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { ReactQueryDevtools } from "@tanstack/react-query-devtools"
import { useState } from "react"
import { MovieProvider, useMovieContext } from "@/contexts/movie-context"
import { ToastContainer } from "@/components/ui/toast"
import ChunkErrorHandler from "@/components/error-boundary/chunk-error-handler"

function ToastWrapper() {
  const { toasts, removeToast } = useMovieContext()
  return <ToastContainer toasts={toasts} onRemove={removeToast} />
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            refetchOnWindowFocus: false,
          },
        },
      }),
  )

  return (
    <QueryClientProvider client={queryClient}>
      <MovieProvider>
        <ChunkErrorHandler />
        {children}
        <ToastWrapper />
        <ReactQueryDevtools initialIsOpen={false} />
      </MovieProvider>
    </QueryClientProvider>
  )
}
