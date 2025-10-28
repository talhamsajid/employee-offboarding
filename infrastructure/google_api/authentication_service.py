"""
Authentication Service with Factory Pattern
Handles OAuth2 and Service Account authentication
"""

import os
from typing import Any, Optional, Union
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from application.interfaces.services import IAuthenticationService
from domain.exceptions.access_manager_errors import AuthenticationError, ConfigurationError


class OAuth2AuthenticationService(IAuthenticationService):
    """
    OAuth2 Authentication Service
    
    Implements user-based OAuth2 authentication flow.
    """
    
    SCOPES = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.metadata.readonly',
        'https://www.googleapis.com/auth/spreadsheets'
    ]
    
    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.json'):
        """
        Initialize OAuth2 service
        
        Args:
            credentials_path: Path to OAuth2 credentials JSON
            token_path: Path to store authentication token
        """
        self._credentials_path = credentials_path
        self._token_path = token_path
        self._creds: Optional[Union[Credentials, Any]] = None
    
    def authenticate(self) -> Any:
        """
        Authenticate using OAuth2
        
        Returns:
            Credentials object
            
        Raises:
            AuthenticationError: If authentication fails
        """
        # Check if token.json exists with valid credentials
        if os.path.exists(self._token_path):
            self._creds = Credentials.from_authorized_user_file(self._token_path, self.SCOPES)
        
        # If there are no valid credentials, let the user log in
        if not self._creds or not self._creds.valid:
            if self._creds and self._creds.expired and self._creds.refresh_token:
                try:
                    self._creds.refresh(Request())
                except Exception as e:
                    raise AuthenticationError(
                        f"Failed to refresh credentials: {e}",
                        credentials_path=self._credentials_path,
                        auth_type="OAuth2"
                    )
            else:
                if not os.path.exists(self._credentials_path):
                    raise AuthenticationError(
                        f"Credentials file not found at {self._credentials_path}",
                        credentials_path=self._credentials_path,
                        auth_type="OAuth2"
                    )
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self._credentials_path, self.SCOPES)
                    self._creds = flow.run_local_server(port=0)
                except Exception as e:
                    raise AuthenticationError(
                        f"OAuth2 flow failed: {e}",
                        credentials_path=self._credentials_path,
                        auth_type="OAuth2"
                    )
            
            # Save the credentials for the next run
            if self._creds:
                try:
                    with open(self._token_path, 'w') as token:
                        token.write(self._creds.to_json())
                except Exception as e:
                    # Non-fatal error
                    pass
        
        return self._creds
    
    def get_drive_service(self) -> Any:
        """Get authenticated Google Drive service"""
        if not self._creds:
            self.authenticate()
        
        try:
            return build('drive', 'v3', credentials=self._creds)
        except HttpError as error:
            raise AuthenticationError(
                f"Failed to build Drive service: {error}",
                auth_type="OAuth2"
            )
    
    def get_sheets_service(self) -> Any:
        """Get authenticated Google Sheets service"""
        if not self._creds:
            self.authenticate()
        
        try:
            return build('sheets', 'v4', credentials=self._creds)
        except HttpError as error:
            raise AuthenticationError(
                f"Failed to build Sheets service: {error}",
                auth_type="OAuth2"
            )
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated"""
        return self._creds is not None and self._creds.valid


class ServiceAccountAuthenticationService(IAuthenticationService):
    """
    Service Account Authentication Service
    
    Implements domain-wide delegation with service account.
    """
    
    ADMIN_SCOPES = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/admin.directory.user.readonly'
    ]
    
    def __init__(self, service_account_path: str, admin_email: Optional[str] = None):
        """
        Initialize Service Account authentication
        
        Args:
            service_account_path: Path to service account JSON
            admin_email: Admin email to impersonate
        """
        self._service_account_path = service_account_path
        self._admin_email = admin_email
        self._creds: Optional[service_account.Credentials] = None
    
    def authenticate(self) -> Any:
        """
        Authenticate using service account
        
        Returns:
            Credentials object
            
        Raises:
            AuthenticationError: If authentication fails
        """
        if not os.path.exists(self._service_account_path):
            raise AuthenticationError(
                f"Service account file not found at {self._service_account_path}",
                credentials_path=self._service_account_path,
                auth_type="ServiceAccount"
            )
        
        try:
            # Load service account credentials
            self._creds = service_account.Credentials.from_service_account_file(
                self._service_account_path,
                scopes=self.ADMIN_SCOPES
            )
            
            # Impersonate admin user if specified
            if self._admin_email:
                self._creds = self._creds.with_subject(self._admin_email)
            
            return self._creds
        
        except Exception as e:
            raise AuthenticationError(
                f"Service account authentication failed: {e}",
                credentials_path=self._service_account_path,
                auth_type="ServiceAccount"
            )
    
    def get_drive_service(self) -> Any:
        """Get authenticated Google Drive service"""
        if not self._creds:
            self.authenticate()
        
        try:
            return build('drive', 'v3', credentials=self._creds)
        except HttpError as error:
            raise AuthenticationError(
                f"Failed to build Drive service: {error}",
                auth_type="ServiceAccount"
            )
    
    def get_sheets_service(self) -> Any:
        """Get authenticated Google Sheets service"""
        if not self._creds:
            self.authenticate()
        
        try:
            return build('sheets', 'v4', credentials=self._creds)
        except HttpError as error:
            raise AuthenticationError(
                f"Failed to build Sheets service: {error}",
                auth_type="ServiceAccount"
            )
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated"""
        return self._creds is not None


class AuthenticationFactory:
    """
    Authentication Factory (Factory Pattern)
    
    Creates appropriate authentication service based on configuration.
    """
    
    @staticmethod
    def create_oauth2_authenticator(
        credentials_path: str = 'credentials.json',
        token_path: str = 'token.json'
    ) -> IAuthenticationService:
        """
        Create OAuth2 authenticator
        
        Args:
            credentials_path: Path to OAuth2 credentials
            token_path: Path to token file
            
        Returns:
            OAuth2AuthenticationService instance
        """
        return OAuth2AuthenticationService(credentials_path, token_path)
    
    @staticmethod
    def create_service_account_authenticator(
        service_account_path: str,
        admin_email: Optional[str] = None
    ) -> IAuthenticationService:
        """
        Create Service Account authenticator
        
        Args:
            service_account_path: Path to service account JSON
            admin_email: Admin email to impersonate
            
        Returns:
            ServiceAccountAuthenticationService instance
        """
        return ServiceAccountAuthenticationService(service_account_path, admin_email)
    
    @staticmethod
    def create_from_config(config: Any) -> IAuthenticationService:
        """
        Create authenticator from configuration
        
        Args:
            config: Configuration object with google_api settings
            
        Returns:
            Appropriate IAuthenticationService implementation
        """
        # Use service account if configured
        if hasattr(config, 'google_api') and config.google_api.service_account_path:
            return AuthenticationFactory.create_service_account_authenticator(
                config.google_api.service_account_path,
                config.google_api.admin_email
            )
        
        # Default to OAuth2
        credentials_path = config.google_api.credentials_path if hasattr(config, 'google_api') else 'credentials.json'
        token_path = config.google_api.token_path if hasattr(config, 'google_api') else 'token.json'
        
        return AuthenticationFactory.create_oauth2_authenticator(credentials_path, token_path)
