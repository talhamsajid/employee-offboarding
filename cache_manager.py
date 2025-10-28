"""
Cache Manager
Handles caching of Drive file data to reduce API calls
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import hashlib


class CacheManager:
    """Manages file data cache with expiration"""

    def __init__(self, cache_dir='cache', cache_days=7):
        """
        Initialize cache manager

        Args:
            cache_dir: Directory to store cache files
            cache_days: Number of days to keep cache valid
        """
        self.cache_dir = Path(cache_dir)
        self.cache_days = cache_days
        self.cache_file = self.cache_dir / 'drive_files_cache.json'
        self.metadata_file = self.cache_dir / 'cache_metadata.json'

        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(exist_ok=True)

    def _get_cache_key(self, identifier='default'):
        """
        Generate a cache key based on identifier

        Args:
            identifier: String to identify this cache (e.g., user email)

        Returns:
            Cache key string
        """
        return hashlib.md5(identifier.encode()).hexdigest()

    def is_cache_valid(self, identifier='default'):
        """
        Check if cache exists and is still valid

        Args:
            identifier: Cache identifier

        Returns:
            Boolean indicating if cache is valid
        """
        if not self.cache_file.exists() or not self.metadata_file.exists():
            return False

        try:
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)

            cache_key = self._get_cache_key(identifier)
            if cache_key not in metadata:
                return False

            cache_info = metadata[cache_key]
            cache_date = datetime.fromisoformat(cache_info['created_at'])
            expiry_date = cache_date + timedelta(days=self.cache_days)

            is_valid = datetime.now() < expiry_date

            if is_valid:
                print(f"Cache found (created: {cache_date.strftime('%Y-%m-%d %H:%M:%S')})")
                days_left = (expiry_date - datetime.now()).days
                print(f"Cache expires in {days_left} days")

            return is_valid

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error reading cache metadata: {e}")
            return False

    def save_cache(self, files_data, identifier='default'):
        """
        Save files data to cache

        Args:
            files_data: List of file dictionaries to cache
            identifier: Cache identifier

        Returns:
            Boolean indicating success
        """
        try:
            cache_key = self._get_cache_key(identifier)

            # Save files data
            cache_data = {
                cache_key: {
                    'files': files_data,
                    'count': len(files_data)
                }
            }

            # Load existing cache if it exists
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    existing_cache = json.load(f)
                    existing_cache.update(cache_data)
                    cache_data = existing_cache

            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)

            # Save metadata
            metadata = {}
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    metadata = json.load(f)

            metadata[cache_key] = {
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(days=self.cache_days)).isoformat(),
                'file_count': len(files_data),
                'identifier': identifier,
                'cache_days': self.cache_days
            }

            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            print(f"\n✓ Cached {len(files_data)} files (valid for {self.cache_days} days)")
            cache_size = self.cache_file.stat().st_size / 1024  # KB
            print(f"  Cache size: {cache_size:.2f} KB")

            return True

        except Exception as e:
            print(f"Error saving cache: {e}")
            return False

    def load_cache(self, identifier='default'):
        """
        Load files data from cache

        Args:
            identifier: Cache identifier

        Returns:
            List of file dictionaries or None if cache invalid
        """
        if not self.is_cache_valid(identifier):
            return None

        try:
            cache_key = self._get_cache_key(identifier)

            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)

            if cache_key not in cache_data:
                return None

            files = cache_data[cache_key]['files']
            print(f"✓ Loaded {len(files)} files from cache")

            return files

        except Exception as e:
            print(f"Error loading cache: {e}")
            return None

    def clear_cache(self, identifier=None):
        """
        Clear cache files

        Args:
            identifier: Optional specific cache to clear, or all if None

        Returns:
            Boolean indicating success
        """
        try:
            if identifier is None:
                # Clear all cache
                if self.cache_file.exists():
                    self.cache_file.unlink()
                if self.metadata_file.exists():
                    self.metadata_file.unlink()
                print("✓ All cache cleared")
            else:
                # Clear specific cache
                cache_key = self._get_cache_key(identifier)

                if self.cache_file.exists():
                    with open(self.cache_file, 'r') as f:
                        cache_data = json.load(f)

                    if cache_key in cache_data:
                        del cache_data[cache_key]

                    with open(self.cache_file, 'w') as f:
                        json.dump(cache_data, f, indent=2)

                if self.metadata_file.exists():
                    with open(self.metadata_file, 'r') as f:
                        metadata = json.load(f)

                    if cache_key in metadata:
                        del metadata[cache_key]

                    with open(self.metadata_file, 'w') as f:
                        json.dump(metadata, f, indent=2)

                print(f"✓ Cache cleared for: {identifier}")

            return True

        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False

    def get_cache_info(self, identifier='default'):
        """
        Get information about cache

        Args:
            identifier: Cache identifier

        Returns:
            Dictionary with cache information or None
        """
        if not self.metadata_file.exists():
            return None

        try:
            cache_key = self._get_cache_key(identifier)

            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)

            if cache_key not in metadata:
                return None

            cache_info = metadata[cache_key]
            created_at = datetime.fromisoformat(cache_info['created_at'])
            expires_at = datetime.fromisoformat(cache_info['expires_at'])
            now = datetime.now()

            days_old = (now - created_at).days
            days_left = (expires_at - now).days

            return {
                'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'expires_at': expires_at.strftime('%Y-%m-%d %H:%M:%S'),
                'file_count': cache_info['file_count'],
                'days_old': days_old,
                'days_left': max(0, days_left),
                'is_valid': now < expires_at,
                'cache_days': cache_info['cache_days']
            }

        except Exception as e:
            print(f"Error getting cache info: {e}")
            return None

    def list_all_caches(self):
        """
        List all cached entries

        Returns:
            List of cache information dictionaries
        """
        if not self.metadata_file.exists():
            return []

        try:
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)

            caches = []
            for cache_key, info in metadata.items():
                created_at = datetime.fromisoformat(info['created_at'])
                expires_at = datetime.fromisoformat(info['expires_at'])
                now = datetime.now()

                caches.append({
                    'identifier': info.get('identifier', 'default'),
                    'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'expires_at': expires_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'file_count': info['file_count'],
                    'days_left': max(0, (expires_at - now).days),
                    'is_valid': now < expires_at,
                    'cache_key': cache_key
                })

            return caches

        except Exception as e:
            print(f"Error listing caches: {e}")
            return []

    def get_cache_size(self):
        """
        Get total cache size in bytes

        Returns:
            Cache size in bytes
        """
        total_size = 0

        if self.cache_file.exists():
            total_size += self.cache_file.stat().st_size

        if self.metadata_file.exists():
            total_size += self.metadata_file.stat().st_size

        return total_size

    def optimize_cache(self):
        """
        Remove expired cache entries

        Returns:
            Number of entries removed
        """
        if not self.metadata_file.exists():
            return 0

        try:
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)

            # Find expired entries
            now = datetime.now()
            expired_keys = []

            for cache_key, info in metadata.items():
                expires_at = datetime.fromisoformat(info['expires_at'])
                if now >= expires_at:
                    expired_keys.append(cache_key)

            if not expired_keys:
                print("No expired cache entries found")
                return 0

            # Remove expired entries from metadata
            for key in expired_keys:
                del metadata[key]

            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            # Remove expired entries from cache file
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)

                for key in expired_keys:
                    if key in cache_data:
                        del cache_data[key]

                with open(self.cache_file, 'w') as f:
                    json.dump(cache_data, f, indent=2)

            print(f"✓ Removed {len(expired_keys)} expired cache entries")
            return len(expired_keys)

        except Exception as e:
            print(f"Error optimizing cache: {e}")
            return 0
