# Architecture Documentation

## Overview

Google Drive Access Manager is built using **Clean Architecture** principles with strict adherence to **SOLID** design principles and **Domain-Driven Design** (DDD) patterns. This document provides a comprehensive guide to the application's architecture, design patterns, and implementation details.

## Table of Contents

1. [Architectural Overview](#architectural-overview)
2. [Clean Architecture Layers](#clean-architecture-layers)
3. [SOLID Principles](#solid-principles)
4. [Design Patterns](#design-patterns)
5. [Domain-Driven Design](#domain-driven-design)
6. [Data Flow](#data-flow)
7. [Error Handling Strategy](#error-handling-strategy)
8. [Testing Strategy](#testing-strategy)

---

## Architectural Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Presentation Layer                         │
│         (CLI, User Interface, Progress Display)              │
└────────────────────────┬────────────────────────────────────┘
                         │ depends on
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                          │
│        (Use Cases, DTOs, Orchestration Logic)                │
└────────────────────────┬────────────────────────────────────┘
                         │ depends on
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer                              │
│     (Entities, Value Objects, Domain Services, Rules)        │
└─────────────────────────────────────────────────────────────┘
                         ▲ implements
                         │
┌─────────────────────────────────────────────────────────────┐
│                Infrastructure Layer                          │
│  (Google API, Caching, Reporting, Database, External APIs)   │
└─────────────────────────────────────────────────────────────┘
```

**Dependency Rule**: Dependencies point **inward only**. The Domain layer has no dependencies. Infrastructure depends on Application and Domain.

### Directory Structure

```
employee-offboarding/
├── domain/                 # Domain Layer (innermost)
│   ├── entities/          # Business entities with identity
│   ├── value_objects/     # Immutable value objects
│   ├── services/          # Domain services (business logic)
│   └── exceptions/        # Domain-specific exceptions
│
├── application/           # Application Layer
│   ├── dto/              # Data Transfer Objects
│   ├── use_cases/        # Application use cases
│   └── interfaces/       # Repository & service interfaces
│
├── infrastructure/        # Infrastructure Layer (outermost)
│   ├── google_api/       # Google Drive API integration
│   ├── cache/            # Caching implementation
│   ├── reporting/        # Report generation
│   └── logging/          # Audit logging
│
├── presentation/          # Presentation Layer
│   ├── main.py           # Entry point
│   └── cli/              # CLI components
│
└── config/                # Configuration Layer
    ├── configuration.py   # Config management
    └── dependency_injection.py  # DI container
```

---

## Clean Architecture Layers

### 1. Domain Layer (Core Business Logic)

**Purpose**: Contains all business logic, rules, and domain models. Has **zero dependencies** on other layers.

**Components**:

#### Entities
Business objects with identity and lifecycle:

```python
# domain/entities/drive_file.py
class DriveFile:
    """Aggregate Root - represents a Google Drive file"""
    
    def can_revoke_permission_for(self, email: Email) -> bool:
        """Business rule: Cannot revoke if user is owner"""
        if self.is_owned_by(email):
            return False
        return self.has_revocable_permissions_for(email)
```

#### Value Objects
Immutable objects defined by their values:

```python
# domain/value_objects/email.py
class Email:
    """RFC 5322 compliant email with validation"""
    
    def __init__(self, value: str):
        if not self._is_valid(value):
            raise ValueError(f"Invalid email: {value}")
        self._value = value.strip().lower()
    
    @property
    def value(self) -> str:
        return self._value
    
    @property
    def domain(self) -> str:
        return self._value.split('@')[1]
```

**Benefits**:
- Type safety (eliminates primitive obsession)
- Self-validating
- Immutable (thread-safe)
- Domain semantics clear

#### Domain Services
Stateless services implementing business logic that doesn't fit in entities:

```python
# domain/services/permission_service.py
class PermissionService:
    """Domain service for permission-related business logic"""
    
    def can_revoke_permission(
        self,
        file: DriveFile,
        permission: Permission,
        target_email: Email
    ) -> bool:
        """Complex business rule spanning multiple entities"""
        # Business logic here
```

### 2. Application Layer (Use Cases)

**Purpose**: Orchestrates domain objects to fulfill use cases. Defines application workflows.

**Components**:

#### Use Cases
Application-specific business workflows:

```python
# application/use_cases/manage_user_access_use_case.py
class ManageUserAccessUseCase:
    """Main orchestration use case"""
    
    def execute(self, request: AccessManagementRequest) -> AccessManagementResult:
        # 1. Scan Drive
        all_files = self._scan_files(request)
        
        # 2. Analyze permissions
        shared_files = self._analyze_access(all_files, request.target_email)
        
        # 3. Execute operation (revoke/audit)
        results = self._execute_operation(shared_files, request)
        
        # 4. Generate reports
        self._generate_reports(shared_files, request, results)
        
        return results
```

#### DTOs (Data Transfer Objects)
Simple data containers for transferring data between layers:

```python
# application/dto/access_management_request.py
@dataclass
class AccessManagementRequest:
    """Immutable request DTO"""
    target_email: str
    operation_mode: OperationMode
    dry_run: bool
    report_formats: List[str]
    cache_enabled: bool
```

**Benefits**:
- Decouples layers
- Prevents domain model exposure
- Validates at boundaries

#### Interfaces
Abstractions for infrastructure dependencies:

```python
# application/interfaces/repositories.py
class IDriveRepository(ABC):
    """Repository interface (Dependency Inversion)"""
    
    @abstractmethod
    def list_all_files(self) -> List[DriveFile]:
        pass
    
    @abstractmethod
    def find_files_shared_with(self, email: Email) -> List[DriveFile]:
        pass
```

### 3. Infrastructure Layer (External Services)

**Purpose**: Implements interfaces defined by Application layer. Handles all external dependencies.

**Components**:

#### Repositories
Implement data access interfaces:

```python
# infrastructure/google_api/google_drive_repository.py
class GoogleDriveRepository(IDriveRepository):
    """Concrete implementation using Google Drive API"""
    
    def __init__(self, drive_service):
        self._drive_service = drive_service
    
    def list_all_files(self) -> List[DriveFile]:
        # API calls, mapping, error handling
        response = self._drive_service.files().list(...).execute()
        return [DriveFile.from_api_response(item) for item in response['files']]
```

#### External Service Integrations
- Google Drive API
- File system caching
- Report generation (CSV, Excel, JSON)
- Audit logging

### 4. Presentation Layer (User Interface)

**Purpose**: Handles user interaction and input/output. Depends only on Application layer.

**Components**:

```python
# presentation/main.py
def main():
    # Setup DI
    container = setup_container(args)
    
    # Resolve use case
    use_case = container.resolve(ManageUserAccessUseCase)
    
    # Build request from user input
    presenter = CLIPresenter()
    request = presenter.build_request_interactive()
    
    # Execute
    result = use_case.execute(request)
    
    # Display results
    presenter.display_result(result)
```

---

## SOLID Principles

### 1. Single Responsibility Principle (SRP)

**"A class should have only one reason to change"**

**Examples**:
- `Email` - Only validates and represents email addresses
- `PermissionService` - Only handles permission business logic
- `GoogleDriveRepository` - Only interacts with Google Drive API
- `CLIPresenter` - Only handles user interaction

### 2. Open/Closed Principle (OCP)

**"Open for extension, closed for modification"**

**Example: Report Formatters (Strategy Pattern)**

```python
# Adding new format requires NO modification of existing code
class HTMLReportFormatter(IReportFormatter):
    def format(self, data: Dict[str, Any]) -> str:
        # New implementation
        pass

# Just register in ReportGenerator
self._formatters[ReportFormat.HTML] = HTMLReportFormatter()
```

### 3. Liskov Substitution Principle (LSP)

**"Subtypes must be substitutable for their base types"**

**Example**:

```python
# All authentication services are fully substitutable
auth_service: IAuthenticationService = OAuth2AuthenticationService()
# OR
auth_service: IAuthenticationService = ServiceAccountAuthenticationService()

# Both work identically
drive_service = auth_service.get_drive_service()
```

### 4. Interface Segregation Principle (ISP)

**"Clients should not depend on interfaces they don't use"**

**Example**:

```python
# Separate, focused interfaces instead of one fat interface
class IDriveRepository(ABC):
    """Only Drive file operations"""
    pass

class IPermissionRepository(ABC):
    """Only permission operations"""
    pass

class ICacheRepository(ABC):
    """Only caching operations"""
    pass
```

### 5. Dependency Inversion Principle (DIP)

**"Depend on abstractions, not concretions"**

**Example**:

```python
# Use case depends on interface (abstraction)
class ManageUserAccessUseCase:
    def __init__(
        self,
        drive_repository: IDriveRepository,  # Interface, not concrete class
        permission_repository: IPermissionRepository,
        cache_repository: ICacheRepository
    ):
        self._drive_repo = drive_repository
        # ...

# Concrete implementations injected at runtime
use_case = ManageUserAccessUseCase(
    drive_repository=GoogleDriveRepository(service),  # Concrete
    permission_repository=GooglePermissionRepository(service),
    cache_repository=FileCacheRepository(cache_dir)
)
```

---

## Design Patterns

### 1. Repository Pattern

**Purpose**: Abstract data access logic

**Implementation**:
```python
# Interface (Application Layer)
class IDriveRepository(ABC):
    @abstractmethod
    def list_all_files(self) -> List[DriveFile]:
        pass

# Implementation (Infrastructure Layer)
class GoogleDriveRepository(IDriveRepository):
    def list_all_files(self) -> List[DriveFile]:
        # Google API implementation
        pass
```

**Benefits**:
- Testable (easy to mock)
- Swappable implementations
- Centralized data access logic

### 2. Factory Pattern

**Purpose**: Create objects without specifying exact class

**Implementation**:
```python
class AuthenticationFactory:
    @staticmethod
    def create_from_config(config) -> IAuthenticationService:
        if config.service_account_path:
            return ServiceAccountAuthenticationService(...)
        else:
            return OAuth2AuthenticationService(...)
```

**Benefits**:
- Encapsulates object creation
- Enables polymorphism
- Simplifies client code

### 3. Strategy Pattern

**Purpose**: Define family of interchangeable algorithms

**Implementation**:
```python
# Strategy interface
class IReportFormatter(ABC):
    @abstractmethod
    def format(self, data: Dict[str, Any]) -> str:
        pass

# Concrete strategies
class CSVReportFormatter(IReportFormatter):
    def format(self, data) -> str:
        # CSV implementation
        pass

class ExcelReportFormatter(IReportFormatter):
    def format(self, data) -> str:
        # Excel implementation
        pass

# Context
class ReportGenerator:
    def __init__(self):
        self._formatters = {
            ReportFormat.CSV: CSVReportFormatter(),
            ReportFormat.EXCEL: ExcelReportFormatter(),
            ReportFormat.JSON: JSONReportFormatter()
        }
    
    def generate_report(self, format: ReportFormat, data):
        formatter = self._formatters[format]
        return formatter.format(data)
```

**Benefits**:
- Easy to add new formats
- Runtime algorithm selection
- Follows OCP

### 4. Builder Pattern

**Purpose**: Construct complex objects step-by-step

**Implementation**:
```python
class AccessManagementRequestBuilder:
    def __init__(self, target_email: str):
        self._target_email = target_email
        self._operation_mode = OperationMode.REVOKE_ALL
        self._dry_run = False
        # ...
    
    def with_operation(self, mode: OperationMode):
        self._operation_mode = mode
        return self
    
    def as_dry_run(self):
        self._dry_run = True
        return self
    
    def build(self) -> AccessManagementRequest:
        request = AccessManagementRequest(
            target_email=self._target_email,
            operation_mode=self._operation_mode,
            dry_run=self._dry_run,
            # ...
        )
        request.validate()
        return request

# Usage (fluent API)
request = (AccessManagementRequestBuilder("user@example.com")
    .with_operation(OperationMode.REVOKE_ALL)
    .as_dry_run()
    .with_formats(['csv', 'excel'])
    .build())
```

**Benefits**:
- Readable, fluent API
- Validation before construction
- Immutable result object

### 5. Observer Pattern

**Purpose**: Notify multiple objects of state changes

**Implementation**:
```python
# Observer interface
class IProgressObserver(ABC):
    @abstractmethod
    def on_scan_started(self, total_files: int) -> None:
        pass
    
    @abstractmethod
    def on_file_scanned(self, file_name: str, current: int, total: int) -> None:
        pass

# Concrete observer
class CLIProgressObserver(IProgressObserver):
    def on_scan_started(self, total_files: int):
        self._progress_bar = tqdm(total=total_files)
    
    def on_file_scanned(self, file_name: str, current: int, total: int):
        self._progress_bar.update(1)

# Subject (Use Case)
class ManageUserAccessUseCase:
    def set_progress_observer(self, observer: IProgressObserver):
        self._observer = observer
    
    def _scan_files(self):
        self._observer.on_scan_started(total_files)
        for file in files:
            # Process file
            self._observer.on_file_scanned(file.name, current, total)
```

**Benefits**:
- Decouples progress reporting from business logic
- Multiple observers possible
- Testable (use SilentProgressObserver in tests)

### 6. Dependency Injection

**Purpose**: Invert control of dependency creation

**Implementation**:
```python
class ServiceContainer:
    def __init__(self):
        self._services = {}
        self._singletons = {}
    
    def register_singleton(self, interface: type, factory: Callable):
        self._services[interface] = lambda: self._get_or_create_singleton(
            interface, factory
        )
    
    def resolve(self, interface: type):
        return self._services[interface]()

# Configuration (Composition Root)
def configure_services(config):
    container = ServiceContainer()
    
    # Register dependencies
    container.register_singleton(
        IDriveRepository,
        lambda: GoogleDriveRepository(drive_service)
    )
    
    container.register_transient(
        ManageUserAccessUseCase,
        lambda: ManageUserAccessUseCase(
            drive_repository=container.resolve(IDriveRepository),
            # ... other dependencies
        )
    )
    
    return container
```

**Benefits**:
- Testable (inject mocks)
- Flexible (swap implementations)
- Single configuration point

### 7. Value Object Pattern

**Purpose**: Represent domain concepts as immutable objects

**Implementation**:
```python
class Email:
    """Value Object - immutable, self-validating"""
    
    def __init__(self, value: str):
        normalized = value.strip().lower()
        if not self._is_valid(normalized):
            raise ValueError(f"Invalid email: {value}")
        self._value = normalized
    
    @property
    def value(self) -> str:
        return self._value
    
    def __eq__(self, other):
        if not isinstance(other, Email):
            return False
        return self._value == other._value
    
    def __hash__(self):
        return hash(self._value)
```

**Benefits**:
- Eliminates primitive obsession
- Type safety
- Centralized validation
- Immutability (thread-safe)

---

## Domain-Driven Design

### Entities vs Value Objects

| Aspect | Entity | Value Object |
|--------|--------|--------------|
| Identity | Has unique ID | No identity |
| Equality | By ID | By value |
| Mutability | Mutable | Immutable |
| Lifespan | Tracked over time | Replaceable |
| Example | `DriveFile`, `User` | `Email`, `FileId` |

### Aggregates

**DriveFile** is an aggregate root that encapsulates:
- File properties
- Permissions collection
- Business rules

```python
class DriveFile:
    """Aggregate Root"""
    
    def __init__(self, file_id: FileId, name: str):
        self._file_id = file_id
        self._name = name
        self._permissions: List[Permission] = []
    
    def add_permission(self, permission: Permission) -> None:
        """Maintains invariants"""
        if self._has_permission(permission.permission_id):
            raise ValueError("Permission already exists")
        self._permissions.append(permission)
    
    def revoke_permission_for(self, email: Email) -> List[Permission]:
        """Business logic encapsulated"""
        return [p for p in self._permissions 
                if p.belongs_to_user(email) and p.can_be_revoked()]
```

### Bounded Contexts

```
┌─────────────────────────────────────┐
│   Access Management Context         │
│                                     │
│  - DriveFile                        │
│  - Permission                       │
│  - User                             │
│  - Email                            │
│                                     │
└─────────────────────────────────────┘
```

---

## Data Flow

### Complete Request Flow

```
1. User Input (Presentation Layer)
   ↓
2. CLIPresenter validates input
   ↓
3. Builder creates AccessManagementRequest DTO
   ↓
4. ManageUserAccessUseCase.execute(request)
   ↓
5. Use Case orchestrates:
   a. DriveRepository.list_all_files()
      → Google API call
      → Map to DriveFile entities
   b. FileAnalysisService.find_files_shared_with()
      → Domain logic
   c. PermissionRepository.revoke_permission()
      → Google API call
   d. ReportService.generate_report()
      → Strategy pattern (CSV/Excel/JSON)
   e. AuditLogger.log_operation()
      → File system write
   ↓
6. Return AccessManagementResult DTO
   ↓
7. CLIPresenter.display_result()
   ↓
8. User sees formatted output
```

---

## Error Handling Strategy

### Exception Hierarchy

```
AccessManagerError (base)
├── AuthenticationError
├── PermissionDeniedError
├── RateLimitError
├── ValidationError
├── FileNotFoundError
├── ConfigurationError
├── RepositoryError
└── CacheError
```

### Error Handling Layers

1. **Domain Layer**: Throw domain exceptions
2. **Application Layer**: Catch infrastructure errors, throw application errors
3. **Infrastructure Layer**: Catch external errors, wrap in domain exceptions
4. **Presentation Layer**: Catch all, display user-friendly messages

**Example**:
```python
# Infrastructure Layer
try:
    response = drive_service.files().list().execute()
except HttpError as e:
    if e.resp.status == 403:
        raise PermissionDeniedError("Insufficient permissions", file_id=file_id)
    elif e.resp.status == 429:
        raise RateLimitError("API rate limit exceeded")
    else:
        raise RepositoryError(f"Drive API error: {e}")

# Presentation Layer
try:
    result = use_case.execute(request)
except AuthenticationError as e:
    presenter.display_error("Authentication failed", e)
except PermissionDeniedError as e:
    presenter.display_error("Permission denied", e)
except AccessManagerError as e:
    presenter.display_error("Operation failed", e)
```

---

## Testing Strategy

### Test Pyramid

```
        ╱╲
       ╱E2E╲          Few (1-5) - Full system tests
      ╱──────╲
     ╱Integr.╲        Some (10-20) - Layer integration
    ╱──────────╲
   ╱   Unit     ╲     Many (100+) - Component tests
  ╱──────────────╲
```

### Unit Tests

Test individual components in isolation:

```python
# tests/unit/test_value_objects.py
def test_email_validation():
    # Valid email
    email = Email("user@example.com")
    assert email.value == "user@example.com"
    assert email.domain == "example.com"
    
    # Invalid email
    with pytest.raises(ValueError):
        Email("invalid-email")
    
    # Normalization
    email = Email("  User@EXAMPLE.COM  ")
    assert email.value == "user@example.com"
```

### Integration Tests

Test layer interactions with mocks:

```python
# tests/integration/test_use_cases.py
def test_manage_user_access_use_case():
    # Mock repositories
    drive_repo = Mock(spec=IDriveRepository)
    permission_repo = Mock(spec=IPermissionRepository)
    
    # Setup mocks
    drive_repo.list_all_files.return_value = [mock_file_1, mock_file_2]
    
    # Execute use case
    use_case = ManageUserAccessUseCase(drive_repo, permission_repo, ...)
    result = use_case.execute(request)
    
    # Verify
    assert result.success_count == 2
    drive_repo.list_all_files.assert_called_once()
```

### E2E Tests

Test complete workflows:

```python
# tests/e2e/test_full_workflow.py
def test_full_revocation_workflow(test_config):
    # Real Google API (test account)
    container = setup_container(test_config)
    use_case = container.resolve(ManageUserAccessUseCase)
    
    # Execute real operation
    request = AccessManagementRequestBuilder("test@example.com")
        .as_dry_run()
        .build()
    
    result = use_case.execute(request)
    
    # Verify end-to-end
    assert result is not None
    assert len(result.report_paths) > 0
```

---

## Best Practices

### 1. Keep Domain Pure
- No infrastructure dependencies in domain layer
- Business logic in entities and domain services
- Use value objects to eliminate primitive obsession

### 2. Program to Interfaces
- Define interfaces in application layer
- Implement in infrastructure layer
- Inject via dependency injection

### 3. Immutability
- Value objects are immutable
- DTOs are immutable
- Entities protect their state

### 4. Fail Fast
- Validate at boundaries (presentation, DTOs)
- Use value objects for type safety
- Throw exceptions for invalid states

### 5. Single Responsibility
- Each class has one reason to change
- Small, focused modules
- Clear separation of concerns

---

## Conclusion

This architecture provides:

✅ **Maintainability** - Clear separation of concerns
✅ **Testability** - Dependency injection and interfaces
✅ **Flexibility** - Easy to swap implementations
✅ **Scalability** - Modular, extensible design
✅ **Reliability** - Type safety and domain validation
✅ **Readability** - Self-documenting code with DDD

The investment in proper architecture pays dividends in:
- Faster feature development
- Easier bug fixes
- Confident refactoring
- Better team collaboration
- Production stability
