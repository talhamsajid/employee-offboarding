"""
Audit Logger
Comprehensive audit trail for all operations
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from logging.handlers import RotatingFileHandler


class AuditLogger:
    """
    Audit Logger
    
    Maintains comprehensive audit trail of all access management operations.
    Uses rotating file handler to manage log size.
    """
    
    def __init__(
        self,
        log_dir: str = "logs",
        audit_file: str = "audit.log",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        """
        Initialize audit logger
        
        Args:
            log_dir: Directory for log files
            audit_file: Audit log filename
            max_bytes: Maximum size per log file
            backup_count: Number of backup files to keep
        """
        self._log_dir = Path(log_dir)
        self._log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup audit logger
        self._logger = logging.getLogger('audit')
        self._logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        self._logger.handlers.clear()
        
        # File handler with rotation
        audit_path = self._log_dir / audit_file
        file_handler = RotatingFileHandler(
            audit_path,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        
        # JSON formatter for structured logs
        file_handler.setFormatter(logging.Formatter('%(message)s'))
        self._logger.addHandler(file_handler)
    
    def log_authentication(self, user_email: str, auth_method: str, success: bool) -> None:
        """
        Log authentication attempt
        
        Args:
            user_email: Email of authenticating user
            auth_method: Authentication method used
            success: Whether authentication succeeded
        """
        self._log_event('authentication', {
            'user_email': user_email,
            'auth_method': auth_method,
            'success': success
        })
    
    def log_permission_revocation(
        self,
        file_id: str,
        file_name: str,
        permission_id: str,
        user_email: str,
        performed_by: str,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """
        Log permission revocation
        
        Args:
            file_id: File identifier
            file_name: File name
            permission_id: Permission identifier
            user_email: Email of user whose permission was revoked
            performed_by: Email of user performing the action
            success: Whether revocation succeeded
            error: Error message if failed
        """
        self._log_event('permission_revocation', {
            'file_id': file_id,
            'file_name': file_name,
            'permission_id': permission_id,
            'target_user': user_email,
            'performed_by': performed_by,
            'success': success,
            'error': error
        })
    
    def log_file_access(
        self,
        file_id: str,
        file_name: str,
        user_email: str,
        operation: str
    ) -> None:
        """
        Log file access
        
        Args:
            file_id: File identifier
            file_name: File name
            user_email: User accessing the file
            operation: Operation performed (read, write, delete)
        """
        self._log_event('file_access', {
            'file_id': file_id,
            'file_name': file_name,
            'user_email': user_email,
            'operation': operation
        })
    
    def log_workflow_started(
        self,
        workflow_type: str,
        target_user: str,
        performed_by: str,
        dry_run: bool = False
    ) -> None:
        """
        Log workflow start
        
        Args:
            workflow_type: Type of workflow (offboarding, audit, etc.)
            target_user: Target user email
            performed_by: User performing the workflow
            dry_run: Whether this is a dry run
        """
        self._log_event('workflow_started', {
            'workflow_type': workflow_type,
            'target_user': target_user,
            'performed_by': performed_by,
            'dry_run': dry_run
        })
    
    def log_workflow_completed(
        self,
        workflow_type: str,
        target_user: str,
        files_processed: int,
        permissions_revoked: int,
        errors: int,
        duration_seconds: float
    ) -> None:
        """
        Log workflow completion
        
        Args:
            workflow_type: Type of workflow
            target_user: Target user email
            files_processed: Number of files processed
            permissions_revoked: Number of permissions revoked
            errors: Number of errors encountered
            duration_seconds: Workflow duration
        """
        self._log_event('workflow_completed', {
            'workflow_type': workflow_type,
            'target_user': target_user,
            'files_processed': files_processed,
            'permissions_revoked': permissions_revoked,
            'errors': errors,
            'duration_seconds': duration_seconds
        })
    
    def log_cache_operation(
        self,
        operation: str,
        cache_key: str,
        success: bool,
        hit: Optional[bool] = None
    ) -> None:
        """
        Log cache operation
        
        Args:
            operation: Operation type (save, load, invalidate)
            cache_key: Cache key
            success: Whether operation succeeded
            hit: Whether cache hit occurred (for load operations)
        """
        self._log_event('cache_operation', {
            'operation': operation,
            'cache_key': cache_key,
            'success': success,
            'hit': hit
        })
    
    def log_report_generation(
        self,
        report_format: str,
        file_path: str,
        files_included: int,
        success: bool
    ) -> None:
        """
        Log report generation
        
        Args:
            report_format: Report format (csv, excel, json)
            file_path: Path to generated report
            files_included: Number of files in report
            success: Whether generation succeeded
        """
        self._log_event('report_generation', {
            'report_format': report_format,
            'file_path': file_path,
            'files_included': files_included,
            'success': success
        })
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log error
        
        Args:
            error_type: Type of error
            error_message: Error message
            context: Additional context information
        """
        self._log_event('error', {
            'error_type': error_type,
            'error_message': error_message,
            'context': context or {}
        })
    
    def _log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Log an event with structured data
        
        Args:
            event_type: Type of event
            data: Event data
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            **data
        }
        
        self._logger.info(json.dumps(log_entry))
