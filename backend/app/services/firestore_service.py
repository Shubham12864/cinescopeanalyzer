import os
import logging
import time
from typing import Dict, Any, Optional, List
from google.cloud import firestore
from ..core.config import settings

logger = logging.getLogger(__name__)

class FirestoreService:
    def __init__(self):
        self.db = None
        self.enabled = False
        
    def initialize(self):
        """Initialize async Firestore client using environment variables or application default credentials"""
        try:
            # Check if private key path is provided, otherwise use application default credentials
            if settings.FIREBASE_PRIVATE_KEY_JSON_PATH and os.path.exists(settings.FIREBASE_PRIVATE_KEY_JSON_PATH):
                self.db = firestore.AsyncClient.from_service_account_json(settings.FIREBASE_PRIVATE_KEY_JSON_PATH)
                self.enabled = True
                logger.info("🔥 Async Firestore client initialized from service account JSON")
            elif settings.FIREBASE_PROJECT_ID:
                self.db = firestore.AsyncClient(project=settings.FIREBASE_PROJECT_ID)
                self.enabled = True
                logger.info(f"🔥 Async Firestore client initialized for project {settings.FIREBASE_PROJECT_ID}")
            else:
                # Try application default credentials
                try:
                    self.db = firestore.AsyncClient()
                    self.enabled = True
                    logger.info("🔥 Async Firestore client initialized using Application Default Credentials")
                except Exception as adc_err:
                    logger.warning(f"⚠️ Firestore: No project ID or credentials set. Firestore cache is DISABLED. Error: {adc_err}")
                    self.enabled = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize async Firestore client: {e}")
            self.enabled = False

    async def get_cached_movie(self, movie_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve movie from cache if it exists and hasn't expired"""
        if not self.enabled or not self.db:
            return None
        try:
            doc_ref = self.db.collection("movies_cache").document(movie_id)
            doc = await doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                # Check expiration
                if "expires_at" in data and data["expires_at"] < time.time():
                    logger.info(f"💾 Firestore cache expired for movie {movie_id}")
                    return None
                return data.get("movie_data")
        except Exception as e:
            logger.error(f"Firestore get_cached_movie failed for {movie_id}: {e}")
        return None

    async def cache_movie(self, movie_id: str, movie_data: Dict[str, Any], ttl_seconds: int = 86400):
        """Cache movie data in Firestore"""
        if not self.enabled or not self.db:
            return
        try:
            doc_ref = self.db.collection("movies_cache").document(movie_id)
            await doc_ref.set({
                "movie_id": movie_id,
                "movie_data": movie_data,
                "cached_at": time.time(),
                "expires_at": time.time() + ttl_seconds
            })
            logger.info(f"💾 Cached movie {movie_id} in Firestore")
        except Exception as e:
            logger.error(f"Firestore cache_movie failed for {movie_id}: {e}")

    async def get_cached_analysis(self, movie_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve movie analysis from cache if it exists and hasn't expired"""
        if not self.enabled or not self.db:
            return None
        try:
            doc_ref = self.db.collection("sentiment_cache").document(movie_id)
            doc = await doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                # Check expiration
                if "expires_at" in data and data["expires_at"] < time.time():
                    logger.info(f"💾 Firestore cache expired for analysis {movie_id}")
                    return None
                return data.get("analysis_data")
        except Exception as e:
            logger.error(f"Firestore get_cached_analysis failed for {movie_id}: {e}")
        return None

    async def cache_analysis(self, movie_id: str, analysis_data: Dict[str, Any], ttl_seconds: int = 86400 * 7):
        """Cache analysis data in Firestore (default 7 days)"""
        if not self.enabled or not self.db:
            return
        try:
            doc_ref = self.db.collection("sentiment_cache").document(movie_id)
            await doc_ref.set({
                "movie_id": movie_id,
                "analysis_data": analysis_data,
                "cached_at": time.time(),
                "expires_at": time.time() + ttl_seconds
            })
            logger.info(f"💾 Cached analysis for movie {movie_id} in Firestore")
        except Exception as e:
            logger.error(f"Firestore cache_analysis failed for {movie_id}: {e}")

    async def get_movie_reviews(self, movie_id: str) -> List[Dict[str, Any]]:
        """Get all reviews for a movie from Firestore"""
        if not self.enabled or not self.db:
            return []
        try:
            reviews_ref = self.db.collection("reviews")
            query = reviews_ref.where("movie_id", "==", movie_id)
            docs = await query.get()
            reviews = []
            for doc in docs:
                data = doc.to_dict()
                reviews.append(data)
            # Sort by date descending
            reviews.sort(key=lambda x: x.get("date", ""), reverse=True)
            return reviews
        except Exception as e:
            logger.error(f"Firestore get_movie_reviews failed for {movie_id}: {e}")
            return []

    async def add_movie_review(self, movie_id: str, review: Dict[str, Any]):
        """Add/save a movie review in Firestore"""
        if not self.enabled or not self.db:
            return
        try:
            review_id = review.get("id")
            doc_ref = self.db.collection("reviews").document(review_id)
            await doc_ref.set(review)
            logger.info(f"💾 Saved review {review_id} for movie {movie_id} in Firestore")
        except Exception as e:
            logger.error(f"Firestore add_movie_review failed: {e}")

    async def update_movie_review(self, movie_id: str, review_id: str, review_data: Dict[str, Any]):
        """Update an existing movie review in Firestore"""
        if not self.enabled or not self.db:
            return
        try:
            doc_ref = self.db.collection("reviews").document(review_id)
            await doc_ref.update(review_data)
            logger.info(f"💾 Updated review {review_id} for movie {movie_id} in Firestore")
        except Exception as e:
            logger.error(f"Firestore update_movie_review failed: {e}")

    async def delete_movie_review(self, movie_id: str, review_id: str):
        """Delete a movie review from Firestore"""
        if not self.enabled or not self.db:
            return
        try:
            doc_ref = self.db.collection("reviews").document(review_id)
            await doc_ref.delete()
            logger.info(f"💾 Deleted review {review_id} for movie {movie_id} from Firestore")
        except Exception as e:
            logger.error(f"Firestore delete_movie_review failed: {e}")

# Global singleton
firestore_service = FirestoreService()
