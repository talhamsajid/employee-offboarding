"""
Input Validator
Validates user input for the CLI
"""

import re
from typing import Optional, List
from domain.value_objects.email import Email
from domain.exceptions.access_manager_errors import ValidationError


class InputValidator:
    """
    Input Validator
    
    Validates user input before processing.
    Ensures data integrity at the presentation layer boundary.
    """
    
    @staticmethod
    def validate_email(email_str: str) -> str:
        """
        Validate email address
        
        Args:
            email_str: Email string to validate
            
        Returns:
            Validated email string
            
        Raises:
            ValidationError: If email is invalid
        """
        if not email_str or not email_str.strip():
            raise ValidationError(
                "Email address is required",
                field="email",
                constraint="non-empty"
            )
        
        try:
            email = Email(email_str.strip())
            return str(email)
        except ValueError as e:
            raise ValidationError(
                str(e),
                field="email",
                value=email_str,
                constraint="valid email format"
            )
    
    @staticmethod
    def validate_report_formats(formats: List[str]) -> List[str]:
        """
        Validate report format selections
        
        Args:
            formats: List of format strings
            
        Returns:
            Validated format list
            
        Raises:
            ValidationError: If any format is invalid
        """
        if not formats:
            raise ValidationError(
                "At least one report format must be selected",
                field="report_formats",
                constraint="non-empty"
            )
        
        valid_formats = {'csv', 'excel', 'xlsx', 'json', 'html'}
        validated = []
        
        for fmt in formats:
            fmt_lower = fmt.lower().strip()
            if fmt_lower not in valid_formats:
                raise ValidationError(
                    f"Invalid report format: {fmt}",
                    field="report_formats",
                    value=fmt,
                    constraint=f"must be one of: {', '.join(valid_formats)}"
                )
            
            # Normalize xlsx to excel
            if fmt_lower == 'xlsx':
                fmt_lower = 'excel'
            
            if fmt_lower not in validated:
                validated.append(fmt_lower)
        
        return validated
    
    @staticmethod
    def validate_yes_no(response: str) -> bool:
        """
        Validate yes/no response
        
        Args:
            response: User response
            
        Returns:
            True for yes, False for no
            
        Raises:
            ValidationError: If response is invalid
        """
        if not response or not response.strip():
            raise ValidationError(
                "Response is required",
                field="confirmation",
                constraint="yes or no"
            )
        
        response_lower = response.strip().lower()
        
        if response_lower in ['y', 'yes', 'true', '1']:
            return True
        elif response_lower in ['n', 'no', 'false', '0']:
            return False
        else:
            raise ValidationError(
                f"Invalid response: {response}",
                field="confirmation",
                value=response,
                constraint="must be yes/no, y/n, true/false, or 1/0"
            )
    
    @staticmethod
    def validate_cache_days(days_str: str) -> int:
        """
        Validate cache days input
        
        Args:
            days_str: Days as string
            
        Returns:
            Validated days as integer
            
        Raises:
            ValidationError: If invalid
        """
        try:
            days = int(days_str.strip())
            if days < 0:
                raise ValidationError(
                    "Cache days must be non-negative",
                    field="cache_days",
                    value=days_str,
                    constraint=">=0"
                )
            if days > 365:
                raise ValidationError(
                    "Cache days cannot exceed 365",
                    field="cache_days",
                    value=days_str,
                    constraint="<=365"
                )
            return days
        except ValueError:
            raise ValidationError(
                f"Invalid number: {days_str}",
                field="cache_days",
                value=days_str,
                constraint="must be a valid integer"
            )
    
    @staticmethod
    def sanitize_input(input_str: str, max_length: int = 1000) -> str:
        """
        Sanitize user input
        
        Args:
            input_str: Input string
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
            
        Raises:
            ValidationError: If input is too long or contains dangerous characters
        """
        if not input_str:
            return ""
        
        # Check length
        if len(input_str) > max_length:
            raise ValidationError(
                f"Input too long (max {max_length} characters)",
                field="input",
                value=f"{len(input_str)} characters",
                constraint=f"max {max_length}"
            )
        
        # Remove control characters
        sanitized = ''.join(char for char in input_str if ord(char) >= 32 or char in ['\n', '\t'])
        
        return sanitized.strip()
