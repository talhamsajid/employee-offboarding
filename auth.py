"""
Google Drive API Authentication Module
Handles OAuth2 authentication for Google Drive and related APIs
Supports both user OAuth2 and service account with domain-wide delegation
"""

import os
import json
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/spreadsheets'
]

# Admin scopes for domain-wide delegation
ADMIN_SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/admin.directory.user.readonly'
]


class GoogleAPIAuthenticator:
    """Handles authentication for Google APIs"""

    def __init__(self, credentials_json_path='credentials.json', token_path='token.json',
                 service_account_path=None, admin_email=None):
        """
        Initialize the authenticator

        Args:
            credentials_json_path: Path to the OAuth2 credentials JSON file
            token_path: Path to store the authentication token
            service_account_path: Path to service account JSON (for domain-wide delegation)
            admin_email: Admin email to impersonate (for domain-wide delegation)
        """
        self.credentials_json_path = credentials_json_path
        self.token_path = token_path
        self.service_account_path = service_account_path
        self.admin_email = admin_email
        self.creds = None
        self.use_service_account = service_account_path is not None

    def authenticate(self):
        """
        Authenticate with Google APIs using OAuth2 or Service Account

        Returns:
            Credentials object
        """
        # Use service account with domain-wide delegation if specified
        if self.use_service_account:
            return self._authenticate_service_account()

        # Standard OAuth2 flow
        # Check if token.json exists with valid credentials
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        # If there are no valid credentials, let the user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print("Refreshing expired credentials...")
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_json_path):
                    raise FileNotFoundError(
                        f"Credentials file not found at {self.credentials_json_path}.\n"
                        "Please download OAuth2 credentials from Google Cloud Console."
                    )

                print("Starting OAuth2 authentication flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_json_path, SCOPES)
                self.creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())
            print("Authentication successful!")

        return self.creds

    def _authenticate_service_account(self):
        """
        Authenticate using service account with domain-wide delegation

        Returns:
            Credentials object
        """
        if not os.path.exists(self.service_account_path):
            raise FileNotFoundError(
                f"Service account file not found at {self.service_account_path}"
            )

        print("Authenticating with service account (domain-wide delegation)...")

        # Load service account credentials
        self.creds = service_account.Credentials.from_service_account_file(
            self.service_account_path,
            scopes=ADMIN_SCOPES
        )

        # Impersonate admin user if specified
        if self.admin_email:
            print(f"Impersonating admin user: {self.admin_email}")
            self.creds = self.creds.with_subject(self.admin_email)

        print("Service account authentication successful!")
        return self.creds

    def get_drive_service(self):
        """
        Get authenticated Google Drive service

        Returns:
            Google Drive API service object
        """
        if not self.creds:
            self.authenticate()

        try:
            service = build('drive', 'v3', credentials=self.creds)
            return service
        except HttpError as error:
            print(f"An error occurred: {error}")
            raise

    def get_sheets_service(self):
        """
        Get authenticated Google Sheets service

        Returns:
            Google Sheets API service object
        """
        if not self.creds:
            self.authenticate()

        try:
            service = build('sheets', 'v4', credentials=self.creds)
            return service
        except HttpError as error:
            print(f"An error occurred: {error}")
            raise


def setup_credentials_from_input(credentials_json_content):
    """
    Save credentials JSON content to file

    Args:
        credentials_json_content: JSON string or dict of credentials
    """
    if isinstance(credentials_json_content, str):
        credentials_json_content = json.loads(credentials_json_content)

    with open('credentials.json', 'w') as f:
        json.dump(credentials_json_content, f, indent=2)

    print("Credentials saved to credentials.json")
