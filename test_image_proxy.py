import requests
import urllib.parse

# Test the complete image flow
print("🔍 Testing image proxy flow...")

# 1. Search for a movie
search_response = requests.get('http://localhost:8000/api/movies/search', params={'q': 'dark knight', 'limit': 1})
movies = search_response.json()

if movies:
    movie = movies[0]
    print(f"📽️ Movie: {movie['title']}")
    print(f"🖼️ Original poster URL: {movie['poster']}")
    
    # 2. Test proxy URL
    poster_url = movie['poster']
    proxy_url = f"http://localhost:8000/api/images/proxy?url={urllib.parse.quote(poster_url)}"
    print(f"🔗 Proxy URL: {proxy_url}")
    
    # 3. Test proxy response
    proxy_response = requests.get(proxy_url)
    print(f"✅ Proxy status: {proxy_response.status_code}")
    print(f"📊 Content type: {proxy_response.headers.get('content-type')}")
    print(f"📏 Content size: {len(proxy_response.content)} bytes")
    
else:
    print("❌ No movies found in search")
