"""
Base Google API Manager

This module provides the base class for all Google API managers.
"""

from google.oauth2 import service_account

class GoogleAPIManager:
    """
    Base class for Google API services.
    """

    def __init__(self, key_file, scopes):
        if not key_file:
            raise ValueError("Key file path must be provided")
        if not scopes:
            raise ValueError("At least one scope must be provided")

        try:
            self.credentials = service_account.Credentials.from_service_account_file(
                key_file, scopes=scopes)
        except FileNotFoundError:
            raise FileNotFoundError(f"Service account key file not found: {key_file}")
        except Exception as e:
            raise ValueError(f"Failed to initialize credentials: {str(e)}")
