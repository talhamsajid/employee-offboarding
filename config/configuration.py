"""
Configuration Management
Centralized configuration with validation
"""

import os
import yaml
from typing import Optional, List, Dict, Any
from pathlib import Path
from dataclasses import dataclass, field

from domain.exceptions.access_manager_errors import ConfigurationError


@dataclass
class GoogleAPIConfig:
    """Google API configuration"""
    credentials_path: str = "credentials.json"
    token_path: str = "token.json"
    service_account_path: Optional[str] = None
    admin_email: Optional[str] = None
    scopes: List[str] = field(default_factory=lambda: [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.metadata.readonly',
        'https://www.googleapis.com/auth/spreadsheets'
    ])
    page_size: int = 100
    rate_limit_delay: float = 0.1
    max_retries: int = 3
    timeout_seconds: int = 30
    
    def validate(self) -> None:
        """Validate Google API configuration"""
        if self.page_size < 1 or self.page_size > 1000:
            raise ConfigurationError(
                "Invalid page_size: must be between 1 and 1000",
                config_key="google_api.page_size"
            )
        
        if self.rate_limit_delay < 0:
            raise ConfigurationError(
                "Invalid rate_limit_delay: must be non-negative",
                config_key="google_api.rate_limit_delay"
            )
        
        if self.service_account_path and not os.path.exists(self.service_account_path):
            raise ConfigurationError(
                f"Service account file not found: {self.service_account_path}",
                config_key="google_api.service_account_path"
            )


@dataclass
class CacheConfig:
    """Cache configuration"""
    enabled: bool = True
    cache_dir: str = "cache"
    default_ttl_days: int = 7
    max_size_mb: int = 100
    compression_enabled: bool = True
    
    def validate(self) -> None:
        """Validate cache configuration"""
        if self.default_ttl_days < 0:
            raise ConfigurationError(
                "Invalid default_ttl_days: must be non-negative",
                config_key="cache.default_ttl_days"
            )
        
        if self.max_size_mb < 1:
            raise ConfigurationError(
                "Invalid max_size_mb: must be at least 1",
                config_key="cache.max_size_mb"
            )


@dataclass
class ReportingConfig:
    """Reporting configuration"""
    output_dir: str = "reports"
    default_formats: List[str] = field(default_factory=lambda: ["csv", "excel"])
    include_metadata: bool = True
    timestamp_format: str = "%Y%m%d_%H%M%S"
    excel_engine: str = "openpyxl"
    csv_delimiter: str = ","
    json_indent: int = 2
    
    def validate(self) -> None:
        """Validate reporting configuration"""
        valid_formats = {"csv", "excel", "json", "html"}
        for fmt in self.default_formats:
            if fmt.lower() not in valid_formats:
                raise ConfigurationError(
                    f"Invalid report format: {fmt}",
                    config_key="reporting.default_formats"
                )
        
        if self.json_indent < 0:
            raise ConfigurationError(
                "Invalid json_indent: must be non-negative",
                config_key="reporting.json_indent"
            )


@dataclass
class LoggingConfig:
    """Logging configuration"""
    enabled: bool = True
    log_dir: str = "logs"
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    audit_enabled: bool = True
    audit_file: str = "audit.log"
    max_log_size_mb: int = 10
    backup_count: int = 5
    
    def validate(self) -> None:
        """Validate logging configuration"""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level.upper() not in valid_levels:
            raise ConfigurationError(
                f"Invalid log_level: {self.log_level}",
                config_key="logging.log_level"
            )


@dataclass
class AppConfiguration:
    """
    Application configuration
    
    Central configuration object for the entire application.
    Supports loading from multiple sources with priority.
    """
    google_api: GoogleAPIConfig = field(default_factory=GoogleAPIConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    reporting: ReportingConfig = field(default_factory=ReportingConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Application-level settings
    app_name: str = "Google Drive Access Manager"
    version: str = "2.0.0"
    debug_mode: bool = False
    
    def validate(self) -> None:
        """
        Validate all configuration sections
        
        Raises:
            ConfigurationError: If any configuration is invalid
        """
        self.google_api.validate()
        self.cache.validate()
        self.reporting.validate()
        self.logging.validate()
    
    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist"""
        directories = [
            self.cache.cache_dir,
            self.reporting.output_dir,
            self.logging.log_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)


class ConfigurationLoader:
    """
    Configuration Loader
    
    Loads configuration from multiple sources with priority:
    1. Command-line arguments (highest priority)
    2. Environment variables
    3. Configuration file (YAML)
    4. Hardcoded defaults (lowest priority)
    """
    
    DEFAULT_CONFIG_FILE = "config.yaml"
    
    @classmethod
    def load_from_file(cls, config_path: str) -> AppConfiguration:
        """
        Load configuration from YAML file
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            AppConfiguration object
            
        Raises:
            ConfigurationError: If file cannot be loaded
        """
        if not os.path.exists(config_path):
            raise ConfigurationError(
                f"Configuration file not found: {config_path}",
                config_file=config_path
            )
        
        try:
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)
            
            return cls._parse_config_data(data or {})
        
        except yaml.YAMLError as e:
            raise ConfigurationError(
                f"Failed to parse YAML configuration: {e}",
                config_file=config_path
            )
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load configuration: {e}",
                config_file=config_path
            )
    
    @classmethod
    def load_from_env(cls) -> AppConfiguration:
        """
        Load configuration from environment variables
        
        Environment variables follow pattern: GDAM_<SECTION>_<KEY>
        Example: GDAM_CACHE_ENABLED=false
        
        Returns:
            AppConfiguration object
        """
        config = AppConfiguration()
        
        # Cache settings
        cache_enabled = os.getenv('GDAM_CACHE_ENABLED')
        if cache_enabled:
            config.cache.enabled = cache_enabled.lower() == 'true'
        cache_dir = os.getenv('GDAM_CACHE_DIR')
        if cache_dir:
            config.cache.cache_dir = cache_dir
        cache_ttl = os.getenv('GDAM_CACHE_TTL_DAYS')
        if cache_ttl:
            config.cache.default_ttl_days = int(cache_ttl)
        
        # Google API settings
        creds_path = os.getenv('GDAM_CREDENTIALS_PATH')
        if creds_path:
            config.google_api.credentials_path = creds_path
        sa_path = os.getenv('GDAM_SERVICE_ACCOUNT_PATH')
        if sa_path:
            config.google_api.service_account_path = sa_path
        admin_email = os.getenv('GDAM_ADMIN_EMAIL')
        if admin_email:
            config.google_api.admin_email = admin_email
        
        # Reporting settings
        report_dir = os.getenv('GDAM_REPORT_DIR')
        if report_dir:
            config.reporting.output_dir = report_dir
        
        # Logging settings
        log_level = os.getenv('GDAM_LOG_LEVEL')
        if log_level:
            config.logging.log_level = log_level
        
        # Debug mode
        if os.getenv('GDAM_DEBUG'):
            config.debug_mode = os.getenv('GDAM_DEBUG', 'false').lower() == 'true'
        
        return config
    
    @classmethod
    def load_default(cls) -> AppConfiguration:
        """
        Load default configuration
        
        Returns:
            AppConfiguration with default values
        """
        config = AppConfiguration()
        config.validate()
        return config
    
    @classmethod
    def load(cls, config_file: Optional[str] = None) -> AppConfiguration:
        """
        Load configuration from all sources with priority
        
        Priority order:
        1. Configuration file (if provided)
        2. Environment variables
        3. Defaults
        
        Args:
            config_file: Optional path to configuration file
            
        Returns:
            Merged AppConfiguration object
        """
        # Start with defaults
        config = cls.load_default()
        
        # Merge environment variables
        env_config = cls.load_from_env()
        config = cls._merge_configs(config, env_config)
        
        # Merge file configuration if provided
        if config_file and os.path.exists(config_file):
            file_config = cls.load_from_file(config_file)
            config = cls._merge_configs(config, file_config)
        elif config_file:
            # File specified but doesn't exist - create default
            cls._create_default_config_file(config_file)
        
        # Validate final configuration
        config.validate()
        config.ensure_directories()
        
        return config
    
    @classmethod
    def _parse_config_data(cls, data: Dict[str, Any]) -> AppConfiguration:
        """Parse configuration data dictionary into AppConfiguration"""
        config = AppConfiguration()
        
        # Parse Google API config
        if 'google_api' in data:
            api_data = data['google_api']
            config.google_api = GoogleAPIConfig(**api_data)
        
        # Parse cache config
        if 'cache' in data:
            cache_data = data['cache']
            config.cache = CacheConfig(**cache_data)
        
        # Parse reporting config
        if 'reporting' in data:
            report_data = data['reporting']
            config.reporting = ReportingConfig(**report_data)
        
        # Parse logging config
        if 'logging' in data:
            log_data = data['logging']
            config.logging = LoggingConfig(**log_data)
        
        # Parse app-level settings
        if 'app_name' in data:
            config.app_name = data['app_name']
        if 'version' in data:
            config.version = data['version']
        if 'debug_mode' in data:
            config.debug_mode = data['debug_mode']
        
        return config
    
    @classmethod
    def _merge_configs(cls, base: AppConfiguration, override: AppConfiguration) -> AppConfiguration:
        """
        Merge two configurations (override takes precedence)
        
        Args:
            base: Base configuration
            override: Configuration to merge (takes precedence)
            
        Returns:
            Merged configuration
        """
        # For now, return override if provided, otherwise base
        # In a full implementation, would merge field-by-field
        return override if override else base
    
    @classmethod
    def _create_default_config_file(cls, config_path: str) -> None:
        """Create a default configuration file"""
        config = cls.load_default()
        
        config_data = {
            'app_name': config.app_name,
            'version': config.version,
            'debug_mode': config.debug_mode,
            'google_api': {
                'credentials_path': config.google_api.credentials_path,
                'token_path': config.google_api.token_path,
                'page_size': config.google_api.page_size,
                'rate_limit_delay': config.google_api.rate_limit_delay,
                'max_retries': config.google_api.max_retries,
            },
            'cache': {
                'enabled': config.cache.enabled,
                'cache_dir': config.cache.cache_dir,
                'default_ttl_days': config.cache.default_ttl_days,
                'max_size_mb': config.cache.max_size_mb,
            },
            'reporting': {
                'output_dir': config.reporting.output_dir,
                'default_formats': config.reporting.default_formats,
                'include_metadata': config.reporting.include_metadata,
            },
            'logging': {
                'enabled': config.logging.enabled,
                'log_dir': config.logging.log_dir,
                'log_level': config.logging.log_level,
                'audit_enabled': config.logging.audit_enabled,
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
