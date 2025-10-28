"""
Service Interfaces
Abstract contracts for infrastructure services
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from enum import Enum

from domain.entities.drive_file import DriveFile


class IAuthenticationService(ABC):
    """
    Authentication Service Interface
    
    Abstracts authentication mechanism.
    Allows switching between OAuth2, Service Account, etc.
    """
    
    @abstractmethod
    def authenticate(self) -> Any:
        """
        Authenticate and return credentials
        
        Returns:
            Credentials object
            
        Raises:
            AuthenticationError: If authentication fails
        """
        pass
    
    @abstractmethod
    def get_drive_service(self) -> Any:
        """
        Get authenticated Google Drive service
        
        Returns:
            Google Drive API service object
        """
        pass
    
    @abstractmethod
    def get_sheets_service(self) -> Any:
        """
        Get authenticated Google Sheets service
        
        Returns:
            Google Sheets API service object
        """
        pass
    
    @abstractmethod
    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated
        
        Returns:
            True if authenticated
        """
        pass


class ReportFormat(Enum):
    """Report output formats"""
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    HTML = "html"


class IReportFormatter(ABC):
    """
    Report Formatter Interface (Strategy Pattern)
    
    Abstracts report generation format.
    Each format implements this interface.
    """
    
    @abstractmethod
    def format(self, data: Dict[str, Any]) -> str:
        """
        Format data into report content
        
        Args:
            data: Report data
            
        Returns:
            Formatted report content
        """
        pass
    
    @abstractmethod
    def get_extension(self) -> str:
        """
        Get file extension for this format
        
        Returns:
            File extension (e.g., 'csv', 'xlsx')
        """
        pass
    
    @abstractmethod
    def supports_multi_sheet(self) -> bool:
        """
        Check if format supports multiple sheets
        
        Returns:
            True if multi-sheet supported
        """
        pass


class IReportService(ABC):
    """
    Report Service Interface
    
    Abstracts report generation.
    """
    
    @abstractmethod
    def generate_report(
        self,
        files: List[DriveFile],
        output_path: str,
        report_format: ReportFormat,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a report
        
        Args:
            files: List of files to include in report
            output_path: Path to save report
            report_format: Desired output format
            metadata: Additional metadata to include
            
        Returns:
            Path to generated report file
        """
        pass
    
    @abstractmethod
    def set_formatter(self, formatter: IReportFormatter) -> None:
        """
        Set the report formatter (Strategy Pattern)
        
        Args:
            formatter: Report formatter implementation
        """
        pass


class IProgressObserver(ABC):
    """
    Progress Observer Interface (Observer Pattern)
    
    Allows decoupling progress reporting from business logic.
    """
    
    @abstractmethod
    def on_scan_started(self, total_files: int) -> None:
        """
        Called when file scan starts
        
        Args:
            total_files: Expected number of files
        """
        pass
    
    @abstractmethod
    def on_file_scanned(
        self,
        file_name: str,
        current: int,
        total: int
    ) -> None:
        """
        Called when a file is scanned
        
        Args:
            file_name: Name of scanned file
            current: Current file number
            total: Total files
        """
        pass
    
    @abstractmethod
    def on_scan_completed(self, total_files: int) -> None:
        """
        Called when scan completes
        
        Args:
            total_files: Total files scanned
        """
        pass
    
    @abstractmethod
    def on_revocation_started(self, total_permissions: int) -> None:
        """
        Called when permission revocation starts
        
        Args:
            total_permissions: Number of permissions to revoke
        """
        pass
    
    @abstractmethod
    def on_permission_revoked(
        self,
        file_name: str,
        current: int,
        total: int,
        success: bool
    ) -> None:
        """
        Called when a permission is revoked
        
        Args:
            file_name: Name of file
            current: Current permission number
            total: Total permissions
            success: Whether revocation succeeded
        """
        pass
    
    @abstractmethod
    def on_revocation_completed(
        self,
        total: int,
        successful: int,
        failed: int
    ) -> None:
        """
        Called when revocation completes
        
        Args:
            total: Total permissions processed
            successful: Number of successful revocations
            failed: Number of failed revocations
        """
        pass
