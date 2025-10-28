"""
Permission Role Value Object
Type-safe permission role enumeration
"""

from enum import Enum
from typing import Optional


class PermissionRole(Enum):
    """
    Google Drive permission roles
    
    Defines the access levels for Drive permissions.
    """
    
    OWNER = "owner"
    ORGANIZER = "organizer"  # For shared drives
    FILE_ORGANIZER = "fileOrganizer"  # For shared drives
    WRITER = "writer"
    COMMENTER = "commenter"
    READER = "reader"
    
    @property
    def can_edit(self) -> bool:
        """Check if role can edit content"""
        return self in [
            PermissionRole.OWNER,
            PermissionRole.ORGANIZER,
            PermissionRole.FILE_ORGANIZER,
            PermissionRole.WRITER
        ]
    
    @property
    def can_comment(self) -> bool:
        """Check if role can add comments"""
        return self in [
            PermissionRole.OWNER,
            PermissionRole.ORGANIZER,
            PermissionRole.FILE_ORGANIZER,
            PermissionRole.WRITER,
            PermissionRole.COMMENTER
        ]
    
    @property
    def can_view(self) -> bool:
        """Check if role can view content"""
        return True  # All roles can view
    
    @property
    def is_ownership_role(self) -> bool:
        """Check if role represents ownership"""
        return self in [
            PermissionRole.OWNER,
            PermissionRole.ORGANIZER
        ]
    
    @classmethod
    def from_string(cls, value: str) -> 'PermissionRole':
        """
        Create PermissionRole from string
        
        Args:
            value: Role string (case-insensitive)
            
        Returns:
            PermissionRole enum value
            
        Raises:
            ValueError: If role is invalid
        """
        if not value:
            raise ValueError("Role cannot be empty")
        
        value = value.lower()
        for role in cls:
            if role.value.lower() == value:
                return role
        
        raise ValueError(f"Invalid permission role: {value}")
    
    @classmethod
    def try_parse(cls, value: str) -> Optional['PermissionRole']:
        """
        Try to parse role without raising exception
        
        Args:
            value: Role string
            
        Returns:
            PermissionRole or None if invalid
        """
        try:
            return cls.from_string(value)
        except ValueError:
            return None
    
    def __str__(self) -> str:
        """String representation"""
        return self.value
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"PermissionRole.{self.name}"


class PermissionType(Enum):
    """
    Google Drive permission types
    
    Defines how the permission is granted.
    """
    
    USER = "user"
    GROUP = "group"
    DOMAIN = "domain"
    ANYONE = "anyone"
    
    @property
    def is_direct_user(self) -> bool:
        """Check if permission is for a direct user"""
        return self == PermissionType.USER
    
    @property
    def is_group(self) -> bool:
        """Check if permission is for a group"""
        return self == PermissionType.GROUP
    
    @property
    def is_domain_wide(self) -> bool:
        """Check if permission is domain-wide"""
        return self == PermissionType.DOMAIN
    
    @property
    def is_public(self) -> bool:
        """Check if permission is public (anyone)"""
        return self == PermissionType.ANYONE
    
    @classmethod
    def from_string(cls, value: str) -> 'PermissionType':
        """
        Create PermissionType from string
        
        Args:
            value: Type string (case-insensitive)
            
        Returns:
            PermissionType enum value
            
        Raises:
            ValueError: If type is invalid
        """
        if not value:
            raise ValueError("Permission type cannot be empty")
        
        value = value.lower()
        for ptype in cls:
            if ptype.value.lower() == value:
                return ptype
        
        raise ValueError(f"Invalid permission type: {value}")
    
    @classmethod
    def try_parse(cls, value: str) -> Optional['PermissionType']:
        """
        Try to parse type without raising exception
        
        Args:
            value: Type string
            
        Returns:
            PermissionType or None if invalid
        """
        try:
            return cls.from_string(value)
        except ValueError:
            return None
    
    def __str__(self) -> str:
        """String representation"""
        return self.value
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"PermissionType.{self.name}"
