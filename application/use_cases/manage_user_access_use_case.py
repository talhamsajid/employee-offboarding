"""
Manage User Access Use Case
Main orchestration logic for access management workflows
"""

from datetime import datetime
from typing import List, Optional

from application.interfaces.repositories import IDriveRepository, IPermissionRepository, ICacheRepository
from application.interfaces.services import IReportService, IProgressObserver, ReportFormat
from application.dto.access_management_request import AccessManagementRequest, OperationMode
from application.dto.access_management_result import AccessManagementResult, RevocationResult
from domain.value_objects.email import Email
from domain.services.permission_service import PermissionService
from domain.services.file_analysis_service import FileAnalysisService
from infrastructure.logging.audit_logger import AuditLogger


class ManageUserAccessUseCase:
    """
    Manage User Access Use Case
    
    Orchestrates the complete workflow for managing user access to Drive files.
    Implements Clean Architecture use case pattern.
    """
    
    def __init__(
        self,
        drive_repository: IDriveRepository,
        permission_repository: IPermissionRepository,
        report_service: IReportService,
        cache_repository: Optional[ICacheRepository] = None,
        audit_logger: Optional[AuditLogger] = None,
        progress_observer: Optional[IProgressObserver] = None
    ):
        """
        Initialize use case with dependencies
        
        Args:
            drive_repository: Repository for Drive file operations
            permission_repository: Repository for permission operations
            report_service: Service for generating reports
            cache_repository: Optional cache repository
            audit_logger: Optional audit logger
            progress_observer: Optional progress observer
        """
        self._drive_repo = drive_repository
        self._permission_repo = permission_repository
        self._report_service = report_service
        self._cache_repo = cache_repository
        self._audit_logger = audit_logger
        self._progress_observer = progress_observer
        
        # Domain services
        self._permission_service = PermissionService()
        self._file_analysis_service = FileAnalysisService()
    
    def execute(self, request: AccessManagementRequest) -> AccessManagementResult:
        """
        Execute access management workflow
        
        Args:
            request: Access management request
            
        Returns:
            Access management result
        """
        start_time = datetime.now()
        
        # Validate request
        request.validate()
        
        # Convert email to value object
        target_email = Email(request.target_email)
        
        # Log workflow start
        if self._audit_logger:
            self._audit_logger.log_workflow_started(
                workflow_type=request.operation_mode.value,
                target_user=str(target_email),
                performed_by="system",  # Would come from auth context
                dry_run=request.dry_run
            )
        
        # Initialize result
        result = AccessManagementResult(
            target_email=str(target_email),
            operation_mode=request.operation_mode.value,
            dry_run=request.dry_run,
            started_at=start_time
        )
        
        try:
            # Step 1: Scan Drive files
            if self._progress_observer:
                self._progress_observer.on_scan_started(0)
            
            all_files = self._get_files(request.cache_enabled, request.force_cache_refresh)
            result.total_files_scanned = len(all_files)
            
            if self._progress_observer:
                self._progress_observer.on_scan_completed(len(all_files))
            
            # Step 2: Find files shared with target user
            shared_files = self._file_analysis_service.find_files_shared_with(all_files, target_email)
            result.total_files_with_access = len(shared_files)
            
            # Step 3: Execute operation based on mode
            if request.operation_mode == OperationMode.REVOKE_ALL:
                self._execute_revocation(
                    shared_files,
                    target_email,
                    request.dry_run,
                    request.use_admin_access,
                    result
                )
            elif request.operation_mode == OperationMode.AUDIT_ONLY:
                # Just analyze, don't revoke
                pass
            
            # Step 4: Generate reports
            if shared_files and request.report_formats:
                result.report_paths = self._generate_reports(
                    shared_files,
                    target_email,
                    request.report_formats,
                    result
                )
            
            # Calculate execution time
            end_time = datetime.now()
            result.completed_at = end_time
            result.execution_time_seconds = (end_time - start_time).total_seconds()
            
            # Log completion
            if self._audit_logger:
                self._audit_logger.log_workflow_completed(
                    workflow_type=request.operation_mode.value,
                    target_user=str(target_email),
                    files_processed=result.total_files_with_access,
                    permissions_revoked=result.success_count,
                    errors=result.failure_count,
                    duration_seconds=result.execution_time_seconds
                )
            
            return result
        
        except Exception as error:
            # Log error
            if self._audit_logger:
                self._audit_logger.log_error(
                    error_type=type(error).__name__,
                    error_message=str(error),
                    context={'target_email': str(target_email)}
                )
            raise
    
    def _get_files(self, use_cache: bool, force_refresh: bool):
        """Get all Drive files, using cache if available"""
        cache_key = "all_drive_files"
        
        # Try cache first
        if use_cache and self._cache_repo and not force_refresh:
            cached_files = self._cache_repo.load(cache_key)
            if cached_files:
                if self._audit_logger:
                    self._audit_logger.log_cache_operation(
                        operation="load",
                        cache_key=cache_key,
                        success=True,
                        hit=True
                    )
                return cached_files
        
        # Fetch from repository
        files = self._drive_repo.list_all_files()
        
        # Save to cache
        if use_cache and self._cache_repo:
            from datetime import timedelta
            self._cache_repo.save(cache_key, files, ttl=timedelta(days=7))
            if self._audit_logger:
                self._audit_logger.log_cache_operation(
                    operation="save",
                    cache_key=cache_key,
                    success=True
                )
        
        return files
    
    def _execute_revocation(
        self,
        shared_files,
        target_email: Email,
        dry_run: bool,
        use_admin_access: bool,
        result: AccessManagementResult
    ):
        """Execute permission revocation"""
        if self._progress_observer:
            self._progress_observer.on_revocation_started(len(shared_files))
        
        for idx, file in enumerate(shared_files, 1):
            # Skip if user is owner
            if file.is_owned_by(target_email):
                result.skipped_files.append({
                    'file_id': str(file.file_id),
                    'file_name': file.name,
                    'reason': 'User is owner - cannot revoke ownership'
                })
                continue
            
            # Get revocable permissions
            revocable_perms = file.get_revocable_permissions_for_user(target_email)
            
            for perm in revocable_perms:
                if dry_run:
                    # Simulate revocation
                    revocation_result = RevocationResult(
                        file_id=str(file.file_id),
                        file_name=file.name,
                        permission_id=str(perm.permission_id),
                        status='would_revoke'
                    )
                    result.successful_revocations.append(revocation_result)
                else:
                    # Actually revoke
                    try:
                        success = self._permission_repo.revoke_permission(
                            file.file_id,
                            perm.permission_id,
                            use_admin_access
                        )
                        
                        if success:
                            revocation_result = RevocationResult(
                                file_id=str(file.file_id),
                                file_name=file.name,
                                permission_id=str(perm.permission_id),
                                status='success'
                            )
                            result.successful_revocations.append(revocation_result)
                            
                            if self._audit_logger:
                                self._audit_logger.log_permission_revocation(
                                    file_id=str(file.file_id),
                                    file_name=file.name,
                                    permission_id=str(perm.permission_id),
                                    user_email=str(target_email),
                                    performed_by="system",
                                    success=True
                                )
                    except Exception as error:
                        revocation_result = RevocationResult(
                            file_id=str(file.file_id),
                            file_name=file.name,
                            permission_id=str(perm.permission_id),
                            status='failed',
                            error=str(error)
                        )
                        result.failed_revocations.append(revocation_result)
                        
                        if self._audit_logger:
                            self._audit_logger.log_permission_revocation(
                                file_id=str(file.file_id),
                                file_name=file.name,
                                permission_id=str(perm.permission_id),
                                user_email=str(target_email),
                                performed_by="system",
                                success=False,
                                error=str(error)
                            )
            
            if self._progress_observer:
                self._progress_observer.on_permission_revoked(
                    file.name,
                    idx,
                    len(shared_files),
                    len(revocable_perms) > 0
                )
        
        if self._progress_observer:
            self._progress_observer.on_revocation_completed(
                len(shared_files),
                result.success_count,
                result.failure_count
            )
    
    def _generate_reports(
        self,
        files,
        target_email: Email,
        formats: List[str],
        result: AccessManagementResult
    ) -> List[str]:
        """Generate reports in requested formats"""
        report_paths = []
        
        # Base filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"access_report_{target_email.local_part}_{timestamp}"
        
        # Metadata for report
        metadata = {
            'target_email': str(target_email),
            'generated_at': datetime.now().isoformat(),
            'total_files': len(files),
            'dry_run': result.dry_run
        }
        
        # Convert format strings to enum
        format_enums = []
        for fmt_str in formats:
            try:
                if fmt_str.lower() == 'csv':
                    format_enums.append(ReportFormat.CSV)
                elif fmt_str.lower() in ['excel', 'xlsx']:
                    format_enums.append(ReportFormat.EXCEL)
                elif fmt_str.lower() == 'json':
                    format_enums.append(ReportFormat.JSON)
            except:
                continue
        
        # Generate reports
        for fmt in format_enums:
            try:
                path = self._report_service.generate_report(
                    files,
                    base_name,
                    fmt,
                    metadata
                )
                report_paths.append(path)
                
                if self._audit_logger:
                    self._audit_logger.log_report_generation(
                        report_format=fmt.value,
                        file_path=path,
                        files_included=len(files),
                        success=True
                    )
            except Exception as error:
                if self._audit_logger:
                    self._audit_logger.log_error(
                        error_type="ReportGenerationError",
                        error_message=str(error),
                        context={'format': fmt.value}
                    )
        
        return report_paths
