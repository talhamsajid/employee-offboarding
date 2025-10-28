"""
File Analysis Service
Domain service for analyzing file access patterns
"""

from typing import List, Dict, Any
from collections import defaultdict
from domain.entities.drive_file import DriveFile
from domain.value_objects.email import Email


class FileAnalysisService:
    """
    File Analysis Service (Domain Service)
    
    Analyzes file access patterns and sharing relationships.
    """
    
    def analyze_file_sharing_patterns(
        self,
        files: List[DriveFile]
    ) -> Dict[str, Any]:
        """
        Analyze file sharing patterns
        
        Args:
            files: List of files to analyze
            
        Returns:
            Dictionary with sharing pattern statistics
        """
        total_files = len(files)
        shared_files = sum(1 for f in files if f.shared)
        total_permissions = sum(len(f.permissions) for f in files)
        
        # Analyze by MIME type
        files_by_type = defaultdict(int)
        for file in files:
            files_by_type[file.mime_type] += 1
        
        # Analyze sharing levels
        sharing_levels = {
            'not_shared': 0,
            'limited_sharing': 0,  # 1-5 people
            'moderate_sharing': 0,  # 6-20 people
            'wide_sharing': 0  # 20+ people
        }
        
        for file in files:
            perm_count = len(file.permissions)
            if perm_count == 0 or not file.shared:
                sharing_levels['not_shared'] += 1
            elif perm_count <= 5:
                sharing_levels['limited_sharing'] += 1
            elif perm_count <= 20:
                sharing_levels['moderate_sharing'] += 1
            else:
                sharing_levels['wide_sharing'] += 1
        
        return {
            'total_files': total_files,
            'shared_files': shared_files,
            'unshared_files': total_files - shared_files,
            'total_permissions': total_permissions,
            'avg_permissions_per_file': total_permissions / total_files if total_files > 0 else 0,
            'files_by_type': dict(files_by_type),
            'sharing_levels': sharing_levels
        }
    
    def find_most_shared_files(
        self,
        files: List[DriveFile],
        limit: int = 10
    ) -> List[DriveFile]:
        """
        Find files with the most sharing
        
        Args:
            files: List of files to analyze
            limit: Maximum number of results
            
        Returns:
            List of most shared files
        """
        sorted_files = sorted(
            files,
            key=lambda f: len(f.permissions),
            reverse=True
        )
        
        return sorted_files[:limit]
    
    def find_files_owned_by(
        self,
        files: List[DriveFile],
        owner_email: Email
    ) -> List[DriveFile]:
        """
        Find all files owned by a specific user
        
        Args:
            files: List of files to search
            owner_email: Owner email to find
            
        Returns:
            List of files owned by the user
        """
        return [f for f in files if f.is_owned_by(owner_email)]
    
    def find_files_shared_with(
        self,
        files: List[DriveFile],
        user_email: Email
    ) -> List[DriveFile]:
        """
        Find all files shared with a specific user
        
        Args:
            files: List of files to search
            user_email: User email to find
            
        Returns:
            List of files shared with the user
        """
        return [f for f in files if f.is_shared_with(user_email)]
    
    def get_user_access_summary(
        self,
        files: List[DriveFile],
        user_email: Email
    ) -> Dict[str, Any]:
        """
        Get comprehensive access summary for a user
        
        Args:
            files: List of files to analyze
            user_email: User email
            
        Returns:
            Dictionary with access summary
        """
        owned_files = self.find_files_owned_by(files, user_email)
        shared_files = self.find_files_shared_with(files, user_email)
        
        # Analyze permission types for shared files
        permission_roles = defaultdict(int)
        for file in shared_files:
            perm = file.get_permission_for_user(user_email)
            if perm:
                permission_roles[str(perm.role)] += 1
        
        return {
            'user_email': str(user_email),
            'total_owned_files': len(owned_files),
            'total_shared_files': len(shared_files),
            'permission_breakdown': dict(permission_roles),
            'has_ownership_access': len(owned_files) > 0
        }
    
    def identify_orphaned_files(
        self,
        files: List[DriveFile]
    ) -> List[DriveFile]:
        """
        Identify files with no active owners
        
        Args:
            files: List of files to analyze
            
        Returns:
            List of potentially orphaned files
        """
        orphaned = []
        
        for file in files:
            if not file.owners or len(file.owners) == 0:
                orphaned.append(file)
        
        return orphaned
