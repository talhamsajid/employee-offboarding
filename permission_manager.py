"""
Permission Manager
Handles revoking and managing Google Drive permissions
"""

from googleapiclient.errors import HttpError
from tqdm import tqdm
import time


class PermissionManager:
    """Manages Google Drive file permissions"""

    def __init__(self, drive_service):
        """
        Initialize the permission manager

        Args:
            drive_service: Authenticated Google Drive service
        """
        self.drive_service = drive_service
        self.revocation_log = []

    def revoke_user_access(self, file_id, permission_id, file_name="Unknown",
                          use_admin_override=False):
        """
        Revoke a specific permission from a file

        Args:
            file_id: Google Drive file ID
            permission_id: Permission ID to revoke
            file_name: Name of the file (for logging)
            use_admin_override: Try to use transferOwnership if available

        Returns:
            dict: Result of the revocation attempt
        """
        try:
            # Try standard permission deletion
            self.drive_service.permissions().delete(
                fileId=file_id,
                permissionId=permission_id,
                supportsAllDrives=True,
                useDomainAdminAccess=use_admin_override
            ).execute()

            result = {
                'file_id': file_id,
                'file_name': file_name,
                'permission_id': permission_id,
                'status': 'success',
                'error': None
            }

            self.revocation_log.append(result)
            return result

        except HttpError as error:
            error_reason = self._extract_error_reason(error)

            result = {
                'file_id': file_id,
                'file_name': file_name,
                'permission_id': permission_id,
                'status': 'failed',
                'error': str(error),
                'error_reason': error_reason,
                'error_code': error.resp.status if hasattr(error, 'resp') else None
            }

            self.revocation_log.append(result)
            return result

    def _extract_error_reason(self, error):
        """
        Extract the reason from an HttpError

        Args:
            error: HttpError object

        Returns:
            String describing the error reason
        """
        try:
            error_details = error.error_details
            if error_details and len(error_details) > 0:
                return error_details[0].get('reason', 'unknown')
        except:
            pass

        # Try to parse from error message
        error_str = str(error)
        if 'cannotDeletePermission' in error_str:
            return 'cannotDeletePermission'
        elif 'insufficientPermissions' in error_str:
            return 'insufficientPermissions'
        elif 'fileNotFound' in error_str:
            return 'fileNotFound'

        return 'unknown'

    def revoke_user_from_files(self, shared_files, user_email, dry_run=False,
                               skip_errors=False, use_admin_override=False):
        """
        Revoke user access from multiple files

        Args:
            shared_files: List of dicts with 'file' and 'permission' keys
            user_email: Email address of the user
            dry_run: If True, only simulate the revocation
            skip_errors: If True, continue on permission errors
            use_admin_override: Try to use domain admin access

        Returns:
            dict: Summary of revocation results
        """
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Revoking access for {user_email}...")

        if skip_errors:
            print("  ⚠ Skip-errors mode: Will continue on permission errors")
        if use_admin_override:
            print("  🔐 Using domain admin access override")

        results = {
            'success': [],
            'failed': [],
            'skipped': [],
            'permission_denied': []
        }

        for item in tqdm(shared_files, desc="Revoking permissions"):
            file_data = item['file']
            permission = item['permission']

            file_id = file_data['id']
            file_name = file_data.get('name', 'Unknown')
            permission_id = permission['id']

            # Check if user is owner
            owners = file_data.get('owners', [])
            is_owner = any(
                owner.get('emailAddress', '').lower() == user_email.lower()
                for owner in owners
            )

            if is_owner:
                results['skipped'].append({
                    'file_id': file_id,
                    'file_name': file_name,
                    'reason': 'User is owner - cannot revoke ownership'
                })
                continue

            if dry_run:
                results['success'].append({
                    'file_id': file_id,
                    'file_name': file_name,
                    'permission_id': permission_id,
                    'status': 'would_revoke',
                    'error': None
                })
            else:
                result = self.revoke_user_access(
                    file_id,
                    permission_id,
                    file_name,
                    use_admin_override=use_admin_override
                )

                if result['status'] == 'success':
                    results['success'].append(result)
                else:
                    # Check if it's a permission error
                    error_reason = result.get('error_reason', 'unknown')

                    if error_reason in ['cannotDeletePermission', 'insufficientPermissions']:
                        results['permission_denied'].append(result)

                        if not skip_errors:
                            # Log permission error details
                            print(f"\n⚠ Permission denied for file: {file_name}")
                            print(f"   Error: {error_reason}")
                            print(f"   File ID: {file_id}")
                    else:
                        results['failed'].append(result)

                # Small delay to avoid rate limiting
                time.sleep(0.1)

        # Print summary
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Revocation Summary:")
        print(f"  Successfully revoked: {len(results['success'])}")
        print(f"  Failed: {len(results['failed'])}")
        print(f"  Permission denied: {len(results['permission_denied'])}")
        print(f"  Skipped: {len(results['skipped'])}")

        # Show permission denied details if any
        if results['permission_denied']:
            print(f"\n⚠ {len(results['permission_denied'])} files require admin/owner access")
            print("  Consider using:")
            print("  1. Service account with domain-wide delegation")
            print("  2. Authenticate as the file owner")
            print("  3. Use --skip-errors to continue anyway")

        return results

    def get_permission_info(self, file_id, permission_id):
        """
        Get detailed information about a specific permission

        Args:
            file_id: Google Drive file ID
            permission_id: Permission ID

        Returns:
            Permission metadata dictionary
        """
        try:
            permission = self.drive_service.permissions().get(
                fileId=file_id,
                permissionId=permission_id,
                fields="id, emailAddress, role, type, displayName",
                supportsAllDrives=True
            ).execute()

            return permission

        except HttpError as error:
            print(f"An error occurred getting permission info: {error}")
            return None

    def update_permission_role(self, file_id, permission_id, new_role):
        """
        Update a permission's role (e.g., from 'writer' to 'reader')

        Args:
            file_id: Google Drive file ID
            permission_id: Permission ID
            new_role: New role ('reader', 'writer', 'commenter')

        Returns:
            Updated permission metadata
        """
        try:
            updated_permission = self.drive_service.permissions().update(
                fileId=file_id,
                permissionId=permission_id,
                body={'role': new_role},
                supportsAllDrives=True
            ).execute()

            return updated_permission

        except HttpError as error:
            print(f"An error occurred updating permission: {error}")
            return None
