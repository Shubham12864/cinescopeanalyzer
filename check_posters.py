import requests
import json

# Get movie suggestions
response = requests.get('http://localhost:8000/api/movies/suggestions')
data = response.json()

print("Sample poster URLs from backend:")
for i, movie in enumerate(data[:3]):
    title = movie.get('title', 'Unknown')
    poster = movie.get('poster', 'No poster')
    print(f"{i+1}. {title}: {poster}")

print(f"\nTotal movies returned: {len(data)}")
