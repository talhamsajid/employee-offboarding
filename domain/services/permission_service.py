"""
Permission Service
Domain service for permission-related business logic
"""

from typing import List, Optional
from domain.entities.drive_file import DriveFile
from domain.entities.permission import Permission
from domain.value_objects.email import Email


class PermissionService:
    """
    Permission Service (Domain Service)
    
    Encapsulates complex business logic related to permissions
    that doesn't naturally belong to a single entity.
    """
    
    def can_revoke_all_permissions(
        self,
        file: DriveFile,
        target_user_email: Email,
        current_user_email: Email
    ) -> bool:
        """
        Check if current user can revoke all permissions for target user
        
        Args:
            file: File to check
            target_user_email: Email of user whose permissions to revoke
            current_user_email: Email of user attempting revocation
            
        Returns:
            True if revocation is allowed
        """
        # Cannot revoke if target is owner
        if file.is_owned_by(target_user_email):
            return False
        
        # Current user must be owner to revoke others' permissions
        if not file.is_owned_by(current_user_email):
            return False
        
        return True
    
    def get_revocable_permissions_summary(
        self,
        files: List[DriveFile],
        target_user_email: Email
    ) -> dict:
        """
        Get summary of revocable permissions across files
        
        Args:
            files: List of files to analyze
            target_user_email: Target user email
            
        Returns:
            Dictionary with summary statistics
        """
        total_files = len(files)
        files_with_access = 0
        revocable_count = 0
        non_revocable_count = 0
        
        for file in files:
            if file.is_shared_with(target_user_email):
                files_with_access += 1
                
                if file.can_revoke_permission_for(target_user_email):
                    revocable_permissions = file.get_revocable_permissions_for_user(target_user_email)
                    revocable_count += len(revocable_permissions)
                else:
                    # User is owner - cannot revoke
                    non_revocable_count += 1
        
        return {
            'total_files': total_files,
            'files_with_access': files_with_access,
            'revocable_permissions': revocable_count,
            'non_revocable_files': non_revocable_count
        }
    
    def classify_permissions_by_risk(
        self,
        permissions: List[Permission]
    ) -> dict:
        """
        Classify permissions by risk level
        
        Args:
            permissions: List of permissions to classify
            
        Returns:
            Dictionary with risk classifications
        """
        high_risk = []  # Owner, writer permissions
        medium_risk = []  # Commenter permissions
        low_risk = []  # Reader permissions
        
        for perm in permissions:
            if perm.role.is_ownership_role or perm.role.can_edit:
                high_risk.append(perm)
            elif perm.role.can_comment:
                medium_risk.append(perm)
            else:
                low_risk.append(perm)
        
        return {
            'high_risk': high_risk,
            'medium_risk': medium_risk,
            'low_risk': low_risk
        }
    
    def should_notify_owner(
        self,
        file: DriveFile,
        permission_to_revoke: Permission
    ) -> bool:
        """
        Determine if file owner should be notified of revocation
        
        Args:
            file: File where permission is being revoked
            permission_to_revoke: Permission being revoked
            
        Returns:
            True if owner should be notified
        """
        # Notify for high-risk permissions
        if permission_to_revoke.role.is_ownership_role or permission_to_revoke.role.can_edit:
            return True
        
        # Notify if file has been shared extensively
        if len(file.permissions) > 10:
            return True
        
        return False
