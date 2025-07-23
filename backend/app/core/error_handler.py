"""
Comprehensive error handling system for the CineScope backend API
"""
from typing import Dict, Any, Optional, List
from enum import Enum
import logging
import traceback
from datetime import datetime
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorType(str, Enum):
    """Error type enumeration for categorizing different types of errors"""
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    EXTERNAL_API_ERROR = "external_api_error"
    DATABASE_ERROR = "database_error"
    IMAGE_PROCESSING_ERROR = "image_processing_error"
    SEARCH_ERROR = "search_error"
    TIMEOUT_ERROR = "timeout_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    AUTHENTICATION_ERROR = "authentication_error"
    INTERNAL_SERVER_ERROR = "internal_server_error"


class ErrorSeverity(str, Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorDetail(BaseModel):
    """Detailed error information"""
    code: str
    message: str
    field: Optional[str] = None
    value: Optional[Any] = None


class APIError(BaseModel):
    """Standardized API error response model"""
    error: bool = True
    error_type: ErrorType
    message: str
    details: Optional[List[ErrorDetail]] = None
    timestamp: str
    request_id: Optional[str] = None
    retry_after: Optional[int] = None  # For rate limiting


class CineScopeException(Exception):
    """Base exception class for CineScope application"""
    
    def __init__(
        self,
        message: str,
        error_type: ErrorType = ErrorType.INTERNAL_SERVER_ERROR,
        status_code: int = 500,
        details: Optional[List[ErrorDetail]] = None,
        retry_after: Optional[int] = None
    ):
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.details = details or []
        self.retry_after = retry_after
        super().__init__(self.message)


class ValidationException(CineScopeException):
    """Exception for validation errors"""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        details = [ErrorDetail(
            code="VALIDATION_FAILED",
            message=message,
            field=field,
            value=str(value) if value is not None else None
        )]
        super().__init__(
            message=message,
            error_type=ErrorType.VALIDATION_ERROR,
            status_code=400,
            details=details
        )


class NotFoundException(CineScopeException):
    """Exception for resource not found errors"""
    
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with identifier '{identifier}' not found"
        details = [ErrorDetail(
            code="RESOURCE_NOT_FOUND",
            message=message,
            field="id",
            value=identifier
        )]
        super().__init__(
            message=message,
            error_type=ErrorType.NOT_FOUND,
            status_code=404,
            details=details
        )


class ExternalAPIException(CineScopeException):
    """Exception for external API errors"""
    
    def __init__(self, service: str, message: str, status_code: int = 503):
        details = [ErrorDetail(
            code="EXTERNAL_API_ERROR",
            message=f"{service} API error: {message}",
            field="service",
            value=service
        )]
        super().__init__(
            message=f"External service temporarily unavailable: {service}",
            error_type=ErrorType.EXTERNAL_API_ERROR,
            status_code=status_code,
            details=details,
            retry_after=60  # Suggest retry after 60 seconds
        )


class ImageProcessingException(CineScopeException):
    """Exception for image processing errors"""
    
    def __init__(self, url: str, reason: str):
        message = f"Failed to process image: {reason}"
        details = [ErrorDetail(
            code="IMAGE_PROCESSING_FAILED",
            message=message,
            field="image_url",
            value=url
        )]
        super().__init__(
            message=message,
            error_type=ErrorType.IMAGE_PROCESSING_ERROR,
            status_code=422,
            details=details
        )


class SearchException(CineScopeException):
    """Exception for search operation errors"""
    
    def __init__(self, query: str, reason: str):
        message = f"Search failed for query '{query}': {reason}"
        details = [ErrorDetail(
            code="SEARCH_FAILED",
            message=message,
            field="query",
            value=query
        )]
        super().__init__(
            message="Search operation failed",
            error_type=ErrorType.SEARCH_ERROR,
            status_code=422,
            details=details
        )


class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def log_error(
        self,
        error: Exception,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ):
        """Log error with appropriate severity and context"""
        
        # Determine log level based on severity
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }.get(severity, logging.ERROR)
        
        # Prepare log message
        error_info = {
            "error_type": getattr(error, 'error_type', 'unknown'),
            "message": str(error),
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id
        }
        
        if context:
            error_info["context"] = context
        
        # Log stack trace for high severity errors
        if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            error_info["traceback"] = traceback.format_exc()
        
        self.logger.log(log_level, f"Error occurred: {error_info}")
    
    def create_error_response(
        self,
        error: Exception,
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """Create standardized error response"""
        
        if isinstance(error, CineScopeException):
            api_error = APIError(
                error_type=error.error_type,
                message=error.message,
                details=error.details,
                timestamp=datetime.utcnow().isoformat(),
                request_id=request_id,
                retry_after=error.retry_after
            )
            return JSONResponse(
                status_code=error.status_code,
                content=api_error.dict()
            )
        
        elif isinstance(error, HTTPException):
            api_error = APIError(
                error_type=ErrorType.INTERNAL_SERVER_ERROR,
                message=error.detail,
                timestamp=datetime.utcnow().isoformat(),
                request_id=request_id
            )
            return JSONResponse(
                status_code=error.status_code,
                content=api_error.dict()
            )
        
        else:
            # Generic error handling
            api_error = APIError(
                error_type=ErrorType.INTERNAL_SERVER_ERROR,
                message="An unexpected error occurred",
                timestamp=datetime.utcnow().isoformat(),
                request_id=request_id
            )
            return JSONResponse(
                status_code=500,
                content=api_error.dict()
            )
    
    def handle_external_api_error(
        self,
        service: str,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> ExternalAPIException:
        """Handle external API errors with proper logging"""
        
        self.log_error(
            error,
            severity=ErrorSeverity.MEDIUM,
            context={
                "service": service,
                **(context or {})
            }
        )
        
        return ExternalAPIException(
            service=service,
            message=str(error)
        )
    
    def handle_validation_error(
        self,
        message: str,
        field: str = None,
        value: Any = None
    ) -> ValidationException:
        """Handle validation errors"""
        
        validation_error = ValidationException(message, field, value)
        self.log_error(validation_error, severity=ErrorSeverity.LOW)
        return validation_error
    
    def handle_not_found_error(
        self,
        resource: str,
        identifier: str
    ) -> NotFoundException:
        """Handle resource not found errors"""
        
        not_found_error = NotFoundException(resource, identifier)
        self.log_error(not_found_error, severity=ErrorSeverity.LOW)
        return not_found_error


# Global error handler instance
error_handler = ErrorHandler()


def get_request_id(request: Request) -> Optional[str]:
    """Extract request ID from headers or generate one"""
    return request.headers.get("X-Request-ID") or request.headers.get("X-Correlation-ID")


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for FastAPI"""
    
    request_id = get_request_id(request)
    
    # Log the error
    error_handler.log_error(
        exc,
        severity=ErrorSeverity.HIGH if not isinstance(exc, CineScopeException) else ErrorSeverity.MEDIUM,
        context={
            "method": request.method,
            "url": str(request.url),
            "client": request.client.host if request.client else None
        },
        request_id=request_id
    )
    
    # Return standardized error response
    return error_handler.create_error_response(exc, request_id)