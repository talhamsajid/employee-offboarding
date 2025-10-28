"""
Google Permission Repository Implementation
Implements IPermissionRepository using Google Drive API
"""

import time
from typing import List
from googleapiclient.errors import HttpError

from application.interfaces.repositories import IPermissionRepository
from domain.entities.permission import Permission
from domain.value_objects.identifiers import FileId, PermissionId
from domain.exceptions.access_manager_errors import (
    RepositoryError,
    PermissionDeniedError,
    RateLimitError,
    FileNotFoundError as DomainFileNotFoundError,
    ValidationError
)
from domain.value_objects.permission_role import PermissionRole


class GooglePermissionRepository(IPermissionRepository):
    """
    Google Permission Repository
    
    Concrete implementation of IPermissionRepository using Google Drive API.
    Handles permission operations with proper error handling.
    """
    
    def __init__(self, drive_service, rate_limit_delay: float = 0.1):
        """
        Initialize Google Permission Repository
        
        Args:
            drive_service: Authenticated Google Drive API service
            rate_limit_delay: Delay between requests to avoid rate limits
        """
        self._drive_service = drive_service
        self._rate_limit_delay = rate_limit_delay
    
    def get_file_permissions(self, file_id: FileId) -> List[Permission]:
        """
        Get all permissions for a file
        
        Args:
            file_id: File identifier
            
        Returns:
            List of Permission entities
            
        Raises:
            FileNotFoundError: If file not found
            PermissionDeniedError: If insufficient permissions
            RepositoryError: If API call fails
        """
        try:
            response = self._drive_service.permissions().list(
                fileId=str(file_id),
                fields="permissions(id, emailAddress, role, type, displayName, domain, deleted)",
                supportsAllDrives=True
            ).execute()
            
            permissions = []
            for perm_data in response.get('permissions', []):
                try:
                    permission = Permission.from_api_response(perm_data)
                    permissions.append(permission)
                except (ValueError, KeyError):
                    # Skip invalid permissions
                    continue
            
            return permissions
        
        except HttpError as error:
            if error.resp.status == 404:
                raise DomainFileNotFoundError(
                    f"File not found: {file_id}",
                    file_id=str(file_id)
                )
            if error.resp.status == 403:
                raise PermissionDeniedError(
                    f"Insufficient permissions to access file {file_id}",
                    file_id=str(file_id),
                    required_permission="read"
                )
            if error.resp.status == 429:
                raise RateLimitError(
                    "Google Drive API rate limit exceeded",
                    retry_after=60,
                    quota_type="drive_api"
                )
            raise RepositoryError(
                f"Failed to get permissions for file {file_id}: {error}",
                repository="GooglePermissionRepository",
                operation="get_file_permissions"
            )
    
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
            RepositoryError: If API call fails
        """
        try:
            self._drive_service.permissions().delete(
                fileId=str(file_id),
                permissionId=str(permission_id),
                supportsAllDrives=True,
                useDomainAdminAccess=use_admin_access
            ).execute()
            
            # Small delay to avoid rate limiting
            time.sleep(self._rate_limit_delay)
            
            return True
        
        except HttpError as error:
            error_reason = self._extract_error_reason(error)
            
            if error.resp.status == 404:
                raise DomainFileNotFoundError(
                    f"File or permission not found",
                    file_id=str(file_id)
                )
            
            if error.resp.status == 403 or error_reason in [
                'cannotDeletePermission',
                'insufficientPermissions'
            ]:
                raise PermissionDeniedError(
                    f"Cannot revoke permission: {error_reason}",
                    file_id=str(file_id),
                    required_permission="owner or admin"
                )
            
            if error.resp.status == 429:
                raise RateLimitError(
                    "Google Drive API rate limit exceeded",
                    retry_after=60,
                    quota_type="drive_api"
                )
            
            raise RepositoryError(
                f"Failed to revoke permission: {error}",
                repository="GooglePermissionRepository",
                operation="revoke_permission"
            )
    
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
            RepositoryError: If API call fails
        """
        # Validate role
        try:
            role = PermissionRole.from_string(new_role)
        except ValueError as e:
            raise ValidationError(
                str(e),
                field="role",
                value=new_role,
                constraint="must be reader, writer, commenter, or owner"
            )
        
        try:
            updated_perm_data = self._drive_service.permissions().update(
                fileId=str(file_id),
                permissionId=str(permission_id),
                body={'role': str(role)},
                fields="id, emailAddress, role, type, displayName",
                supportsAllDrives=True
            ).execute()
            
            # Small delay to avoid rate limiting
            time.sleep(self._rate_limit_delay)
            
            return Permission.from_api_response(updated_perm_data)
        
        except HttpError as error:
            if error.resp.status == 404:
                raise DomainFileNotFoundError(
                    f"File or permission not found",
                    file_id=str(file_id)
                )
            
            if error.resp.status == 403:
                raise PermissionDeniedError(
                    f"Cannot update permission role",
                    file_id=str(file_id),
                    required_permission="owner or admin"
                )
            
            if error.resp.status == 429:
                raise RateLimitError(
                    "Google Drive API rate limit exceeded",
                    retry_after=60,
                    quota_type="drive_api"
                )
            
            raise RepositoryError(
                f"Failed to update permission role: {error}",
                repository="GooglePermissionRepository",
                operation="update_permission_role"
            )
    
    def _extract_error_reason(self, error: HttpError) -> str:
        """
        Extract the reason from an HttpError
        
        Args:
            error: HttpError object
            
        Returns:
            String describing the error reason
        """
        try:
            error_details = error.error_details
            if error_details and len(error_details) > 0:
                detail = error_details[0]
                if isinstance(detail, dict):
                    return detail.get('reason', 'unknown')
        except:
            pass
        
        # Try to parse from error message
        error_str = str(error)
        if 'cannotDeletePermission' in error_str:
            return 'cannotDeletePermission'
        elif 'insufficientPermissions' in error_str:
            return 'insufficientPermissions'
        elif 'fileNotFound' in error_str:
            return 'fileNotFound'
        
        return 'unknown'
