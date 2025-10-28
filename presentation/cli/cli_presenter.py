"""
CLI Presenter
Handles user interaction and command-line interface presentation logic
"""

import sys
from typing import List, Optional

from domain.value_objects.email import Email
from application.dto.access_management_request import (
    AccessManagementRequest,
    AccessManagementRequestBuilder,
    OperationMode
)
from application.dto.access_management_result import AccessManagementResult
from presentation.cli.input_validator import InputValidator
from application.interfaces.services import ReportFormat


class CLIPresenter:
    """
    CLI Presenter (Presentation Layer)
    
    Handles user interaction, input collection, and output presentation.
    Separates UI logic from business logic.
    """
    
    def __init__(self, validator: Optional[InputValidator] = None):
        """
        Initialize CLI presenter
        
        Args:
            validator: Input validator instance (defaults to new InputValidator)
        """
        self._validator = validator or InputValidator()
    
    def display_banner(self) -> None:
        """Display application banner"""
        print("\n" + "=" * 70)
        print("  Google Drive Access Manager")
        print("  Manage user access and permissions across Google Drive")
        print("=" * 70 + "\n")
    
    def display_error(self, message: str, error: Optional[Exception] = None) -> None:
        """
        Display error message
        
        Args:
            message: Error message to display
            error: Optional exception object
        """
        print(f"\n❌ Error: {message}", file=sys.stderr)
        if error:
            print(f"   Details: {str(error)}", file=sys.stderr)
        print()
    
    def display_warning(self, message: str) -> None:
        """Display warning message"""
        print(f"\n⚠️  Warning: {message}\n")
    
    def display_info(self, message: str) -> None:
        """Display informational message"""
        print(f"\nℹ️  {message}\n")
    
    def display_success(self, message: str) -> None:
        """Display success message"""
        print(f"\n✅ {message}\n")
    
    def get_user_email(self, prompt: str = "Enter user email address") -> str:
        """
        Get and validate user email from input
        
        Args:
            prompt: Prompt message for the user
            
        Returns:
            Validated email string
        """
        while True:
            email_str = input(f"{prompt}: ").strip()
            
            try:
                return self._validator.validate_email(email_str)
            except ValueError as e:
                self.display_error(str(e))
    
    def get_operation_mode(self) -> OperationMode:
        """
        Get operation mode from user
        
        Returns:
            Selected OperationMode
        """
        print("\nSelect operation mode:")
        print("  1. Revoke all permissions (remove user access)")
        print("  2. Audit only (generate report without changes)")
        
        while True:
            choice = input("\nEnter choice (1 or 2): ").strip()
            
            if choice == "1":
                return OperationMode.REVOKE_ALL
            elif choice == "2":
                return OperationMode.AUDIT_ONLY
            else:
                self.display_error("Invalid choice. Please enter 1 or 2.")
    
    def get_report_formats(self) -> List[ReportFormat]:
        """
        Get desired report formats from user
        
        Returns:
            List of selected ReportFormat enums
        """
        print("\nSelect report formats (comma-separated):")
        print("  csv   - CSV format (compatible with Excel)")
        print("  excel - Excel format with formatting")
        print("  json  - JSON format for programmatic use")
        
        while True:
            formats_str = input("\nEnter formats [csv,excel]: ").strip()
            
            # Use default if empty
            if not formats_str:
                formats_str = "csv,excel"
            
            try:
                formats_list = [f.strip() for f in formats_str.split(',')]
                format_strs = self._validator.validate_report_formats(formats_list)
                
                # Convert strings to enums
                formats = []
                for fmt in format_strs:
                    if fmt == 'csv':
                        formats.append(ReportFormat.CSV)
                    elif fmt == 'excel':
                        formats.append(ReportFormat.EXCEL)
                    elif fmt == 'json':
                        formats.append(ReportFormat.JSON)
                
                return formats
            except ValueError as e:
                self.display_error(str(e))
    
    def confirm_operation(
        self,
        email: str,
        operation: OperationMode,
        dry_run: bool = False
    ) -> bool:
        """
        Confirm operation with user
        
        Args:
            email: Target user email
            operation: Operation to perform
            dry_run: Whether this is a dry run
            
        Returns:
            True if user confirms, False otherwise
        """
        print("\n" + "-" * 70)
        print("Operation Summary:")
        print(f"  User: {email}")
        print(f"  Mode: {operation.value}")
        
        if dry_run:
            print(f"  Type: DRY RUN (no actual changes)")
        else:
            print(f"  Type: LIVE EXECUTION (will make changes)")
        
        print("-" * 70)
        
        if operation == OperationMode.REVOKE_ALL and not dry_run:
            self.display_warning(
                "This will permanently remove the user's access to all shared files!"
            )
        
        confirmation = input("\nProceed with this operation? (yes/no): ").strip().lower()
        
        try:
            return self._validator.validate_yes_no(confirmation)
        except ValueError:
            return False
    
    def get_cache_preference(self) -> tuple[bool, bool]:
        """
        Get cache preferences from user
        
        Returns:
            Tuple of (use_cache, force_refresh)
        """
        print("\nCache Options:")
        print("  Use cached data if available (faster, may be outdated)")
        print("  or force fresh scan (slower, always current)")
        
        use_cache_str = input("\nUse cache if available? (yes/no) [yes]: ").strip().lower()
        
        if not use_cache_str:
            use_cache_str = "yes"
        
        try:
            use_cache = self._validator.validate_yes_no(use_cache_str)
        except ValueError:
            use_cache = True
        
        force_refresh = False
        if use_cache:
            refresh_str = input("Force cache refresh? (yes/no) [no]: ").strip().lower()
            if not refresh_str:
                refresh_str = "no"
            
            try:
                force_refresh = self._validator.validate_yes_no(refresh_str)
            except ValueError:
                force_refresh = False
        
        return use_cache, force_refresh
    
    def display_result(self, result: AccessManagementResult) -> None:
        """
        Display operation result to user
        
        Args:
            result: AccessManagementResult to display
        """
        print("\n" + "=" * 70)
        print("OPERATION RESULT")
        print("=" * 70 + "\n")
        
        # Display summary
        print("Summary:")
        print(f"  Total files found: {result.total_files_scanned}")
        print(f"  Files with user access: {result.total_files_with_access}")
        
        if result.operation_mode == OperationMode.REVOKE_ALL.value:
            print(f"\nRevocation Results:")
            print(f"  Successful: {result.success_count}")
            print(f"  Failed: {result.failure_count}")
            print(f"  Skipped: {result.skipped_count}")
            
            if result.dry_run:
                print(f"\n  ⚠️  DRY RUN - No actual changes were made")
        
        # Display reports
        if result.report_paths:
            print(f"\nReports Generated:")
            for report_path in result.report_paths:
                print(f"  📄 {report_path}")
        
        # Display errors
        if result.has_errors:
            error_count = result.failure_count + result.permission_denied_count
            print(f"\nErrors Encountered ({error_count}):")
            # Show failed revocations
            for failed in result.failed_revocations[:3]:
                print(f"  ❌ {failed.file_name}: {failed.error}")
            
            if error_count > 3:
                print(f"  ... and {error_count - 3} more errors")
        
        print("\n" + "=" * 70 + "\n")
        
        # Display status message
        if result.success_count > 0 and result.failure_count == 0:
            self.display_success("Operation completed successfully!")
        elif result.failure_count > 0:
            self.display_warning(
                f"Operation completed with {result.failure_count} failures. "
                "Check the reports for details."
            )
        else:
            self.display_info("Operation completed.")
    
    def build_request_interactive(self) -> Optional[AccessManagementRequest]:
        """
        Build AccessManagementRequest through interactive prompts
        
        Returns:
            AccessManagementRequest if successful, None if user cancels
        """
        try:
            # Get user email
            email = self.get_user_email()
            
            # Get operation mode
            operation = self.get_operation_mode()
            
            # Get report formats
            formats = self.get_report_formats()
            
            # Get cache preferences
            use_cache, force_refresh = self.get_cache_preference()
            
            # Determine if dry run
            dry_run = False
            if operation == OperationMode.REVOKE_ALL:
                dry_run_str = input("\nPerform dry run first? (yes/no) [yes]: ").strip().lower()
                if not dry_run_str:
                    dry_run_str = "yes"
                
                try:
                    dry_run = self._validator.validate_yes_no(dry_run_str)
                except ValueError:
                    dry_run = True
            
            # Build request
            builder = AccessManagementRequestBuilder(email)
            builder.with_operation(operation)
            
            # Add formats
            format_names = [fmt.value for fmt in formats]
            builder.with_formats(format_names)
            
            if dry_run:
                builder.as_dry_run()
            
            if use_cache:
                # Cache is enabled by default
                if force_refresh:
                    builder.force_refresh_cache()
            else:
                builder.without_cache()
            
            request = builder.build()
            
            # Confirm operation
            if not self.confirm_operation(email, operation, dry_run):
                self.display_info("Operation cancelled by user.")
                return None
            
            return request
            
        except KeyboardInterrupt:
            self.display_info("\nOperation cancelled by user.")
            return None
        except Exception as e:
            self.display_error("Failed to build request", e)
            return None
