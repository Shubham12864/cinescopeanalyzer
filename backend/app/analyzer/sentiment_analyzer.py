import re
from collections import Counter
import string

# Try to import NLTK, handle gracefully if not available
try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    NLTK_AVAILABLE = True
    
    # Download required data with better error handling
    try:
        nltk.download('vader_lexicon', quiet=True)
        nltk.download('punkt', quiet=True)
    except Exception as e:
        print(f"NLTK download warning: {e}")
        NLTK_AVAILABLE = False
except ImportError:
    NLTK_AVAILABLE = False
    print("NLTK not available, using basic sentiment analysis")

# Try to import TextBlob
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("TextBlob not available, using basic sentiment analysis")

class SentimentAnalyzer:
    def __init__(self):
        try:
            from textblob import TextBlob
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self.vader = SentimentIntensityAnalyzer()
        except ImportError as e:
            print(f"Warning: Sentiment analysis dependencies not available: {e}")
            self.vader = None
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of given text"""
        if not self.vader:
            return {"sentiment": "neutral", "score": 0.0}
        
        try:
            scores = self.vader.polarity_scores(text)
            compound = scores['compound']
            
            if compound >= 0.05:
                sentiment = "positive"
            elif compound <= -0.05:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            return {
                "sentiment": sentiment,
                "score": compound,
                "detailed_scores": scores
            }
        except Exception as e:
            return {"sentiment": "neutral", "score": 0.0, "error": str(e)}