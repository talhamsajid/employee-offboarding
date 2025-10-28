"""
User Entity
Represents a user in the system
"""

from typing import Optional
from domain.value_objects.email import Email


class User:
    """
    User domain entity
    
    Represents a user (employee, contractor, etc.) whose access
    needs to be managed.
    """
    
    def __init__(
        self,
        email: Email,
        display_name: Optional[str] = None,
        is_active: bool = True
    ):
        """
        Initialize User entity
        
        Args:
            email: User's email address
            display_name: User's display name
            is_active: Whether user is active in the organization
        """
        self._email = email
        self._display_name = display_name or str(email)
        self._is_active = is_active
    
    @property
    def email(self) -> Email:
        """Get the user's email"""
        return self._email
    
    @property
    def display_name(self) -> str:
        """Get the user's display name"""
        return self._display_name
    
    @property
    def is_active(self) -> bool:
        """Check if user is active"""
        return self._is_active
    
    @property
    def domain(self) -> str:
        """Get the user's domain"""
        return self._email.domain
    
    def deactivate(self) -> None:
        """Mark user as inactive (offboarded)"""
        self._is_active = False
    
    def activate(self) -> None:
        """Mark user as active"""
        self._is_active = True
    
    def __eq__(self, other) -> bool:
        """Check equality based on email"""
        if not isinstance(other, User):
            return False
        return self._email == other._email
    
    def __hash__(self) -> int:
        """Hash based on email"""
        return hash(self._email)
    
    def __str__(self) -> str:
        """String representation"""
        status = "active" if self._is_active else "inactive"
        return f"{self._display_name} <{self._email}> ({status})"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"User(email={self._email}, display_name='{self._display_name}')"
