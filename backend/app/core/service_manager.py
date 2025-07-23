"""
Seif TYPE_CHECKING:
    from ..services.movie_service import MovieService
    from ..services.comprehensive_movie_service_working import ComprehensiveMovieService
    from ..services.image_cache_service import ImageCacheService
    from ..core.api_manager import APIManagere Manager for Singleton Instances
Prevents multiple service initializations that cause memory leaks and duplicate outputs
"""
import logging
from typing import Optional, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..services.movie_service import MovieService
    from ..services.comprehensive_movie_service import ComprehensiveMovieService
    from ..services.image_cache_service import ImageCacheService

logger = logging.getLogger(__name__)

class ServiceManager:
    """Singleton service manager to provide shared service instances"""
    _instance: Optional['ServiceManager'] = None
    _movie_service: Optional['MovieService'] = None
    _comprehensive_service: Optional['ComprehensiveMovieService'] = None
    _image_cache_service: Optional['ImageCacheService'] = None
    _api_manager: Any = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceManager, cls).__new__(cls)
            logger.info("🔧 ServiceManager singleton created")
        return cls._instance
    
    def get_movie_service(self):
        """Get or create MovieService singleton with proper dependency injection"""
        if self._movie_service is None:
            # Import here to avoid circular imports
            from ..services.movie_service import MovieService
            
            # Get shared instances first
            api_manager = self.get_api_manager()
            comprehensive_service = self.get_comprehensive_service()
            
            # Create MovieService with both injected dependencies to prevent double initialization
            self._movie_service = MovieService(
                comprehensive_service=comprehensive_service,
                api_manager=api_manager
            )
            logger.info("🎬 MovieService singleton initialized with dependency injection")
        return self._movie_service
    
    def get_api_manager(self):
        """Get or create APIManager singleton"""
        if self._api_manager is None:
            from ..core.api_manager import APIManager
            self._api_manager = APIManager()
            logger.info("🔧 APIManager singleton initialized")
        return self._api_manager
    
    def get_comprehensive_service(self):
        """Get or create ComprehensiveMovieService singleton"""
        if self._comprehensive_service is None:
            from ..services.comprehensive_movie_service_working import ComprehensiveMovieService
            
            # Use shared API manager to prevent double initialization
            api_manager = self.get_api_manager()
            self._comprehensive_service = ComprehensiveMovieService(api_manager=api_manager)
            logger.info("🔍 ComprehensiveMovieService singleton initialized")
        return self._comprehensive_service
    
    def get_image_cache_service(self):
        """Get or create ImageCacheService singleton"""
        if self._image_cache_service is None:
            from ..services.image_cache_service import ImageCacheService
            self._image_cache_service = ImageCacheService()
            logger.info("🖼️ ImageCacheService singleton initialized")
        return self._image_cache_service

# Global service manager instance
service_manager = ServiceManager()
