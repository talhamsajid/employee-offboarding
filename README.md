# Employee Offboarding Tool - Google Drive Access Revocation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Code style: PEP8](https://img.shields.io/badge/code%20style-PEP8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

A Python-based tool for securely revoking Google Drive access and generating comprehensive reports during employee offboarding.

## Features

- **Comprehensive Drive Scanning**: Scans all accessible Google Drive resources (Docs, Sheets, Forms, Sites, etc.)
- **Intelligent Caching**: Stores Drive data locally for 7 days (configurable), dramatically improving performance
- **Access Revocation**: Automatically revokes permissions for offboarded employees
- **Detailed Reporting**: Generates reports in multiple formats (CSV, Excel, JSON)
- **Interactive CLI**: User-friendly command-line interface with prompts for sensitive data
- **Dry Run Mode**: Test revocation without making actual changes
- **Safety Features**: Prevents revoking ownership permissions, detailed error handling

## Quick Start - One Command Setup! 🚀

Get up and running in seconds with automated setup scripts:

### Mac/Linux
```bash
bash setup_and_run.sh
```

### Windows
```cmd
setup_and_run.bat
```

### Cross-platform (Python)
```bash
python3 launcher.py
```

These scripts automatically:
- ✓ Check Python & pip installation
- ✓ Create virtual environment
- ✓ Install all dependencies
- ✓ Guide you through Google credentials setup
- ✓ Launch the application

**That's it!** See the installation section below for manual setup.

## Prerequisites

- Python 3.7 or higher (only requirement - scripts handle the rest!)
- Google Cloud Project with Drive API enabled
- OAuth2 credentials for Google APIs (instructions provided during setup)

## Manual Setup Instructions

If you prefer manual setup or the automated scripts don't work:

### 1. Clone or Download the Project

```bash
cd employee-offboarding
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Google Drive API
   - Google Sheets API (optional, for future features)

### 4. Create OAuth2 Credentials

1. In Google Cloud Console, go to **APIs & Services > Credentials**
2. Click **Create Credentials > OAuth client ID**
3. Choose **Desktop app** as the application type
4. Download the credentials JSON file

### 5. Configure Credentials

You have three options:

**Option 1**: Place the downloaded credentials file as `credentials.json` in the project directory

**Option 2**: The tool will prompt you to provide credentials interactively when you run it

**Option 3**: Paste the credentials JSON content when prompted by the tool

## Usage

### Run the Tool

```bash
# Basic run (uses cache)
python main.py

# Force refresh cache
python main.py --refresh-cache

# Show cache information
python main.py --cache-info

# Run without cache
python main.py --no-cache

# Show all options
python main.py --help
```

### Interactive Steps

The tool will guide you through:

1. **Cache Check**: Automatically uses cached data if available (7-day default)
2. **Credentials Setup**: Provide or verify Google API credentials
3. **Authentication**: OAuth2 browser authentication (first time only)
4. **Employee Email**: Enter the email address to revoke access from
5. **Operation Mode**:
   - Generate report only (no changes)
   - Revoke access and generate report
   - Dry run (simulate without changes)
6. **Report Format**: Choose CSV, Excel, JSON, or all formats

### Cache Feature

The tool automatically caches Drive scan results for 7 days:
- **First run**: Full Drive scan (may take minutes)
- **Subsequent runs**: Instant from cache (2-3 seconds)
- **Automatic expiration**: Cache refreshes after 7 days

**Cache Commands:**
```bash
python main.py --cache-info        # Show cache status
python main.py --refresh-cache     # Force refresh
python main.py --clear-cache       # Clear cache
python main.py --cache-days 14     # Custom duration
```

### Example Session

```
==============================================================================
  Employee Offboarding Tool - Google Drive Access Revocation
==============================================================================

──────────────────────────────────────────────────────────────────────────────
  Google API Credentials Setup
──────────────────────────────────────────────────────────────────────────────

✓ Found existing credentials.json
Use existing credentials? [Y/n]: y

──────────────────────────────────────────────────────────────────────────────
  Authentication
──────────────────────────────────────────────────────────────────────────────

✓ Successfully authenticated with Google Drive API

──────────────────────────────────────────────────────────────────────────────
  Employee Information
──────────────────────────────────────────────────────────────────────────────

Enter employee email address to revoke: former-employee@example.com

Target: former-employee@example.com

──────────────────────────────────────────────────────────────────────────────
  Operation Mode
──────────────────────────────────────────────────────────────────────────────

What would you like to do?
1. Generate report only (no changes)
2. Revoke access and generate report
3. Dry run (simulate revocation without making changes)

Choose mode (1-3) [1]: 2

──────────────────────────────────────────────────────────────────────────────
  Scanning Google Drive
──────────────────────────────────────────────────────────────────────────────

Scanning Google Drive for all files...
Total files found: 1,234

Analyzing permissions for former-employee@example.com...
Found 45 files shared with former-employee@example.com

Summary:
  Total files in Drive: 1,234
  Files shared with former-employee@example.com: 45

Proceed with revoking access? [y/N]: y

──────────────────────────────────────────────────────────────────────────────
  Revoking Access
──────────────────────────────────────────────────────────────────────────────

Revoking access for former-employee@example.com...

Revocation Summary:
  Successfully revoked: 43
  Failed: 0
  Skipped: 2

──────────────────────────────────────────────────────────────────────────────
  Generating Report
──────────────────────────────────────────────────────────────────────────────

Choose report format:
1. CSV
2. Excel (XLSX)
3. JSON
4. All formats

Choose format (1-4) [2]: 2

Combined report generated: reports/combined_report_former-employee_at_example.com_20241014_153022.xlsx

──────────────────────────────────────────────────────────────────────────────
  Operation Complete
──────────────────────────────────────────────────────────────────────────────

✓ Access revocation completed
  Successfully revoked: 43
  Failed: 0
  Skipped: 2

✓ Reports generated:
  - reports/combined_report_former-employee_at_example.com_20241014_153022.xlsx

Thank you for using Employee Offboarding Tool!
```

## Project Structure

```
employee-offboarding/
├── main.py                    # Main CLI application
├── launcher.py                # Cross-platform launcher
├── setup_and_run.sh           # Mac/Linux automated setup
├── setup_and_run.bat          # Windows automated setup
├── auth.py                    # Google API authentication
├── drive_scanner.py           # Drive resource scanning
├── permission_manager.py      # Permission management
├── report_generator.py        # Report generation
├── cache_manager.py           # Cache management
├── requirements.txt           # Python dependencies
├── .gitignore                # Git ignore rules
├── .env.example              # Environment variables template
├── README.md                  # This file
├── LICENSE                    # MIT License
├── credentials.json          # OAuth2 credentials (not in repo)
├── token.json                # Auth token (not in repo)
├── venv/                     # Virtual environment (auto-created)
├── cache/                    # Cache directory (auto-created)
└── reports/                  # Generated reports (not in repo)
```

## Report Contents

### Shared Files Report

- File ID
- File Name
- File Type (MIME type)
- Owner(s)
- Permission Role (reader, writer, commenter)
- Permission Type (user, group, domain, anyone)
- Web Link
- Created Time
- Modified Time
- File Size

### Revocation Report

- File ID
- File Name
- Status (Success, Failed, Skipped)
- Error (if applicable)

### Combined Report (Excel only)

Multiple sheets:
- **Summary**: Overview of operation
- **Shared Files**: All files that were shared
- **Revocation Results**: Detailed revocation outcomes

## Security Considerations

- **Credentials**: Never commit `credentials.json` or `token.json` to version control
- **Ownership Protection**: The tool will not revoke ownership permissions (only direct sharing)
- **Audit Trail**: All operations are logged in detailed reports
- **Dry Run**: Always test with dry run mode first in production environments
- **Interactive Prompts**: Sensitive data is never hardcoded, always prompted

## Troubleshooting

### Authentication Issues

If you encounter authentication errors:

1. Delete `token.json` and re-authenticate
2. Verify OAuth2 credentials in Google Cloud Console
3. Ensure Drive API is enabled for your project

### Permission Errors

If you see "insufficientPermissions" errors:

- Ensure you're authenticating with an account that has admin privileges
- Check that Drive API scopes include full Drive access

### Rate Limiting

If you hit rate limits:

- The tool includes automatic delays between API calls
- For very large organizations, consider running during off-peak hours
- Adjust `time.sleep()` values in the code if needed

## Advanced Usage

### Programmatic Usage

You can also use the modules programmatically:

```python
from auth import GoogleAPIAuthenticator
from drive_scanner import DriveScanner
from permission_manager import PermissionManager

# Authenticate
auth = GoogleAPIAuthenticator()
drive_service = auth.get_drive_service()

# Scan Drive
scanner = DriveScanner(drive_service)
all_files = scanner.get_all_files()

# Find shared files
shared_files = scanner.get_files_shared_with_user('user@example.com')

# Revoke access
pm = PermissionManager(drive_service)
results = pm.revoke_user_from_files(shared_files, 'user@example.com')
```

## Limitations

- Cannot revoke ownership permissions (by design for safety)
- Requires admin-level Drive access
- Rate limited by Google Drive API quotas
- Does not handle Google Workspace shared drives differently (treats all as regular files)

## Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Guidelines

- Maintain security-first approach
- Add comprehensive error handling
- Include docstrings for new functions
- Update documentation for new features
- Test with dry run mode before submitting
- Follow PEP 8 style guidelines

### Reporting Issues

If you find a bug or have a suggestion:

1. Check existing issues first
2. Create a new issue with detailed description
3. Include steps to reproduce (for bugs)
4. Specify your environment (OS, Python version)

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:

1. Check the [Issues](../../issues) page
2. Review the Troubleshooting section above
3. Check Google Drive API documentation
4. Verify API status in Google Cloud Console

## Roadmap

- [ ] Support for Google Workspace Shared Drives
- [ ] Bulk user offboarding from CSV
- [ ] Integration with HRIS systems
- [ ] Slack/Email notifications
- [ ] Web-based dashboard
- [ ] Scheduling and automation

## Acknowledgments

Built with:
- [Google API Python Client](https://github.com/googleapis/google-api-python-client)
- [Pandas](https://pandas.pydata.org/)
- [Colorama](https://github.com/tartley/colorama)
- [tqdm](https://github.com/tqdm/tqdm)

## Changelog

### Version 1.0.0 (2024-10-14)
- Initial release
- Automated setup scripts for all platforms
- Drive scanning functionality
- Permission revocation with safety checks
- Multi-format reporting (CSV, Excel, JSON)
- Interactive CLI with colored output
- Dry run mode
- Comprehensive documentation
