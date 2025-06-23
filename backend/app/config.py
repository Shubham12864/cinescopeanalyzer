class Config:
    # IMDb Configuration
    IMDB_BASE_URL = "https://www.imdb.com"
    
    # Rotten Tomatoes Configuration
    RT_BASE_URL = "https://www.rottentomatoes.com"
    
    # Metacritic Configuration
    METACRITIC_BASE_URL = "https://www.metacritic.com"
    
    # Request Configuration
    TIMEOUT = 10
    MAX_RETRIES = 3
    
    # User Agent
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    # Review limits
    MAX_REVIEWS = 15
    MIN_REVIEW_LENGTH = 50