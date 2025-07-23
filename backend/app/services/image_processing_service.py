"""
Image Processing Service for consistent image URL processing and caching
"""
import re
import hashlib
import logging
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, unquote
from pathlib import Path
import json
import time
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import io

logger = logging.getLogger(__name__)

class ImageURLProcessor:
    """Handles consistent image URL processing and validation"""
    
    def __init__(self):
        self.url_cache = {}  # In-memory cache for processed URLs
        self.cache_ttl = 3600  # 1 hour TTL for URL processing cache
        
    def clean_and_validate_url(self, url: str) -> Optional[str]:
        """Clean and validate image URL before proxy requests"""
        if not url:
            return None
            
        try:
            # Clean the URL
            clean_url = self._clean_url(url)
            
            # Validate URL format
            if not self._is_valid_url(clean_url):
                logger.warning(f"Invalid URL format: {url}")
                return None
                
            # Check for invalid values
            if self._is_invalid_value(clean_url):
                logger.debug(f"Invalid URL value detected: {clean_url}")
                return None
                
            # Normalize URL
            normalized_url = self._normalize_url(clean_url)
            
            logger.debug(f"URL processed: {url} -> {normalized_url}")
            return normalized_url
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            return None
    
    def _clean_url(self, url: str) -> str:
        """Clean URL by removing unwanted characters and whitespace"""
        # Remove newlines, carriage returns, and extra spaces
        clean_url = url.replace('\n', '').replace('\r', '').replace('\t', '').strip()
        
        # URL decode if needed
        clean_url = unquote(clean_url)
        
        # Remove any trailing/leading quotes
        clean_url = clean_url.strip('"\'')
        
        return clean_url
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False
    
    def _is_invalid_value(self, url: str) -> bool:
        """Check for invalid URL values like N/A, null, etc."""
        invalid_values = {
            'n/a', 'null', 'none', 'undefined', 'nil', 
            'empty', '', 'no image', 'no_image', 'placeholder'
        }
        return url.lower() in invalid_values
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for consistent processing"""
        # Ensure HTTPS for security
        if url.startswith('http://'):
            url = url.replace('http://', 'https://', 1)
            
        # Handle common image service patterns
        url = self._handle_image_service_patterns(url)
        
        return url
    
    def _handle_image_service_patterns(self, url: str) -> str:
        """Handle different image source formats (OMDB, scraped, etc.)"""
        
        # OMDB poster URLs - ensure proper size
        if 'media-amazon.com' in url and 'SX300' not in url and 'SY300' not in url:
            # Add size parameter if missing
            if '@._V1_' in url and not any(size in url for size in ['SX', 'SY']):
                url = url.replace('@._V1_', '@._V1_SX300_')
        
        # TMDB image URLs - ensure proper size
        if 'image.tmdb.org' in url:
            # Standardize to w500 size for posters
            if '/w92/' in url:
                url = url.replace('/w92/', '/w500/')
            elif '/w154/' in url:
                url = url.replace('/w154/', '/w500/')
            elif '/w185/' in url:
                url = url.replace('/w185/', '/w500/')
            elif '/original/' in url:
                url = url.replace('/original/', '/w500/')
        
        # IMDb image URLs - handle different formats
        if 'imdb.com' in url:
            # Ensure proper image format
            if not any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                if not url.endswith('/'):
                    url += '.jpg'
        
        return url
    
    def get_cached_processed_url(self, original_url: str) -> Optional[str]:
        """Get cached processed URL if available and not expired"""
        if not original_url:
            return None
            
        cache_key = self._generate_cache_key(original_url)
        
        if cache_key in self.url_cache:
            cached_data = self.url_cache[cache_key]
            
            # Check if cache is still valid
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                logger.debug(f"Using cached processed URL for: {original_url}")
                return cached_data['processed_url']
            else:
                # Remove expired cache entry
                del self.url_cache[cache_key]
        
        return None
    
    def cache_processed_url(self, original_url: str, processed_url: str) -> None:
        """Cache processed URL for future use"""
        if not original_url or not processed_url:
            return
            
        cache_key = self._generate_cache_key(original_url)
        
        self.url_cache[cache_key] = {
            'processed_url': processed_url,
            'timestamp': time.time()
        }
        
        logger.debug(f"Cached processed URL: {original_url} -> {processed_url}")
    
    def _generate_cache_key(self, url: str) -> str:
        """Generate cache key for URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def clear_expired_cache(self) -> None:
        """Clear expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, data in self.url_cache.items()
            if current_time - data['timestamp'] >= self.cache_ttl
        ]
        
        for key in expired_keys:
            del self.url_cache[key]
        
        if expired_keys:
            logger.info(f"Cleared {len(expired_keys)} expired URL cache entries")

class ImageSourceHandler:
    """Handles different image source formats and processing"""
    
    def __init__(self):
        self.source_processors = {
            'omdb': self._process_omdb_image,
            'tmdb': self._process_tmdb_image,
            'imdb': self._process_imdb_image,
            'scraped': self._process_scraped_image,
            'generic': self._process_generic_image
        }
    
    def process_image_by_source(self, url: str, source: str = 'generic') -> Dict[str, Any]:
        """Process image URL based on its source"""
        if not url:
            return {'processed_url': None, 'source': source, 'valid': False}
        
        processor = self.source_processors.get(source, self._process_generic_image)
        
        try:
            result = processor(url)
            result['source'] = source
            return result
        except Exception as e:
            logger.error(f"Error processing {source} image {url}: {e}")
            return {'processed_url': None, 'source': source, 'valid': False, 'error': str(e)}
    
    def _process_omdb_image(self, url: str) -> Dict[str, Any]:
        """Process OMDB image URLs"""
        if 'media-amazon.com' not in url:
            return {'processed_url': url, 'valid': True, 'modifications': []}
        
        modifications = []
        processed_url = url
        
        # Ensure proper size parameter
        if 'SX300' not in url and 'SY300' not in url:
            if '@._V1_' in url:
                processed_url = url.replace('@._V1_', '@._V1_SX300_')
                modifications.append('added_size_parameter')
        
        # Ensure HTTPS
        if processed_url.startswith('http://'):
            processed_url = processed_url.replace('http://', 'https://', 1)
            modifications.append('enforced_https')
        
        return {
            'processed_url': processed_url,
            'valid': True,
            'modifications': modifications,
            'original_url': url
        }
    
    def _process_tmdb_image(self, url: str) -> Dict[str, Any]:
        """Process TMDB image URLs"""
        if 'image.tmdb.org' not in url:
            return {'processed_url': url, 'valid': True, 'modifications': []}
        
        modifications = []
        processed_url = url
        
        # Standardize to w500 size for better quality
        size_replacements = {
            '/w92/': '/w500/',
            '/w154/': '/w500/',
            '/w185/': '/w500/',
            '/original/': '/w500/'  # Reduce original size for performance
        }
        
        for old_size, new_size in size_replacements.items():
            if old_size in processed_url:
                processed_url = processed_url.replace(old_size, new_size)
                modifications.append(f'size_changed_{old_size.strip("/")}')
                break
        
        return {
            'processed_url': processed_url,
            'valid': True,
            'modifications': modifications,
            'original_url': url
        }
    
    def _process_imdb_image(self, url: str) -> Dict[str, Any]:
        """Process IMDb image URLs"""
        modifications = []
        processed_url = url
        
        # Ensure proper image extension
        if not any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
            if not url.endswith('/'):
                processed_url += '.jpg'
                modifications.append('added_extension')
        
        # Ensure HTTPS
        if processed_url.startswith('http://'):
            processed_url = processed_url.replace('http://', 'https://', 1)
            modifications.append('enforced_https')
        
        return {
            'processed_url': processed_url,
            'valid': True,
            'modifications': modifications,
            'original_url': url
        }
    
    def _process_scraped_image(self, url: str) -> Dict[str, Any]:
        """Process scraped image URLs"""
        modifications = []
        processed_url = url
        
        # Basic cleaning for scraped URLs
        if processed_url.startswith('//'):
            processed_url = 'https:' + processed_url
            modifications.append('added_protocol')
        
        # Ensure HTTPS
        if processed_url.startswith('http://'):
            processed_url = processed_url.replace('http://', 'https://', 1)
            modifications.append('enforced_https')
        
        return {
            'processed_url': processed_url,
            'valid': True,
            'modifications': modifications,
            'original_url': url
        }
    
    def _process_generic_image(self, url: str) -> Dict[str, Any]:
        """Process generic image URLs"""
        modifications = []
        processed_url = url
        
        # Ensure HTTPS
        if processed_url.startswith('http://'):
            processed_url = processed_url.replace('http://', 'https://', 1)
            modifications.append('enforced_https')
        
        return {
            'processed_url': processed_url,
            'valid': True,
            'modifications': modifications,
            'original_url': url
        }

class ImageProcessingService:
    """Main service for image processing pipeline"""
    
    def __init__(self):
        self.url_processor = ImageURLProcessor()
        self.source_handler = ImageSourceHandler()
        self.processing_stats = {
            'total_processed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'invalid_urls': 0,
            'processing_errors': 0
        }
    
    def process_image_url(self, url: str, source: str = 'generic') -> Dict[str, Any]:
        """Main method to process image URL with caching"""
        if not url:
            self.processing_stats['invalid_urls'] += 1
            return {
                'processed_url': None,
                'valid': False,
                'source': source,
                'cached': False,
                'error': 'Empty URL provided'
            }
        
        self.processing_stats['total_processed'] += 1
        
        # Check cache first
        cached_url = self.url_processor.get_cached_processed_url(url)
        if cached_url:
            self.processing_stats['cache_hits'] += 1
            return {
                'processed_url': cached_url,
                'valid': True,
                'source': source,
                'cached': True
            }
        
        self.processing_stats['cache_misses'] += 1
        
        try:
            # Clean and validate URL
            clean_url = self.url_processor.clean_and_validate_url(url)
            if not clean_url:
                self.processing_stats['invalid_urls'] += 1
                return {
                    'processed_url': None,
                    'valid': False,
                    'source': source,
                    'cached': False,
                    'error': 'Invalid URL format or value'
                }
            
            # Process by source
            result = self.source_handler.process_image_by_source(clean_url, source)
            
            # Cache the result if valid
            if result.get('valid') and result.get('processed_url'):
                self.url_processor.cache_processed_url(url, result['processed_url'])
            
            result['cached'] = False
            return result
            
        except Exception as e:
            self.processing_stats['processing_errors'] += 1
            logger.error(f"Error in image processing pipeline for {url}: {e}")
            return {
                'processed_url': None,
                'valid': False,
                'source': source,
                'cached': False,
                'error': str(e)
            }
    
    def process_multiple_urls(self, urls: List[str], source: str = 'generic') -> List[Dict[str, Any]]:
        """Process multiple image URLs efficiently"""
        results = []
        
        for url in urls:
            result = self.process_image_url(url, source)
            results.append(result)
        
        return results
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        stats = self.processing_stats.copy()
        
        if stats['total_processed'] > 0:
            stats['cache_hit_rate'] = stats['cache_hits'] / stats['total_processed']
            stats['error_rate'] = (stats['invalid_urls'] + stats['processing_errors']) / stats['total_processed']
        else:
            stats['cache_hit_rate'] = 0
            stats['error_rate'] = 0
        
        return stats
    
    def clear_cache(self) -> None:
        """Clear processing cache"""
        self.url_processor.url_cache.clear()
        logger.info("Image processing cache cleared")
    
    def cleanup_expired_cache(self) -> None:
        """Clean up expired cache entries"""
        self.url_processor.clear_expired_cache()

class FallbackImageGenerator:
    """Service for generating meaningful fallback images with movie titles"""
    
    def __init__(self):
        self.cache_dir = Path("./cache/fallback_images")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.generated_cache = {}  # In-memory cache for generated images
        self.cache_ttl = 86400  # 24 hours TTL for generated images
        
    def generate_fallback_image(
        self, 
        title: str = "Movie Poster", 
        width: int = 300, 
        height: int = 450,
        cache_key: Optional[str] = None
    ) -> bytes:
        """Generate a meaningful fallback image with movie title and caching"""
        
        # Generate cache key if not provided
        if not cache_key:
            cache_key = self._generate_cache_key(title, width, height)
        
        # Check in-memory cache first
        cached_image = self._get_cached_image(cache_key)
        if cached_image:
            logger.debug(f"Using cached fallback image for: {title}")
            return cached_image
        
        # Check file cache
        cached_file = self._get_cached_file(cache_key)
        if cached_file:
            logger.debug(f"Using file cached fallback image for: {title}")
            self._cache_image_in_memory(cache_key, cached_file)
            return cached_file
        
        # Generate new image
        try:
            image_bytes = self._create_fallback_image(title, width, height)
            
            # Cache the generated image
            self._cache_image_in_memory(cache_key, image_bytes)
            self._cache_image_to_file(cache_key, image_bytes)
            
            logger.info(f"Generated new fallback image for: {title}")
            return image_bytes
            
        except Exception as e:
            logger.error(f"Error generating fallback image for {title}: {e}")
            return self._create_minimal_fallback(width, height)
    
    def _create_fallback_image(self, title: str, width: int, height: int) -> bytes:
        """Create the actual fallback image with proper aspect ratio and design"""
        try:
            # Ensure proper aspect ratio (2:3 for movie posters)
            if width / height != 2/3:
                if width > height * 2/3:
                    width = int(height * 2/3)
                else:
                    height = int(width * 3/2)
            
            # Create image with gradient background
            img = Image.new('RGB', (width, height), color='#1a1a1a')
            draw = ImageDraw.Draw(img)
            
            # Create gradient effect
            for y in range(height):
                gradient_color = int(26 + (y / height) * 20)  # Subtle gradient
                color = f'#{gradient_color:02x}{gradient_color:02x}{gradient_color:02x}'
                draw.line([(0, y), (width, y)], fill=color)
            
            # Load fonts with fallbacks
            font_large, font_medium, font_small = self._load_fonts()
            
            # Draw movie poster frame
            self._draw_poster_frame(draw, width, height)
            
            # Draw movie title with proper text wrapping
            self._draw_movie_title(draw, title, width, height, font_large, font_medium)
            
            # Draw "No Image Available" text
            self._draw_no_image_text(draw, width, height, font_small)
            
            # Add film strip decoration
            self._draw_film_strip(draw, width, height)
            
            # Convert to bytes
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG', optimize=True)
            return img_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error in _create_fallback_image: {e}")
            return self._create_minimal_fallback(width, height)
    
    def _load_fonts(self):
        """Load fonts with proper fallbacks"""
        font_large = None
        font_medium = None
        font_small = None
        
        # Try to load system fonts
        font_paths = [
            "arial.ttf", "Arial.ttf", "helvetica.ttf", "Helvetica.ttf",
            "/System/Library/Fonts/Arial.ttf",  # macOS
            "/Windows/Fonts/arial.ttf",  # Windows
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # Linux
        ]
        
        for font_path in font_paths:
            try:
                font_large = ImageFont.truetype(font_path, 24)
                font_medium = ImageFont.truetype(font_path, 18)
                font_small = ImageFont.truetype(font_path, 14)
                break
            except:
                continue
        
        # Fallback to default font
        if not font_large:
            try:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            except:
                pass
        
        return font_large, font_medium, font_small
    
    def _draw_poster_frame(self, draw, width: int, height: int):
        """Draw a movie poster frame"""
        # Main poster area
        margin = 20
        frame_color = '#333333'
        border_color = '#666666'
        
        # Outer frame
        draw.rectangle([margin, margin, width - margin, height - margin], 
                      fill=frame_color, outline=border_color, width=2)
        
        # Inner frame for poster area
        inner_margin = margin + 15
        draw.rectangle([inner_margin, inner_margin, width - inner_margin, height - inner_margin * 3], 
                      fill='#2a2a2a', outline=border_color, width=1)
    
    def _draw_movie_title(self, draw, title: str, width: int, height: int, font_large, font_medium):
        """Draw movie title with proper text wrapping"""
        if not font_large:
            return
        
        # Text area
        text_y_start = height - 120
        text_width = width - 40
        
        # Wrap text
        lines = self._wrap_text(title, font_large, text_width)
        
        # If too many lines, try smaller font
        if len(lines) > 3 and font_medium:
            lines = self._wrap_text(title, font_medium, text_width)
            current_font = font_medium
        else:
            current_font = font_large
        
        # Draw each line
        line_height = 30 if current_font == font_large else 25
        y_offset = text_y_start
        
        for i, line in enumerate(lines[:3]):  # Max 3 lines
            if current_font:
                bbox = draw.textbbox((0, 0), line, font=current_font)
                text_width_actual = bbox[2] - bbox[0]
                x = (width - text_width_actual) // 2
                
                # Add text shadow
                draw.text((x + 1, y_offset + 1), line, fill='#000000', font=current_font)
                # Main text
                draw.text((x, y_offset), line, fill='#ffffff', font=current_font)
                
                y_offset += line_height
    
    def _wrap_text(self, text: str, font, max_width: int) -> List[str]:
        """Wrap text to fit within specified width"""
        if not font:
            return [text]
        
        words = text.split()
        lines = []
        current_line = []
        
        # Create temporary image to measure text
        temp_img = Image.new('RGB', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = temp_draw.textbbox((0, 0), test_line, font=font)
            
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Word is too long, add it anyway
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _draw_no_image_text(self, draw, width: int, height: int, font_small):
        """Draw 'No Image Available' text"""
        if not font_small:
            return
        
        no_image_text = "No Image Available"
        bbox = draw.textbbox((0, 0), no_image_text, font=font_small)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = height - 30
        
        # Add text shadow
        draw.text((x + 1, y + 1), no_image_text, fill='#000000', font=font_small)
        # Main text
        draw.text((x, y), no_image_text, fill='#888888', font=font_small)
    
    def _draw_film_strip(self, draw, width: int, height: int):
        """Draw film strip decoration"""
        # Left film strip
        strip_width = 8
        hole_size = 4
        hole_spacing = 12
        
        # Left strip
        draw.rectangle([5, 20, 5 + strip_width, height - 20], fill='#444444')
        
        # Right strip  
        draw.rectangle([width - 5 - strip_width, 20, width - 5, height - 20], fill='#444444')
        
        # Film holes
        for y in range(30, height - 30, hole_spacing):
            # Left holes
            draw.rectangle([7, y, 7 + hole_size, y + hole_size], fill='#1a1a1a')
            # Right holes
            draw.rectangle([width - 7 - hole_size, y, width - 7, y + hole_size], fill='#1a1a1a')
    
    def _create_minimal_fallback(self, width: int, height: int) -> bytes:
        """Create minimal fallback image when all else fails"""
        try:
            img = Image.new('RGB', (width, height), color='#333333')
            draw = ImageDraw.Draw(img)
            
            # Simple centered text
            text = "No Image"
            try:
                font = ImageFont.load_default()
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                y = height // 2 - 10
                draw.text((x, y), text, fill='#ffffff', font=font)
            except:
                pass
            
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            return img_buffer.getvalue()
        except:
            # Ultimate fallback - return empty bytes
            return b''
    
    def _generate_cache_key(self, title: str, width: int, height: int) -> str:
        """Generate cache key for fallback image"""
        key_string = f"{title}_{width}_{height}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cached_image(self, cache_key: str) -> Optional[bytes]:
        """Get cached image from memory"""
        if cache_key in self.generated_cache:
            cached_data = self.generated_cache[cache_key]
            
            # Check if cache is still valid
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data['image_bytes']
            else:
                # Remove expired cache entry
                del self.generated_cache[cache_key]
        
        return None
    
    def _cache_image_in_memory(self, cache_key: str, image_bytes: bytes):
        """Cache image in memory"""
        self.generated_cache[cache_key] = {
            'image_bytes': image_bytes,
            'timestamp': time.time()
        }
    
    def _get_cached_file(self, cache_key: str) -> Optional[bytes]:
        """Get cached image from file"""
        cache_file = self.cache_dir / f"{cache_key}.png"
        
        if cache_file.exists():
            try:
                # Check file age
                file_age = time.time() - cache_file.stat().st_mtime
                if file_age < self.cache_ttl:
                    return cache_file.read_bytes()
                else:
                    # Remove expired file
                    cache_file.unlink()
            except Exception as e:
                logger.warning(f"Error reading cached file {cache_file}: {e}")
        
        return None
    
    def _cache_image_to_file(self, cache_key: str, image_bytes: bytes):
        """Cache image to file"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.png"
            cache_file.write_bytes(image_bytes)
        except Exception as e:
            logger.warning(f"Error caching image to file: {e}")
    
    def clear_cache(self):
        """Clear all cached fallback images"""
        # Clear memory cache
        self.generated_cache.clear()
        
        # Clear file cache
        try:
            for cache_file in self.cache_dir.glob("*.png"):
                cache_file.unlink()
            logger.info("Fallback image cache cleared")
        except Exception as e:
            logger.warning(f"Error clearing file cache: {e}")
    
    def cleanup_expired_cache(self):
        """Clean up expired cache entries"""
        current_time = time.time()
        
        # Clean memory cache
        expired_keys = [
            key for key, data in self.generated_cache.items()
            if current_time - data['timestamp'] >= self.cache_ttl
        ]
        
        for key in expired_keys:
            del self.generated_cache[key]
        
        # Clean file cache
        try:
            for cache_file in self.cache_dir.glob("*.png"):
                file_age = current_time - cache_file.stat().st_mtime
                if file_age >= self.cache_ttl:
                    cache_file.unlink()
        except Exception as e:
            logger.warning(f"Error cleaning file cache: {e}")
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired fallback image cache entries")

# Global instances
image_processing_service = ImageProcessingService()
fallback_image_generator = FallbackImageGenerator()