"""
Permission Entity
Represents a Google Drive permission with business logic
"""

from typing import Optional
from datetime import datetime

from domain.value_objects.email import Email
from domain.value_objects.identifiers import PermissionId
from domain.value_objects.permission_role import PermissionRole, PermissionType


class Permission:
    """
    Permission domain entity
    
    Represents a permission on a Drive file with business logic
    for determining if it can be revoked.
    """
    
    def __init__(
        self,
        permission_id: PermissionId,
        role: PermissionRole,
        permission_type: PermissionType,
        email: Optional[Email] = None,
        display_name: Optional[str] = None,
        domain: Optional[str] = None,
        deleted: bool = False
    ):
        """
        Initialize Permission entity
        
        Args:
            permission_id: Unique permission identifier
            role: Permission role (owner, writer, reader, etc.)
            permission_type: Type (user, group, domain, anyone)
            email: Email address (for user/group permissions)
            display_name: Display name of the permission holder
            domain: Domain name (for domain permissions)
            deleted: Whether the permission has been deleted
        """
        self._permission_id = permission_id
        self._role = role
        self._permission_type = permission_type
        self._email = email
        self._display_name = display_name
        self._domain = domain
        self._deleted = deleted
    
    @property
    def permission_id(self) -> PermissionId:
        """Get the permission ID"""
        return self._permission_id
    
    @property
    def role(self) -> PermissionRole:
        """Get the permission role"""
        return self._role
    
    @property
    def permission_type(self) -> PermissionType:
        """Get the permission type"""
        return self._permission_type
    
    @property
    def email(self) -> Optional[Email]:
        """Get the email address"""
        return self._email
    
    @property
    def display_name(self) -> Optional[str]:
        """Get the display name"""
        return self._display_name
    
    @property
    def domain(self) -> Optional[str]:
        """Get the domain"""
        return self._domain
    
    @property
    def deleted(self) -> bool:
        """Check if permission is deleted"""
        return self._deleted
    
    def is_owner_permission(self) -> bool:
        """
        Check if this is an owner permission
        
        Returns:
            True if permission grants ownership
        """
        return self._role.is_ownership_role
    
    def can_be_revoked(self) -> bool:
        """
        Check if this permission can be revoked
        
        Owner permissions cannot be revoked directly.
        
        Returns:
            True if permission can be revoked
        """
        # Cannot revoke owner permissions
        if self.is_owner_permission():
            return False
        
        # Cannot revoke if already deleted
        if self._deleted:
            return False
        
        return True
    
    def belongs_to_user(self, user_email: Email) -> bool:
        """
        Check if this permission belongs to a specific user
        
        Args:
            user_email: Email to check
            
        Returns:
            True if permission belongs to user
        """
        if not self._email:
            return False
        
        return self._email.equals(user_email)
    
    def mark_as_deleted(self) -> None:
        """Mark this permission as deleted"""
        self._deleted = True
    
    def __eq__(self, other) -> bool:
        """Check equality based on permission ID"""
        if not isinstance(other, Permission):
            return False
        return self._permission_id == other._permission_id
    
    def __hash__(self) -> int:
        """Hash based on permission ID"""
        return hash(self._permission_id)
    
    def __str__(self) -> str:
        """String representation"""
        email_str = str(self._email) if self._email else "N/A"
        return f"Permission({self._role}, {self._permission_type}, {email_str})"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return (f"Permission(id={self._permission_id}, role={self._role}, "
                f"type={self._permission_type}, email={self._email})")
    
    @classmethod
    def from_api_response(cls, data: dict) -> 'Permission':
        """
        Create Permission from Google Drive API response
        
        Args:
            data: API response dictionary
            
        Returns:
            Permission entity
        """
        permission_id = PermissionId(data['id'])
        role = PermissionRole.from_string(data['role'])
        permission_type = PermissionType.from_string(data['type'])
        
        email = None
        if 'emailAddress' in data and data['emailAddress']:
            email = Email.try_parse(data['emailAddress'])
        
        display_name = data.get('displayName')
        domain = data.get('domain')
        deleted = data.get('deleted', False)
        
        return cls(
            permission_id=permission_id,
            role=role,
            permission_type=permission_type,
            email=email,
            display_name=display_name,
            domain=domain,
            deleted=deleted
        )
