"""
Excel Report Formatter
Implements IReportFormatter for Excel format
"""

from typing import Dict, Any, List, TYPE_CHECKING
import io

if TYPE_CHECKING:
    import pandas as pd

try:
    import pandas as pd  # type: ignore
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None  # type: ignore

from application.interfaces.services import IReportFormatter


class ExcelReportFormatter(IReportFormatter):
    """
    Excel Report Formatter (Strategy Pattern)
    
    Formats report data as Excel files using pandas.
    Supports multiple sheets for different data views.
    """
    
    def __init__(self, engine: str = 'openpyxl', include_metadata: bool = True):
        """
        Initialize Excel formatter
        
        Args:
            engine: Excel writer engine ('openpyxl' or 'xlsxwriter')
            include_metadata: Whether to include metadata sheet
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required for Excel formatting. Install with: pip install pandas openpyxl")
        
        self._engine = engine
        self._include_metadata = include_metadata
    
    def format(self, data: Dict[str, Any]) -> str:
        """
        Format data as Excel (returns base64-encoded bytes)
        
        Args:
            data: Report data containing 'files' and 'metadata'
            
        Returns:
            Excel file content as base64-encoded string
        """
        if not PANDAS_AVAILABLE or pd is None:
            raise ImportError("pandas not available")
        
        files = data.get('files', [])
        metadata = data.get('metadata', {})
        
        # Create DataFrames
        dfs = self._create_dataframes(files, metadata)
        
        # Write to Excel buffer
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine=self._engine) as writer:  # type: ignore
            # Write main files sheet
            if 'files' in dfs and not dfs['files'].empty:  # type: ignore
                dfs['files'].to_excel(writer, sheet_name='Files', index=False)  # type: ignore
            
            # Write permissions detail sheet if available
            if 'permissions' in dfs and not dfs['permissions'].empty:  # type: ignore
                dfs['permissions'].to_excel(writer, sheet_name='Permissions', index=False)  # type: ignore
            
            # Write metadata sheet
            if self._include_metadata and 'metadata' in dfs and not dfs['metadata'].empty:  # type: ignore
                dfs['metadata'].to_excel(writer, sheet_name='Metadata', index=False)  # type: ignore
        
        # Return base64 encoded for string representation
        import base64
        return base64.b64encode(output.getvalue()).decode('utf-8')
    
    def get_extension(self) -> str:
        """Get file extension"""
        return 'xlsx'
    
    def supports_multi_sheet(self) -> bool:
        """Excel supports multiple sheets"""
        return True
    
    def _create_dataframes(self, files: List, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create pandas DataFrames from file data
        
        Args:
            files: List of file entries
            metadata: Report metadata
            
        Returns:
            Dictionary of DataFrames
        """
        dfs = {}
        
        if not files:
            return dfs
        
        # Files sheet
        file_rows = []
        permission_rows = []
        
        for file_entry in files:
            if isinstance(file_entry, dict):
                # Handle dict format from old system
                file_data = file_entry.get('file', {})
                permission_data = file_entry.get('permission', {})
                
                file_row = {
                    'File Name': file_data.get('name', 'Unknown'),
                    'File ID': file_data.get('id', ''),
                    'Owner': self._get_owner_email(file_data),
                    'MIME Type': file_data.get('mimeType', ''),
                    'Shared': file_data.get('shared', False),
                    'Created': file_data.get('createdTime', ''),
                    'Modified': file_data.get('modifiedTime', ''),
                    'Web Link': file_data.get('webViewLink', '')
                }
                file_rows.append(file_row)
                
                # Permission detail
                if permission_data:
                    perm_row = {
                        'File Name': file_data.get('name', 'Unknown'),
                        'File ID': file_data.get('id', ''),
                        'Permission Email': permission_data.get('emailAddress', ''),
                        'Permission Type': permission_data.get('type', ''),
                        'Permission Role': permission_data.get('role', ''),
                        'Display Name': permission_data.get('displayName', '')
                    }
                    permission_rows.append(perm_row)
            else:
                # Handle DriveFile entity
                file_row = {
                    'File Name': file_entry.name,
                    'File ID': str(file_entry.file_id),
                    'Owner': ', '.join(str(owner) for owner in file_entry.owners),
                    'MIME Type': file_entry.mime_type,
                    'Shared': file_entry.shared,
                    'Permission Count': len(file_entry.permissions),
                    'Created': str(file_entry.created_time) if file_entry.created_time else '',
                    'Modified': str(file_entry.modified_time) if file_entry.modified_time else '',
                    'Web Link': file_entry.web_view_link or ''
                }
                file_rows.append(file_row)
                
                # Permission details
                for perm in file_entry.permissions:
                    perm_row = {
                        'File Name': file_entry.name,
                        'File ID': str(file_entry.file_id),
                        'Permission Email': str(perm.email) if perm.email else '',
                        'Permission Type': str(perm.permission_type),
                        'Permission Role': str(perm.role),
                        'Display Name': perm.display_name or ''
                    }
                    permission_rows.append(perm_row)
        
        if file_rows:
            dfs['files'] = pd.DataFrame(file_rows)  # type: ignore
        
        if permission_rows:
            dfs['permissions'] = pd.DataFrame(permission_rows)  # type: ignore
        
        # Metadata sheet
        if metadata:
            metadata_rows = [{'Key': k, 'Value': str(v)} for k, v in metadata.items()]
            dfs['metadata'] = pd.DataFrame(metadata_rows)  # type: ignore
        
        return dfs
    
    def _get_owner_email(self, file_data: dict) -> str:
        """Extract owner email from file data"""
        owners = file_data.get('owners', [])
        if owners and len(owners) > 0:
            return owners[0].get('emailAddress', 'Unknown')
        return 'Unknown'
    
    def write_to_file(self, data: Dict[str, Any], file_path: str) -> None:
        """
        Write Excel file directly to disk
        
        Args:
            data: Report data
            file_path: Path to write Excel file
        """
        if not PANDAS_AVAILABLE or pd is None:
            raise ImportError("pandas not available")
        
        files = data.get('files', [])
        metadata = data.get('metadata', {})
        
        dfs = self._create_dataframes(files, metadata)
        
        with pd.ExcelWriter(file_path, engine=self._engine) as writer:  # type: ignore
            if 'files' in dfs and not dfs['files'].empty:  # type: ignore
                dfs['files'].to_excel(writer, sheet_name='Files', index=False)  # type: ignore
            
            if 'permissions' in dfs and not dfs['permissions'].empty:  # type: ignore
                dfs['permissions'].to_excel(writer, sheet_name='Permissions', index=False)  # type: ignore
            
            if self._include_metadata and 'metadata' in dfs and not dfs['metadata'].empty:  # type: ignore
                dfs['metadata'].to_excel(writer, sheet_name='Metadata', index=False)  # type: ignore
