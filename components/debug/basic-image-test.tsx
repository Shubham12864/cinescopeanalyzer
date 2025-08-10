"use client"

export function BasicImageTest() {
  const testUrl = "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg"
  
  return (
    <div className="p-4 bg-red-900 text-white">
      <h2 className="text-xl font-bold mb-4">🎯 Basic Image Test</h2>
      
      <div className="space-y-4">
        <div className="p-4 bg-red-800 border-2 border-red-500">
          <h3>Test 1: Direct img tag with fixed size</h3>
          <img 
            src={testUrl}
            alt="Basic test"
            width="200"
            height="300"
            style={{ 
              border: '3px solid yellow',
              backgroundColor: 'blue'
            }}
            onLoad={() => console.log('✅ Basic image loaded')}
            onError={() => console.log('❌ Basic image failed')}
          />
        </div>
        
        <div className="p-4 bg-red-800 border-2 border-red-500">
          <h3>Test 2: URL display</h3>
          <p className="text-xs break-all bg-black p-2">{testUrl}</p>
        </div>
        
        <div className="p-4 bg-red-800 border-2 border-red-500">
          <h3>Test 3: Network test</h3>
          <button 
            onClick={() => fetch(testUrl).then(r => console.log('Fetch result:', r.status))}
            className="bg-blue-600 p-2 rounded"
          >
            Test Network Access
          </button>
        </div>
      </div>
    </div>
  )
}
