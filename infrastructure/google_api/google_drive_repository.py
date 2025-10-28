"""
Google Drive Repository Implementation
Implements IDriveRepository using Google Drive API
"""

import time
from typing import List, Optional
from googleapiclient.errors import HttpError

from application.interfaces.repositories import IDriveRepository
from domain.entities.drive_file import DriveFile
from domain.value_objects.email import Email
from domain.value_objects.identifiers import FileId
from domain.exceptions.access_manager_errors import (
    RepositoryError,
    FileNotFoundError as DomainFileNotFoundError,
    RateLimitError
)


class GoogleDriveRepository(IDriveRepository):
    """
    Google Drive Repository
    
    Concrete implementation of IDriveRepository using Google Drive API.
    Handles API communication, pagination, and error handling.
    """
    
    def __init__(self, drive_service, page_size: int = 100, rate_limit_delay: float = 0.1):
        """
        Initialize Google Drive Repository
        
        Args:
            drive_service: Authenticated Google Drive API service
            page_size: Number of files to fetch per request
            rate_limit_delay: Delay between requests to avoid rate limits
        """
        self._drive_service = drive_service
        self._page_size = page_size
        self._rate_limit_delay = rate_limit_delay
    
    def list_all_files(self, page_size: int = 100) -> List[DriveFile]:
        """
        List all accessible Drive files
        
        Args:
            page_size: Number of files to fetch per API request
            
        Returns:
            List of DriveFile entities
            
        Raises:
            RepositoryError: If API call fails
            RateLimitError: If rate limit exceeded
        """
        files = []
        page_token = None
        actual_page_size = page_size or self._page_size
        
        try:
            while True:
                # Fetch files with permissions metadata
                response = self._drive_service.files().list(
                    pageSize=actual_page_size,
                    pageToken=page_token,
                    fields="nextPageToken, files(id, name, mimeType, owners, permissions, "
                           "shared, createdTime, modifiedTime, webViewLink, size)",
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True
                ).execute()
                
                batch_files = response.get('files', [])
                
                # Convert to domain entities
                for file_data in batch_files:
                    try:
                        drive_file = DriveFile.from_api_response(file_data)
                        files.append(drive_file)
                    except (ValueError, KeyError) as e:
                        # Skip invalid files
                        continue
                
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
                
                # Rate limiting
                time.sleep(self._rate_limit_delay)
            
            return files
        
        except HttpError as error:
            if error.resp.status == 429:
                raise RateLimitError(
                    "Google Drive API rate limit exceeded",
                    retry_after=60,
                    quota_type="drive_api"
                )
            raise RepositoryError(
                f"Failed to list files: {error}",
                repository="GoogleDriveRepository",
                operation="list_all_files"
            )
        except Exception as error:
            raise RepositoryError(
                f"Unexpected error listing files: {error}",
                repository="GoogleDriveRepository",
                operation="list_all_files"
            )
    
    def get_file_by_id(self, file_id: FileId) -> Optional[DriveFile]:
        """
        Get a specific file by ID
        
        Args:
            file_id: File identifier
            
        Returns:
            DriveFile entity or None if not found
            
        Raises:
            RepositoryError: If API call fails
        """
        try:
            file_data = self._drive_service.files().get(
                fileId=str(file_id),
                fields="id, name, mimeType, owners, permissions, shared, "
                       "createdTime, modifiedTime, webViewLink, size",
                supportsAllDrives=True
            ).execute()
            
            return DriveFile.from_api_response(file_data)
        
        except HttpError as error:
            if error.resp.status == 404:
                return None
            if error.resp.status == 429:
                raise RateLimitError(
                    "Google Drive API rate limit exceeded",
                    retry_after=60,
                    quota_type="drive_api"
                )
            raise RepositoryError(
                f"Failed to get file {file_id}: {error}",
                repository="GoogleDriveRepository",
                operation="get_file_by_id"
            )
        except Exception as error:
            raise RepositoryError(
                f"Unexpected error getting file {file_id}: {error}",
                repository="GoogleDriveRepository",
                operation="get_file_by_id"
            )
    
    def find_files_shared_with(self, email: Email) -> List[DriveFile]:
        """
        Find all files shared with a specific user
        
        Args:
            email: User email address
            
        Returns:
            List of DriveFile entities shared with the user
        """
        all_files = self.list_all_files()
        shared_files = []
        
        for file in all_files:
            if file.is_shared_with(email):
                shared_files.append(file)
        
        return shared_files
    
    def find_files_owned_by(self, email: Email) -> List[DriveFile]:
        """
        Find all files owned by a specific user
        
        Args:
            email: Owner email address
            
        Returns:
            List of DriveFile entities owned by the user
        """
        all_files = self.list_all_files()
        owned_files = []
        
        for file in all_files:
            if file.is_owned_by(email):
                owned_files.append(file)
        
        return owned_files
