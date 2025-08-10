// Quick test to verify image URLs from mock data
const testUrls = [
  'https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg', // The Dark Knight
  'https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg', // Inception
  'https://m.media-amazon.com/images/M/MV5BNzQzOTk3OTAtNDQ0Zi00ZTVkLWI0MTEtMDllZjNkYzNjNTc4L2ltYWdlXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg' // The Matrix
]

async function testImageUrls() {
  console.log('🔍 Testing image URLs...')
  
  for (const url of testUrls) {
    try {
      const response = await fetch(url, { method: 'HEAD' })
      console.log(`✅ ${url} - Status: ${response.status}`)
    } catch (error) {
      console.log(`❌ ${url} - Error: ${error.message}`)
    }
  }
}

// This is just for testing, can be run in browser console
if (typeof window !== 'undefined') {
  window.testImageUrls = testImageUrls
}
