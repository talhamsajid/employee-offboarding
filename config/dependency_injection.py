"""
Dependency Injection Container
Manages object creation and dependencies
"""

from typing import Dict, Any, Callable, Optional
from config.configuration import AppConfiguration, ConfigurationLoader


class ServiceContainer:
    """
    Simple dependency injection container
    
    Manages service registration and resolution.
    Supports singleton, transient, and scoped lifetimes.
    """
    
    def __init__(self):
        """Initialize the service container"""
        self._services: Dict[type, Callable] = {}
        self._singletons: Dict[type, Any] = {}
        self._configuration: Optional[AppConfiguration] = None
    
    def register_singleton(self, interface: type, implementation: Callable) -> None:
        """
        Register a singleton service (created once, reused)
        
        Args:
            interface: Interface or base class
            implementation: Factory function or class
        """
        self._services[interface] = lambda: self._get_or_create_singleton(
            interface, implementation
        )
    
    def register_transient(self, interface: type, implementation: Callable) -> None:
        """
        Register a transient service (created each time)
        
        Args:
            interface: Interface or base class
            implementation: Factory function or class
        """
        self._services[interface] = implementation
    
    def register_instance(self, interface: type, instance: Any) -> None:
        """
        Register an existing instance
        
        Args:
            interface: Interface or base class
            instance: Instance to register
        """
        self._singletons[interface] = instance
        self._services[interface] = lambda: instance
    
    def resolve(self, interface: type) -> Any:
        """
        Resolve a service by interface
        
        Args:
            interface: Interface or base class to resolve
            
        Returns:
            Service instance
            
        Raises:
            KeyError: If service not registered
        """
        if interface not in self._services:
            raise KeyError(f"Service not registered: {interface}")
        
        return self._services[interface]()
    
    def _get_or_create_singleton(self, interface: type, factory: Callable) -> Any:
        """Get or create singleton instance"""
        if interface not in self._singletons:
            self._singletons[interface] = factory()
        return self._singletons[interface]
    
    def set_configuration(self, config: AppConfiguration) -> None:
        """
        Set application configuration
        
        Args:
            config: Application configuration
        """
        self._configuration = config
        self.register_instance(AppConfiguration, config)
    
    def get_configuration(self) -> AppConfiguration:
        """
        Get application configuration
        
        Returns:
            Application configuration
        """
        if self._configuration is None:
            self._configuration = ConfigurationLoader.load()
            self.register_instance(AppConfiguration, self._configuration)
        return self._configuration


# Global container instance
_container: Optional[ServiceContainer] = None


def get_container() -> ServiceContainer:
    """
    Get the global service container
    
    Returns:
        ServiceContainer instance
    """
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container


def reset_container() -> None:
    """Reset the global container (useful for testing)"""
    global _container
    _container = None


def configure_services(config: Optional[AppConfiguration] = None) -> ServiceContainer:
    """
    Configure all services in the container
    
    This is the main composition root for the application.
    All dependencies are wired up here.
    
    Args:
        config: Optional configuration (loads default if not provided)
        
    Returns:
        Configured ServiceContainer
    """
    container = get_container()
    
    # Load configuration
    if config is None:
        config = ConfigurationLoader.load()
    container.set_configuration(config)
    
    # Register infrastructure services (lazy imports to avoid circular dependencies)
    def create_auth_service():
        from infrastructure.google_api.authentication_service import AuthenticationFactory
        return AuthenticationFactory.create_service(config.google_api)
    
    def create_drive_repository():
        from infrastructure.google_api.google_drive_repository import GoogleDriveRepository
        auth_service = container.resolve(object)  # Will be replaced with proper type
        return GoogleDriveRepository(auth_service.get_drive_service())
    
    def create_permission_repository():
        from infrastructure.google_api.google_permission_repository import GooglePermissionRepository
        auth_service = container.resolve(object)  # Will be replaced with proper type
        return GooglePermissionRepository(auth_service.get_drive_service())
    
    def create_cache_repository():
        from infrastructure.cache.file_cache_repository import FileCacheRepository
        return FileCacheRepository(
            cache_dir=config.cache.cache_dir,
            compression_enabled=config.cache.compression_enabled
        )
    
    def create_report_service():
        from infrastructure.reporting.report_generator import ReportGenerator
        return ReportGenerator(output_dir=config.reporting.output_dir)
    
    def create_audit_logger():
        from infrastructure.logging.audit_logger import AuditLogger
        return AuditLogger(
            log_dir=config.logging.log_dir,
            enabled=config.logging.audit_enabled
        )
    
    # Register domain services
    def create_permission_service():
        from domain.services.permission_service import PermissionService
        return PermissionService()
    
    def create_file_analysis_service():
        from domain.services.file_analysis_service import FileAnalysisService
        permission_service = create_permission_service()
        return FileAnalysisService(permission_service)
    
    # Register use cases
    def create_manage_access_use_case():
        from application.use_cases.manage_user_access_use_case import ManageUserAccessUseCase
        # Create dependencies (simplified - in production would use proper DI)
        drive_repo = create_drive_repository()
        permission_repo = create_permission_repository()
        cache_repo = create_cache_repository()
        report_service = create_report_service()
        audit_logger = create_audit_logger()
        permission_service = create_permission_service()
        file_analysis_service = create_file_analysis_service()
        
        return ManageUserAccessUseCase(
            drive_repository=drive_repo,
            permission_repository=permission_repo,
            cache_repository=cache_repo,
            report_service=report_service,
            audit_logger=audit_logger,
            permission_service=permission_service,
            file_analysis_service=file_analysis_service,
            config=config
        )
    
    # Register services
    container.register_singleton(object, create_auth_service)  # Auth service
    container.register_transient(object, create_manage_access_use_case)  # Use case
    
    from application.use_cases.manage_user_access_use_case import ManageUserAccessUseCase
    container.register_transient(ManageUserAccessUseCase, create_manage_access_use_case)
    
    return container
