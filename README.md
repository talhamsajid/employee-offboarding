# Google Drive Access Manager

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Architecture: Clean](https://img.shields.io/badge/architecture-Clean-blue.svg)](ARCHITECTURE.md)
[![SOLID](https://img.shields.io/badge/principles-SOLID-green.svg)](ARCHITECTURE.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

An enterprise-grade application for managing Google Drive access control with comprehensive audit trails. Refactored from a monolithic script into a Clean Architecture application following SOLID principles and Domain-Driven Design.

## 🎯 What's New in v2.0

**Complete architectural transformation:**
- ✨ **Clean Architecture** - Proper layer separation (Domain, Application, Infrastructure, Presentation)
- 🎨 **Design Patterns** - Repository, Factory, Strategy, Builder, Observer, Dependency Injection
- 🏗️ **SOLID Principles** - All five principles rigorously applied
- 🔒 **Type Safety** - Value Objects eliminate primitive obsession
- 📊 **Domain-Driven Design** - Rich domain models with business logic
- 🧪 **Testable** - Complete separation of concerns enables comprehensive testing
- 📝 **Enterprise-Ready** - Production-grade error handling and audit logging

## ✨ Key Features

### Core Capabilities
- **🔍 Comprehensive Scanning** - All Google Drive resources (Docs, Sheets, Slides, Forms, Sites)
- **🔐 Access Revocation** - Safe permission removal with ownership protection
- **📊 Multi-Format Reports** - CSV, Excel (XLSX), JSON with rich formatting
- **💾 Intelligent Caching** - File-based cache with TTL and compression (7-day default)
- **🎭 Dry Run Mode** - Preview changes before execution
- **📝 Audit Logging** - Complete operation trail with structured logging

### Architecture Highlights
- **🏛️ Clean Architecture** - Domain, Application, Infrastructure, Presentation layers
- **🎯 SOLID Principles** - Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **🎨 Design Patterns** - Repository, Factory, Strategy, Builder, Observer, Value Object, Entity
- **🔒 Type Safety** - Value Objects (Email, FileId, PermissionRole) replace primitives
- **💉 Dependency Injection** - ServiceContainer manages all dependencies
- **🧪 Testable Design** - Interfaces and DI enable comprehensive unit/integration testing

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd employee-offboarding

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Initial Setup

1. **Google Cloud Project Setup**:
   - Create project at [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Google Drive API
   - Create OAuth2 credentials (Desktop app)
   - Download `credentials.json` to project root

2. **Run the Application**:

```bash
# Interactive mode (recommended)
python -m presentation.main

# Batch mode
python -m presentation.main --email user@domain.com --mode revoke --formats csv,excel

# Dry run mode
python -m presentation.main --email user@domain.com --mode revoke --dry-run
```

## 📋 Prerequisites

- **Python 3.8+** (3.10+ recommended for best type checking)
- **Google Cloud Project** with Drive API enabled
- **OAuth2 Credentials** or Service Account (for domain-wide delegation)
- **Dependencies**: See `requirements.txt` (automatically installed)

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

## 💻 Usage

### Command-Line Interface

```bash
# Interactive mode with prompts
python -m presentation.main

# Batch mode (all parameters specified)
python -m presentation.main \
  --email user@domain.com \
  --mode revoke \
  --formats csv,excel \
  --dry-run

# Audit only (no changes)
python -m presentation.main --email user@domain.com --mode audit

# Cache management
python -m presentation.main --refresh-cache  # Force refresh
python -m presentation.main --no-cache       # Disable cache
python -m presentation.main --cache-days 14  # Custom TTL

# Custom configuration
python -m presentation.main --config ./my-config.yaml

# Show help
python -m presentation.main --help
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
python -m presentation.main --cache-info        # Show cache status
python -m presentation.main --refresh-cache     # Force refresh
python -m presentation.main --clear-cache       # Clear cache
python -m presentation.main --cache-days 14     # Custom duration
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

## 📁 Project Structure (Clean Architecture)

```
employee-offboarding/
├── domain/                          # Domain Layer (Business Logic)
│   ├── entities/                   # Entities with identity
│   │   ├── drive_file.py          # Aggregate root for Drive files
│   │   ├── permission.py          # Permission entity
│   │   └── user.py                # User entity
│   ├── value_objects/             # Immutable value objects
│   │   ├── email.py              # Email with validation
│   │   ├── file_id.py            # Type-safe file ID
│   │   ├── permission_id.py      # Type-safe permission ID
│   │   └── permission_role.py    # Role enum (reader, writer, owner)
│   ├── services/                  # Domain services
│   │   ├── permission_service.py # Permission business logic
│   │   └── file_analysis_service.py # File analysis logic
│   └── exceptions/                # Domain exceptions
│       └── access_manager_errors.py # Custom exception hierarchy
│
├── application/                     # Application Layer (Use Cases)
│   ├── dto/                       # Data Transfer Objects
│   │   ├── access_management_request.py  # Request DTO with Builder
│   │   └── access_management_result.py   # Result DTO
│   ├── use_cases/                 # Use case implementations
│   │   └── manage_user_access_use_case.py # Main orchestration
│   └── interfaces/                # Repository & service interfaces
│       ├── repositories.py        # IDriveRepository, IPermissionRepository, ICacheRepository
│       └── services.py           # IAuthService, IReportService, IProgressObserver
│
├── infrastructure/                  # Infrastructure Layer (External Services)
│   ├── google_api/               # Google API implementations
│   │   ├── authentication_service.py      # OAuth2 & ServiceAccount (Factory)
│   │   ├── google_drive_repository.py     # Drive API repository
│   │   └── google_permission_repository.py # Permission API repository
│   ├── cache/                    # Caching infrastructure
│   │   ├── file_cache_repository.py # File-based cache with TTL
│   │   └── cache_decorators.py   # Caching, logging, retry decorators
│   ├── reporting/                # Report generation (Strategy pattern)
│   │   ├── report_generator.py   # Main report service
│   │   └── formatters/           # Format strategies
│   │       ├── csv_formatter.py
│   │       ├── excel_formatter.py
│   │       └── json_formatter.py
│   └── logging/                  # Logging infrastructure
│       └── audit_logger.py       # Structured audit logging
│
├── presentation/                    # Presentation Layer (UI)
│   ├── main.py                   # Application entry point
│   └── cli/                      # CLI components
│       ├── cli_presenter.py      # User interaction handler
│       ├── input_validator.py    # Input validation
│       └── progress_observer.py  # Progress display (Observer)
│
├── config/                         # Configuration Layer
│   ├── configuration.py          # Multi-source config management
│   ├── dependency_injection.py   # DI container
│   └── defaults.yaml            # Default configuration
│
├── tests/                          # Test Suite
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── e2e/                     # End-to-end tests
│
├── requirements.txt              # Python dependencies
├── .gitignore                   # Git ignore rules
├── README.md                     # This file
├── ARCHITECTURE.md              # Architecture documentation
├── CHANGELOG.md                 # Version history
└── LICENSE                       # MIT License
```

**Key Architecture Concepts:**
- **Domain Layer**: Pure business logic, no dependencies on other layers
- **Application Layer**: Orchestrates use cases, depends only on Domain
- **Infrastructure Layer**: Implements interfaces, depends on Application & Domain
- **Presentation Layer**: User interface, depends on Application layer
- **Dependency Rule**: Dependencies point inward (Presentation → Application → Domain)

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

## 🔒 Security & Best Practices

- **Credentials Protection**: Never commit `credentials.json`, `token.json`, or service account keys
- **Ownership Safety**: Cannot revoke owner permissions (prevents accidental data loss)
- **Audit Trail**: All operations logged with structured JSON audit logs
- **Dry Run First**: Always test with `--dry-run` in production
- **Principle of Least Privilege**: Use appropriate scopes for authentication
- **Value Objects**: Type-safe email and ID validation prevents injection attacks

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

## 🔧 Development

### Architecture Overview

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design documentation.

**Key Design Patterns:**
- Repository Pattern (Drive, Permission, Cache repositories)
- Factory Pattern (Authentication service creation)
- Strategy Pattern (Report formatters)
- Builder Pattern (Request construction)
- Observer Pattern (Progress reporting)
- Dependency Injection (ServiceContainer)

### Adding New Features

```python
# Example: Adding a new report format
from application.interfaces.services import IReportFormatter

class HTMLReportFormatter(IReportFormatter):
    def format(self, data: Dict[str, Any]) -> str:
        # Implementation
        pass
    
    def get_extension(self) -> str:
        return 'html'

# Register in ReportGenerator
self._formatters[ReportFormat.HTML] = HTMLReportFormatter()
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test suite
pytest tests/unit/test_domain_entities.py
```

## 🚧 Known Limitations

- Cannot revoke ownership permissions (by design for safety)
- Requires appropriate Drive API access scopes
- Subject to Google Drive API rate limits (automatic throttling included)
- Shared drives treated as regular files (no special handling yet)

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

## 🗺️ Roadmap

### v2.1 (Next Release)
- [ ] Complete test suite with 80%+ coverage
- [ ] Additional use cases (Audit-only, Report generation, Cache management)
- [ ] Performance benchmarks and optimization

### v3.0 (Future)
- [ ] Google Workspace Shared Drives support
- [ ] Bulk user operations from CSV
- [ ] Web-based dashboard (FastAPI + React)
- [ ] HRIS system integrations
- [ ] Slack/Email notifications
- [ ] Scheduled automation

## Acknowledgments

Built with:
- [Google API Python Client](https://github.com/googleapis/google-api-python-client)
- [Pandas](https://pandas.pydata.org/)
- [Colorama](https://github.com/tartley/colorama)
- [tqdm](https://github.com/tqdm/tqdm)

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

### Version 2.0.0 (2024 - Current)
**Complete Architecture Refactoring**
- ✨ Clean Architecture with 4 layers (Domain, Application, Infrastructure, Presentation)
- 🎨 7+ Design Patterns implemented
- 🏗️ SOLID principles throughout
- 🔒 Value Objects for type safety
- 📊 Domain-Driven Design
- 💉 Dependency Injection
- 📝 Comprehensive audit logging
- 📁 Proper project structure

### Version 1.0.0 (2024-10-14)
- Initial monolithic implementation
- Basic Drive scanning and permission revocation
- Multi-format reporting
- Cache management
- Interactive CLI
