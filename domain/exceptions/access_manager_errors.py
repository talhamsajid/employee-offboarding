"""
Access Manager Custom Exceptions
Hierarchical exception structure for better error handling
"""

from typing import Optional, Dict, Any
from datetime import datetime


class AccessManagerError(Exception):
    """
    Base exception for all Access Manager errors
    
    All custom exceptions inherit from this base class.
    Provides consistent error handling and context tracking.
    """
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Initialize the exception
        
        Args:
            message: Error message
            context: Additional context information
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.timestamp = datetime.now()
    
    def __str__(self) -> str:
        """String representation"""
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} ({context_str})"
        return self.message
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"{self.__class__.__name__}('{self.message}', context={self.context})"


class AuthenticationError(AccessManagerError):
    """
    Authentication-related errors
    
    Raised when authentication fails or credentials are invalid.
    """
    
    def __init__(
        self,
        message: str,
        credentials_path: Optional[str] = None,
        auth_type: Optional[str] = None
    ):
        """
        Initialize authentication error
        
        Args:
            message: Error message
            credentials_path: Path to credentials file
            auth_type: Type of authentication (OAuth2, ServiceAccount)
        """
        context = {}
        if credentials_path:
            context['credentials_path'] = credentials_path
        if auth_type:
            context['auth_type'] = auth_type
        
        super().__init__(message, context)


class PermissionDeniedError(AccessManagerError):
    """
    Permission denied errors
    
    Raised when an operation fails due to insufficient permissions.
    """
    
    def __init__(
        self,
        message: str,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        required_permission: Optional[str] = None
    ):
        """
        Initialize permission denied error
        
        Args:
            message: Error message
            file_id: File ID where permission was denied
            file_name: File name
            required_permission: Permission level required
        """
        context = {}
        if file_id:
            context['file_id'] = file_id
        if file_name:
            context['file_name'] = file_name
        if required_permission:
            context['required_permission'] = required_permission
        
        super().__init__(message, context)


class RateLimitError(AccessManagerError):
    """
    Rate limit exceeded errors
    
    Raised when API rate limits are exceeded.
    """
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        quota_type: Optional[str] = None
    ):
        """
        Initialize rate limit error
        
        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
            quota_type: Type of quota exceeded
        """
        context = {}
        if retry_after:
            context['retry_after'] = retry_after
        if quota_type:
            context['quota_type'] = quota_type
        
        super().__init__(message, context)


class CacheError(AccessManagerError):
    """
    Cache-related errors
    
    Raised when cache operations fail.
    """
    
    def __init__(
        self,
        message: str,
        cache_key: Optional[str] = None,
        operation: Optional[str] = None
    ):
        """
        Initialize cache error
        
        Args:
            message: Error message
            cache_key: Cache key that caused the error
            operation: Operation that failed (save, load, delete)
        """
        context = {}
        if cache_key:
            context['cache_key'] = cache_key
        if operation:
            context['operation'] = operation
        
        super().__init__(message, context)


class ValidationError(AccessManagerError):
    """
    Validation errors
    
    Raised when input validation fails.
    """
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        constraint: Optional[str] = None
    ):
        """
        Initialize validation error
        
        Args:
            message: Error message
            field: Field that failed validation
            value: Invalid value
            constraint: Constraint that was violated
        """
        context = {}
        if field:
            context['field'] = field
        if value is not None:
            context['value'] = str(value)
        if constraint:
            context['constraint'] = constraint
        
        super().__init__(message, context)


class FileNotFoundError(AccessManagerError):
    """
    File not found errors
    
    Raised when a requested file does not exist.
    """
    
    def __init__(
        self,
        message: str,
        file_id: Optional[str] = None,
        file_path: Optional[str] = None
    ):
        """
        Initialize file not found error
        
        Args:
            message: Error message
            file_id: Drive file ID
            file_path: Local file path
        """
        context = {}
        if file_id:
            context['file_id'] = file_id
        if file_path:
            context['file_path'] = file_path
        
        super().__init__(message, context)


class ConfigurationError(AccessManagerError):
    """
    Configuration errors
    
    Raised when configuration is invalid or missing.
    """
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_file: Optional[str] = None
    ):
        """
        Initialize configuration error
        
        Args:
            message: Error message
            config_key: Configuration key that is invalid
            config_file: Configuration file path
        """
        context = {}
        if config_key:
            context['config_key'] = config_key
        if config_file:
            context['config_file'] = config_file
        
        super().__init__(message, context)


class RepositoryError(AccessManagerError):
    """
    Repository operation errors
    
    Raised when repository operations fail.
    """
    
    def __init__(
        self,
        message: str,
        repository: Optional[str] = None,
        operation: Optional[str] = None
    ):
        """
        Initialize repository error
        
        Args:
            message: Error message
            repository: Repository name
            operation: Operation that failed
        """
        context = {}
        if repository:
            context['repository'] = repository
        if operation:
            context['operation'] = operation
        
        super().__init__(message, context)
