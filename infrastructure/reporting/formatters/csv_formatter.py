"""
CSV Report Formatter
Implements IReportFormatter for CSV format
"""

import csv
import io
from typing import Dict, Any, List

from application.interfaces.services import IReportFormatter


class CSVReportFormatter(IReportFormatter):
    """
    CSV Report Formatter (Strategy Pattern)
    
    Formats report data as CSV files.
    """
    
    def __init__(self, delimiter: str = ',', include_header: bool = True):
        """
        Initialize CSV formatter
        
        Args:
            delimiter: CSV delimiter character
            include_header: Whether to include header row
        """
        self._delimiter = delimiter
        self._include_header = include_header
    
    def format(self, data: Dict[str, Any]) -> str:
        """
        Format data as CSV
        
        Args:
            data: Report data containing 'files' and 'metadata'
            
        Returns:
            CSV-formatted string
        """
        output = io.StringIO()
        
        files = data.get('files', [])
        if not files:
            return ""
        
        # Prepare rows
        rows = []
        for file_entry in files:
            if isinstance(file_entry, dict):
                # Handle dict format from old system
                file_data = file_entry.get('file', {})
                permission_data = file_entry.get('permission', {})
                
                row = {
                    'File Name': file_data.get('name', 'Unknown'),
                    'File ID': file_data.get('id', ''),
                    'Owner': self._get_owner_email(file_data),
                    'Permission Type': permission_data.get('type', ''),
                    'Permission Role': permission_data.get('role', ''),
                    'Permission Email': permission_data.get('emailAddress', ''),
                    'Shared': file_data.get('shared', False),
                    'Web Link': file_data.get('webViewLink', '')
                }
            else:
                # Handle DriveFile entity
                row = {
                    'File Name': file_entry.name,
                    'File ID': str(file_entry.file_id),
                    'Owner': ', '.join(str(owner) for owner in file_entry.owners),
                    'Permission Count': len(file_entry.permissions),
                    'Shared': file_entry.shared,
                    'Web Link': file_entry.web_view_link or ''
                }
            
            rows.append(row)
        
        if not rows:
            return ""
        
        # Write CSV
        fieldnames = list(rows[0].keys())
        writer = csv.DictWriter(
            output,
            fieldnames=fieldnames,
            delimiter=self._delimiter
        )
        
        if self._include_header:
            writer.writeheader()
        
        writer.writerows(rows)
        
        return output.getvalue()
    
    def get_extension(self) -> str:
        """Get file extension"""
        return 'csv'
    
    def supports_multi_sheet(self) -> bool:
        """CSV does not support multiple sheets"""
        return False
    
    def _get_owner_email(self, file_data: dict) -> str:
        """Extract owner email from file data"""
        owners = file_data.get('owners', [])
        if owners and len(owners) > 0:
            return owners[0].get('emailAddress', 'Unknown')
        return 'Unknown'
