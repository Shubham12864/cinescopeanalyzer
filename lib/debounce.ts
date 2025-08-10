/**
 * Debouncing utilities for search and API calls
 */

/**
 * Generic debounce function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout | null = null

  return (...args: Parameters<T>) => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }

    timeoutId = setTimeout(() => {
      func(...args)
      timeoutId = null
    }, delay)
  }
}

/**
 * Debounce function that returns a promise
 */
export function debounceAsync<T extends (...args: any[]) => Promise<any>>(
  func: T,
  delay: number
): (...args: Parameters<T>) => Promise<ReturnType<T>> {
  let timeoutId: NodeJS.Timeout | null = null
  let pendingPromise: Promise<ReturnType<T>> | null = null

  return (...args: Parameters<T>): Promise<ReturnType<T>> => {
    // If there's already a pending promise, return it
    if (pendingPromise) {
      return pendingPromise
    }

    // Clear existing timeout
    if (timeoutId) {
      clearTimeout(timeoutId)
    }

    // Create new promise that will resolve after delay
    pendingPromise = new Promise((resolve, reject) => {
      timeoutId = setTimeout(async () => {
        try {
          const result = await func(...args)
          resolve(result)
        } catch (error) {
          reject(error)
        } finally {
          timeoutId = null
          pendingPromise = null
        }
      }, delay)
    })

    return pendingPromise
  }
}

/**
 * Specialized search debouncer with cancellation support
 */
export class SearchDebouncer {
  private timeoutId: NodeJS.Timeout | null = null
  private currentController: AbortController | null = null
  private readonly delay: number

  constructor(delay: number = 500) {
    this.delay = delay
  }

  /**
   * Debounce a search function with abort controller support
   */
  search<T>(
    searchFn: (query: string, signal?: AbortSignal) => Promise<T>,
    query: string
  ): Promise<T> {
    // Cancel any existing search
    this.cancel()

    return new Promise((resolve, reject) => {
      this.timeoutId = setTimeout(async () => {
        try {
          // Create new abort controller for this search
          this.currentController = new AbortController()
          
          console.log(`🔍 Debounced search executing: "${query}" (delay: ${this.delay}ms)`)
          const result = await searchFn(query, this.currentController.signal)
          
          // Only resolve if this search wasn't cancelled
          if (!this.currentController.signal.aborted) {
            resolve(result)
          }
        } catch (error) {
          // Only reject if this search wasn't cancelled
          if (!this.currentController?.signal.aborted) {
            reject(error)
          }
        } finally {
          this.timeoutId = null
          this.currentController = null
        }
      }, this.delay)
    })
  }

  /**
   * Cancel any pending search
   */
  cancel(): void {
    if (this.timeoutId) {
      clearTimeout(this.timeoutId)
      this.timeoutId = null
      console.log('🚫 Search debounce cancelled')
    }

    if (this.currentController) {
      this.currentController.abort()
      this.currentController = null
      console.log('🚫 Search request aborted')
    }
  }

  /**
   * Check if there's a pending search
   */
  isPending(): boolean {
    return this.timeoutId !== null
  }
}

/**
 * Create a throttled version of a function
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean = false

  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => {
        inThrottle = false
      }, limit)
    }
  }
}

export default debounce