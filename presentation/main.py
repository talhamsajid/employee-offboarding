#!/usr/bin/env python3
"""
Google Drive Access Manager
Main entry point - refactored to use Clean Architecture with Dependency Injection
"""

import sys
import os
import argparse
from typing import Optional
from datetime import timedelta

# Presentation layer
from presentation.cli.cli_presenter import CLIPresenter
from presentation.cli.progress_observer import CLIProgressObserver, SilentProgressObserver

# Application layer
from application.dto.access_management_request import OperationMode
from application.use_cases.manage_user_access_use_case import ManageUserAccessUseCase

# Configuration and DI
from config.configuration import ConfigurationLoader
from config.dependency_injection import ServiceContainer

# Domain exceptions
from domain.exceptions.access_manager_errors import (
    AccessManagerError,
    AuthenticationError,
    ValidationError,
    ConfigurationError
)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='Google Drive Access Manager - Enterprise-grade access control',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Interactive mode (recommended)
  python -m presentation.main

  # Batch mode with all parameters
  python -m presentation.main --email user@domain.com --mode revoke --formats csv,excel

  # Dry run to preview changes
  python -m presentation.main --email user@domain.com --mode revoke --dry-run

  # Audit only (no changes)
  python -m presentation.main --email user@domain.com --mode audit

  # Force cache refresh
  python -m presentation.main --refresh-cache

  # Disable cache
  python -m presentation.main --no-cache

  # Custom configuration file
  python -m presentation.main --config ./my-config.yaml
        '''
    )

    # Required parameters (for batch mode)
    parser.add_argument(
        '--email',
        type=str,
        help='Target user email address'
    )

    parser.add_argument(
        '--mode',
        type=str,
        choices=['revoke', 'audit'],
        help='Operation mode: revoke (remove access) or audit (report only)'
    )

    # Report options
    parser.add_argument(
        '--formats',
        type=str,
        help='Report formats (comma-separated): csv,excel,json'
    )

    # Execution options
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate changes without actual revocation'
    )

    parser.add_argument(
        '--skip-errors',
        action='store_true',
        help='Continue on errors instead of aborting'
    )

    # Cache options
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable caching (always scan fresh)'
    )

    parser.add_argument(
        '--refresh-cache',
        action='store_true',
        help='Force cache refresh even if valid'
    )

    parser.add_argument(
        '--cache-days',
        type=int,
        help='Cache validity in days (default: 7)'
    )

    # Configuration
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file (YAML)'
    )

    # UI options
    parser.add_argument(
        '--no-progress',
        action='store_true',
        help='Disable progress bars'
    )

    parser.add_argument(
        '--batch',
        action='store_true',
        help='Batch mode (no interactive prompts, requires --email and --mode)'
    )

    return parser.parse_args()


def setup_container(args: argparse.Namespace) -> ServiceContainer:
    """
    Setup dependency injection container
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Configured ServiceContainer
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    # Load configuration
    config_loader = ConfigurationLoader()
    
    if args.config and os.path.exists(args.config):
        config = config_loader.load_from_file(args.config)
    else:
        config = config_loader.load_default()
    
    # Override with CLI args if provided
    if args.cache_days is not None:
        config.cache.default_ttl_days = args.cache_days
    
    # Create container and store config
    container = ServiceContainer()
    container.set_configuration(config)
    
    return container


def create_use_case(container: ServiceContainer) -> ManageUserAccessUseCase:
    """
    Create ManageUserAccessUseCase with dependencies
    
    Args:
        container: Service container with configuration
        
    Returns:
        Configured use case instance
    """
    config = container.get_configuration()
    
    # Create infrastructure services
    from infrastructure.google_api.authentication_service import AuthenticationFactory
    from infrastructure.google_api.google_drive_repository import GoogleDriveRepository
    from infrastructure.google_api.google_permission_repository import GooglePermissionRepository
    from infrastructure.cache.file_cache_repository import FileCacheRepository
    from infrastructure.reporting.report_generator import ReportGenerator
    from infrastructure.logging.audit_logger import AuditLogger
    
    # Create domain services
    from domain.services.permission_service import PermissionService
    from domain.services.file_analysis_service import FileAnalysisService
    
    # Setup authentication
    auth_service = AuthenticationFactory.create_oauth2_authenticator(
        credentials_path=config.google_api.credentials_path,
        token_path=config.google_api.token_path
    )
    auth_service.authenticate()
    drive_service = auth_service.get_drive_service()
    
    # Create repositories
    drive_repo = GoogleDriveRepository(drive_service)
    permission_repo = GooglePermissionRepository(drive_service)
    cache_repo = FileCacheRepository(cache_dir=config.cache.cache_dir)
    
    # Create other services
    report_service = ReportGenerator(output_dir=config.reporting.output_dir)
    audit_logger = AuditLogger(log_dir=config.logging.log_dir)
    
    # Create domain services
    permission_service = PermissionService()
    file_analysis_service = FileAnalysisService()
    
    # Create use case
    use_case = ManageUserAccessUseCase(
        drive_repository=drive_repo,
        permission_repository=permission_repo,
        cache_repository=cache_repo,
        report_service=report_service,
        audit_logger=audit_logger
    )
    
    return use_case


def run_interactive_mode(
    container: ServiceContainer,
    presenter: CLIPresenter,
    use_case: ManageUserAccessUseCase
) -> int:
    """
    Run in interactive mode with user prompts
    
    Args:
        container: Dependency injection container
        presenter: CLI presenter instance
        use_case: Main use case instance
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    presenter.display_banner()
    
    # Build request interactively
    request = presenter.build_request_interactive()
    
    if request is None:
        # User cancelled
        return 0
    
    try:
        # Execute operation
        result = use_case.execute(request)
        
        # Display results
        presenter.display_result(result)
        
        # Return success if no critical errors
        return 0 if result.failure_count == 0 else 1
        
    except AuthenticationError as e:
        presenter.display_error(
            "Authentication failed. Please check your credentials.",
            e
        )
        return 1
    except ValidationError as e:
        presenter.display_error("Invalid input", e)
        return 1
    except AccessManagerError as e:
        presenter.display_error("Operation failed", e)
        return 1
    except Exception as e:
        presenter.display_error("Unexpected error occurred", e)
        return 1


def run_batch_mode(
    args: argparse.Namespace,
    container: ServiceContainer,
    presenter: CLIPresenter,
    use_case: ManageUserAccessUseCase
) -> int:
    """
    Run in batch mode without prompts
    
    Args:
        args: Command-line arguments
        container: Dependency injection container
        presenter: CLI presenter instance
        use_case: Main use case instance
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Validate required parameters
    if not args.email or not args.mode:
        presenter.display_error(
            "Batch mode requires --email and --mode parameters"
        )
        return 1
    
    try:
        # Build request from arguments
        from application.dto.access_management_request import AccessManagementRequestBuilder
        
        builder = AccessManagementRequestBuilder(args.email)
        
        # Set operation mode
        if args.mode == 'revoke':
            builder.with_operation(OperationMode.REVOKE_ALL)
        else:
            builder.with_operation(OperationMode.AUDIT_ONLY)
        
        # Set formats
        if args.formats:
            formats = [f.strip() for f in args.formats.split(',')]
            builder.with_formats(formats)
        
        # Set options
        if args.dry_run:
            builder.as_dry_run()
        
        if args.skip_errors:
            builder.skip_errors()
        
        if args.no_cache:
            builder.without_cache()
        elif args.refresh_cache:
            builder.force_refresh_cache()
        
        request = builder.build()
        
        # Execute
        result = use_case.execute(request)
        
        # Display results
        presenter.display_result(result)
        
        return 0 if result.failure_count == 0 else 1
        
    except ValidationError as e:
        presenter.display_error("Invalid parameters", e)
        return 1
    except AuthenticationError as e:
        presenter.display_error("Authentication failed", e)
        return 1
    except AccessManagerError as e:
        presenter.display_error("Operation failed", e)
        return 1
    except Exception as e:
        presenter.display_error("Unexpected error", e)
        return 1


def main() -> int:
    """
    Main entry point
    
    Returns:
        Exit code
    """
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Setup dependency injection container
        container = setup_container(args)
        
        # Resolve dependencies
        presenter = CLIPresenter()
        
        # Setup progress observer
        if args.no_progress or args.batch:
            progress_observer = SilentProgressObserver()
        else:
            progress_observer = CLIProgressObserver(use_progress_bar=True)
        
        # Resolve use case with observer
        use_case = container.resolve(ManageUserAccessUseCase)
        use_case.set_progress_observer(progress_observer)
        
        # Choose mode
        if args.batch:
            return run_batch_mode(args, container, presenter, use_case)
        else:
            return run_interactive_mode(container, presenter, use_case)
            
    except ConfigurationError as e:
        print(f"\n❌ Configuration Error: {e}", file=sys.stderr)
        print("Please check your configuration file and credentials.\n", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user\n")
        return 0
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
