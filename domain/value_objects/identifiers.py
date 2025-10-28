"""
File ID and Permission ID Value Objects
Type-safe identifiers for Drive resources
"""

from typing import Optional


class FileId:
    """
    Google Drive File ID value object
    
    Immutable identifier for a Drive file.
    Provides type safety and validation.
    """
    
    def __init__(self, value: str):
        """
        Initialize FileId
        
        Args:
            value: File ID string
            
        Raises:
            ValueError: If file ID is invalid
        """
        if not value or not isinstance(value, str):
            raise ValueError("File ID must be a non-empty string")
        
        value = value.strip()
        if not value:
            raise ValueError("File ID cannot be empty or whitespace")
        
        # Google Drive file IDs are typically 25-50 characters
        if len(value) < 10 or len(value) > 100:
            raise ValueError(f"Invalid file ID length: {len(value)}")
        
        self._value = value
    
    @property
    def value(self) -> str:
        """Get the file ID value"""
        return self._value
    
    def __eq__(self, other) -> bool:
        """Equality operator"""
        if isinstance(other, FileId):
            return self._value == other._value
        if isinstance(other, str):
            return self._value == other
        return False
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries"""
        return hash(self._value)
    
    def __str__(self) -> str:
        """String representation"""
        return self._value
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"FileId('{self._value}')"
    
    @classmethod
    def try_parse(cls, value: str) -> Optional['FileId']:
        """
        Try to parse file ID without raising exception
        
        Args:
            value: File ID string
            
        Returns:
            FileId object or None if invalid
        """
        try:
            return cls(value)
        except ValueError:
            return None


class PermissionId:
    """
    Google Drive Permission ID value object
    
    Immutable identifier for a permission.
    Provides type safety and validation.
    """
    
    def __init__(self, value: str):
        """
        Initialize PermissionId
        
        Args:
            value: Permission ID string
            
        Raises:
            ValueError: If permission ID is invalid
        """
        if not value or not isinstance(value, str):
            raise ValueError("Permission ID must be a non-empty string")
        
        value = value.strip()
        if not value:
            raise ValueError("Permission ID cannot be empty or whitespace")
        
        self._value = value
    
    @property
    def value(self) -> str:
        """Get the permission ID value"""
        return self._value
    
    def __eq__(self, other) -> bool:
        """Equality operator"""
        if isinstance(other, PermissionId):
            return self._value == other._value
        if isinstance(other, str):
            return self._value == other
        return False
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries"""
        return hash(self._value)
    
    def __str__(self) -> str:
        """String representation"""
        return self._value
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"PermissionId('{self._value}')"
    
    @classmethod
    def try_parse(cls, value: str) -> Optional['PermissionId']:
        """
        Try to parse permission ID without raising exception
        
        Args:
            value: Permission ID string
            
        Returns:
            PermissionId object or None if invalid
        """
        try:
            return cls(value)
        except ValueError:
            return None
