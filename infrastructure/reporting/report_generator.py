"""
Report Generator with Strategy Pattern
Generates reports in multiple formats
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from application.interfaces.services import IReportService, IReportFormatter, ReportFormat
from domain.entities.drive_file import DriveFile
from infrastructure.reporting.formatters.csv_formatter import CSVReportFormatter
from infrastructure.reporting.formatters.json_formatter import JSONReportFormatter

try:
    from infrastructure.reporting.formatters.excel_formatter import ExcelReportFormatter
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False


class ReportGenerator(IReportService):
    """
    Report Generator (Strategy Pattern)
    
    Generates reports using different formatters.
    Supports CSV, JSON, and Excel (if pandas available).
    """
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize report generator
        
        Args:
            output_dir: Directory to save reports
        """
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._formatter: Optional[IReportFormatter] = None
        
        # Initialize formatters
        self._formatters = {
            ReportFormat.CSV: CSVReportFormatter(),
            ReportFormat.JSON: JSONReportFormatter()
        }
        
        if EXCEL_AVAILABLE:
            self._formatters[ReportFormat.EXCEL] = ExcelReportFormatter()  # type: ignore
    
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
            output_path: Path to save report (relative to output_dir)
            report_format: Desired output format
            metadata: Additional metadata to include
            
        Returns:
            Path to generated report file
        """
        # Get appropriate formatter
        if report_format not in self._formatters:
            raise ValueError(f"Unsupported report format: {report_format}")
        
        formatter = self._formatters[report_format]
        
        # Prepare data
        report_data = {
            'files': files,
            'metadata': metadata or self._generate_default_metadata(files)
        }
        
        # Format data
        formatted_content = formatter.format(report_data)
        
        # Determine output path
        if not output_path.endswith(f".{formatter.get_extension()}"):
            output_path = f"{output_path}.{formatter.get_extension()}"
        
        full_path = self._output_dir / output_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        if report_format == ReportFormat.EXCEL:
            # Excel returns base64-encoded content
            import base64
            content_bytes = base64.b64decode(formatted_content)
            with open(full_path, 'wb') as f:
                f.write(content_bytes)
        else:
            # Text formats (CSV, JSON)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
        
        return str(full_path)
    
    def set_formatter(self, formatter: IReportFormatter) -> None:
        """
        Set custom report formatter (Strategy Pattern)
        
        Args:
            formatter: Report formatter implementation
        """
        self._formatter = formatter
    
    def generate_multi_format_reports(
        self,
        files: List[DriveFile],
        base_name: str,
        formats: List[ReportFormat],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Generate reports in multiple formats
        
        Args:
            files: List of files to include
            base_name: Base name for report files
            formats: List of desired formats
            metadata: Additional metadata
            
        Returns:
            List of paths to generated reports
        """
        report_paths = []
        
        for fmt in formats:
            if fmt in self._formatters:
                try:
                    path = self.generate_report(files, base_name, fmt, metadata)
                    report_paths.append(path)
                except Exception as e:
                    # Log error but continue with other formats
                    print(f"Warning: Failed to generate {fmt.value} report: {e}")
        
        return report_paths
    
    def _generate_default_metadata(self, files: List[DriveFile]) -> Dict[str, Any]:
        """
        Generate default metadata for report
        
        Args:
            files: List of files in report
            
        Returns:
            Dictionary of metadata
        """
        shared_count = sum(1 for f in files if f.shared)
        total_permissions = sum(len(f.permissions) for f in files)
        
        return {
            'generated_at': datetime.now().isoformat(),
            'total_files': len(files),
            'shared_files': shared_count,
            'total_permissions': total_permissions,
            'tool': 'Google Drive Access Manager',
            'version': '2.0.0'
        }
