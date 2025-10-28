"""
Access Management Request DTO
Data transfer object for access management requests
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class OperationMode(Enum):
    """Access management operation modes"""
    REVOKE_ALL = "revoke_all"
    AUDIT_ONLY = "audit_only"
    DOWNGRADE_PERMISSIONS = "downgrade_permissions"
    GRANT_ACCESS = "grant_access"


@dataclass
class AccessManagementRequest:
    """
    Access Management Request DTO
    
    Encapsulates all parameters for an access management operation.
    Uses Builder pattern for complex construction.
    """
    
    target_email: str
    operation_mode: OperationMode = OperationMode.REVOKE_ALL
    dry_run: bool = False
    report_formats: List[str] = field(default_factory=lambda: ['csv', 'excel'])
    skip_errors: bool = False
    use_admin_access: bool = False
    cache_enabled: bool = True
    force_cache_refresh: bool = False
    
    def __post_init__(self):
        """Post-initialization processing"""
        pass  # field default_factory handles initialization
    
    def validate(self) -> None:
        """
        Validate request parameters
        
        Raises:
            ValueError: If parameters are invalid
        """
        if not self.target_email or '@' not in self.target_email:
            raise ValueError(f"Invalid target email: {self.target_email}")
        
        valid_formats = {'csv', 'excel', 'json', 'html'}
        for fmt in self.report_formats:
            if fmt.lower() not in valid_formats:
                raise ValueError(f"Invalid report format: {fmt}")


class AccessManagementRequestBuilder:
    """
    Builder for AccessManagementRequest (Builder Pattern)
    
    Provides fluent API for constructing complex requests.
    """
    
    def __init__(self, target_email: str):
        """
        Initialize builder
        
        Args:
            target_email: Target user email (required)
        """
        self._target_email = target_email
        self._operation_mode = OperationMode.REVOKE_ALL
        self._dry_run = False
        self._report_formats = ['csv', 'excel']
        self._skip_errors = False
        self._use_admin_access = False
        self._cache_enabled = True
        self._force_cache_refresh = False
    
    def with_operation(self, mode: OperationMode) -> 'AccessManagementRequestBuilder':
        """Set operation mode"""
        self._operation_mode = mode
        return self
    
    def as_dry_run(self) -> 'AccessManagementRequestBuilder':
        """Enable dry run mode"""
        self._dry_run = True
        return self
    
    def with_formats(self, formats: List[str]) -> 'AccessManagementRequestBuilder':
        """Set report formats"""
        self._report_formats = formats
        return self
    
    def skip_errors(self) -> 'AccessManagementRequestBuilder':
        """Enable skip errors mode"""
        self._skip_errors = True
        return self
    
    def use_admin_access(self) -> 'AccessManagementRequestBuilder':
        """Enable admin access override"""
        self._use_admin_access = True
        return self
    
    def without_cache(self) -> 'AccessManagementRequestBuilder':
        """Disable caching"""
        self._cache_enabled = False
        return self
    
    def force_refresh_cache(self) -> 'AccessManagementRequestBuilder':
        """Force cache refresh"""
        self._force_cache_refresh = True
        return self
    
    def build(self) -> AccessManagementRequest:
        """
        Build the request
        
        Returns:
            AccessManagementRequest instance
        """
        request = AccessManagementRequest(
            target_email=self._target_email,
            operation_mode=self._operation_mode,
            dry_run=self._dry_run,
            report_formats=self._report_formats,
            skip_errors=self._skip_errors,
            use_admin_access=self._use_admin_access,
            cache_enabled=self._cache_enabled,
            force_cache_refresh=self._force_cache_refresh
        )
        
        request.validate()
        return request
