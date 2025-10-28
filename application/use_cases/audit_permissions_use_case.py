"""
Audit Permissions Use Case
Read-only use case for auditing user permissions without making changes
"""

from typing import List, Optional
from datetime import datetime

from domain.entities.drive_file import DriveFile
from domain.value_objects.email import Email
from domain.services.file_analysis_service import FileAnalysisService
from application.dto.access_management_request import AccessManagementRequest
from application.dto.access_management_result import AccessManagementResult, RevocationResult
from application.interfaces.repositories import IDriveRepository, ICacheRepository
from application.interfaces.services import IReportService, IProgressObserver
from infrastructure.logging.audit_logger import AuditLogger


class AuditPermissionsUseCase:
    """
    Audit Permissions Use Case
    
    Read-only use case for generating permission audit reports
    without making any changes to Drive files.
    
    Use Cases:
    - Periodic access reviews
    - Compliance audits
    - Security assessments
    - Pre-offboarding analysis
    """
    
    def __init__(
        self,
        drive_repository: IDriveRepository,
        cache_repository: ICacheRepository,
        report_service: IReportService,
        audit_logger: AuditLogger,
        file_analysis_service: Optional[FileAnalysisService] = None
    ):
        """
        Initialize audit use case
        
        Args:
            drive_repository: Drive file repository
            cache_repository: Cache repository
            report_service: Report generation service
            audit_logger: Audit logger
            file_analysis_service: File analysis domain service
        """
        self._drive_repo = drive_repository
        self._cache_repo = cache_repository
        self._report_service = report_service
        self._audit_logger = audit_logger
        self._file_analysis_service = file_analysis_service or FileAnalysisService()
        self._progress_observer: Optional[IProgressObserver] = None
    
    def set_progress_observer(self, observer: IProgressObserver) -> None:
        """Set progress observer"""
        self._progress_observer = observer
    
    def execute(self, request: AccessManagementRequest) -> AccessManagementResult:
        """
        Execute audit operation
        
        Args:
            request: Access management request (must be AUDIT_ONLY mode)
            
        Returns:
            AccessManagementResult with audit findings
            
        Raises:
            ValueError: If request is not in AUDIT_ONLY mode
        """
        from application.dto.access_management_request import OperationMode
        
        # Validate request is audit-only
        if request.operation_mode != OperationMode.AUDIT_ONLY:
            raise ValueError(
                f"AuditPermissionsUseCase requires AUDIT_ONLY mode, "
                f"got {request.operation_mode}"
            )
        
        started_at = datetime.now()
        
        # Create result object
        result = AccessManagementResult(
            target_email=request.target_email,
            operation_mode=OperationMode.AUDIT_ONLY.value,
            dry_run=False,
            started_at=started_at
        )
        
        try:
            # 1. Get all Drive files
            all_files = self._get_files(
                request.cache_enabled,
                request.force_cache_refresh
            )
            result.total_files_scanned = len(all_files)
            
            # 2. Find files shared with target user
            target_email = Email(request.target_email)
            shared_files = self._file_analysis_service.find_files_shared_with(
                all_files,
                target_email
            )
            result.total_files_with_access = len(shared_files)
            
            # 3. Analyze permissions (read-only)
            self._analyze_permissions(shared_files, target_email, result)
            
            # 4. Generate reports
            if request.report_formats:
                result.report_paths = self._generate_reports(
                    shared_files,
                    target_email,
                    request.report_formats
                )
            
            # 5. Log completion
            result.completed_at = datetime.now()
            result.execution_time_seconds = (
                result.completed_at - started_at
            ).total_seconds()
            
            return result
            
        except Exception as e:
            # Log error
            self._audit_logger.log_error(
                error_type="AuditPermissionsError",
                error_message=str(e),
                context={
                    'operation': 'audit_permissions',
                    'target_user': request.target_email
                }
            )
            raise
    
    def _get_files(
        self,
        cache_enabled: bool,
        force_refresh: bool
    ) -> List[DriveFile]:
        """
        Get all Drive files (with caching)
        
        Args:
            cache_enabled: Whether to use cache
            force_refresh: Force cache refresh
            
        Returns:
            List of DriveFile entities
        """
        cache_key = "all_drive_files"
        
        # Try cache first
        if cache_enabled and not force_refresh:
            cached_files = self._cache_repo.load(cache_key)
            if cached_files:
                if self._progress_observer:
                    self._progress_observer.on_scan_started(len(cached_files))
                    self._progress_observer.on_scan_completed(len(cached_files))
                return cached_files
        
        # Scan Drive
        if self._progress_observer:
            self._progress_observer.on_scan_started(0)
        
        all_files = self._drive_repo.list_all_files()
        
        if self._progress_observer:
            for i, file in enumerate(all_files, 1):
                self._progress_observer.on_file_scanned(
                    file.name,
                    i,
                    len(all_files)
                )
            self._progress_observer.on_scan_completed(len(all_files))
        
        # Cache results
        if cache_enabled:
            self._cache_repo.save(cache_key, all_files)
        
        return all_files
    
    def _analyze_permissions(
        self,
        files: List[DriveFile],
        target_email: Email,
        result: AccessManagementResult
    ) -> None:
        """
        Analyze permissions for audit report
        
        Args:
            files: Files to analyze
            target_email: Target user email
            result: Result object to populate
        """
        for file in files:
            # Get user's permission on this file (singular)
            user_permission = file.get_permission_for_user(target_email)
            
            if not user_permission:
                continue  # User doesn't have permission on this file
            
            # Classify permission
            if user_permission.is_owner_permission():
                # User owns this file - cannot revoke
                result.skipped_files.append({
                    'file_id': str(file.file_id),
                    'file_name': file.name,
                    'reason': 'User is owner',
                    'permission_role': user_permission.role.value
                })
            elif user_permission.can_be_revoked():
                # Permission could be revoked (for informational purposes)
                revocation = RevocationResult(
                    file_id=str(file.file_id),
                    file_name=file.name,
                    permission_id=str(user_permission.permission_id),
                    status='revocable',
                    error=None
                )
                result.successful_revocations.append(revocation)
            else:
                # Permission exists but cannot be revoked
                result.skipped_files.append({
                    'file_id': str(file.file_id),
                    'file_name': file.name,
                    'reason': 'Permission not revocable',
                    'permission_role': user_permission.role.value
                })
    
    def _generate_reports(
        self,
        files: List[DriveFile],
        target_email: Email,
        formats: List[str]
    ) -> List[str]:
        """
        Generate audit reports
        
        Args:
            files: Files to include in report
            target_email: Target user email
            formats: Report formats to generate
            
        Returns:
            List of generated report file paths
        """
        from application.interfaces.services import ReportFormat
        
        # Map format strings to enums
        format_mapping = {
            'csv': ReportFormat.CSV,
            'excel': ReportFormat.EXCEL,
            'json': ReportFormat.JSON
        }
        
        report_formats = [
            format_mapping.get(fmt.lower(), ReportFormat.CSV)
            for fmt in formats
        ]
        
        # Generate base name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_email = target_email.value.replace('@', '_at_').replace('.', '_')
        base_name = f"audit_report_{safe_email}_{timestamp}"
        
        # Metadata
        metadata = {
            'report_type': 'Permission Audit',
            'target_user': target_email.value,
            'generated_at': datetime.now().isoformat(),
            'total_files': len(files),
            'read_only': True
        }
        
        # Generate reports using interface method
        from infrastructure.reporting.report_generator import ReportGenerator
        
        # Note: Using concrete implementation directly since interface doesn't have this method
        if isinstance(self._report_service, ReportGenerator):
            report_paths = self._report_service.generate_multi_format_reports(
                files=files,
                base_name=base_name,
                formats=report_formats,
                metadata=metadata
            )
        else:
            # Fallback: generate reports one by one
            report_paths = []
            for fmt in report_formats:
                try:
                    path = self._report_service.generate_report(
                        files=files,
                        output_path=f"{base_name}.{fmt.value}",
                        report_format=fmt,
                        metadata=metadata
                    )
                    report_paths.append(path)
                except Exception as e:
                    # Log warning but continue
                    pass
        
        return report_paths
    
    def audit_user_access(
        self,
        user_email: str,
        report_formats: Optional[List[str]] = None
    ) -> AccessManagementResult:
        """
        Convenience method for auditing a user's access
        
        Args:
            user_email: User email to audit
            report_formats: Report formats (default: ['csv', 'excel'])
            
        Returns:
            AccessManagementResult with audit findings
        """
        from application.dto.access_management_request import (
            AccessManagementRequestBuilder,
            OperationMode
        )
        
        # Build request
        builder = AccessManagementRequestBuilder(user_email)
        builder.with_operation(OperationMode.AUDIT_ONLY)
        
        if report_formats:
            builder.with_formats(report_formats)
        
        request = builder.build()
        
        # Execute audit
        return self.execute(request)
