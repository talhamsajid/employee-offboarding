"""
DriveFile Entity
Represents a Google Drive file with business logic
"""

from typing import List, Optional
from datetime import datetime

from domain.value_objects.email import Email
from domain.value_objects.identifiers import FileId
from domain.entities.permission import Permission


class DriveFile:
    """
    DriveFile domain entity (Aggregate Root)
    
    Represents a Google Drive file with its permissions.
    Contains business logic for permission management.
    """
    
    def __init__(
        self,
        file_id: FileId,
        name: str,
        mime_type: str,
        owners: List[Email],
        permissions: List[Permission],
        created_time: Optional[datetime] = None,
        modified_time: Optional[datetime] = None,
        web_view_link: Optional[str] = None,
        size: Optional[int] = None,
        shared: bool = False
    ):
        """
        Initialize DriveFile entity
        
        Args:
            file_id: Unique file identifier
            name: File name
            mime_type: MIME type of the file
            owners: List of owner email addresses
            permissions: List of permissions on the file
            created_time: File creation timestamp
            modified_time: File modification timestamp
            web_view_link: URL to view file in browser
            size: File size in bytes
            shared: Whether file is shared
        """
        self._file_id = file_id
        self._name = name
        self._mime_type = mime_type
        self._owners = owners
        self._permissions = permissions
        self._created_time = created_time
        self._modified_time = modified_time
        self._web_view_link = web_view_link
        self._size = size
        self._shared = shared
    
    @property
    def file_id(self) -> FileId:
        """Get the file ID"""
        return self._file_id
    
    @property
    def name(self) -> str:
        """Get the file name"""
        return self._name
    
    @property
    def mime_type(self) -> str:
        """Get the MIME type"""
        return self._mime_type
    
    @property
    def owners(self) -> List[Email]:
        """Get the file owners"""
        return self._owners.copy()
    
    @property
    def permissions(self) -> List[Permission]:
        """Get the file permissions"""
        return self._permissions.copy()
    
    @property
    def created_time(self) -> Optional[datetime]:
        """Get the creation time"""
        return self._created_time
    
    @property
    def modified_time(self) -> Optional[datetime]:
        """Get the modification time"""
        return self._modified_time
    
    @property
    def web_view_link(self) -> Optional[str]:
        """Get the web view link"""
        return self._web_view_link
    
    @property
    def size(self) -> Optional[int]:
        """Get the file size"""
        return self._size
    
    @property
    def shared(self) -> bool:
        """Check if file is shared"""
        return self._shared
    
    @property
    def is_folder(self) -> bool:
        """Check if file is a folder"""
        return self._mime_type == 'application/vnd.google-apps.folder'
    
    @property
    def is_google_doc(self) -> bool:
        """Check if file is a Google Workspace document"""
        google_mime_types = [
            'application/vnd.google-apps.document',
            'application/vnd.google-apps.spreadsheet',
            'application/vnd.google-apps.presentation',
            'application/vnd.google-apps.form',
            'application/vnd.google-apps.drawing'
        ]
        return self._mime_type in google_mime_types
    
    def is_shared_with(self, email: Email) -> bool:
        """
        Check if file is shared with a specific user
        
        Args:
            email: Email address to check
            
        Returns:
            True if file is shared with the user
        """
        for permission in self._permissions:
            if permission.belongs_to_user(email):
                return True
        return False
    
    def is_owned_by(self, email: Email) -> bool:
        """
        Check if file is owned by a specific user
        
        Args:
            email: Email address to check
            
        Returns:
            True if user is an owner
        """
        return email in self._owners
    
    def can_revoke_permission_for(self, email: Email) -> bool:
        """
        Check if permissions for a user can be revoked
        
        Cannot revoke if user is an owner.
        
        Args:
            email: Email address to check
            
        Returns:
            True if permission can be revoked
        """
        # Cannot revoke owner permissions
        if self.is_owned_by(email):
            return False
        
        # Check if user has any revocable permissions
        for permission in self._permissions:
            if permission.belongs_to_user(email) and permission.can_be_revoked():
                return True
        
        return False
    
    def get_permission_for_user(self, email: Email) -> Optional[Permission]:
        """
        Get the permission for a specific user
        
        Args:
            email: Email address
            
        Returns:
            Permission object or None if not found
        """
        for permission in self._permissions:
            if permission.belongs_to_user(email):
                return permission
        return None
    
    def get_revocable_permissions_for_user(self, email: Email) -> List[Permission]:
        """
        Get all revocable permissions for a user
        
        Args:
            email: Email address
            
        Returns:
            List of revocable permissions
        """
        revocable = []
        for permission in self._permissions:
            if permission.belongs_to_user(email) and permission.can_be_revoked():
                revocable.append(permission)
        return revocable
    
    def remove_permission(self, permission: Permission) -> None:
        """
        Remove a permission from the file
        
        Args:
            permission: Permission to remove
        """
        self._permissions = [p for p in self._permissions if p != permission]
    
    def add_permission(self, permission: Permission) -> None:
        """
        Add a permission to the file
        
        Args:
            permission: Permission to add
        """
        # Don't add duplicates
        if permission not in self._permissions:
            self._permissions.append(permission)
    
    def __eq__(self, other) -> bool:
        """Check equality based on file ID"""
        if not isinstance(other, DriveFile):
            return False
        return self._file_id == other._file_id
    
    def __hash__(self) -> int:
        """Hash based on file ID"""
        return hash(self._file_id)
    
    def __str__(self) -> str:
        """String representation"""
        return f"DriveFile('{self._name}', {len(self._permissions)} permissions)"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return (f"DriveFile(id={self._file_id}, name='{self._name}', "
                f"mime_type='{self._mime_type}')")
    
    @classmethod
    def from_api_response(cls, data: dict) -> 'DriveFile':
        """
        Create DriveFile from Google Drive API response
        
        Args:
            data: API response dictionary
            
        Returns:
            DriveFile entity
        """
        file_id = FileId(data['id'])
        name = data.get('name', 'Unknown')
        mime_type = data.get('mimeType', 'application/octet-stream')
        
        # Parse owners
        owners = []
        for owner_data in data.get('owners', []):
            email = Email.try_parse(owner_data.get('emailAddress', ''))
            if email:
                owners.append(email)
        
        # Parse permissions
        permissions = []
        for perm_data in data.get('permissions', []):
            try:
                permission = Permission.from_api_response(perm_data)
                permissions.append(permission)
            except (ValueError, KeyError):
                # Skip invalid permissions
                continue
        
        # Parse timestamps
        created_time = None
        if 'createdTime' in data:
            try:
                created_time = datetime.fromisoformat(
                    data['createdTime'].replace('Z', '+00:00')
                )
            except ValueError:
                pass
        
        modified_time = None
        if 'modifiedTime' in data:
            try:
                modified_time = datetime.fromisoformat(
                    data['modifiedTime'].replace('Z', '+00:00')
                )
            except ValueError:
                pass
        
        web_view_link = data.get('webViewLink')
        size = data.get('size')
        if size is not None:
            size = int(size)
        
        shared = data.get('shared', False)
        
        return cls(
            file_id=file_id,
            name=name,
            mime_type=mime_type,
            owners=owners,
            permissions=permissions,
            created_time=created_time,
            modified_time=modified_time,
            web_view_link=web_view_link,
            size=size,
            shared=shared
        )
