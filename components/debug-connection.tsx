"use client"

import { useEffect, useState } from 'react'
import { useMovieContext } from '@/contexts/movie-context'

export function DebugConnection() {
  const [backendStatus, setBackendStatus] = useState('checking...')
  const [suggestions, setSuggestions] = useState('checking...')
  const [apiError, setApiError] = useState('')
  const [retryCount, setRetryCount] = useState(0)
  const { isBackendConnected, movies, testConnection } = useMovieContext()
  
  useEffect(() => {
    const checkConnection = async () => {
      try {
        console.log('🔍 Debug: Starting connection check...')
        
        // Get API base URL with robust detection
        const getApiUrl = () => {
          const envUrl = process.env.NEXT_PUBLIC_API_URL
          if (envUrl) return envUrl
          
          if (typeof window !== 'undefined') {
            const host = window.location.hostname
            if (host === 'localhost' || host === '127.0.0.1') {
              return 'http://localhost:8000'
            }
          }
          return 'http://localhost:8000'
        }
        
        const API_BASE_URL = getApiUrl()
        console.log('🔍 Debug: Using API URL:', API_BASE_URL)
        
        // Test multiple endpoints
        const endpoints = ['/health', '/api/health', '/']
        let healthSuccess = false
        
        for (const endpoint of endpoints) {
          try {
            console.log(`🔍 Debug: Testing endpoint: ${API_BASE_URL}${endpoint}`)
            
            // Use AbortController for timeout
            const controller = new AbortController()
            const timeoutId = setTimeout(() => controller.abort(), 5000)
            
            const healthResponse = await fetch(`${API_BASE_URL}${endpoint}`, {
              method: 'GET',
              headers: {
                'Content-Type': 'application/json',
              },
              signal: controller.signal
            })
            
            clearTimeout(timeoutId)
            
            console.log(`🔍 Debug: ${endpoint} response status:`, healthResponse.status)
            
            if (healthResponse.ok) {
              const healthData = await healthResponse.json()
              setBackendStatus(`✅ Connected via ${endpoint}`)
              console.log('🔍 Debug: Health data:', healthData)
              healthSuccess = true
              break
            }
          } catch (endpointError) {
            console.warn(`🔍 Debug: ${endpoint} failed:`, endpointError)
            continue
          }
        }
        
        if (!healthSuccess) {
          setBackendStatus(`❌ All endpoints failed`)
          setApiError(`Backend not responding on any endpoint`)
          return
        }
        
        // Test suggestions if health check passed
        try {
          const sugController = new AbortController()
          const sugTimeoutId = setTimeout(() => sugController.abort(), 5000)
          
          const suggestionsResponse = await fetch(`${API_BASE_URL}/api/movies/suggestions?limit=4`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
            signal: sugController.signal
          })
          
          clearTimeout(sugTimeoutId)
          
          console.log('🔍 Debug: Suggestions response status:', suggestionsResponse.status)
          
          if (suggestionsResponse.ok) {
            const data = await suggestionsResponse.json()
            setSuggestions(`✅ Got ${data.length} movies`)
            console.log('🔍 Debug: Suggestions data:', data)
            setApiError('') // Clear any previous errors
          } else {
            setSuggestions(`❌ Failed: ${suggestionsResponse.status}`)
            setApiError(`Suggestions API error: ${suggestionsResponse.status}`)
          }
        } catch (sugError) {
          setSuggestions(`❌ Error: ${sugError}`)
          setApiError(`Suggestions error: ${sugError}`)
        }
        
      } catch (error) {
        console.error('🔍 Debug: Connection error:', error)
        setBackendStatus(`❌ Error: ${error}`)
        setSuggestions(`❌ Error: ${error}`)
        setApiError(`Connection error: ${error}`)
      }
    }
    
    checkConnection()
    
    // Auto-retry every 10 seconds if there's an error
    const interval = setInterval(() => {
      if (apiError || !isBackendConnected) {
        setRetryCount(prev => prev + 1)
        checkConnection()
      }
    }, 10000)
    
    return () => clearInterval(interval)
  }, [isBackendConnected, apiError])
  
  const handleManualRetry = () => {
    setRetryCount(prev => prev + 1)
    testConnection()
  }
  
  return (
    <div style={{ 
      position: 'fixed', 
      top: '10px', 
      right: '10px', 
      background: '#000', 
      color: '#fff', 
      padding: '15px', 
      borderRadius: '8px',
      fontSize: '12px',
      zIndex: 9999,
      border: '1px solid #333',
      minWidth: '280px',
      maxWidth: '350px'
    }}>
      <div style={{ marginBottom: '5px', fontWeight: 'bold', color: '#ff6b6b' }}>
        🔍 DEBUG INFO
      </div>
      <div>Backend: {backendStatus}</div>
      <div>Suggestions: {suggestions}</div>
      <div>Context Connected: {isBackendConnected ? '✅' : '❌'}</div>
      <div>Context Movies: {movies?.length || 0}</div>
      <div>Retry Count: {retryCount}</div>
      
      {apiError && (
        <div style={{ color: '#ff6b6b', marginTop: '5px', fontSize: '10px', wordBreak: 'break-word' }}>
          {apiError}
        </div>
      )}
      
      <button 
        onClick={handleManualRetry}
        style={{
          marginTop: '8px',
          padding: '4px 8px',
          background: '#333',
          color: '#fff',
          border: '1px solid #555',
          borderRadius: '4px',
          fontSize: '10px',
          cursor: 'pointer'
        }}
      >
        🔄 Retry Connection
      </button>
    </div>
  )
}
