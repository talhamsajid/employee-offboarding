"""
Google Drive Resource Scanner
Scans all accessible Google Drive resources
"""

from googleapiclient.errors import HttpError
from tqdm import tqdm
import time
from cache_manager import CacheManager


class DriveScanner:
    """Scans Google Drive for all accessible resources"""

    def __init__(self, drive_service, use_cache=True, cache_days=7):
        """
        Initialize the scanner

        Args:
            drive_service: Authenticated Google Drive service
            use_cache: Whether to use caching (default: True)
            cache_days: Number of days to keep cache valid (default: 7)
        """
        self.drive_service = drive_service
        self.all_files = []
        self.use_cache = use_cache
        self.cache_manager = CacheManager(cache_days=cache_days) if use_cache else None

    def get_all_files(self, page_size=100, show_progress=True, force_refresh=False):
        """
        Retrieve all files from Google Drive (with caching)

        Args:
            page_size: Number of files to fetch per request
            show_progress: Whether to show progress bar
            force_refresh: Force refresh cache even if valid

        Returns:
            List of file metadata dictionaries
        """
        # Try to load from cache first
        if self.use_cache and not force_refresh:
            cached_files = self.cache_manager.load_cache()
            if cached_files is not None:
                self.all_files = cached_files
                return cached_files

        # Cache miss or refresh requested - scan Drive
        if force_refresh:
            print("Force refreshing cache - scanning Google Drive...")
        else:
            print("Scanning Google Drive for all files...")

        files = []
        page_token = None

        try:
            # First, get total count for progress bar
            if show_progress:
                response = self.drive_service.files().list(
                    pageSize=1,
                    fields="nextPageToken"
                ).execute()

            while True:
                # Fetch files with permissions metadata
                response = self.drive_service.files().list(
                    pageSize=page_size,
                    pageToken=page_token,
                    fields="nextPageToken, files(id, name, mimeType, owners, permissions, "
                           "shared, createdTime, modifiedTime, webViewLink, size)",
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True
                ).execute()

                batch_files = response.get('files', [])
                files.extend(batch_files)

                if show_progress:
                    print(f"Scanned {len(files)} files...", end='\r')

                page_token = response.get('nextPageToken')
                if not page_token:
                    break

                # Avoid rate limiting
                time.sleep(0.1)

            if show_progress:
                print(f"\nTotal files found: {len(files)}")

            self.all_files = files

            # Save to cache
            if self.use_cache:
                self.cache_manager.save_cache(files)

            return files

        except HttpError as error:
            print(f"An error occurred while scanning Drive: {error}")
            raise

    def get_file_permissions(self, file_id):
        """
        Get detailed permissions for a specific file

        Args:
            file_id: Google Drive file ID

        Returns:
            List of permission dictionaries
        """
        try:
            permissions = self.drive_service.permissions().list(
                fileId=file_id,
                fields="permissions(id, emailAddress, role, type, displayName)",
                supportsAllDrives=True
            ).execute()

            return permissions.get('permissions', [])

        except HttpError as error:
            print(f"An error occurred getting permissions for file {file_id}: {error}")
            return []

    def get_files_shared_with_user(self, user_email, files=None):
        """
        Filter files that are shared with a specific user

        Args:
            user_email: Email address of the user
            files: List of files to filter (uses self.all_files if None)

        Returns:
            List of files shared with the user
        """
        if files is None:
            files = self.all_files

        print(f"\nAnalyzing permissions for {user_email}...")
        shared_files = []

        # Check if we have permissions in the data (from cache or fresh scan)
        has_permissions = files and len(files) > 0 and 'permissions' in files[0]

        if has_permissions:
            # Fast path: permissions already in data (from cache)
            # Just filter in memory - no API calls, no delays needed
            print("Using cached permission data (instant)...")

            for file in files:
                permissions = file.get('permissions', [])

                # Check if user has access
                for permission in permissions:
                    if permission.get('emailAddress', '').lower() == user_email.lower():
                        shared_files.append({
                            'file': file,
                            'permission': permission
                        })
                        break

            print(f"Found {len(shared_files)} files shared with {user_email}")
        else:
            # Slow path: need to fetch permissions for each file
            print("Fetching permissions from Drive API...")

            for file in tqdm(files, desc="Checking permissions"):
                # Fetch permissions
                permissions = self.get_file_permissions(file['id'])

                # Check if user has access
                for permission in permissions:
                    if permission.get('emailAddress', '').lower() == user_email.lower():
                        shared_files.append({
                            'file': file,
                            'permission': permission
                        })
                        break

                # Small delay to avoid rate limiting (only when making API calls)
                time.sleep(0.05)

            print(f"Found {len(shared_files)} files shared with {user_email}")

        return shared_files

    def get_file_details(self, file_id):
        """
        Get detailed information about a specific file

        Args:
            file_id: Google Drive file ID

        Returns:
            File metadata dictionary
        """
        try:
            file = self.drive_service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, owners, permissions, shared, "
                       "createdTime, modifiedTime, webViewLink, size",
                supportsAllDrives=True
            ).execute()

            return file

        except HttpError as error:
            print(f"An error occurred getting file details for {file_id}: {error}")
            return None

    def get_cache_info(self):
        """
        Get cache information

        Returns:
            Dictionary with cache information or None
        """
        if not self.use_cache:
            return None

        return self.cache_manager.get_cache_info()

    def clear_cache(self):
        """
        Clear the cache

        Returns:
            Boolean indicating success
        """
        if not self.use_cache:
            return False

        return self.cache_manager.clear_cache()

    def get_cached_file_count(self):
        """
        Get number of files in cache

        Returns:
            Number of cached files or 0
        """
        if not self.use_cache:
            return 0

        cache_info = self.cache_manager.get_cache_info()
        if cache_info:
            return cache_info['file_count']

        return 0
