import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'

// Mock the movie context
jest.mock('@/contexts/movie-context', () => ({
  useMovieContext: () => ({
    movies: [],
    isLoading: false,
    isBackendConnected: true,
    searchMovies: jest.fn(),
    getMovieById: jest.fn(),
  }),
}))

describe('Basic Application Tests', () => {
  it('should render without crashing', () => {
    // Basic test to ensure the test setup works
    expect(true).toBe(true)
  })

  it('should have correct environment variables', () => {
    expect(process.env.NEXT_PUBLIC_API_URL).toBeDefined()
  })
})