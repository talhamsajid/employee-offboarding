#!/usr/bin/env python3
"""
Employee Offboarding Tool for Google Drive
Revokes access and generates reports for offboarded employees
"""

import sys
import os
import json
import getpass
import argparse
from colorama import init, Fore, Style

from auth import GoogleAPIAuthenticator, setup_credentials_from_input
from drive_scanner import DriveScanner
from permission_manager import PermissionManager
from report_generator import ReportGenerator
from cache_manager import CacheManager

# Initialize colorama for cross-platform colored output
init(autoreset=True)


def print_header():
    """Print application header"""
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.CYAN}  Employee Offboarding Tool - Google Drive Access Revocation")
    print(f"{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}\n")


def print_section(title):
    """Print section header"""
    print(f"\n{Fore.YELLOW}{'─' * 70}")
    print(f"{Fore.YELLOW}  {title}")
    print(f"{Fore.YELLOW}{'─' * 70}{Style.RESET_ALL}\n")


def get_user_input(prompt, required=True, default=None):
    """
    Get user input with optional default value

    Args:
        prompt: Prompt message
        required: Whether input is required
        default: Default value if no input provided

    Returns:
        User input string
    """
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "

    while True:
        value = input(prompt).strip()

        if value:
            return value
        elif default:
            return default
        elif not required:
            return None
        else:
            print(f"{Fore.RED}This field is required. Please try again.{Style.RESET_ALL}")


def get_yes_no_input(prompt, default='n'):
    """
    Get yes/no input from user

    Args:
        prompt: Prompt message
        default: Default value ('y' or 'n')

    Returns:
        Boolean
    """
    default_text = 'Y/n' if default.lower() == 'y' else 'y/N'
    response = input(f"{prompt} [{default_text}]: ").strip().lower()

    if not response:
        response = default

    return response in ['y', 'yes']


def setup_google_credentials():
    """
    Setup Google API credentials interactively

    Returns:
        Boolean indicating success
    """
    print_section("Google API Credentials Setup")

    if os.path.exists('credentials.json'):
        print(f"{Fore.GREEN}✓ Found existing credentials.json{Style.RESET_ALL}")
        use_existing = get_yes_no_input("Use existing credentials?", default='y')

        if use_existing:
            return True

    print("\nYou need to provide OAuth2 credentials from Google Cloud Console.")
    print("Visit: https://console.cloud.google.com/apis/credentials")
    print("\nOptions:")
    print("1. Paste credentials JSON directly")
    print("2. Provide path to credentials JSON file")
    print("3. Exit (manually place credentials.json in this directory)")

    choice = get_user_input("\nChoose option (1-3)", default='3')

    if choice == '1':
        print("\nPaste your credentials JSON (press Enter twice when done):")
        lines = []
        while True:
            line = input()
            if line:
                lines.append(line)
            else:
                if lines:
                    break

        try:
            credentials_json = json.loads('\n'.join(lines))
            setup_credentials_from_input(credentials_json)
            print(f"{Fore.GREEN}✓ Credentials saved successfully{Style.RESET_ALL}")
            return True
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}✗ Invalid JSON format: {e}{Style.RESET_ALL}")
            return False

    elif choice == '2':
        creds_path = get_user_input("Enter path to credentials JSON file")

        if not os.path.exists(creds_path):
            print(f"{Fore.RED}✗ File not found: {creds_path}{Style.RESET_ALL}")
            return False

        try:
            with open(creds_path, 'r') as f:
                credentials_json = json.load(f)
            setup_credentials_from_input(credentials_json)
            print(f"{Fore.GREEN}✓ Credentials saved successfully{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}✗ Error reading credentials: {e}{Style.RESET_ALL}")
            return False

    else:
        print("\nPlease place your credentials.json file in this directory and run again.")
        return False


def parse_arguments():
    """
    Parse command-line arguments

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Employee Offboarding Tool - Google Drive Access Revocation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Normal run with cache
  python main.py

  # Force refresh cache
  python main.py --refresh-cache

  # Run without cache
  python main.py --no-cache

  # Show cache information
  python main.py --cache-info

  # Clear cache
  python main.py --clear-cache

  # Set cache duration (default: 7 days)
  python main.py --cache-days 14
        '''
    )

    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable caching (always scan fresh from Drive)'
    )

    parser.add_argument(
        '--refresh-cache',
        action='store_true',
        help='Force refresh cache even if valid'
    )

    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='Clear the cache and exit'
    )

    parser.add_argument(
        '--cache-info',
        action='store_true',
        help='Show cache information and exit'
    )

    parser.add_argument(
        '--cache-days',
        type=int,
        default=7,
        help='Number of days to keep cache valid (default: 7)'
    )

    # Admin and permission flags
    parser.add_argument(
        '--service-account',
        type=str,
        help='Path to service account JSON file (for domain-wide delegation)'
    )

    parser.add_argument(
        '--admin-email',
        type=str,
        help='Admin email to impersonate (requires service account with domain-wide delegation)'
    )

    parser.add_argument(
        '--skip-errors',
        action='store_true',
        help='Continue on permission errors (useful when not all files are accessible)'
    )

    parser.add_argument(
        '--use-admin-access',
        action='store_true',
        help='Try to use domain admin access for permission operations'
    )

    return parser.parse_args()


def handle_cache_operations(args):
    """
    Handle cache-only operations

    Args:
        args: Parsed command-line arguments

    Returns:
        Boolean indicating if app should continue (False if cache operation handled)
    """
    cache_manager = CacheManager(cache_days=args.cache_days)

    # Show cache info
    if args.cache_info:
        print_header()
        print_section("Cache Information")

        cache_info = cache_manager.get_cache_info()

        if cache_info:
            print(f"{Fore.CYAN}Cache Status:{Style.RESET_ALL}")
            print(f"  Created: {cache_info['created_at']}")
            print(f"  Expires: {cache_info['expires_at']}")
            print(f"  Files cached: {cache_info['file_count']:,}")
            print(f"  Days old: {cache_info['days_old']}")
            print(f"  Days remaining: {cache_info['days_left']}")
            print(f"  Valid: {Fore.GREEN + 'Yes' if cache_info['is_valid'] else Fore.RED + 'No'}{Style.RESET_ALL}")

            # Show cache size
            cache_size = cache_manager.get_cache_size()
            cache_size_kb = cache_size / 1024
            cache_size_mb = cache_size_kb / 1024

            if cache_size_mb > 1:
                print(f"  Cache size: {cache_size_mb:.2f} MB")
            else:
                print(f"  Cache size: {cache_size_kb:.2f} KB")
        else:
            print(f"{Fore.YELLOW}No cache found{Style.RESET_ALL}")
            print("Run the tool normally to create cache.")

        return False

    # Clear cache
    if args.clear_cache:
        print_header()
        print_section("Clear Cache")

        confirm = get_yes_no_input("Are you sure you want to clear the cache?", default='n')

        if confirm:
            if cache_manager.clear_cache():
                print(f"\n{Fore.GREEN}✓ Cache cleared successfully{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.YELLOW}No cache to clear{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}Operation cancelled{Style.RESET_ALL}")

        return False

    return True


def main():
    """Main application entry point"""
    # Parse command-line arguments
    args = parse_arguments()

    # Handle cache-only operations
    if not handle_cache_operations(args):
        return

    print_header()

    # Show cache configuration
    if not args.no_cache:
        if args.refresh_cache:
            print(f"{Fore.CYAN}ℹ Cache: Force refresh enabled{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN}ℹ Cache: Enabled (valid for {args.cache_days} days){Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}ℹ Cache: Disabled{Style.RESET_ALL}")

    # Step 1: Setup credentials
    if not setup_google_credentials():
        print(f"\n{Fore.RED}Failed to setup credentials. Exiting.{Style.RESET_ALL}")
        sys.exit(1)

    # Step 2: Authenticate
    print_section("Authentication")
    try:
        # Check if using service account
        if args.service_account:
            print(f"{Fore.CYAN}ℹ Using service account authentication{Style.RESET_ALL}")
            if args.admin_email:
                print(f"{Fore.CYAN}ℹ Impersonating admin: {args.admin_email}{Style.RESET_ALL}")

            authenticator = GoogleAPIAuthenticator(
                service_account_path=args.service_account,
                admin_email=args.admin_email
            )
        else:
            authenticator = GoogleAPIAuthenticator()

        authenticator.authenticate()
        drive_service = authenticator.get_drive_service()
        print(f"{Fore.GREEN}✓ Successfully authenticated with Google Drive API{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Authentication failed: {e}{Style.RESET_ALL}")
        sys.exit(1)

    # Step 3: Get employee email
    print_section("Employee Information")
    employee_email = get_user_input("Enter employee email address to revoke")

    # Validate email format
    if '@' not in employee_email:
        print(f"{Fore.RED}✗ Invalid email address{Style.RESET_ALL}")
        sys.exit(1)

    print(f"\n{Fore.CYAN}Target: {employee_email}{Style.RESET_ALL}")

    # Step 4: Choose operation mode
    print_section("Operation Mode")
    print("What would you like to do?")
    print("1. Generate report only (no changes)")
    print("2. Revoke access and generate report")
    print("3. Dry run (simulate revocation without making changes)")

    mode = get_user_input("Choose mode (1-3)", default='1')

    # Step 5: Scan Drive
    print_section("Scanning Google Drive")
    scanner = DriveScanner(
        drive_service,
        use_cache=not args.no_cache,
        cache_days=args.cache_days
    )

    # Show cache status if using cache
    if not args.no_cache:
        cache_info = scanner.get_cache_info()
        if cache_info and not args.refresh_cache:
            print(f"{Fore.GREEN}ℹ Using cached data from {cache_info['created_at']}{Style.RESET_ALL}")
            print(f"  Cache expires in {cache_info['days_left']} days")
            print(f"  Run with --refresh-cache to update\n")

    try:
        all_files = scanner.get_all_files(force_refresh=args.refresh_cache)
    except Exception as e:
        print(f"{Fore.RED}✗ Failed to scan Drive: {e}{Style.RESET_ALL}")
        sys.exit(1)

    # Step 6: Find files shared with employee
    shared_files = scanner.get_files_shared_with_user(employee_email, all_files)

    if not shared_files:
        print(f"\n{Fore.YELLOW}No files found shared with {employee_email}{Style.RESET_ALL}")
        print("Nothing to do. Exiting.")
        sys.exit(0)

    # Step 7: Display summary
    print(f"\n{Fore.CYAN}Summary:{Style.RESET_ALL}")
    print(f"  Total files in Drive: {len(all_files)}")
    print(f"  Files shared with {employee_email}: {len(shared_files)}")

    # Step 8: Revoke access (if requested)
    revocation_results = None

    if mode in ['2', '3']:
        dry_run = (mode == '3')

        confirm = get_yes_no_input(
            f"\n{'[DRY RUN] ' if dry_run else ''}Proceed with revoking access?",
            default='n'
        )

        if not confirm:
            print(f"{Fore.YELLOW}Operation cancelled by user{Style.RESET_ALL}")
            sys.exit(0)

        print_section(f"{'[DRY RUN] ' if dry_run else ''}Revoking Access")

        permission_manager = PermissionManager(drive_service)
        revocation_results = permission_manager.revoke_user_from_files(
            shared_files,
            employee_email,
            dry_run=dry_run,
            skip_errors=args.skip_errors,
            use_admin_override=args.use_admin_access
        )

    # Step 9: Generate report
    print_section("Generating Report")

    print("Choose report format:")
    print("1. CSV")
    print("2. Excel (XLSX)")
    print("3. JSON")
    print("4. All formats")

    format_choice = get_user_input("Choose format (1-4)", default='2')

    format_map = {
        '1': 'csv',
        '2': 'excel',
        '3': 'json'
    }

    report_generator = ReportGenerator()

    try:
        if format_choice == '4':
            # Generate all formats
            formats = ['csv', 'excel', 'json']
        else:
            formats = [format_map.get(format_choice, 'csv')]

        generated_files = []

        for fmt in formats:
            if revocation_results:
                # Generate combined report
                report_file = report_generator.generate_combined_report(
                    shared_files,
                    revocation_results,
                    employee_email,
                    format=fmt
                )
            else:
                # Generate shared files report only
                report_file = report_generator.generate_shared_files_report(
                    shared_files,
                    employee_email,
                    format=fmt
                )

            if isinstance(report_file, list):
                generated_files.extend(report_file)
            else:
                generated_files.append(report_file)

        # Print final summary
        print_section("Operation Complete")

        if revocation_results:
            print(f"{Fore.GREEN}✓ Access revocation completed{Style.RESET_ALL}")
            print(f"  Successfully revoked: {len(revocation_results['success'])}")
            print(f"  Failed: {len(revocation_results['failed'])}")
            print(f"  Permission denied: {len(revocation_results.get('permission_denied', []))}")
            print(f"  Skipped: {len(revocation_results['skipped'])}")

        print(f"\n{Fore.GREEN}✓ Reports generated:{Style.RESET_ALL}")
        for report_file in generated_files:
            print(f"  - {report_file}")

        # Show cache hint
        if not args.no_cache and args.refresh_cache:
            cache_info = scanner.get_cache_info()
            if cache_info:
                print(f"\n{Fore.CYAN}ℹ Cache updated - next scan will be faster!{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}Thank you for using Employee Offboarding Tool!{Style.RESET_ALL}\n")

    except Exception as e:
        print(f"{Fore.RED}✗ Failed to generate report: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Operation cancelled by user{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}✗ Unexpected error: {e}{Style.RESET_ALL}")
        sys.exit(1)
