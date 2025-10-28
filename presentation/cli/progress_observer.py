"""
CLI Progress Observer
Implements IProgressObserver for console output
"""

from application.interfaces.services import IProgressObserver

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False


class CLIProgressObserver(IProgressObserver):
    """
    CLI Progress Observer (Observer Pattern)
    
    Displays progress information in the console using tqdm progress bars.
    """
    
    def __init__(self, use_progress_bar: bool = True):
        """
        Initialize CLI progress observer
        
        Args:
            use_progress_bar: Whether to use tqdm progress bars (if available)
        """
        self._use_progress_bar = use_progress_bar and TQDM_AVAILABLE
        self._current_bar = None
    
    def on_scan_started(self, total_files: int) -> None:
        """Called when file scan starts"""
        print("\n🔍 Scanning Google Drive files...")
        
        if self._use_progress_bar and total_files > 0:
            self._current_bar = tqdm(total=total_files, desc="Scanning", unit="file")  # type: ignore
    
    def on_file_scanned(
        self,
        file_name: str,
        current: int,
        total: int
    ) -> None:
        """Called when a file is scanned"""
        if self._current_bar:
            self._current_bar.update(1)
        elif current % 100 == 0 or current == total:
            print(f"  Scanned {current}/{total} files...", end='\r')
    
    def on_scan_completed(self, total_files: int) -> None:
        """Called when scan completes"""
        if self._current_bar:
            self._current_bar.close()
            self._current_bar = None
        
        print(f"\n✓ Scan complete: {total_files} files found")
    
    def on_revocation_started(self, total_permissions: int) -> None:
        """Called when permission revocation starts"""
        print(f"\n🔒 Revoking permissions ({total_permissions} files to process)...")
        
        if self._use_progress_bar and total_permissions > 0:
            self._current_bar = tqdm(total=total_permissions, desc="Revoking", unit="permission")  # type: ignore
    
    def on_permission_revoked(
        self,
        file_name: str,
        current: int,
        total: int,
        success: bool
    ) -> None:
        """Called when a permission is revoked"""
        if self._current_bar:
            self._current_bar.update(1)
            status = "✓" if success else "✗"
            self._current_bar.set_postfix_str(f"{status} {file_name[:30]}")
        else:
            status = "✓" if success else "✗"
            print(f"  {status} [{current}/{total}] {file_name[:50]}", end='\r')
    
    def on_revocation_completed(
        self,
        total: int,
        successful: int,
        failed: int
    ) -> None:
        """Called when revocation completes"""
        if self._current_bar:
            self._current_bar.close()
            self._current_bar = None
        
        print(f"\n✓ Revocation complete: {successful} successful, {failed} failed")


class SilentProgressObserver(IProgressObserver):
    """
    Silent Progress Observer
    
    No-op implementation for when progress output is not desired.
    """
    
    def on_scan_started(self, total_files: int) -> None:
        pass
    
    def on_file_scanned(self, file_name: str, current: int, total: int) -> None:
        pass
    
    def on_scan_completed(self, total_files: int) -> None:
        pass
    
    def on_revocation_started(self, total_permissions: int) -> None:
        pass
    
    def on_permission_revoked(
        self,
        file_name: str,
        current: int,
        total: int,
        success: bool
    ) -> None:
        pass
    
    def on_revocation_completed(self, total: int, successful: int, failed: int) -> None:
        pass
