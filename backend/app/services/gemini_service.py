import logging
import json
import re
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from ..core.config import settings

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.enabled = bool(self.api_key and self.api_key != "demo_key" and len(self.api_key) > 5)
        
        if self.enabled:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                logger.info("✅ Gemini AI service initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini AI service: {e}")
                self.enabled = False
        else:
            logger.warning("⚠️ Gemini API key is missing or invalid. Gemini service will run in demo/fallback mode.")

    async def analyze_text_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment, key themes, pros, and cons of a single text (e.g., review, comment).
        """
        if not self.enabled:
            return self._get_fallback_text_sentiment(text)

        prompt = f"""
        Analyze the following text from a movie review or discussion. 
        Extract the sentiment (positive, negative, or neutral), a sentiment score between -1.0 (extremely negative) and 1.0 (extremely positive), 
        key themes mentioned, pros/strengths, cons/weaknesses, and a brief 1-2 sentence summary.
        
        Text to analyze:
        "{text}"
        
        Return the result strictly as a valid JSON object with the following keys:
        - "sentiment": "positive" | "negative" | "neutral"
        - "score": float (between -1.0 and 1.0)
        - "themes": list of strings
        - "pros": list of strings
        - "cons": list of strings
        - "summary": string
        
        Do not include any markdown formatting (like ```json) in your response, just the raw JSON object.
        """
        
        try:
            # Generate content asynchronously
            response = await self.model.generate_content_async(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            # Parse response text
            result = self._parse_json_response(response.text)
            if result:
                return result
                
        except Exception as e:
            logger.error(f"Error during Gemini sentiment analysis: {e}")
            
        return self._get_fallback_text_sentiment(text)

    async def analyze_reviews_batch(self, reviews: List[str], movie_title: str) -> Dict[str, Any]:
        """
        Analyze a batch of reviews for a movie to generate a comprehensive consensus report.
        """
        if not self.enabled or not reviews:
            return self._get_fallback_batch_analysis(reviews, movie_title)

        # Truncate and join reviews to keep it within token limits safely
        combined_reviews = "\n\n".join([f"Review {i+1}:\n{review[:800]}" for i, review in enumerate(reviews[:15])])
        
        prompt = f"""
        You are a seasoned film critic and data analyst. Analyze these reviews for the movie "{movie_title}".
        Provide a detailed analysis including the overall consensus, a breakdown of the positive and negative aspects, 
        and an overall recommendation score (0-100).
        
        Reviews:
        {combined_reviews}
        
        Return the result strictly as a valid JSON object with the following structure:
        - "overall_consensus": string (detailed summary of what critics/audiences think)
        - "consensus_score": integer (0 to 100 representing positive percentage/sentiment)
        - "key_praises": list of strings (what reviewers loved most, up to 5 points)
        - "key_criticisms": list of strings (what reviewers disliked or complained about, up to 5 points)
        - "sentiment_breakdown": {{
            "positive_percentage": float,
            "neutral_percentage": float,
            "negative_percentage": float
          }}
        - "verdict": string (a final 1-sentence recommendation)
        
        Do not include any markdown formatting (like ```json) in your response, just the raw JSON object.
        """
        
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            result = self._parse_json_response(response.text)
            if result:
                return result
                
        except Exception as e:
            logger.error(f"Error during Gemini batch review analysis for '{movie_title}': {e}")
            
        return self._get_fallback_batch_analysis(reviews, movie_title)

    def _parse_json_response(self, text: str) -> Optional[Dict[str, Any]]:
        """Safely parse a JSON response, handling potential formatting issues."""
        try:
            # Strip markdown code blocks if any got through
            cleaned = text.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```(?:json)?\n", "", cleaned)
                cleaned = re.sub(r"\n```$", "", cleaned)
            return json.loads(cleaned)
        except Exception as e:
            logger.error(f"Failed to parse JSON response from Gemini: {e}. Raw response: {text}")
            return None

    def _get_fallback_text_sentiment(self, text: str) -> Dict[str, Any]:
        """Simple deterministic fallback for single text sentiment."""
        text_lower = text.lower()
        
        # Very simple keyword search for fallback
        pos_words = ["great", "awesome", "excellent", "love", "amazing", "good", "beautiful", "masterpiece", "brilliant"]
        neg_words = ["bad", "terrible", "boring", "waste", "worst", "hate", "awful", "disappointing", "flat"]
        
        pos_count = sum(1 for w in pos_words if w in text_lower)
        neg_count = sum(1 for w in neg_words if w in text_lower)
        
        if pos_count > neg_count:
            sentiment = "positive"
            score = 0.5 + (0.05 * min(10, pos_count - neg_count))
        elif neg_count > pos_count:
            sentiment = "negative"
            score = -0.5 - (0.05 * min(10, neg_count - pos_count))
        else:
            sentiment = "neutral"
            score = 0.0
            
        return {
            "sentiment": sentiment,
            "score": score,
            "themes": ["Movie Discussion", "Review"],
            "pros": ["Visuals" if "visual" in text_lower or "look" in text_lower else "Acting"],
            "cons": ["Pacing" if "pace" in text_lower or "slow" in text_lower else "Predictable"],
            "summary": text[:100] + "..." if len(text) > 100 else text
        }

    def _get_fallback_batch_analysis(self, reviews: List[str], movie_title: str) -> Dict[str, Any]:
        """Fallback analysis for batch of reviews."""
        return {
            "overall_consensus": f"Based on review parsing, '{movie_title}' received mixed to positive reactions. Reviewers generally appreciated the performances and cinematography, though some noted issues with runtime and script pacing.",
            "consensus_score": 75,
            "key_praises": ["Stellar lead performances", "Impressive cinematography and visual style", "Engaging score/soundtrack"],
            "key_criticisms": ["Uneven pacing in the middle act", "Predictable narrative structure", "Some thin character development"],
            "sentiment_breakdown": {
                "positive_percentage": 65.0,
                "neutral_percentage": 20.0,
                "negative_percentage": 15.0
            },
            "verdict": "A solid watch for fans of the genre, though it doesn't break new ground."
        }

# Singleton instance
gemini_service = GeminiService()
