"""
Phase 4 Extended: Detailed Search Results Analysis
"""
import requests
import json

def analyze_search_results():
    """Analyze search results for different queries"""
    queries = ["batman", "inception", "marvel"]
    
    print("🔍 PHASE 4 EXTENDED: Search Results Analysis")
    print("=" * 60)
    
    for query in queries:
        print(f"\n🎬 Query: '{query}'")
        print("-" * 30)
        
        try:
            response = requests.get(f"http://localhost:8000/api/movies/search?q={query}&limit=2", timeout=10)
            
            if response.status_code == 200:
                movies = response.json()
                print(f"✅ Found {len(movies)} movies")
                
                for i, movie in enumerate(movies, 1):
                    print(f"\n  📽️  Movie {i}:")
                    print(f"     Title: {movie.get('title', 'Unknown')}")
                    print(f"     Year: {movie.get('year', 'Unknown')}")
                    print(f"     ID: {movie.get('id', 'Unknown')}")
                    
                    poster = movie.get('poster', '')
                    print(f"     Poster URL: {poster[:100]}...")
                    
                    # Analyze poster URL in detail
                    print("     🔍 Poster URL Analysis:")
                    if not poster or poster == "N/A":
                        print("       ❌ No poster URL provided")
                    elif "api/images/image-proxy" in poster:
                        print("       ✅ Using /api/images/image-proxy endpoint")
                        if poster.count("image-proxy") > 1:
                            print("       ❌ CIRCULAR REFERENCE DETECTED!")
                        else:
                            print("       ✅ Clean proxy URL")
                    elif "api/movies/image-proxy" in poster:
                        print("       ✅ Using /api/movies/image-proxy endpoint")
                    elif "m.media-amazon.com" in poster:
                        print("       ⚠️  Direct OMDB URL (not proxied)")
                    else:
                        print("       ⚠️  Unknown URL pattern")
                    
                    # Test if the poster URL actually works
                    if poster and poster != "N/A":
                        try:
                            # Try GET request first (more compatible)
                            img_response = requests.get(poster, timeout=5, stream=True)
                            if img_response.status_code == 200:
                                content_type = img_response.headers.get('content-type', 'unknown')
                                content_length = len(img_response.content) if hasattr(img_response, 'content') else 'unknown'
                                print(f"       ✅ Image loads successfully ({content_type}, {content_length} bytes)")
                            else:
                                print(f"       ❌ Image fails to load (HTTP {img_response.status_code})")
                        except Exception as e:
                            print(f"       ❌ Image request failed: {str(e)[:50]}")
                    
            else:
                print(f"❌ Search failed: HTTP {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Query failed: {e}")

if __name__ == "__main__":
    analyze_search_results()
