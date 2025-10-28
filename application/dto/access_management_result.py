"""
Access Management Result DTO
Data transfer object for access management results
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class RevocationResult:
    """Result of a single permission revocation"""
    file_id: str
    file_name: str
    permission_id: str
    status: str  # 'success', 'failed', 'skipped'
    error: Optional[str] = None
    error_reason: Optional[str] = None


@dataclass
class AccessManagementResult:
    """
    Access Management Result DTO
    
    Encapsulates all results from an access management operation.
    """
    
    target_email: str
    operation_mode: str
    dry_run: bool
    
    # Results
    successful_revocations: List[RevocationResult] = field(default_factory=list)
    failed_revocations: List[RevocationResult] = field(default_factory=list)
    skipped_files: List[Dict[str, Any]] = field(default_factory=list)
    permission_denied: List[RevocationResult] = field(default_factory=list)
    
    # Metadata
    total_files_scanned: int = 0
    total_files_with_access: int = 0
    total_permissions_processed: int = 0
    execution_time_seconds: float = 0.0
    report_paths: List[str] = field(default_factory=list)
    cache_used: bool = False
    
    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    @property
    def success_count(self) -> int:
        """Number of successful revocations"""
        return len(self.successful_revocations)
    
    @property
    def failure_count(self) -> int:
        """Number of failed revocations"""
        return len(self.failed_revocations)
    
    @property
    def skipped_count(self) -> int:
        """Number of skipped files"""
        return len(self.skipped_files)
    
    @property
    def permission_denied_count(self) -> int:
        """Number of permission denied errors"""
        return len(self.permission_denied)
    
    @property
    def is_successful(self) -> bool:
        """Check if operation was overall successful"""
        return self.failure_count == 0 and self.success_count > 0
    
    @property
    def has_errors(self) -> bool:
        """Check if there were any errors"""
        return self.failure_count > 0 or self.permission_denied_count > 0
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary dictionary
        
        Returns:
            Dictionary with summary information
        """
        return {
            'target_email': self.target_email,
            'operation_mode': self.operation_mode,
            'dry_run': self.dry_run,
            'total_files_scanned': self.total_files_scanned,
            'total_files_with_access': self.total_files_with_access,
            'successful_revocations': self.success_count,
            'failed_revocations': self.failure_count,
            'skipped_files': self.skipped_count,
            'permission_denied': self.permission_denied_count,
            'execution_time_seconds': self.execution_time_seconds,
            'cache_used': self.cache_used,
            'reports_generated': len(self.report_paths),
            'report_paths': self.report_paths
        }
    
    def print_summary(self) -> None:
        """Print formatted summary to console"""
        print("\n" + "="*60)
        print(f"ACCESS MANAGEMENT {'DRY RUN ' if self.dry_run else ''}RESULTS")
        print("="*60)
        print(f"Target User: {self.target_email}")
        print(f"Operation: {self.operation_mode}")
        print(f"\nFiles Scanned: {self.total_files_scanned}")
        print(f"Files with Access: {self.total_files_with_access}")
        print(f"\n✓ Successful Revocations: {self.success_count}")
        print(f"✗ Failed Revocations: {self.failure_count}")
        print(f"⊘ Skipped Files: {self.skipped_count}")
        print(f"⚠ Permission Denied: {self.permission_denied_count}")
        print(f"\nExecution Time: {self.execution_time_seconds:.2f}s")
        print(f"Cache Used: {'Yes' if self.cache_used else 'No'}")
        
        if self.report_paths:
            print(f"\nReports Generated:")
            for path in self.report_paths:
                print(f"  • {path}")
        
        print("="*60 + "\n")
