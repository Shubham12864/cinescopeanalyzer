"use client"

import { useEffect, useState } from 'react'

export function ImageDebugTest() {
  const [testUrls] = useState([
    'https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg',
    'https://m.media-amazon.com/images/M/MV5BMDFkYTc0MGEtZmNhMC00ZDIzLWFmNTEtODM1ZmRlYWMwMWFmXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg',
    'https://via.placeholder.com/300x450/1a1a1a/ffffff.png?text=Fallback'
  ])

  const [loadResults, setLoadResults] = useState<{[key: string]: string}>({})

  useEffect(() => {
    console.log('🧪 Image Debug Test started')
  }, [])

  const handleImageLoad = (url: string) => {
    console.log('✅ Image loaded:', url)
    setLoadResults(prev => ({ ...prev, [url]: 'loaded' }))
  }

  const handleImageError = (url: string) => {
    console.log('❌ Image failed:', url)
    setLoadResults(prev => ({ ...prev, [url]: 'failed' }))
  }

  return (
    <div className="p-4 bg-gray-900 text-white">
      <h2 className="text-xl font-bold mb-4">🧪 Image Debug Test</h2>
      
      <div className="grid grid-cols-3 gap-4">
        {testUrls.map((url, index) => (
          <div key={index} className="border border-gray-600 p-2">
            <h3 className="text-sm mb-2">Test {index + 1}</h3>
            <img
              src={url}
              alt={`Test ${index + 1}`}
              className="w-full h-48 object-cover border border-red-500"
              onLoad={() => handleImageLoad(url)}
              onError={() => handleImageError(url)}
            />
            <p className="text-xs mt-2">
              Status: {loadResults[url] || 'loading...'}
            </p>
            <p className="text-xs text-gray-400 break-all">
              URL: {url.substring(0, 50)}...
            </p>
          </div>
        ))}
      </div>
      
      <div className="mt-4 p-2 bg-gray-800 rounded">
        <h3 className="font-bold">Debug Info:</h3>
        <pre className="text-xs">{JSON.stringify(loadResults, null, 2)}</pre>
      </div>
    </div>
  )
}
