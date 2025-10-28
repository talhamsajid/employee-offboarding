# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Support for Google Workspace Shared Drives
- Bulk user offboarding from CSV
- Integration with HRIS systems
- Slack/Email notifications
- Web-based dashboard
- Scheduling and automation

## [1.0.0] - 2024-10-14

### Added
- Initial public release
- Automated setup scripts for Mac/Linux/Windows
- Google Drive file scanning functionality
- Permission revocation with safety checks
- Multi-format reporting (CSV, Excel, JSON)
- Interactive CLI with colored output and progress bars
- Dry run mode for safe testing
- Intelligent 7-day caching system for performance
- OAuth2 authentication flow
- Comprehensive documentation
- Cross-platform launcher

### Security
- Protection against revoking ownership permissions
- Sensitive data never hardcoded (interactive prompts)
- Audit trail through detailed reports
- Credentials excluded from version control

## Release Notes

### Version 1.0.0 Highlights

This is the first open-source release of the Employee Offboarding Tool, designed to help organizations securely revoke Google Drive access during employee offboarding.

**Key Features:**
- 🚀 One-command setup and launch
- 🔒 Security-first design with dry-run mode
- 📊 Comprehensive reporting in multiple formats
- ⚡ Intelligent caching for improved performance
- 🎨 User-friendly CLI with progress indicators
- 📝 Complete documentation and contribution guidelines

**System Requirements:**
- Python 3.7+
- Google Cloud Project with Drive API enabled
- OAuth2 credentials

For upgrade instructions and migration guides, see the [README.md](README.md).
