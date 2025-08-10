import { useEffect, useState } from 'react'

export function ApiResponseTest() {
  const [apiData, setApiData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const testApi = async () => {
      try {
        console.log('🔍 Fetching API data...')
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await fetch(`${API_BASE_URL}/api/movies/popular`)
        const data = await response.json()
        console.log('📦 Raw API Response:', data)
        
        if (data.value && data.value.length > 0) {
          const firstMovie = data.value[0]
          console.log('🎬 First movie poster URL:', JSON.stringify(firstMovie.poster))
          console.log('📏 URL length:', firstMovie.poster.length)
          console.log('🔍 URL contains line breaks:', /\n|\r/.test(firstMovie.poster))
          console.log('🔍 URL starts with https:', firstMovie.poster.startsWith('https'))
        }
        
        setApiData(data)
      } catch (error) {
        console.error('❌ API Error:', error)
      } finally {
        setLoading(false)
      }
    }

    testApi()
  }, [])

  if (loading) return <div className="p-4 text-white">Loading API test...</div>

  return (
    <div className="p-4 bg-gray-900 text-white">
      <h2 className="text-xl font-bold mb-4">🔍 API Response Test</h2>
      
      {apiData && apiData.value && (
        <div className="space-y-4">
          <h3 className="font-bold">First Movie Data:</h3>
          <div className="bg-gray-800 p-2 rounded">
            <p><strong>Title:</strong> {apiData.value[0].title}</p>
            <p><strong>Poster URL:</strong></p>
            <pre className="text-xs bg-gray-700 p-2 rounded mt-1 break-all">
              {JSON.stringify(apiData.value[0].poster)}
            </pre>
            <p className="mt-2"><strong>Cleaned URL:</strong></p>
            <pre className="text-xs bg-gray-700 p-2 rounded mt-1 break-all">
              {apiData.value[0].poster?.replace(/\s+/g, '').trim()}
            </pre>
          </div>
          
          <div className="bg-gray-800 p-2 rounded">
            <h4 className="font-bold">Direct Image Test:</h4>
            <img 
              src={apiData.value[0].poster?.replace(/\s+/g, '').trim()}
              alt="Direct test"
              className="w-32 h-48 object-cover border border-red-500 mt-2"
              onLoad={() => console.log('✅ Direct image loaded')}
              onError={() => console.log('❌ Direct image failed')}
            />
          </div>
        </div>
      )}
    </div>
  )
}
