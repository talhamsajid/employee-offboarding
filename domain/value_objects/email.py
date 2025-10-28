"""
Email Value Object
Immutable email address with validation
"""

import re
from typing import Optional


class Email:
    """
    Email value object with validation
    
    Immutable object representing an email address.
    Ensures email format is valid upon creation.
    """
    
    # RFC 5322 simplified email pattern
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    def __init__(self, value: str):
        """
        Initialize email with validation
        
        Args:
            value: Email address string
            
        Raises:
            ValueError: If email format is invalid
        """
        if not value or not isinstance(value, str):
            raise ValueError("Email must be a non-empty string")
        
        # Normalize email (lowercase)
        normalized = value.strip().lower()
        
        if not self.EMAIL_PATTERN.match(normalized):
            raise ValueError(f"Invalid email format: {value}")
        
        self._value = normalized
    
    @property
    def value(self) -> str:
        """Get the email value"""
        return self._value
    
    @property
    def domain(self) -> str:
        """Extract domain from email"""
        return self._value.split('@')[1]
    
    @property
    def local_part(self) -> str:
        """Extract local part (before @) from email"""
        return self._value.split('@')[0]
    
    def equals(self, other: 'Email') -> bool:
        """
        Check equality with another Email
        
        Args:
            other: Another Email object
            
        Returns:
            True if emails are equal
        """
        if not isinstance(other, Email):
            return False
        return self._value == other._value
    
    def __eq__(self, other) -> bool:
        """Equality operator"""
        if isinstance(other, Email):
            return self._value == other._value
        if isinstance(other, str):
            try:
                return self._value == Email(other)._value
            except ValueError:
                return False
        return False
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries"""
        return hash(self._value)
    
    def __str__(self) -> str:
        """String representation"""
        return self._value
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"Email('{self._value}')"
    
    @classmethod
    def try_parse(cls, value: str) -> Optional['Email']:
        """
        Try to parse email without raising exception
        
        Args:
            value: Email string to parse
            
        Returns:
            Email object or None if invalid
        """
        try:
            return cls(value)
        except ValueError:
            return None
