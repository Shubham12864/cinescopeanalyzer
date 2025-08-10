"use client"

import { useState, useEffect } from 'react'

export function ProxyImageTest() {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  const originalUrl = "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg"
  const proxyUrl = `${API_BASE_URL}/api/movies/image-proxy?url=${encodeURIComponent(originalUrl)}`
  
  return (
    <div className="p-4 bg-green-900 text-white">
      <h2 className="text-xl font-bold mb-4">🔄 Proxy Image Test</h2>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 bg-green-800 border-2 border-green-500">
          <h3 className="mb-2">Direct Amazon URL</h3>
          <img 
            src={originalUrl}
            alt="Direct Amazon"
            className="w-32 h-48 object-cover border-2 border-red-500"
            onLoad={() => console.log('✅ Direct Amazon image loaded')}
            onError={() => console.log('❌ Direct Amazon image failed')}
          />
        </div>
        
        <div className="p-4 bg-green-800 border-2 border-green-500">
          <h3 className="mb-2">Via Backend Proxy</h3>
          <img 
            src={proxyUrl}
            alt="Proxy Amazon"
            className="w-32 h-48 object-cover border-2 border-blue-500"
            onLoad={() => console.log('✅ Proxy image loaded')}
            onError={() => console.log('❌ Proxy image failed')}
          />
        </div>
      </div>
      
      <div className="mt-4 text-xs">
        <p><strong>Original URL:</strong> {originalUrl}</p>
        <p><strong>Proxy URL:</strong> {proxyUrl}</p>
      </div>
    </div>
  )
}
