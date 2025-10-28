"""
JSON Report Formatter
Implements IReportFormatter for JSON format
"""

import json
from typing import Dict, Any, List
from datetime import datetime

from application.interfaces.services import IReportFormatter


class JSONReportFormatter(IReportFormatter):
    """
    JSON Report Formatter (Strategy Pattern)
    
    Formats report data as JSON with proper serialization.
    """
    
    def __init__(self, indent: int = 2, ensure_ascii: bool = False):
        """
        Initialize JSON formatter
        
        Args:
            indent: Number of spaces for indentation
            ensure_ascii: Whether to escape non-ASCII characters
        """
        self._indent = indent
        self._ensure_ascii = ensure_ascii
    
    def format(self, data: Dict[str, Any]) -> str:
        """
        Format data as JSON
        
        Args:
            data: Report data containing 'files' and 'metadata'
            
        Returns:
            JSON-formatted string
        """
        files = data.get('files', [])
        metadata = data.get('metadata', {})
        
        # Convert to JSON-serializable format
        serializable_data = {
            'metadata': metadata,
            'files': self._serialize_files(files),
            'summary': {
                'total_files': len(files),
                'generated_at': datetime.now().isoformat()
            }
        }
        
        return json.dumps(
            serializable_data,
            indent=self._indent,
            ensure_ascii=self._ensure_ascii,
            default=str
        )
    
    def get_extension(self) -> str:
        """Get file extension"""
        return 'json'
    
    def supports_multi_sheet(self) -> bool:
        """JSON supports nested structure (similar to multi-sheet)"""
        return True
    
    def _serialize_files(self, files: List) -> List[Dict[str, Any]]:
        """
        Serialize file data to JSON-compatible format
        
        Args:
            files: List of file entries
            
        Returns:
            List of serializable dictionaries
        """
        serialized = []
        
        for file_entry in files:
            if isinstance(file_entry, dict):
                # Already in dict format
                serialized.append(file_entry)
            else:
                # Convert DriveFile entity to dict
                file_dict = {
                    'file_id': str(file_entry.file_id),
                    'name': file_entry.name,
                    'mime_type': file_entry.mime_type,
                    'owners': [str(owner) for owner in file_entry.owners],
                    'shared': file_entry.shared,
                    'created_time': str(file_entry.created_time) if file_entry.created_time else None,
                    'modified_time': str(file_entry.modified_time) if file_entry.modified_time else None,
                    'web_view_link': file_entry.web_view_link,
                    'size': file_entry.size,
                    'is_folder': file_entry.is_folder,
                    'permissions': self._serialize_permissions(file_entry.permissions)
                }
                serialized.append(file_dict)
        
        return serialized
    
    def _serialize_permissions(self, permissions: List) -> List[Dict[str, Any]]:
        """
        Serialize permission data
        
        Args:
            permissions: List of Permission entities
            
        Returns:
            List of serializable dictionaries
        """
        serialized = []
        
        for perm in permissions:
            if isinstance(perm, dict):
                serialized.append(perm)
            else:
                perm_dict = {
                    'permission_id': str(perm.permission_id),
                    'role': str(perm.role),
                    'type': str(perm.permission_type),
                    'email': str(perm.email) if perm.email else None,
                    'display_name': perm.display_name,
                    'domain': perm.domain,
                    'deleted': perm.deleted,
                    'is_owner': perm.is_owner_permission(),
                    'can_be_revoked': perm.can_be_revoked()
                }
                serialized.append(perm_dict)
        
        return serialized
