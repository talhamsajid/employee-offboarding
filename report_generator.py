"""
Report Generator
Generates reports in various formats (JSON, CSV, Excel)
"""

import json
import csv
import pandas as pd
from datetime import datetime
import os


class ReportGenerator:
    """Generates reports of Drive access and revocation activities"""

    def __init__(self, output_dir='reports'):
        """
        Initialize the report generator

        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = output_dir

        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate_shared_files_report(self, shared_files, user_email, format='csv'):
        """
        Generate a report of files shared with a user

        Args:
            shared_files: List of dicts with 'file' and 'permission' keys
            user_email: Email address of the user
            format: Report format ('json', 'csv', 'excel')

        Returns:
            str: Path to the generated report file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"shared_files_{user_email.replace('@', '_at_')}_{timestamp}"

        # Prepare data
        report_data = []
        for item in shared_files:
            file_data = item['file']
            permission = item['permission']

            owners = file_data.get('owners', [])
            owner_emails = ', '.join([o.get('emailAddress', 'Unknown') for o in owners])

            report_data.append({
                'File ID': file_data['id'],
                'File Name': file_data.get('name', 'Unknown'),
                'File Type': file_data.get('mimeType', 'Unknown'),
                'Owner(s)': owner_emails,
                'Permission Role': permission.get('role', 'Unknown'),
                'Permission Type': permission.get('type', 'Unknown'),
                'Web Link': file_data.get('webViewLink', 'N/A'),
                'Created Time': file_data.get('createdTime', 'Unknown'),
                'Modified Time': file_data.get('modifiedTime', 'Unknown'),
                'File Size': file_data.get('size', 'N/A')
            })

        # Generate report in specified format
        if format.lower() == 'json':
            return self._generate_json_report(report_data, base_filename)
        elif format.lower() == 'csv':
            return self._generate_csv_report(report_data, base_filename)
        elif format.lower() in ['excel', 'xlsx']:
            return self._generate_excel_report(report_data, base_filename)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def generate_revocation_report(self, revocation_results, user_email, format='csv'):
        """
        Generate a report of revocation activities

        Args:
            revocation_results: Dict with 'success', 'failed', 'skipped' keys
            user_email: Email address of the user
            format: Report format ('json', 'csv', 'excel')

        Returns:
            str: Path to the generated report file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"revocation_report_{user_email.replace('@', '_at_')}_{timestamp}"

        # Prepare data
        report_data = []

        # Add successful revocations
        for item in revocation_results.get('success', []):
            report_data.append({
                'File ID': item['file_id'],
                'File Name': item['file_name'],
                'Status': 'Revoked Successfully',
                'Error': None
            })

        # Add failed revocations
        for item in revocation_results.get('failed', []):
            report_data.append({
                'File ID': item['file_id'],
                'File Name': item['file_name'],
                'Status': 'Failed to Revoke',
                'Error': item.get('error', 'Unknown error')
            })

        # Add skipped items
        for item in revocation_results.get('skipped', []):
            report_data.append({
                'File ID': item['file_id'],
                'File Name': item['file_name'],
                'Status': 'Skipped',
                'Error': item.get('reason', 'Unknown reason')
            })

        # Generate report in specified format
        if format.lower() == 'json':
            return self._generate_json_report(report_data, base_filename)
        elif format.lower() == 'csv':
            return self._generate_csv_report(report_data, base_filename)
        elif format.lower() in ['excel', 'xlsx']:
            return self._generate_excel_report(report_data, base_filename)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def generate_combined_report(self, shared_files, revocation_results, user_email, format='excel'):
        """
        Generate a combined report with both shared files and revocation results

        Args:
            shared_files: List of dicts with 'file' and 'permission' keys
            revocation_results: Dict with 'success', 'failed', 'skipped' keys
            user_email: Email address of the user
            format: Report format ('json', 'csv', 'excel')

        Returns:
            str: Path to the generated report file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"combined_report_{user_email.replace('@', '_at_')}_{timestamp}"

        # Prepare shared files data
        shared_data = []
        for item in shared_files:
            file_data = item['file']
            permission = item['permission']

            owners = file_data.get('owners', [])
            owner_emails = ', '.join([o.get('emailAddress', 'Unknown') for o in owners])

            shared_data.append({
                'File ID': file_data['id'],
                'File Name': file_data.get('name', 'Unknown'),
                'File Type': file_data.get('mimeType', 'Unknown'),
                'Owner(s)': owner_emails,
                'Permission Role': permission.get('role', 'Unknown'),
                'Web Link': file_data.get('webViewLink', 'N/A')
            })

        # Prepare revocation data
        revocation_data = []
        for item in revocation_results.get('success', []):
            revocation_data.append({
                'File ID': item['file_id'],
                'File Name': item['file_name'],
                'Status': 'Revoked Successfully'
            })

        for item in revocation_results.get('failed', []):
            revocation_data.append({
                'File ID': item['file_id'],
                'File Name': item['file_name'],
                'Status': f"Failed: {item.get('error', 'Unknown')}"
            })

        for item in revocation_results.get('skipped', []):
            revocation_data.append({
                'File ID': item['file_id'],
                'File Name': item['file_name'],
                'Status': f"Skipped: {item.get('reason', 'Unknown')}"
            })

        # Generate Excel report with multiple sheets
        if format.lower() in ['excel', 'xlsx']:
            filepath = os.path.join(self.output_dir, f"{base_filename}.xlsx")

            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = {
                    'Metric': [
                        'User Email',
                        'Total Files Shared',
                        'Successfully Revoked',
                        'Failed to Revoke',
                        'Skipped',
                        'Report Generated'
                    ],
                    'Value': [
                        user_email,
                        len(shared_files),
                        len(revocation_results.get('success', [])),
                        len(revocation_results.get('failed', [])),
                        len(revocation_results.get('skipped', [])),
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

                # Shared files sheet
                if shared_data:
                    pd.DataFrame(shared_data).to_excel(writer, sheet_name='Shared Files', index=False)

                # Revocation results sheet
                if revocation_data:
                    pd.DataFrame(revocation_data).to_excel(writer, sheet_name='Revocation Results', index=False)

            print(f"Combined report generated: {filepath}")
            return filepath
        else:
            # For non-Excel formats, generate separate reports
            shared_file = self.generate_shared_files_report(shared_files, user_email, format)
            revocation_file = self.generate_revocation_report(revocation_results, user_email, format)
            return [shared_file, revocation_file]

    def _generate_json_report(self, data, base_filename):
        """Generate JSON report"""
        filepath = os.path.join(self.output_dir, f"{base_filename}.json")

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"JSON report generated: {filepath}")
        return filepath

    def _generate_csv_report(self, data, base_filename):
        """Generate CSV report"""
        filepath = os.path.join(self.output_dir, f"{base_filename}.csv")

        if data:
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding='utf-8')
        else:
            # Create empty CSV with headers
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("No data available\n")

        print(f"CSV report generated: {filepath}")
        return filepath

    def _generate_excel_report(self, data, base_filename):
        """Generate Excel report"""
        filepath = os.path.join(self.output_dir, f"{base_filename}.xlsx")

        if data:
            df = pd.DataFrame(data)
            df.to_excel(filepath, index=False, engine='openpyxl')
        else:
            # Create empty Excel file
            df = pd.DataFrame(['No data available'])
            df.to_excel(filepath, index=False, engine='openpyxl')

        print(f"Excel report generated: {filepath}")
        return filepath
