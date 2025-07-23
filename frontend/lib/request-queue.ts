/**
 * Request queue utility for optimizing concurrent requests
 */

interface QueuedRequest<T> {
  id: string
  promise: Promise<T>
  resolve: (value: T) => void
  reject: (error: any) => void
  priority: number
  timestamp: number
}

class RequestQueue {
  private queue: QueuedRequest<any>[] = []
  private activeRequests = new Map<string, Promise<any>>()
  private readonly maxConcurrent: number
  private currentlyRunning = 0
  private stats = {
    totalRequests: 0,
    completedRequests: 0,
    failedRequests: 0,
    averageResponseTime: 0
  }

  constructor(maxConcurrent: number = 6) {
    this.maxConcurrent = maxConcurrent
  }

  /**
   * Add a request to the queue with optional priority and deduplication
   */
  async enqueue<T>(
    requestFn: () => Promise<T>,
    options: {
      id?: string
      priority?: number
      deduplicate?: boolean
    } = {}
  ): Promise<T> {
    const {
      id = `req_${Date.now()}_${Math.random()}`,
      priority = 0,
      deduplicate = true
    } = options

    // Check for duplicate requests if deduplication is enabled
    if (deduplicate && this.activeRequests.has(id)) {
      console.log(`🔄 Request deduplication: reusing existing request ${id}`)
      return this.activeRequests.get(id)!
    }

    return new Promise<T>((resolve, reject) => {
      const queuedRequest: QueuedRequest<T> = {
        id,
        promise: requestFn(),
        resolve,
        reject,
        priority,
        timestamp: Date.now()
      }

      // Insert request in priority order (higher priority first)
      const insertIndex = this.queue.findIndex(req => req.priority < priority)
      if (insertIndex === -1) {
        this.queue.push(queuedRequest)
      } else {
        this.queue.splice(insertIndex, 0, queuedRequest)
      }

      console.log(`📥 Request queued: ${id} (priority: ${priority}, queue size: ${this.queue.length})`)
      this.processQueue()
    })
  }

  /**
   * Process the queue by running requests up to the concurrent limit
   */
  private async processQueue(): Promise<void> {
    if (this.currentlyRunning >= this.maxConcurrent || this.queue.length === 0) {
      return
    }

    const request = this.queue.shift()!
    this.currentlyRunning++
    this.stats.totalRequests++

    // Add to active requests for deduplication
    this.activeRequests.set(request.id, request.promise)

    console.log(`🚀 Processing request: ${request.id} (${this.currentlyRunning}/${this.maxConcurrent} active)`)

    const startTime = Date.now()

    try {
      const result = await request.promise
      const responseTime = Date.now() - startTime
      
      // Update stats
      this.stats.completedRequests++
      this.stats.averageResponseTime = 
        (this.stats.averageResponseTime * (this.stats.completedRequests - 1) + responseTime) / 
        this.stats.completedRequests

      request.resolve(result)
      console.log(`✅ Request completed: ${request.id} (${responseTime}ms)`)
    } catch (error) {
      this.stats.failedRequests++
      request.reject(error)
      console.log(`❌ Request failed: ${request.id}`, error)
    } finally {
      this.currentlyRunning--
      this.activeRequests.delete(request.id)
      
      // Process next request in queue
      this.processQueue()
    }
  }

  /**
   * Get queue statistics with performance metrics
   */
  getStats() {
    return {
      queueSize: this.queue.length,
      activeRequests: this.currentlyRunning,
      maxConcurrent: this.maxConcurrent,
      totalActive: this.activeRequests.size,
      performance: {
        totalRequests: this.stats.totalRequests,
        completedRequests: this.stats.completedRequests,
        failedRequests: this.stats.failedRequests,
        successRate: this.stats.totalRequests > 0 
          ? (this.stats.completedRequests / this.stats.totalRequests) * 100 
          : 0,
        averageResponseTime: Math.round(this.stats.averageResponseTime)
      }
    }
  }

  /**
   * Clear all queued requests (doesn't cancel active ones)
   */
  clear(): void {
    const clearedCount = this.queue.length
    this.queue = []
    console.log(`🧹 Request queue cleared: ${clearedCount} requests removed`)
  }

  /**
   * Cancel a specific request by ID
   */
  cancel(id: string): boolean {
    const index = this.queue.findIndex(req => req.id === id)
    if (index !== -1) {
      const request = this.queue.splice(index, 1)[0]
      request.reject(new Error('Request cancelled'))
      console.log(`🚫 Request cancelled: ${id}`)
      return true
    }
    return false
  }
}

// Create singleton instance for image requests - optimized for better performance
export const imageRequestQueue = new RequestQueue(6) // Increased to 6 concurrent for better image loading

// Create singleton instance for API requests
export const apiRequestQueue = new RequestQueue(4) // Reduced to 4 to prevent API overload

// High priority queue for critical requests (search, navigation)
export const priorityRequestQueue = new RequestQueue(2)

// Utility function to wrap image loading with queue
export async function queueImageLoad(
  src: string,
  priority: number = 0
): Promise<HTMLImageElement> {
  return imageRequestQueue.enqueue(
    () => {
      return new Promise<HTMLImageElement>((resolve, reject) => {
        const img = new Image()
        img.onload = () => resolve(img)
        img.onerror = reject
        img.src = src
      })
    },
    {
      id: `image:${src}`,
      priority,
      deduplicate: true
    }
  )
}

// Utility function to wrap API calls with queue
export async function queueApiCall<T>(
  apiCall: () => Promise<T>,
  id: string,
  priority: number = 0
): Promise<T> {
  return apiRequestQueue.enqueue(apiCall, {
    id,
    priority,
    deduplicate: true
  })
}

// Utility function for high-priority requests (search, navigation)
export async function queuePriorityRequest<T>(
  request: () => Promise<T>,
  id: string
): Promise<T> {
  return priorityRequestQueue.enqueue(request, {
    id,
    priority: 10, // High priority
    deduplicate: true
  })
}

// Utility to get performance stats for all queues
export function getAllQueueStats() {
  return {
    imageQueue: imageRequestQueue.getStats(),
    apiQueue: apiRequestQueue.getStats(),
    priorityQueue: priorityRequestQueue.getStats()
  }
}

export default RequestQueue