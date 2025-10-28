"""
Repository Interfaces
Abstract data access layer following Repository pattern
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any
from datetime import timedelta

from domain.entities.drive_file import DriveFile
from domain.entities.permission import Permission
from domain.value_objects.email import Email
from domain.value_objects.identifiers import FileId, PermissionId


class IDriveRepository(ABC):
    """
    Drive Repository Interface
    
    Abstracts access to Google Drive files.
    Follows Liskov Substitution Principle - any implementation
    can be substituted without breaking client code.
    """
    
    @abstractmethod
    def list_all_files(self, page_size: int = 100) -> List[DriveFile]:
        """
        List all accessible Drive files
        
        Args:
            page_size: Number of files to fetch per API request
            
        Returns:
            List of DriveFile entities
        """
        pass
    
    @abstractmethod
    def get_file_by_id(self, file_id: FileId) -> Optional[DriveFile]:
        """
        Get a specific file by ID
        
        Args:
            file_id: File identifier
            
        Returns:
            DriveFile entity or None if not found
        """
        pass
    
    @abstractmethod
    def find_files_shared_with(self, email: Email) -> List[DriveFile]:
        """
        Find all files shared with a specific user
        
        Args:
            email: User email address
            
        Returns:
            List of DriveFile entities shared with the user
        """
        pass
    
    @abstractmethod
    def find_files_owned_by(self, email: Email) -> List[DriveFile]:
        """
        Find all files owned by a specific user
        
        Args:
            email: Owner email address
            
        Returns:
            List of DriveFile entities owned by the user
        """
        pass


class IPermissionRepository(ABC):
    """
    Permission Repository Interface
    
    Abstracts permission management operations.
    """
    
    @abstractmethod
    def get_file_permissions(self, file_id: FileId) -> List[Permission]:
        """
        Get all permissions for a file
        
        Args:
            file_id: File identifier
            
        Returns:
            List of Permission entities
        """
        pass
    
    @abstractmethod
    def revoke_permission(
        self,
        file_id: FileId,
        permission_id: PermissionId,
        use_admin_access: bool = False
    ) -> bool:
        """
        Revoke a specific permission
        
        Args:
            file_id: File identifier
            permission_id: Permission identifier
            use_admin_access: Use domain admin access override
            
        Returns:
            True if successfully revoked
            
        Raises:
            PermissionDeniedError: If insufficient permissions
            FileNotFoundError: If file not found
        """
        pass
    
    @abstractmethod
    def update_permission_role(
        self,
        file_id: FileId,
        permission_id: PermissionId,
        new_role: str
    ) -> Permission:
        """
        Update a permission's role
        
        Args:
            file_id: File identifier
            permission_id: Permission identifier
            new_role: New role (reader, writer, commenter)
            
        Returns:
            Updated Permission entity
            
        Raises:
            PermissionDeniedError: If insufficient permissions
            ValidationError: If role is invalid
        """
        pass


class ICacheRepository(ABC):
    """
    Cache Repository Interface
    
    Abstracts caching implementation.
    Follows Interface Segregation - only caching operations.
    """
    
    @abstractmethod
    def save(self, key: str, data: Any, ttl: Optional[timedelta] = None) -> None:
        """
        Save data to cache
        
        Args:
            key: Cache key
            data: Data to cache
            ttl: Time to live (optional)
            
        Raises:
            CacheError: If save operation fails
        """
        pass
    
    @abstractmethod
    def load(self, key: str) -> Optional[Any]:
        """
        Load data from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found/expired
        """
        pass
    
    @abstractmethod
    def invalidate(self, key: str) -> None:
        """
        Invalidate cached data
        
        Args:
            key: Cache key
        """
        pass
    
    @abstractmethod
    def is_valid(self, key: str) -> bool:
        """
        Check if cache entry is valid
        
        Args:
            key: Cache key
            
        Returns:
            True if cache entry exists and is not expired
        """
        pass
    
    @abstractmethod
    def clear_all(self) -> None:
        """
        Clear all cached data
        """
        pass
